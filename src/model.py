import os
import random
import time
import requests
import json
from tqdm import tqdm
import threading

TIMEOUT = int(os.environ.get('AUTOSURVEY_TIMEOUT', 900))
# 레이트리밋(429)은 초 단위로 풀리지 않는다. 기본 5회 / 최대 16초 백오프로는
# 동시 16요청이 몰릴 때 소진되고, 소진되면 서브섹션이 통째로 사라진다.
MAX_RETRY = int(os.environ.get('AUTOSURVEY_MAX_RETRY', 8))
# temperature 는 에이전트 호출부에 하드코딩돼 있다(아웃라인·본문 1, judge 0).
# 결정론이 필요한 실험(temperature=0)을 위해 전역 오버라이드만 열어 둔다 —
# 비워 두면(기본) 원본 동작 그대로다.
# ⚠ 설정하면 judge 의 0 을 포함해 **모든** 호출에 일괄 적용된다.
_t = os.environ.get('AUTOSURVEY_TEMPERATURE', '').strip()
TEMPERATURE_OVERRIDE = float(_t) if _t else None


class APIModel:

    def __init__(self, model, api_key, api_url) -> None:
        self.__api_key = api_key
        self.__api_url = api_url
        self.model = model
        # 재시도는 프롬프트 전체를 다시 청구시키므로 비용에 직결된다.
        # 원본은 중간 재시도를 전혀 남기지 않아 조용히 돈이 새도 알 수 없었다.
        self.retry_count = 0
        # 출력이 잘린 호출 수. 0이 아니면 그 서베이는 문장이 끊긴 채로 들어간 것이다.
        self.truncated = 0
        # 최종 실패한 요청 수. 0이 아니면 산출물에 빈 서브섹션이 있다는 뜻이라
        # main.py가 저장을 거부한다.
        self.failed = 0
        self.usage = {'prompt': 0, 'completion': 0, 'reasoning': 0, 'cost': 0.0}
        self._lock = threading.Lock()

    def _note_truncation(self):
        with self._lock:
            self.truncated += 1

    def _extra_payload(self):
        """AUTOSURVEY_REASONING / AUTOSURVEY_PROVIDER 를 페이로드에 반영한다.

        둘 다 환경변수를 주지 않으면 아무것도 추가하지 않아 원본 동작이 유지된다.

        reasoning — deepseek-v4-pro 실측: 추론이 출력 토큰의 45%를 차지하는데 본문
        분량은 오히려 끈 쪽이 조금 더 길었다. 비용 36% 절감, 응답 31% 단축.

        provider — OpenRouter 는 같은 모델을 여러 provider 로 라우팅하고, 그들의
        quantization 이 제각각이다. deepseek-v4-flash-0731 은 19개 엔드포인트에
        fp4/fp8/unknown 이 섞여 있다. 고정하지 않으면 **한 서베이 안에서 서브섹션마다
        다른 정밀도의 모델이 쓴다.** 통제 실험이 성립하지 않는다.

        값은 OpenRouter 의 엔드포인트 tag 를 그대로 쓴다 (`parasail/fp8` 형식).
        provider 와 quantization 을 한 번에 고정한다. 확인:
            curl -s https://openrouter.ai/api/v1/models/<model>/endpoints | jq '.data.endpoints[].tag'
        """
        extra = {}

        mode = os.environ.get('AUTOSURVEY_REASONING', '').lower()
        if mode in ('off', 'false', '0', 'disabled'):
            extra["reasoning"] = {"enabled": False}

        provider = os.environ.get('AUTOSURVEY_PROVIDER', '').strip()
        if provider:
            # allow_fallbacks=False 가 핵심이다. True 면 그 provider 가 붐빌 때
            # 조용히 다른 곳(다른 quantization)으로 넘어가 고정이 무의미해진다.
            extra["provider"] = {
                "order": [p.strip() for p in provider.split(',') if p.strip()],
                "allow_fallbacks": False,
            }
        return extra

    def _record(self, usage):
        if not usage:
            return
        det = usage.get('completion_tokens_details') or {}
        with self._lock:
            self.usage['prompt'] += usage.get('prompt_tokens', 0)
            self.usage['completion'] += usage.get('completion_tokens', 0)
            self.usage['reasoning'] += det.get('reasoning_tokens', 0)
            self.usage['cost'] += float(usage.get('cost', 0) or 0)

    def __req(self, text, temperature, max_try=None):
        if TEMPERATURE_OVERRIDE is not None:
            temperature = TEMPERATURE_OVERRIDE
        max_try = max_try or MAX_RETRY
        url = f"{self.__api_url}"
        # temperature는 messages 배열이 아니라 최상위에 와야 실제로 적용된다.
        # (원본은 message 안에 넣어서 서버 기본값으로 돌고 있었고, vLLM 등은 400을 낼 수 있다)
        pay_load_dict = {
            "model": self.model,
            "temperature": temperature,
            "messages": [{"role": "user", "content": text}],
            **self._extra_payload(),
        }
        payload = json.dumps(pay_load_dict)
        headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {self.__api_key}',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
        }
        last_err = None
        for attempt in range(max_try):
            try:
                response = requests.post(url, headers=headers, data=payload, timeout=TIMEOUT)
                if response.status_code != 200:
                    last_err = f"HTTP {response.status_code}: {response.text[:300]}"
                else:
                    body = response.json()
                    # OpenRouter는 업스트림 실패를 200 + {"error": ...} 로 돌려줄 때가 있다.
                    if 'choices' not in body:
                        last_err = f"응답에 choices 없음: {str(body)[:300]}"
                    else:
                        self._record(body.get('usage'))
                        choice = body['choices'][0]
                        # finish_reason='length' 는 provider 의 출력 한도에 걸려
                        # 문장 중간에서 잘렸다는 뜻이다. 내용은 정상처럼 돌아오므로
                        # 검사하지 않으면 잘린 서브섹션이 조용히 서베이에 들어간다.
                        # 인용 검사(check_survey.py)로는 잡히지 않는다.
                        if choice.get('finish_reason') == 'length':
                            self._note_truncation()
                            print(f'[APIModel] ⚠ 출력이 잘렸습니다(finish_reason=length). '
                                  f'provider 출력 한도 또는 reasoning 토큰 과다. '
                                  f'누적 {self.truncated}건', flush=True)
                        return choice['message']['content']
            except Exception as e:
                last_err = repr(e)
            # 재시도는 프롬프트를 다시 청구시킨다. 반드시 보이게 남긴다.
            with self._lock:
                self.retry_count += 1
            # 429는 다른 에러와 백오프가 달라야 한다. 초 단위로 풀리지 않는다.
            rate_limited = str(last_err).startswith('HTTP 429')
            delay = min((15 if rate_limited else 2) * (2 ** attempt), 120)
            # ⚠ 지터가 핵심이다. 동시 16요청이 같은 백오프를 쓰면 매번 같은 순간에
            # 함께 깨어나 레이트리밋을 다시 정면으로 맞는다. 재시도가 소진된 실제
            # 원인이 이것이었다.
            delay *= 0.75 + random.random() * 0.5
            print(f"[APIModel] 재시도 {attempt + 1}/{max_try} "
                  f"(누적 {self.retry_count}회, 프롬프트 {len(text)}자, "
                  f"{delay:.0f}초 대기): {last_err}", flush=True)
            time.sleep(delay)
        # None을 파이프라인에 흘려보내면 토큰 카운터가 죽고 그 스레드가 통째로
        # 사라진다. 밖에서는 조용하고, 산출물에는 섹션 하나가 없다.
        with self._lock:
            self.failed += 1
        print(f"[APIModel] 최종 실패 ({max_try}회, 누적 {self.failed}건): {last_err}",
              flush=True)
        return None
    
    def chat(self, text, temperature=1):
        response = self.__req(text, temperature=temperature, max_try=5)
        return response

    def __chat(self, text, temperature, res_l, idx):
        
        response = self.__req(text, temperature=temperature)
        res_l[idx] = response
        return response
        
    def batch_chat(self, text_batch, temperature=0):
        # writer.py가 섹션당 스레드 1개로 batch_chat을 부르므로 실제 동시 요청은
        # section_num * max_threads 까지 올라간다. 상용 API 레이트리밋에 맞춰
        # AUTOSURVEY_MAX_THREADS 로 낮출 수 있게 해둔다.
        max_threads = int(os.environ.get('AUTOSURVEY_MAX_THREADS', 15))
        res_l = ['No response'] * len(text_batch)
        thread_l = []
        for i, text in zip(range(len(text_batch)), text_batch):
            thread = threading.Thread(target=self.__chat, args=(text, temperature, res_l, i))
            thread_l.append(thread)
            thread.start()
            while len(thread_l) >= max_threads: 
                for t in thread_l:
                    if not t .is_alive():
                        thread_l.remove(t)
                time.sleep(0.3) # Short delay to avoid busy-waiting

        for thread in tqdm(thread_l):
            thread.join()
        # 실패를 여기서 잡지 않으면 None이 그대로 흘러가 토큰 카운터에서
        # TypeError로 죽고, 죽는 곳이 워커 스레드라 본 실행은 태연히 계속된다.
        # 결과는 섹션 하나가 빈 서베이다. 조용한 손상보다 시끄러운 중단이 낫다.
        bad = [i for i, r in enumerate(res_l) if not isinstance(r, str)]
        if bad:
            raise RuntimeError(
                f'{len(bad)}/{len(res_l)}개 요청이 최종 실패했습니다(인덱스 {bad[:5]}). '
                f'부분 결과로 서베이를 쓰면 섹션이 조용히 빕니다. '
                f'AUTOSURVEY_MAX_THREADS를 낮추거나 AUTOSURVEY_MAX_RETRY를 올리세요.')
        return res_l
