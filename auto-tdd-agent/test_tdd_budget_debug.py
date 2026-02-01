"""
Quick TDD test with max_turns=5 for budget extraction debugging
"""

import json
import os
from pathlib import Path

# TDD는 규칙 기반 모드로 실행 (LLM 없이)
os.environ["USE_LLM"] = "false"
os.environ["USE_IPC_LLM"] = "false"

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data" / "scenarios"


def load_test_case(tc_id: str):
    """테스트 케이스 로드"""
    tc_file = DATA_DIR / f"{tc_id}.json"
    with open(tc_file, "r", encoding="utf-8") as f:
        return json.load(f)


def run_tdd_with_debug(tc_id: str = "s01_v01", max_turns: int = 5):
    """TDD 실행 with debug output for budget extraction"""
    print("=" * 70)
    print(f"TDD Debug Test - {tc_id} (max_turns={max_turns})")
    print("=" * 70)
    print("[설정] 규칙 기반 모드로 실행 (LLM 미사용)")
    print()

    # 1. 테스트 케이스 로드
    print("1. 테스트 케이스 로드 중...")
    tc = load_test_case(tc_id)
    print(f"   ✓ 테스트 케이스: {tc['id']} - {tc['name']}")
    print(f"   - Ground Truth Budget: {tc['ground_truth'].get('budget', 'N/A')}")
    print()

    # 2. 그래프 및 어댑터 생성
    print("2. LangGraph 설정 중...")
    from src.graph import create_graph
    from tests.infrastructure.adapter import LangGraphAdapter
    from tests.infrastructure.simulator import ScenarioSimulator

    graph = create_graph()
    adapter = LangGraphAdapter(graph)
    simulator = ScenarioSimulator(tc)
    print("   ✓ 그래프 및 어댑터 생성 완료")
    print()

    # 3. 대화 시작
    print("3. 대화 시작...")
    initial_message = tc["user_info"]["base"]["initial_message"]
    print(f"   [User] {initial_message}")

    step_result = adapter.start_conversation(initial_message)

    if step_result.error:
        print(f"   ✗ 오류: {step_result.error}")
        return

    print(f"   [Agent] {step_result.agent_question}")
    print(f"   - 현재 Plan: {step_result.current_plan}")
    print()

    # 4. 대화 루프 (max_turns까지만)
    print("4. 대화 루프 실행...")
    print("-" * 70)

    turn_history = []

    for turn in range(max_turns):
        print(f"\n[Turn {turn + 1}/{max_turns}]")

        if step_result.is_complete:
            print("   → 대화 완료!")
            break

        if not step_result.agent_question:
            print("   → Agent가 질문하지 않음 (종료)")
            break

        # 사용자 응답 생성
        user_response = simulator.respond(step_result.agent_question)
        print(f"   [User] {user_response}")

        # Budget 추출 디버깅
        from src.services.response_parser import ResponseParser

        parser = ResponseParser(use_llm=False)
        parsed = parser.parse(user_response)

        if "budget" in parsed:
            print(f"   [Debug] Budget 추출됨: {parsed['budget']}")
        elif (
            "예산" in step_result.agent_question
            or "비용" in step_result.agent_question
            or "돈" in step_result.agent_question
        ):
            print(f"   [Debug] Budget 관련 질문에 응답: '{user_response}'")
            print(f"   [Debug] 추출된 값: {parsed}")

        # 대화 계속
        step_result = adapter.continue_conversation(user_response)

        if step_result.error:
            print(f"   ✗ 오류: {step_result.error}")
            break

        print(f"   [Agent] {step_result.agent_question}")
        print(
            f"   - 현재 Plan: {json.dumps(step_result.current_plan, ensure_ascii=False)}"
        )

        # 히스토리 저장
        turn_history.append(
            {
                "turn": turn + 1,
                "question": step_result.agent_question,
                "response": user_response,
                "plan": step_result.current_plan.copy()
                if step_result.current_plan
                else {},
            }
        )

    print("\n" + "=" * 70)
    print("5. 최종 결과")
    print("=" * 70)
    print(f"   - 총 턴 수: {len(turn_history)}")
    print(f"   - 완료 여부: {step_result.is_complete}")
    print(
        f"   - 최종 Plan: {json.dumps(step_result.current_plan, ensure_ascii=False, indent=2)}"
    )
    print(f"   - Ground Truth Budget: {tc['ground_truth'].get('budget', 'N/A')}")

    if step_result.current_plan and "budget" in step_result.current_plan:
        extracted_budget = step_result.current_plan["budget"]
        expected_budget = tc["ground_truth"].get("budget")
        match = extracted_budget == expected_budget
        print(
            f"   - Budget 추출 결과: {extracted_budget} {'✓ 일치' if match else '✗ 불일치'}"
        )
    else:
        print(f"   - Budget 추출 결과: 미추출 ✗")

    print()


if __name__ == "__main__":
    run_tdd_with_debug("s01_v01", max_turns=5)
