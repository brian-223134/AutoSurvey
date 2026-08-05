"""테스트용 모듈 로더.

두 가지를 해결한다.

1. `scripts/` 는 패키지가 아니라 독립 실행 스크립트 모음이다. 경로로 직접 로드한다.
2. `main.py` 는 `src.database` 를 통해 torch / faiss / sentence_transformers 를
   끌어온다. 순수 함수 하나를 테스트하려고 10초를 쓸 이유가 없으므로 스텁을 끼운다.
"""
import importlib.util
import os
import sys
import types

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
    테스트 대상(check_provider_pin)은 DB 를 건드리지 않는다.
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
