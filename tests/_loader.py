"""테스트용 모듈 로더.

두 가지를 해결한다.

1. `scripts/` 는 패키지가 아니라 독립 실행 스크립트 모음이다. 경로로 직접 로드한다.
2. `main.py` 는 `src.database` 를 통해 torch / faiss / sentence_transformers 를
   끌어온다. 순수 함수 하나를 테스트하려고 10초를 쓸 이유가 없으므로 스텁을 끼운다.

`load_database()` 는 반대로 **src.database 자체를** 테스트할 때 쓴다 — torch·transformers·
sentence_transformers·h5py 만 스텁하고 faiss·numpy·tinydb 는 실제 것을 쓴다. 임베딩 모델 자리에는
`FakeEmbedder`(결정적 bag-of-words 벡터)를 끼우면 파일 형식·검색·정책까지 네트워크 없이 돈다.
"""
import hashlib
import importlib.util
import os
import re
import sys
import types

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def load_script(name):
    """scripts/<name>.py 를 모듈로 로드한다."""
    path = os.path.join(ROOT, 'scripts', f'{name}.py')
    spec = importlib.util.spec_from_file_location(f'_script_{name}', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _stub(name, **attrs):
    mod = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(mod, k, v)
    return mod


def load_main():
    """무거운 의존성을 스텁으로 갈아끼운 뒤 main.py 를 로드한다.

    src.database 자체를 통째로 스텁한다 — main.py 가 쓰는 것은 `database` 이름뿐이고
    테스트 대상(check_provider_pin)은 DB 를 건드리지 않는다. 실제 database 클래스가 필요한
    end-to-end 테스트는 `load_database()` 로 얻은 클래스를 `main.database` 에 patch 한다.
    """
    if 'main' in sys.modules:
        return sys.modules['main']

    saved = {k: sys.modules.get(k) for k in ('src.database',)}
    sys.modules['src.database'] = _stub('src.database', database=object)
    try:
        import main  # noqa: E402
        return main
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v


class FakeEmbedder:
    """SentenceTransformer 대역. 단어 해시 bag-of-words → L2 정규화 벡터(결정적, 프로세스 무관).

    nomic 프리픽스('search_query: ' / 'search_document: ')는 떼어낸다. 같은 단어를 공유하는
    질의·문서가 가까워지므로 검색 순위가 의미를 갖는다 — 정확한 임베딩이 아니라 '검색이 돈다'가 목적.
    """
    DIM = 64

    def __init__(self, name='fake', **kw):
        self.name = name

    def to(self, device):
        return self

    @classmethod
    def vector(cls, text):
        text = re.sub(r'^search_(query|document): ', '', text)
        v = np.zeros(cls.DIM, dtype='float32')
        for w in re.findall(r'[a-z0-9]+', text.lower()):
            h = int(hashlib.blake2b(w.encode(), digest_size=4).hexdigest(), 16)
            v[h % cls.DIM] += 1.0
        n = np.linalg.norm(v)
        return v / n if n else v

    def encode(self, texts, **kw):
        return np.stack([self.vector(t) for t in texts]).astype('float32')


class FakeTokenCounter:
    """tiktoken 대역 — 단어 수 × scale. scale 을 키우면 작은 DB 로도 아웃라인 chunking 이 여러 조각으로 갈린다."""
    scale = 1

    def __init__(self):
        self.model_price = {}

    def num_tokens_from_string(self, s):
        return len(s.split()) * self.scale

    def num_tokens_from_list_string(self, l):
        return sum(self.num_tokens_from_string(s) for s in l)

    def compute_price(self, input_tokens, output_tokens, model):
        return 0.0

    def text_truncation(self, text, max_len=1000):
        return ' '.join(text.split()[:max_len])


def load_database():
    """src.database 를 실제로 로드하되 torch·transformers·sentence_transformers·h5py·src.utils 는 스텁.

    반환 모듈의 `SentenceTransformer` 는 `FakeEmbedder` 다(파일 형식·검색·정책은 실제 코드 그대로).
    """
    if 'src.database' in sys.modules and getattr(sys.modules['src.database'], '_test_loaded', False):
        return sys.modules['src.database']
    saved = {k: sys.modules.get(k) for k in
             ('torch', 'transformers', 'sentence_transformers', 'h5py', 'src.utils', 'src.database')}
    sys.modules['torch'] = _stub('torch', device=lambda n: n,
                                 cuda=types.SimpleNamespace(is_available=lambda: False),
                                 backends=types.SimpleNamespace())
    sys.modules['transformers'] = _stub('transformers', AutoModel=object, AutoTokenizer=object,
                                        AutoModelForSequenceClassification=object)
    sys.modules['sentence_transformers'] = _stub('sentence_transformers', SentenceTransformer=FakeEmbedder)
    sys.modules['h5py'] = _stub('h5py')
    sys.modules['src.utils'] = _stub('src.utils', tokenCounter=FakeTokenCounter)
    sys.modules.pop('src.database', None)
    try:
        import src.database as db
        db._test_loaded = True
        return db
    finally:
        for k, v in saved.items():
            if k == 'src.database':
                continue          # 방금 로드한 모듈을 유지한다
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
