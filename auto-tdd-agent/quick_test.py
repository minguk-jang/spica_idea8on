#!/usr/bin/env python3
"""
간단한 TDD 테스트 - 3턴으로 제한
"""

import sys
import os

# Force unbuffered output
sys.stdout = os.fdopen(sys.stdout.fileno(), "w", 1)
sys.stderr = os.fdopen(sys.stderr.fileno(), "w", 1)

# 환경 변수 설정 (imports 전)
os.environ["USE_LLM"] = "false"
os.environ["USE_IPC_LLM"] = "false"

sys.path.insert(0, "/Users/mingukjang/git/spica_idea8on/2601/auto-tdd-agent")

import json
from src.graph import create_graph
from tests.infrastructure.adapter import LangGraphAdapter
from tests.infrastructure.simulator import ScenarioSimulator

# 테스트 케이스 로드
tc_path = "/Users/mingukjang/git/spica_idea8on/2601/auto-tdd-agent/data/scenarios/s01_v01.json"
with open(tc_path, "r", encoding="utf-8") as f:
    tc = json.load(f)

print("=" * 60)
print("간단한 TDD 테스트 (3턴 제한)")
print("=" * 60)
print(f"테스트 케이스: {tc['id']}")
print()

# 그래프 및 어댑터 생성
graph = create_graph()
adapter = LangGraphAdapter(graph)
simulator = ScenarioSimulator(tc)

# 초기 메시지
initial_message = tc["user_info"]["base"].get(
    "initial_message", "여행 계획을 도와주세요."
)
print(f"초기 메시지: '{initial_message}'")
print()

# 대화 시작
step_result = adapter.start_conversation(initial_message)
print(f"[턴 1] 질문: {step_result.agent_question}")

# 6턴으로 제한 (budget, companions, purpose 수집을 위해)
for turn in range(1, 7):  # 턴 2, 3, 4, 5, 6, 7
    if step_result.is_complete or not step_result.agent_question:
        print("  -> 대화 완료 또는 질문 없음")
        break

    # 사용자 응답 생성
    user_response = simulator.respond(step_result.agent_question)
    print(f"      응답: {user_response}")

    # 대화 계속
    step_result = adapter.continue_conversation(user_response)

    print(f"  현재 Plan: {step_result.current_plan}")

    if step_result.agent_question:
        print(f"\n[턴 {turn + 1}] 질문: {step_result.agent_question}")

print()
print("=" * 60)
print("최종 결과")
print("=" * 60)
print(f"최종 Plan: {step_result.current_plan}")
print(f"Ground Truth: {tc['ground_truth']}")

# 비교
missing = []
for key in tc["ground_truth"]:
    if key not in step_result.current_plan:
        missing.append(key)

if missing:
    print(f"\n누락된 슬롯: {missing}")
else:
    print("\n✅ 모든 슬롯 수집 완료!")
