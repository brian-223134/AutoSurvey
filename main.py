import os
import json
import argparse
import requests
from src.agents.outline_writer import outlineWriter
from src.agents.writer import subsectionWriter
from src.agents.judge import Judge
from src.database import database
from tqdm import tqdm
import time

def remove_descriptions(text):
    lines = text.split('\n')
    
    filtered_lines = [line for line in lines if not line.strip().startswith("Description")]
    
    result = '\n'.join(filtered_lines)
    
    return result

def write(topic, model, section_num, subsection_len, rag_num, refinement):
    outline, outline_wo_description = write_outline(topic, model, section_num)

    if refinement:
        raw_survey, raw_survey_with_references, raw_references, refined_survey, refined_survey_with_references, refined_references = write_subsection(topic, model, outline, subsection_len = subsection_len, rag_num = rag_num, refinement = True)
        return refined_survey_with_references
    else:
        raw_survey, raw_survey_with_references, raw_references = write_subsection(topic, model, outline, subsection_len = subsection_len, rag_num = rag_num, refinement = False)
        return raw_survey_with_references

def write_outline(topic, model, section_num, outline_reference_num, db, api_key, api_url, subsection_num=0,
                  enforce_section_num=False):
    outline_writer = outlineWriter(model=model, api_key=api_key, api_url = api_url, database=db,
                                   subsection_num=subsection_num, enforce_section_num=enforce_section_num)
    hello = outline_writer.api_model.chat('hello')
    if hello is None:
        raise RuntimeError('API 연결 실패: 위의 [APIModel] 로그를 확인하세요 (--api_url / --api_key / 서버 상태)')
    print(hello)
    outline = outline_writer.draft_outline(topic, outline_reference_num, 30000, section_num)
    report_usage('outline', outline_writer)
    return outline, remove_descriptions(outline)


def report_usage(stage, agent):
    """tiktoken 추정치와 API가 실제로 청구한 값을 함께 출력한다.

    둘이 벌어지면 재시도나 추론 토큰 때문이므로 원인을 바로 알 수 있다.
    """
    u = agent.api_model.usage
    print(f'[tokens] {stage:7s} 추정 in={agent.input_token_usage:,} out={agent.output_token_usage:,}',
          flush=True)
    print(f'[usage]  {stage:7s} 청구 in={u["prompt"]:,} out={u["completion"]:,} '
          f'(추론 {u["reasoning"]:,}) 비용 ${u["cost"]:.4f} 재시도 {agent.api_model.retry_count}회',
          flush=True)
    # 잘림은 조용히 넘어가면 안 된다. 문장이 끊긴 서브섹션이 그대로 서베이에 들어간다.
    if getattr(agent.api_model, 'truncated', 0):
        print(f'[usage]  {stage:7s} ⚠ 출력 잘림 {agent.api_model.truncated}건 — '
              f'해당 서브섹션은 문장 중간에서 끊겼습니다. provider 출력 한도나 '
              f'reasoning 설정을 확인하세요', flush=True)
    # 재시도를 다 쓴 요청이 하나라도 있으면 그 서브섹션은 비어 있다. 저장하면
    # 섹션이 빠진 서베이가 조용히 남고, check_survey.py 도 인용만 보므로 잡지 못한다.
    # 부분 산출물을 남기느니 여기서 멈춘다.
    failed = getattr(agent.api_model, 'failed', 0)
    if failed:
        raise RuntimeError(
            f'{stage} 단계에서 {failed}개 요청이 재시도를 다 쓰고 실패했습니다. '
            f'해당 서브섹션이 비어 있으므로 저장하지 않고 중단합니다.\n'
            f'  · 429였다면 AUTOSURVEY_MAX_THREADS를 낮추세요(현재 '
            f'{os.environ.get("AUTOSURVEY_MAX_THREADS", "15")}).\n'
            f'  · 재시도 한도는 AUTOSURVEY_MAX_RETRY로 올릴 수 있습니다(현재 '
            f'{os.environ.get("AUTOSURVEY_MAX_RETRY", "8")}).')

