"""arxiv_paper_db.json → nomic 임베딩 → FAISS 인덱스.

build_database.ipynb를 대체한다. 노트북은 그대로 실행되지 않았다:
  - 셀 14가 CPU IndexFlatL2에 faiss.index_gpu_to_cpu()를 호출해 에러
  - 출력 파일명(titles.index / abstracts.index / paperid_to_index.json)이
    src/database.py가 읽는 이름과 불일치

출력 (src/database.py가 읽는 이름 그대로):
    faiss_paper_title_embeddings.bin   database.py:26
    faiss_paper_abs_embeddings.bin     database.py:28
    arxivid_to_index_abs.json          database.py:32

주의: 인덱스를 만든 임베딩 모델과 검색에 쓰는 모델(main.py --embedding_model)이
반드시 같아야 한다.
"""

import argparse
import json
import os
import sys

import faiss
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from tqdm import trange


def get_embeddings(model, texts, batch_size):
    """nomic은 'search_document: ' 프리픽스로 색인하고 'search_query: '로 검색한다.

    src/database.py의 get_embeddings()가 query 프리픽스를 붙이므로 여기는 document 쪽.
    """
    out = []
    for i in trange(0, len(texts), batch_size):
        batch = ['search_document: ' + t for t in texts[i:i + batch_size]]
        out.append(model.encode(batch, show_progress_bar=False))
    return np.concatenate(out, axis=0).astype('float32')


def build_flat_index(embeddings):
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--db-path', default='./database',
                        help='arxiv_paper_db.json이 있는 디렉터리 (출력도 여기)')
    parser.add_argument('--embedding-model', default='nomic-ai/nomic-embed-text-v1')
    parser.add_argument('--batch-size', type=int, default=256)
    parser.add_argument('--device', default=None,
                        help='기본값: cuda 가용 시 cuda, 아니면 cpu')
    args = parser.parse_args()

    db_file = os.path.join(args.db_path, 'arxiv_paper_db.json')
    if not os.path.exists(db_file):
        print(f'{db_file} 없음. 먼저 scripts/harvest_arxiv.py를 실행하세요.', file=sys.stderr)
        return 1

    with open(db_file) as f:
        papers = json.load(f)
    # TinyDB가 self.table.all()로 읽는 순서와 동일하게 유지해야 한다.
    papers_l = list(papers['cs_paper_info'].items())
    print(f'{len(papers_l)}편 로드')

    device = args.device or ('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'임베딩 모델 로딩: {args.embedding_model} (device={device})')
    model = SentenceTransformer(args.embedding_model, trust_remote_code=True)
    model.to(torch.device(device))

    titles = [p[1]['title'] for p in papers_l]
    abstracts = [p[1]['abs'] for p in papers_l]

    print('\ntitle 임베딩')
    title_emb = get_embeddings(model, titles, args.batch_size)
    print('abstract 임베딩')
    abs_emb = get_embeddings(model, abstracts, args.batch_size)

    title_path = os.path.join(args.db_path, 'faiss_paper_title_embeddings.bin')
    abs_path = os.path.join(args.db_path, 'faiss_paper_abs_embeddings.bin')
    # 인덱스는 CPU에서 생성되므로 index_gpu_to_cpu()를 거치지 않는다(노트북 셀 14의 버그).
    faiss.write_index(build_flat_index(title_emb), title_path)
    faiss.write_index(build_flat_index(abs_emb), abs_path)
    print(f'\n{title_path}\n{abs_path}')

    # TinyDB 키가 아니라 리스트상의 위치를 인덱스로 쓴다.
    # FAISS에 add된 순서가 곧 이 순서이므로 키 번호 체계와 무관하게 항상 맞다.
    id_to_index = {p[1]['id']: i for i, p in enumerate(papers_l)}
    map_path = os.path.join(args.db_path, 'arxivid_to_index_abs.json')
    with open(map_path, 'w') as f:
        json.dump(id_to_index, f)
    print(map_path)

    if len(id_to_index) != len(papers_l):
        print(f'경고: 중복 arXiv id 존재 ({len(papers_l)} → {len(id_to_index)}). '
              f'검색 결과가 일부 유실될 수 있습니다.', file=sys.stderr)

    print(f'\n완료: {len(papers_l)}편, dim={title_emb.shape[1]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
