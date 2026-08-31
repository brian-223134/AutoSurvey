import os
import re
import numpy as np
import tiktoken
from tqdm import trange,tqdm
import time
import torch
from src.model import APIModel
from src.database import database
from src.utils import tokenCounter
from src.prompt import ROUGH_OUTLINE_PROMPT, MERGING_OUTLINE_PROMPT, SUBSECTION_OUTLINE_PROMPT, EDIT_FINAL_OUTLINE_PROMPT
from transformers import AutoModel, AutoTokenizer,  AutoModelForSequenceClassification

# 원본은 `outline.split('Subsection 1: ')[1]` 처럼 정확한 문자열 일치에 의존했다.
# Claude-3-Haiku는 형식을 잘 지켰지만 다른 모델은 "**Subsection 1:** ..." 처럼
# 마크다운 장식을 붙이거나 콜론 뒤 공백을 빠뜨려 IndexError로 죽는다.
# 번호를 키로 삼는 관대한 정규식으로 바꾼다.
def _labelled(word):
    return re.compile(
        r'^[\s>*_#\-]*' + word + r'\s*(\d+)\s*[:.\-]\s*\**\s*(.+?)\s*\**\s*$',
        re.MULTILINE)


SECTION_RE = re.compile(
    r'^[\s>*_#\-]*(?<!Sub)Section\s*(\d+)\s*[:.\-]\s*\**\s*(.+?)\s*\**\s*$',
    re.MULTILINE)
SUBSECTION_RE = _labelled('Subsection')
DESCRIPTION_RE = _labelled('Description')
TITLE_RE = re.compile(r'^[\s>*_#\-]*Title\s*[:.]\s*\**\s*(.+?)\s*\**\s*$', re.MULTILINE)


def _strip_decoration(text):
    return text.strip().strip('*_# ').strip()


def _numbered_pairs(outline, name_re):
    """'<Name> N: 제목' / 'Description N: 설명' 쌍을 번호 기준으로 묶는다.

    설명이 없는 항목은 빈 문자열로 채운다. 호출부가 두 리스트를 zip 하므로
    길이가 어긋나면 항목이 조용히 유실되기 때문이다.
    """
    names = {int(n): _strip_decoration(v) for n, v in name_re.findall(outline)}
    descs = {int(n): _strip_decoration(v) for n, v in DESCRIPTION_RE.findall(outline)}
    keys = sorted(names)
    return [names[k] for k in keys], [descs.get(k, '') for k in keys]


