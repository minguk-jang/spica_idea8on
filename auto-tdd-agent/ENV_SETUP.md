# 환경 설정 가이드

## GLM API 키 설정

### 1. API 키 발급

1. [Zhipu AI 플랫폼](https://open.bigmodel.cn)에 접속
2. 회원가입 및 로그인
3. API 키 발급

### 2. .env 파일 설정

프로젝트 루트에 `.env` 파일이 있습니다:

```bash
# .env 파일 열기
code .env
# 또는
vi .env
```

다음과 같이 API 키를 입력하세요:

```env
# GLM API 설정
GLM_API_KEY=your_actual_api_key_here  # <-- 여기에 실제 API 키 입력
GLM_MODEL=glm-4-flash
GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4

# Agent 설정
MAX_TURNS=15
TEMPERATURE=0.7

# 로깅 설정
LOG_LEVEL=INFO
```

### 3. 설정 확인

```bash
# 환경 변수 로드 테스트
uv run python -c "
from src.core.env_config import EnvConfig
print('API Key 설정:', '✓' if EnvConfig.GLM_API_KEY != 'your_api_key_here' else '✗')
print('Model:', EnvConfig.GLM_MODEL)
print('Base URL:', EnvConfig.GLM_BASE_URL)
"
```

## 모드 선택

### 규칙 기반 모드 (기본)

LLM 없이 규칙 기반으로 동작합니다. API 키가 없어도 테스트 가능합니다.

```python
from src.services.question_generator import QuestionGenerator
from src.services.response_parser import ResponseParser

generator = QuestionGenerator(use_llm=False)  # 규칙 기반
parser = ResponseParser(use_llm=False)  # 규칙 기반
```

### LLM 모드

GLM API를 사용하여 동작합니다. API 키 설정이 필요합니다.

```python
from src.services.question_generator import QuestionGenerator
from src.services.response_parser import ResponseParser

generator = QuestionGenerator(use_llm=True)  # LLM 사용
parser = ResponseParser(use_llm=True)  # LLM 사용
```

## 주의사항

⚠️ `.env` 파일은 git에 커밋되지 않습니다 (`.gitignore`에 포함됨)

✅ `.env.example` 파일은 git에 커밋되어 참고용으로 사용됩니다

🔑 API 키는 절대 공개 저장소에 올리지 마세요