def write_subsection(topic, model, outline, subsection_len, rag_num, db, api_key, api_url, refinement = True):

    subsection_writer = subsectionWriter(model=model, api_key=api_key, api_url = api_url, database=db)
    if refinement:
        result = subsection_writer.write(topic, outline, subsection_len = subsection_len, rag_num = rag_num, refining = True)
    else:
        result = subsection_writer.write(topic, outline, subsection_len = subsection_len, rag_num = rag_num, refining = False)
    report_usage('writer', subsection_writer)
    return result

def paras_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--gpu',default='0', type=str, help='Specify the GPU to use')
    parser.add_argument('--saving_path',default='./output/', type=str, help='Directory to save the output survey')
    parser.add_argument('--model',default='gpt-4o-2024-05-13', type=str, help='Model to use')
    parser.add_argument('--topic',default='', type=str, help='Topic to generate survey for')
    parser.add_argument('--section_num',default=7, type=int, help='Number of sections in the outline')
    parser.add_argument('--subsection_len',default=700, type=int,
                        help='Length of each subsection. 프롬프트에서 이 값은 상한이 아니라 '
                             '**하한**("more than N words")이라 모델마다 실제 분량이 크게 다르다. '
                             '실측 계수: haiku 0.77x / deepseek-v4-pro 1.67x. 목표 분량을 계수로 나눠 넣을 것')
    parser.add_argument('--subsection_num',default=0, type=int,
                        help='섹션당 서브섹션 개수 상한. 0이면 원본 AutoSurvey 그대로(모델 재량). '
                             '값을 주면 아웃라인 프롬프트에 개수를 명시하고 초과분은 잘라낸다. '
                             '총 분량 = section_num x subsection_num x (subsection_len x 모델 계수)')
    parser.add_argument('--enforce_section_num', action='store_true',
                        help='--section_num 을 merge 프롬프트까지 관철한다. 원본은 러프 아웃라인에만 '
                             '개수를 넣어 merge 에서 소실되고, 최종 섹션 수가 드리프트한다(5 지시 → 8 관측). '
                             '논문 §2 "predetermines the number of sections" 서술의 구현. '
                             '플래그가 없으면(기본) merge 프롬프트는 원본과 글자 단위로 같다')
    parser.add_argument('--outline_reference_num',default=1500, type=int, help='Number of references for outline generation')
    parser.add_argument('--rag_num',default=60, type=int, help='Number of references to use for RAG')
    parser.add_argument('--api_url',default='https://api.openai.com/v1/chat/completions', type=str, help='url for API request')
    parser.add_argument('--api_key',default='', type=str, help='API key for the model')
    parser.add_argument('--db_path',default='./database', type=str, help='Directory of the database.')
    parser.add_argument('--embedding_model',default='nomic-ai/nomic-embed-text-v1', type=str, help='Embedding model for retrieval.')
    args = parser.parse_args()
    return args

def build_reference_detail(references, db):
    """{번호: arxiv_id} 에 제목·날짜·링크를 붙인다.

    'reference' 필드만으로는 arXiv id밖에 없고 .md의 References에는 제목밖에
    없어서, 어느 쪽을 봐도 실제 논문을 찾아갈 수가 없었다. DB에 정보가 다 있으므로
    저장 시점에 조인해 둔다.

    ⚠ 'reference' 필드는 건드리지 않는다. src/agents/judge.py의 citation_quality()가
       그 구조({번호: id})에 의존한다.
    """
    infos = {p['id']: p for p in db.get_paper_info_from_ids(list(references.values()))}
    detail = {}
    for num, rid in references.items():
        p = infos.get(rid, {})
        detail[str(num)] = {
            'id': rid,
            # arXiv 제목에는 줄바꿈과 들여쓰기가 들어 있다.
            'title': ' '.join((p.get('title') or '').split()),
            'date': (p.get('date') or '').strip(),
            'url': f'https://arxiv.org/abs/{rid}',
        }
    return detail


