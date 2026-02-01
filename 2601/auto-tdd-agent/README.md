# Auto-TDD Agent

LangGraph 기반 Planning Agent의 TDD 환경 구축 프로젝트

## 프로젝트 개요

- **목표**: Python 규칙 기반 시뮬레이터를 통한 비용 효율적인 빠른 TDD 사이클 구현
- **핵심 원칙**: Claude가 사용자를 연기하는 것이 아니라 `tests/simulator.py`가 시뮬레이션 수행
- **차별점**: LLM 호출 없이 순수 Python 규칙으로 테스트 실행
- **새로운 기능**: IPC 기반 LLM 클라이언트로 외부 API 없이 테스트 가능

## 디렉토리 구조

```
/auto-tdd-agent
├── /data
│   ├── /scenarios          # 테스트 케이스 시나리오
│   ├── knowledge_base.json # 도메인 지식 베이스
│   └── plan_schema.json    # Plan 스키마 정의
├── /prompts                # 프롬프트 템플릿
│   ├── question_generator.yaml
│   ├── slot_updater.yaml
│   └── prompt_history.md
├── /src                    # Agent 소스 코드
│   ├── /core              # 핵심 모듈
│   │   ├── state.py       # AgentState 정의
│   │   ├── types.py       # 타입 정의
│   │   ├── config.py      # 설정 관리
│   │   └── env_config.py  # 환경 변수 설정
│   ├── /nodes             # 노드 함수들
│   │   ├── question_node.py
│   │   ├── process_node.py
│   │   └── router.py
│   ├── /services          # 비즈니스 로직
│   │   ├── question_generator.py
│   │   ├── response_parser.py
│   │   └── plan_manager.py
│   ├── /utils             # 유틸리티
│   │   ├── prompt_loader.py
│   │   ├── validator.py
│   │   ├── llm_client.py       # GLM API 클라이언트
│   │   ├── ipc_llm_client.py   # IPC 기반 LLM 클라이언트
│   │   └── ipc_llm_server.py   # IPC LLM 서버
│   ├── graph.py           # 그래프 조립
│   ├── agent.py           # Agent 통합 인터페이스
│   └── __init__.py
├── /tests                  # 테스트
│   ├── /infrastructure    # 테스트 인프라
│   │   ├── simulator.py
│   │   ├── adapter.py
│   │   └── tdd_runner.py
│   ├── /evaluation        # 평가 로직
│   │   └── evaluator.py
│   ├── /unit              # 단위 테스트
│   ├── /integration       # 통합 테스트
│   └── conftest.py        # pytest 설정
├── /outputs
│   └── /logs              # 테스트 로그
├── pyproject.toml         # 프로젝트 설정 (uv)
├── .python-version        # Python 버전 고정
├── .env                   # 환경 변수 (API 키 등)
├── run_ipc_tests.py       # IPC 기반 테스트 러너
└── test_agent_live.py     # 라이브 테스트 스크립트
```

## 설치 및 실행

### 1. 환경 설정

```bash
# Python 버전 설정 및 가상환경 생성
uv venv

# 의존성 설치
uv sync

# 가상환경 활성화 (선택사항)
source .venv/bin/activate  # macOS/Linux
```

### 2. API 키 설정 (선택사항)

`.env` 파일에 GLM API 키를 설정하세요 (IPC 모드 사용 시 불필요):

```bash
# .env 파일 열기
code .env

# GLM_API_KEY를 실제 키로 변경
GLM_API_KEY=your_actual_api_key_here
```

자세한 내용은 [ENV_SETUP.md](ENV_SETUP.md)를 참고하세요.

### 3. 테스트 실행

#### 방법 1: IPC 기반 테스트 (권장 - API 비용 없음)

```bash
# IPC LLM 서버를 자동으로 시작하고 테스트 실행
uv run python run_ipc_tests.py --mode test

# 라이브 Agent 테스트 실행
uv run python run_ipc_tests.py --mode live

# IPC 서버만 실행 (별도 터미널에서)
uv run python run_ipc_tests.py --mode server
```

#### 방법 2: 기존 pytest 방식

```bash
# 단위 테스트 실행
uv run pytest tests/unit/ -v

# 통합 테스트 실행
uv run pytest tests/integration/ -v

# 모든 테스트 실행
uv run pytest tests/ -v
```

#### 방법 3: TDD 러너

```bash
# TDD 실행 (권장)
uv run python tests/infrastructure/tdd_runner.py
```

#### 방법 4: 라이브 테스트 (실제 API 호출)

```bash
# 실제 GLM API를 호출하는 라이브 테스트
uv run python test_agent_live.py
```

### 4. 로그 확인

```bash
# 특정 테스트 케이스 로그 확인
cat outputs/logs/s01_v01.json

# 모든 로그 확인
ls -l outputs/logs/
```

## IPC 기반 LLM 테스트

