# Planning Agent TDD Skill

LangGraph 기반 Planning Agent의 TDD 환경 운영 매뉴얼 및 디버깅 플레이북

## 개요

이 Skill은 Planning Agent의 테스트 주도 개발(TDD) 환경을 관리하고, 테스트 실행, 로그 분석, 실패 디버깅을 지원합니다.

## 사용 트리거

사용자가 다음과 같은 요청을 할 때 이 Skill을 활성화:

- "TDD 실행해줘"
- "테스트 돌려줘"
- "Planning Agent 테스트"
- "시뮬레이터 실행"
- "테스트 결과 확인"

## 주요 기능

### 1. TDD 실행

```bash
cd auto-tdd-agent
uv run python tests/run_tdd.py
```

**기대 출력:**
```
============================================================
Planning Agent TDD 실행
============================================================

총 1개의 테스트 케이스를 발견했습니다.

[s01_v01] 기본 시나리오 - 모든 정보 한번에 제공 실행 중...
  ✗ 실패 (3턴)
  실패 원인: 누락된 슬롯: destination, start_date, duration

============================================================
요약
============================================================
성공: 0/1
실패: 1/1

실패 케이스:
  - s01_v01: missed_slot
```

### 2. 로그 분석

테스트 실행 후 로그 확인:

```bash
cat outputs/logs/s01_v01.json
```

**로그 구조:**
```json
{
  "test_case_id": "s01_v01",
  "success": false,
  "turn_count": 3,
  "final_plan": {},
  "ground_truth": {
    "destination": "제주도",
    "start_date": "2026-03-15",
    "duration": "3박 4일"
  },
  "failure_category": "missed_slot",
  "failure_detail": "누락된 슬롯: destination, start_date, duration",
  "turn_history": [
    {
      "turn": 1,
      "question": "여행 목적지가 어디인가요?",
      "response": "제주도"
    }
  ]
}
```

### 3. 실패 유형별 디버깅 가이드

#### PARSING_ERROR (파싱 실패)
**증상:** Agent가 사용자 응답을 파싱하지 못함

**확인 사항:**
1. `src/nodes.py`의 `parse_user_response()` 함수 확인
2. 프롬프트 템플릿 (`prompts/slot_updater.yaml`) 검토
3. 로그의 `turn_history`에서 사용자 응답 형식 확인

**해결 방법:**
- 파싱 로직 개선
- 프롬프트에 few-shot 예제 추가
- 정규식 패턴 업데이트

#### REDUNDANT_QUESTION (중복 질문)
**증상:** 동일한 질문을 반복

**확인 사항:**
1. `src/graph.py`의 `ask_user()` 함수 확인
2. `current_plan` 상태가 제대로 업데이트되는지 확인
3. 질문 생성 로직이 이미 수집된 슬롯을 확인하는지 체크

**해결 방법:**
- 질문 생성 전 `current_plan` 검증 로직 추가
- 프롬프트에 "이미 수집된 정보는 다시 묻지 마세요" 추가

#### MISSED_SLOT (슬롯 누락)
**증상:** 필요한 정보를 수집하지 못함

**확인 사항:**
1. `data/plan_schema.json`의 `required_slots` 확인
2. `src/graph.py`의 `should_continue()` 함수 확인
3. 로그에서 어느 턴에 수집을 시도했는지 확인

**해결 방법:**
- 슬롯 추적 로직 개선
- 질문 전략 수정 (한 번에 여러 슬롯 수집)
- 프롬프트 개선

#### WRONG_VALUE (잘못된 값)
**증상:** 수집한 값이 ground_truth와 다름

**확인 사항:**
1. 로그의 `final_plan`과 `ground_truth` 비교
2. 파싱 로직에서 값 변환이 올바른지 확인
3. 시뮬레이터가 올바른 값을 반환했는지 확인

**해결 방법:**
- 값 정규화 로직 추가
- 동의어 처리 개선
- 프롬프트에 값 형식 명시

#### WRONG_INFERENCE (잘못된 추론)
**증상:** 사용자가 제공하지 않은 정보를 잘못 추론

**확인 사항:**
1. Agent가 추론한 값과 실제 사용자 응답 비교
2. 프롬프트가 추론을 유도하는지 확인

**해결 방법:**
- 프롬프트에 "사용자가 명시하지 않은 정보는 추론하지 마세요" 추가
- 슬롯 업데이트 검증 로직 강화

#### TURN_OVERFLOW (턴 초과)
**증상:** 15턴 내에 정보 수집 완료 못함

**확인 사항:**
1. 질문 효율성 확인 (한 질문에 여러 정보 수집 가능한지)
2. 불필요한 중복 질문이 있는지 확인
3. 시뮬레이터가 너무 비협조적인지 확인

**해결 방법:**
- 질문 전략 최적화
- 한 질문에 여러 슬롯 수집
- 테스트 케이스의 `response_rules` 조정

#### UNKNOWN (알 수 없는 실패)
**증상:** 위 카테고리에 해당하지 않는 실패

**확인 사항:**
1. 로그 전체 검토
2. 예외 스택 트레이스 확인
3. `evaluator.py`의 `classify_failure()` 로직 검토

**해결 방법:**
- 로그에 더 많은 정보 추가
- 새로운 실패 카테고리 정의
- 테스트 케이스 검증

## 개발 워크플로우

### 1단계: Red (테스트 실패 확인)
```bash
uv run python tests/run_tdd.py
```
- 초기 상태에서는 모든 테스트가 실패해야 함
- 실패 원인을 로그에서 확인

### 2단계: Green (최소 구현)
1. `src/graph.py` 수정
   - `ask_user()`: 질문 생성 로직
   - `process_input()`: 입력 파싱 로직
   - `should_continue()`: 완료 조건

2. 테스트 재실행
   ```bash
   uv run python tests/run_tdd.py
   ```

3. 성공할 때까지 반복

### 3단계: Refactor
- 코드 정리
- 추가 테스트 케이스 작성
- 프롬프트 최적화

## 새로운 테스트 케이스 추가

1. `data/scenarios/` 디렉토리에 새 JSON 파일 생성
   ```json
   {
     "id": "s02_v01",
     "name": "시나리오 이름",
     "description": "설명",
     "user_info": { ... },
     "response_rules": { ... },
     "ground_truth": { ... }
   }
   ```

2. TDD 실행 시 자동으로 포함됨

## 모니터링 지표

- **성공률**: 전체 테스트 중 성공한 비율
- **평균 턴 수**: 정보 수집에 걸린 평균 턴 수
- **실패 분포**: 각 실패 카테고리별 빈도

## 트러블슈팅

### 의존성 문제
```bash
uv sync --reinstall
```

### Python 버전 문제
```bash
# .python-version 파일 확인
cat .python-version

# Python 버전 설치
uv python install 3.11
```

### 로그가 생성되지 않음
```bash
# outputs/logs 디렉토리 확인
ls -la outputs/logs/

# 권한 확인
chmod -R 755 outputs/
```

## 참고 자료

- LangGraph 문서: https://langchain-ai.github.io/langgraph/
- uv 문서: https://docs.astral.sh/uv/
- 프로젝트 README: `auto-tdd-agent/README.md`

## 변경 이력

- **v0.1.0** (2026-02-01): 초기 Skill 생성
