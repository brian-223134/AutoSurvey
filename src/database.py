import os
import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer,  AutoModelForSequenceClassification
from sentence_transformers import SentenceTransformer
import h5py
from src.utils import tokenCounter
import json
from tqdm import tqdm
import faiss
from tinydb import TinyDB, Query


def _resolve_device():
    # 'cuda' 하드코딩 대신 환경변수로 오버라이드 가능하게 (CPU 노드 디버깅용)
    name = os.environ.get('AUTOSURVEY_DEVICE', 'auto')
    if name != 'auto':
        return torch.device(name)
    if torch.cuda.is_available():
        return torch.device('cuda')
    if getattr(torch.backends, 'mps', None) and torch.backends.mps.is_available():
        return torch.device('mps')
    return torch.device('cpu')


class database():

    def __init__(self, db_path, embedding_model) -> None:

        self.db_path = db_path
        self.embedding_model = SentenceTransformer(embedding_model, trust_remote_code=True)

        self.embedding_model.to(_resolve_device())

        self.db = TinyDB(f'{db_path}/arxiv_paper_db.json')
        self.table = self.db.table('cs_paper_info')

        self.User = Query()
        self.token_counter = tokenCounter()
        # TinyDB의 one_of()는 문서 전체 선형 스캔이라 53만 편 규모에서 호출당 수 분이 걸린다.
        # 시작 시 1회 메모리 인덱스를 만들어 id 조회를 O(1)로 바꾼다.
        self._by_id = {p['id']: p for p in self.table.all()}
        self.title_loaded_index = faiss.read_index(f'{db_path}/faiss_paper_title_embeddings.bin')

        self.abs_loaded_index = faiss.read_index(f'{db_path}/faiss_paper_abs_embeddings.bin')
        self.id_to_index, self.index_to_id = self.load_index_arxivid(db_path)

    def load_index_arxivid(self, db_path):
        with open(f'{db_path}/arxivid_to_index_abs.json','r') as f:
            id_to_index = json.loads(f.read())
        id_to_index = {id: int(index) for id, index in id_to_index.items()}
        index_to_id = {int(index): id for id, index in id_to_index.items()}
        return id_to_index, index_to_id
    
    def get_embeddings(self, batch_text):
        batch_text = ['search_query: ' + _ for _ in batch_text]
        embeddings = self.embedding_model.encode(batch_text)
        return embeddings

    def get_embeddings_documents(self, batch_text):
        batch_text = ['search_document: ' + _ for _ in batch_text]
        embeddings = self.embedding_model.encode(batch_text)
        return embeddings
        
    def batch_search(self, query_vectors, top_k=1, title=False):
        query_vectors = np.array(query_vectors).astype('float32')
        if title:
            distances, indices = self.title_loaded_index.search(query_vectors, top_k)
        else:
            distances, indices = self.abs_loaded_index.search(query_vectors, top_k)
        results = []
        for i, query in tqdm(enumerate(query_vectors)):
            result = [(self.index_to_id[idx], distances[i][j]) for j, idx in enumerate(indices[i]) if idx != -1]
            results.append([_[0] for _ in result])
        return results

    def search(self, query_vector, top_k=1, title=False):
        query_vector = np.array([query_vector]).astype('float32')
        if title:
            distances, indices = self.title_loaded_index.search(query_vector, top_k)
        else:
            distances, indices = self.abs_loaded_index.search(query_vector, top_k)
        results = [(self.index_to_id[idx], distances[0][i]) for i, idx in enumerate(indices[0]) if idx != -1]
        return [_[0] for _ in results]

    def get_ids_from_query(self, query, num,  shuffle = False):
        q = self.get_embeddings([query])[0]
        return self.search(q, top_k=num)
    
    def get_titles_from_citations(self, citations):
        q = self.get_embeddings_documents(citations)
        ids = self.batch_search(q,1, True)
        return [_[0] for _ in ids]

    def get_ids_from_queries(self, queries, num,  shuffle = False):
        q = self.get_embeddings(queries)
        ids = self.batch_search(q,num)
        return ids
    
    def get_date_from_ids(self, ids):
        return [r['date'] for r in self.get_paper_info_from_ids(ids)]

    def get_title_from_ids(self, ids):
        return [r['title'] for r in self.get_paper_info_from_ids(ids)]

    def get_abs_from_ids(self, ids):
        return [r['abs'] for r in self.get_paper_info_from_ids(ids)]

    def get_paper_info_from_ids(self, ids):
        return [self._by_id[i] for i in ids if i in self._by_id]

    def get_paper_from_ids(self, ids, max_len = 1500):
        loaded_data = {}
        with h5py.File(f'{self.db_path}/paper_content.h5', 'r') as f:
            for key in f.keys():
                if key in ids:
                    loaded_data[key] = str(f[key][()])
                if len(ids) == len(loaded_data):
                    break
        print(loaded_data[list(loaded_data.keys())[0]])
        return [self.token_counter.text_truncation(loaded_data[_], max_len) for _ in ids]