### 특징
- **외부 API 없이 테스트**: 실제 LLM API 호출 없이 로컬에서 완전한 테스트 가능
- **스마트 응답 생성**: 미리 정의된 응답 패턴으로 자동 응답 생성
- **멀티 프로세스 지원**: 테스트 프로세스와 LLM 서버가 IPC로 통신

### 작동 방식

```
[테스트 프로세스] --Unix Socket--> [IPC LLM 서버]
     ↓                                    ↓
LLM.invoke() 호출                프롬프트 분석 및 응답 생성
     ↓                                    ↓
 응답 수신 <--------------------- 스마트 응답 (PREDEFINED_RESPONSES)
```

### 환경 변수

```bash
# IPC 모드 활성화
export USE_IPC_LLM=true

# GLM API 사용 (기본값)
unset USE_IPC_LLM
```

## 테스트 결과

### 현재 상태

| 테스트 유형 | 테스트 수 | 결과 | 비고 |
|------------|----------|------|------|
| 단위 테스트 | 19개 | ✅ 전체 통과 | PlanManager, QuestionGenerator, ResponseParser |
| 통합 테스트 | 4개 | ✅ 전체 통과 | 그래프 생성, 컴파일, 실행 |
| 라이브 테스트 | 4턴 | ✅ 완료 | IPC 기반 LLM으로 완전한 대화 흐름 |

### 테스트 상세 내역

#### 단위 테스트
- `test_plan_manager.py`: Plan 업데이트, 완료 여부 확인, 다음 슬롯 가져오기 (8개)
- `test_question_generator.py`: 질문 생성 로직 (4개)
- `test_response_parser.py`: 목적지, 날짜, 기간, 예산 파싱 (7개)

#### 통합 테스트
- `test_graph_creation`: 그래프 생성 테스트
- `test_graph_compilation`: 그래프 컴파일 테스트
- `test_graph_single_turn`: 단일 턴 실행 테스트
- `test_graph_multi_turn`: 다중 턴 실행 테스트

#### 라이브 테스트 흐름
1. "여행 계획 도와주세요" → 목적지 질문
2. "제주도로 가고 싶어요" → 출발일 질문 (Plan: `{'destination': '제주도'}`)
3. "3월 15일에 출발할 거예요" → 기간 질문 (Plan 업데이트)
4. "3박 4일로 계획하고 있어요" → 완료 또는 추가 질문

## TDD 사이클

### Red → Green → Refactor

- **Red**: 테스트 작성 및 실패 확인
- **Green**: 최소한의 코드로 테스트 통과
- **Refactor**: 코드 개선 및 중복 제거

## 테스트 시나리오

### s01_v01: 기본 시나리오
- 사용자가 모든 정보를 협조적으로 한번에 제공
- reveal_strategy: all_at_once
- style: concise

## 실패 카테고리

테스트 실패 시 다음 7가지 유형으로 분류:

1. **PARSING_ERROR**: 사용자 입력 파싱 실패
2. **REDUNDANT_QUESTION**: 중복 질문
3. **MISSED_SLOT**: 슬롯 수집 누락
4. **WRONG_VALUE**: 잘못된 값 수집
5. **WRONG_INFERENCE**: 잘못된 추론
6. **TURN_OVERFLOW**: 턴 수 초과 (최대 15턴)
7. **UNKNOWN**: 알 수 없는 실패

## 기술 스택

- **LangGraph**: Agent 오케스트레이션
- **Python 3.11+**: 개발 언어
- **uv**: 패키지 관리
- **LangChain**: LLM 통합
- **Unix Domain Socket**: IPC 통신

## 주요 파일 설명

### Core Files
- `src/agent.py`: PlanningAgent 클래스 - 메인 인터페이스
- `src/graph.py`: LangGraph 그래프 정의 (process_input → ask_user)
- `src/core/state.py`: AgentState 타입 정의
- `src/core/config.py`: AgentConfig 설정 관리

### Service Files
- `src/services/question_generator.py`: 다음 질문 생성 로직
- `src/services/response_parser.py`: 사용자 응답 파싱 로직
- `src/services/plan_manager.py`: Plan 상태 관리

### IPC Files
- `src/utils/ipc_llm_client.py`: IPC 기반 LLM 클라이언트
- `src/utils/ipc_llm_server.py`: IPC LLM 서버 (데모용)
- `run_ipc_tests.py`: IPC 테스트 실행 스크립트

## 다음 단계

1. ✅ IPC 기반 LLM 클라이언트 구현 완료
2. ✅ 단위/통합 테스트 통과
3. 🔄 Agent 로직 고도화 (슬롯 추론 개선)
4. 🔄 추가 테스트 시나리오 작성
   - vague_first: 처음엔 모호하게 답변
   - reluctant: 최소한의 정보만 제공
   - talkative: 많은 정보를 한번에 제공
5. 🔄 프롬프트 템플릿 최적화
6. 🔄 knowledge_base.json에 도메인 지식 추가

## 라이선스

MIT
