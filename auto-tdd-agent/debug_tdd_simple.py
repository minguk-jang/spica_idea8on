"""
TDD 디버깅 스크립트
"""

import os
import sys

# 프로젝트 루트를 path에 추가
sys.path.insert(0, "/Users/mingukjang/git/spica_idea8on/2601/auto-tdd-agent")

# 규칙 기반 모드 설정
os.environ["USE_LLM"] = "false"
os.environ["USE_IPC_LLM"] = "false"

from src.graph import create_graph
from tests.infrastructure.adapter import LangGraphAdapter
from tests.infrastructure.simulator import ScenarioSimulator
import json

# 테스트 케이스 로드
tc_path = "/Users/mingukjang/git/spica_idea8on/2601/auto-tdd-agent/data/scenarios/s01_v01.json"
with open(tc_path, "r", encoding="utf-8") as f:
    tc = json.load(f)

print("=" * 60)
print("TDD 디버깅 시작")
print("=" * 60)
print(f"\n테스트 케이스: {tc['id']}")
print(f"시나리오: {tc['name']}")
print(f"Ground Truth: {tc['ground_truth']}")
print()

# 그래프 생성
print("[1] 그래프 생성...")
graph = create_graph()
print("   ✓ 그래프 생성 완료")

# 어댑터 생성
print("\n[2] 어댑터 초기화...")
adapter = LangGraphAdapter(graph)
print("   ✓ 어댑터 초기화 완료")

# 초기 메시지
initial_message = tc["user_info"]["base"].get(
    "initial_message", "여행 계획을 도와주세요."
)
print(f"\n[3] 초기 메시지: '{initial_message}'")

# 대화 시작
print("\n[4] 대화 시작 (start_conversation)...")
step_result = adapter.start_conversation(initial_message)

print(f"   결과:")
print(f"   - error: {step_result.error}")
print(f"   - is_complete: {step_result.is_complete}")
print(f"   - agent_question: {step_result.agent_question}")
print(f"   - current_plan: {step_result.current_plan}")

if step_result.error:
    print(f"\n   ❌ 오류 발생: {step_result.error}")
    sys.exit(1)

if step_result.is_complete:
    print(f"\n   ⚠️  첫 턴에서 완료됨 (이상함)")
    sys.exit(1)

if not step_result.agent_question:
    print(f"\n   ❌ Agent가 질문을 하지 않음")
    sys.exit(1)

print(f"\n   ✓ 대화 시작 성공")

# 시뮬레이터 생성
print("\n[5] 시뮬레이터 초기화...")
simulator = ScenarioSimulator(tc)
print("   ✓ 시뮬레이터 초기화 완료")

# 대화 루프
print("\n[6] 대화 루프 시작...")
print("=" * 60)

max_turns = 15
for turn in range(max_turns):
    print(f"\n[Turn {turn + 1}]")
    print(f"  Agent 질문: {step_result.agent_question}")

    # 시뮬레이터로 응답 생성
    user_response = simulator.respond(step_result.agent_question)
    print(f"  User 응답: {user_response}")

    # 대화 계속
    step_result = adapter.continue_conversation(user_response)

    print(f"  결과:")
    print(f"    - error: {step_result.error}")
    print(f"    - is_complete: {step_result.is_complete}")
    print(f"    - current_plan: {step_result.current_plan}")

    if step_result.error:
        print(f"\n  ❌ 오류 발생: {step_result.error}")
        break

    if step_result.is_complete:
        print(f"\n  ✓ 대화 완료!")
        break

    if not step_result.agent_question:
        print(f"\n  ⚠️  Agent가 다음 질문을 하지 않음")
        break

print("\n" + "=" * 60)
print("[7] 최종 결과")
print("=" * 60)
print(f"총 턴 수: {turn + 1}")
print(f"최종 Plan: {step_result.current_plan}")
print(f"Ground Truth: {tc['ground_truth']}")

# 비교
missing = []
wrong = []
for key, value in tc["ground_truth"].items():
    if key not in step_result.current_plan:
        missing.append(key)
    elif step_result.current_plan[key] != value:
        wrong.append(
            f"{key}: got '{step_result.current_plan[key]}', expected '{value}'"
        )

if missing:
    print(f"\n❌ 누락된 슬롯: {missing}")
if wrong:
    print(f"\n❌ 잘못된 값: {wrong}")

if not missing and not wrong:
    print("\n✅ 모든 슬롯이 정확히 수집됨!")
else:
    print("\n⚠️  일부 슬롯이 누락되거나 잘못됨")

print("\n" + "=" * 60)
print("디버깅 완료")
print("=" * 60)