class outlineWriter():

    def __init__(self, model:str, api_key:str, api_url:str, database, subsection_num:int = 0,
                 enforce_section_num:bool = False) -> None:

        self.model, self.api_key, self.api_url = model, api_key, api_url
        self.api_model = APIModel(self.model, self.api_key, self.api_url)

        self.db = database
        self.token_counter = tokenCounter()
        self.input_token_usage, self.output_token_usage = 0, 0
        # 서브섹션 개수 상한. 0이면 원본 그대로 — 프롬프트에 'several'이 들어가고
        # 개수는 모델 재량이 된다. 원본 AutoSurvey의 동작을 기본값으로 유지한다.
        self.subsection_num = subsection_num
        # 섹션 수를 merge 단계까지 관철할지. [SECTION NUM]은 러프 아웃라인 프롬프트에만
        # 있어서 최종 개수를 정하는 merge에서 소실된다 — retrieval shuffle 때문에
        # 지시 5가 8로 드리프트하기도 한다(2026-08-31 실측, 논문은 "predetermined"라
        # 명시). False(기본)면 merge 프롬프트가 원본과 글자 단위로 같다.
        self.enforce_section_num = enforce_section_num

    def draft_outline(self, topic, reference_num = 600, chunk_size = 30000, section_num = 6):
        # Get database
        references_ids = self.db.get_ids_from_query(topic, num = reference_num, shuffle = True)
        references_infos = self.db.get_paper_info_from_ids(references_ids)

        references_titles = [r['title'] for r in references_infos]
        references_abs = [r['abs'] for r in references_infos]
        abs_chunks, titles_chunks = self.chunking(references_abs, references_titles, chunk_size=chunk_size)

        # generate rough section-level outline
        outlines = self.generate_rough_outlines(topic=topic, papers_chunks = abs_chunks, titles_chunks = titles_chunks, section_num=section_num)
        
        # merge outline
        section_outline = self.merge_outlines(topic=topic, outlines=outlines,
                                              section_num=section_num if self.enforce_section_num else 0)

        # generate subsection-level outline
        subsection_outlines = self.generate_subsection_outlines(topic=topic, section_outline= section_outline,rag_num= 50)
        
        merged_outline = self.process_outlines(section_outline, subsection_outlines)

        # edit final outline
        final_outline = self.edit_final_outline(merged_outline, topic)

        return final_outline

    def without_merging(self, topic, reference_num = 600, chunk_size = 30000, section_num = 6):
        references_ids = self.db.get_ids_from_topic(topic = topic, num = reference_num, shuffle = False)
        references_infos = self.db.get_paper_info_from_ids(references_ids)

        references_titles = [r['title'] for r in references_infos]
        references_papers = [r['abs'] for r in references_infos]
        papers_chunks, titles_chunks = self.chunking(references_papers, references_titles, chunk_size=chunk_size)

        # generate rough section-level outline
        section_outline = self.generate_rough_outlines(topic=topic, papers_chunks = [papers_chunks[0]], titles_chunks = [titles_chunks[0]], section_num=section_num)[0]
        
        # generate subsection-level outline
        subsection_outlines = self.generate_subsection_outlines(topic=topic, section_outline= section_outline)
        
        final_outline = self.process_outlines(section_outline, subsection_outlines)

        return final_outline, section_outline, subsection_outlines

    def compute_price(self):
        return self.token_counter.compute_price(input_tokens=self.input_token_usage, output_tokens=self.output_token_usage, model=self.model)

    def generate_rough_outlines(self, topic, papers_chunks, titles_chunks, section_num = 8):
        '''
        You wants to write a overall and comprehensive academic survey about "[TOPIC]".\n\
        You are provided with a list of papers related to the topic below:\n\
        ---
        [PAPER LIST]
        ---
        You need to draft a outline based on the given papers.
        The outline should contains a title and several sections.
        Each section follows with a brief sentence to describe what to write in this section.
        The outline is supposed to be comprehensive and contains [SECTION NUM] sections.

        Return in the format:
        <format>
        Title: [TITLE OF THE SURVEY]
        Section 1: [NAME OF SECTION 1]
        Description 1: [DESCRIPTION OF SENTCTION 1]

        Section 2: [NAME OF SECTION 2]
        Description 2: [DESCRIPTION OF SENTCTION 2]

        ...

        Section K: [NAME OF SECTION K]
        Description K: [DESCRIPTION OF SENTCTION K]
        </format>
        The outline:
        '''

        prompts = []

        for i in trange(len(papers_chunks)):
            titles = titles_chunks[i]
            papers = papers_chunks[i]
            paper_texts = '' 
            for i, t, p in zip(range(len(papers)), titles, papers):
                paper_texts += f'---\npaper_title: {t}\n\npaper_content:\n\n{p}\n'
            paper_texts+='---\n'

            prompt = self.__generate_prompt(ROUGH_OUTLINE_PROMPT, paras={'PAPER LIST': paper_texts, 'TOPIC': topic, 'SECTION NUM': str(section_num)})
            prompts.append(prompt)
        self.input_token_usage += self.token_counter.num_tokens_from_list_string(prompts)
        outlines = self.api_model.batch_chat(text_batch=prompts, temperature=1)
        self.output_token_usage += self.token_counter.num_tokens_from_list_string(outlines)
        return outlines
    
    def merge_outlines(self, topic, outlines, section_num=0):
        '''
        You are an expert in artificial intelligence who wants to write a overall survey about [TOPIC].\n\
        You are provided with a list of outlines as candidates below:\n\
        ---
        [OUTLINE LIST]
        ---
        Each outline contains a title and several sections.\n\
        Each section follows with a brief sentence to describe what to write in this section.\n\n\
        You need to generate a final outline based on these provided outlines.\n\
        Return in the format:
        <format>
        Title: [TITLE OF THE SURVEY]
        Section 1: [NAME OF SECTION 1]
        Description 1: [DESCRIPTION OF SENTCTION 1]

        Section 2: [NAME OF SECTION 2]
        Description 2: [DESCRIPTION OF SENTCTION 2]

        ...

        Section K: [NAME OF SECTION K]
        Description K: [DESCRIPTION OF SENTCTION K]
        </format>
        Only return the final outline without any other informations:
        '''
        outline_texts = '' 
        for i, o in zip(range(len(outlines)), outlines):
            outline_texts += f'---\noutline_id: {i}\n\noutline_content:\n\n{o}\n'
        outline_texts+='---\n'
        # section_num=0(기본)이면 빈 문자열이 들어가 원본 프롬프트와 글자 단위로 같다.
        # 문구는 러프 아웃라인 프롬프트의 해당 문장과 같은 어법을 쓴다.
        constraint = (f'\nThe final outline is supposed to contain {section_num} sections.'
                      if section_num else '')
        prompt = self.__generate_prompt(MERGING_OUTLINE_PROMPT,
                                        paras={'OUTLINE LIST': outline_texts, 'TOPIC':topic,
                                               'SECTION NUM CONSTRAINT': constraint})
        self.input_token_usage += self.token_counter.num_tokens_from_string(prompt)

        outline = self.api_model.chat(prompt, temperature=1)
        self.output_token_usage += self.token_counter.num_tokens_from_string(outline)
        return outline
    
    def generate_subsection_outlines(self, topic, section_outline, rag_num):
        '''
        You are an expert in artificial intelligence who wants to write a overall survey about [TOPIC].\n\
        You have created a overall outline below:\n\
        ---
        [OVERALL OUTLINE]
        ---
        The outline contains a title and several sections.\n\
        Each section follows with a brief sentence to describe what to write in this section.\n\n\
        <instruction>
        You need to enrich the section [SECTION NAME].
        The description of [SECTION NAME]: [SECTION DESCRIPTION]
        You need to generate the framwork containing [SUBSECTION NUM] subsections based on the overall outlines.\n\
        Each subsection follows with a brief sentence to describe what to write in this subsection.
        These papers provided for references:
        ---
        [PAPER LIST]
        ---
        Return the outline in the format:
        <format>
        Subsection 1: [NAME OF SUBSECTION 1]
        Description 1: [DESCRIPTION OF SUBSENTCTION 1]

        Subsection 2: [NAME OF SUBSECTION 2]
        Description 2: [DESCRIPTION OF SUBSENTCTION 2]

        ...

        Subsection K: [NAME OF SUBSECTION K]
        Description K: [DESCRIPTION OF SUBSENTCTION K]
        </format>
        </instruction>
        Only return the outline without any other informations:
        '''


        survey_title, survey_sections, survey_section_descriptions = self.extract_title_sections_descriptions(section_outline)

        prompts = []

        for section_name, section_description in zip(survey_sections, survey_section_descriptions):
            references_ids = self.db.get_ids_from_query(section_description, num = rag_num, shuffle = True)
            references_infos = self.db.get_paper_info_from_ids(references_ids)

            references_titles = [r['title'] for r in references_infos]
            references_papers = [r['abs'] for r in references_infos]
            paper_texts = '' 
            for i, t, p in zip(range(len(references_papers)), references_titles, references_papers):
                paper_texts += f'---\npaper_title: {t}\n\npaper_content:\n\n{p}\n'
            paper_texts+='---\n'
            prompt = self.__generate_prompt(SUBSECTION_OUTLINE_PROMPT, paras={'OVERALL OUTLINE': section_outline,'SECTION NAME': section_name,\
                                                                          'SECTION DESCRIPTION':section_description,'TOPIC':topic,'PAPER LIST':paper_texts,\
                                                                          'SUBSECTION NUM': self._subsection_num_phrase()})
            prompts.append(prompt)
        self.input_token_usage += self.token_counter.num_tokens_from_list_string(prompts)

        sub_outlines = self.api_model.batch_chat(prompts, temperature=1)

        self.output_token_usage += self.token_counter.num_tokens_from_list_string(sub_outlines)
        return sub_outlines

    def edit_final_outline(self, outline, topic):
        '''
        You are an expert in artificial intelligence who wants to write a overall survey about [TOPIC].\n\
        You have created a draft outline below:\n\
        ---
        [OVERALL OUTLINE]
        ---
        The outline contains a title and several sections.\n\
        Each section follows with a brief sentence to describe what to write in this section.\n\n\
        Under each section, there are several subsections.
        Each subsection also follows with a brief sentence of descripition.
        You need to modify the outline to make it both comprehensive and coherent with no repeated subsections.
        Return the final outline in the format:
        <format>
        # [TITLE OF SURVEY]

        ## [NAME OF SECTION 1]

        ### [NAME OF SUBSECTION 1]

        ### [NAME OF SUBSECTION 2]

        ...

        ### [NAME OF SUBSECTION L]
        
        ## [NAME OF SECTION 2]

        ...

        ## [NAME OF SECTION K]

        ...
        </format>
        Only return the final outline without any other informations:
        '''

        # TOPIC을 넘기지 않으면 프롬프트에 리터럴 '[TOPIC]'이 그대로 남는다.
        prompt = self.__generate_prompt(EDIT_FINAL_OUTLINE_PROMPT, paras={'OVERALL OUTLINE': outline, 'TOPIC': topic})
        self.input_token_usage += self.token_counter.num_tokens_from_string(prompt)
        outline = self.api_model.chat(prompt, temperature=1)
        self.output_token_usage += self.token_counter.num_tokens_from_string(outline)
        return outline.replace('<format>\n','').replace('</format>','')
 
    def __generate_prompt(self, template, paras):
        prompt = template
        for k in paras.keys():
            prompt = prompt.replace(f'[{k}]', paras[k])
        return prompt
    
    def extract_title_sections_descriptions(self, outline):
        title_m = TITLE_RE.search(outline)
        if title_m:
            title = title_m.group(1).strip()
        else:
            # Title 줄이 없으면 첫 비어있지 않은 줄을 제목으로 쓴다.
            lines = [l.strip() for l in outline.split('\n') if l.strip()]
            title = _strip_decoration(lines[0]) if lines else 'Survey'

        sections, descriptions = _numbered_pairs(outline, SECTION_RE)
        if not sections:
            raise RuntimeError(
                'LLM 응답에서 "Section N: ..." 을 찾지 못했습니다. 원본 응답:\n'
                + outline[:1000])
        return title, sections, descriptions

    def extract_subsections_subdescriptions(self, outline):
        return _numbered_pairs(outline, SUBSECTION_RE)
    
    def chunking(self, papers, titles, chunk_size = 14000):
        paper_chunks, title_chunks = [], []
        total_length = self.token_counter.num_tokens_from_list_string(papers)
        num_of_chunks = int(total_length / chunk_size) + 1
        avg_len = int(total_length / num_of_chunks) + 1
        split_points = []
        l = 0
        for j in range(len(papers)):
            l += self.token_counter.num_tokens_from_string(papers[j])
            if l > avg_len:
                l = 0
                split_points.append(j)
                continue
        start = 0
        for point in split_points:
            paper_chunks.append(papers[start:point])
            title_chunks.append(titles[start:point])
            start = point
        paper_chunks.append(papers[start:])
        title_chunks.append(titles[start:])
        return paper_chunks, title_chunks
       
    def _subsection_num_phrase(self):
        """프롬프트에 들어갈 개수 표현.

        기본값(0)이면 원본과 **글자 단위로 같은** 'several'이 들어간다.
        분량 통제가 필요할 때만 숫자를 박는다.
        """
        return 'several' if not self.subsection_num else f'exactly {self.subsection_num}'

    def process_outlines(self, section_outline, sub_outlines):
        res = ''
        survey_title, survey_sections, survey_section_descriptions = self.extract_title_sections_descriptions(outline=section_outline)
        res += f'# {survey_title}\n\n'
        for i in range(len(survey_sections)):
            section = survey_sections[i]
            res += f'## {i+1} {section}\nDescription: {survey_section_descriptions[i]}\n\n'
            subsections, subsection_descriptions = self.extract_subsections_subdescriptions(sub_outlines[i])
            # 프롬프트로 개수를 지시해도 모델이 넘길 수 있다. 여기서 잘라 상한을 보장한다.
            # 앞에서부터 남기는 이유: 아웃라인은 논리 순서로 생성되므로 뒤쪽이 부수적이다.
            if self.subsection_num and len(subsections) > self.subsection_num:
                subsections = subsections[:self.subsection_num]
                subsection_descriptions = subsection_descriptions[:self.subsection_num]
            for j in range(len(subsections)):
                subsection = subsections[j]
                res += f'### {i+1}.{j+1} {subsection}\nDescription: {subsection_descriptions[j]}\n\n'
        return res