def check_provider_pin(model):
    """AUTOSURVEY_PROVIDER 의 tag 가 이 모델에 실제로 존재하는지 확인한다.

    provider tag 는 **모델마다 다릅니다.** `.env` 에 deepseek 용 `parasail/fp8` 을
    박아 둔 채 `--model anthropic/claude-3-haiku` 로 돌리면(haiku 는 amazon-bedrock
    하나뿐) allow_fallbacks=false 라 요청이 통째로 실패합니다. 모델은 CLI 인자이고
    provider 는 환경변수라 둘이 조용히 어긋날 수 있어, DB 로딩 전에 잡는다.

    조회 실패(네트워크 등)는 막지 않는다 — 검증 때문에 실행을 못 하면 곤란하다.
    """
    pin = os.environ.get('AUTOSURVEY_PROVIDER', '').strip()
    if not pin:
        return
    tags = [t.strip() for t in pin.split(',') if t.strip()]
    try:
        r = requests.get(
            f'https://openrouter.ai/api/v1/models/{model}/endpoints', timeout=30)
        available = [e.get('tag') for e in r.json()['data']['endpoints']]
    except Exception as e:
        print(f'[provider] 확인 생략 (조회 실패: {e}). 핀={pin}', flush=True)
        return

    missing = [t for t in tags if t not in available]
    if missing:
        raise RuntimeError(
            f'AUTOSURVEY_PROVIDER={pin} 인데 모델 "{model}" 에는 {missing} 엔드포인트가 '
            f'없습니다. allow_fallbacks=false 이므로 요청이 전부 실패합니다.\n'
            f'  이 모델의 tag: {available}\n'
            f'  모델을 바꿨다면 .env 의 AUTOSURVEY_PROVIDER 도 함께 바꾸거나 비우세요.')
    print(f'[provider] {model} → {pin} 고정 (fallback 없음)', flush=True)


def resolve_api_key(args):
    """--api_key 또는 환경변수에서 키를 얻는다.

    이 서버는 /proc에 hidepid가 없어 다른 사용자가 ps로 명령줄을 볼 수 있다.
    커맨드라인 대신 환경변수(.env)를 쓰면 키가 노출되지 않는다.
    """
    key = (args.api_key
           or os.environ.get('OPENROUTER_API_KEY')
           or os.environ.get('AUTOSURVEY_API_KEY')
           or '')
    return key.strip()


def main(args):

    api_key = resolve_api_key(args)
    # DB 로딩에 수 분이 걸리므로 키 검사를 먼저 한다.
    if not api_key:
        raise RuntimeError(
            'API 키가 없습니다. `source .env` 후 실행하거나 --api_key로 넘기세요.')

    check_provider_pin(args.model)

    db = database(db_path = args.db_path, embedding_model = args.embedding_model)

    if not os.path.exists(args.saving_path):
        os.mkdir(args.saving_path)

    outline_with_description, outline_wo_description = write_outline(args.topic, args.model, args.section_num, args.outline_reference_num, db, api_key, args.api_url, args.subsection_num, args.enforce_section_num)

    raw_survey, raw_survey_with_references, raw_references, refined_survey, refined_survey_with_references, refined_references = write_subsection(args.topic, args.model, outline_with_description, args.subsection_len, args.rag_num, db, api_key, args.api_url)

    # 'a+' 로 두면 같은 토픽 재실행 시 이어붙어 evaluation.py의 json.loads가 깨진다.
    with open(f'{args.saving_path}/{args.topic}.md', 'w') as f:
        f.write(refined_survey_with_references)
    with open(f'{args.saving_path}/{args.topic}.json', 'w') as f:
        save_dic = {}
        save_dic['survey'] = refined_survey_with_references
        save_dic['reference'] = refined_references
        save_dic['reference_detail'] = build_reference_detail(refined_references, db)
        f.write(json.dumps(save_dic, indent=4, ensure_ascii=False))

if __name__ == '__main__':

    args = paras_args()

    main(args)