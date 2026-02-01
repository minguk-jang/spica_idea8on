"""
TDD 디버그 스크립트 - s01_v01 테스트 케이스 디버깅
"""

import json
import traceback
from pathlib import Path

# 프로젝트 루트 경로 설정
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data" / "scenarios"


def load_test_case(tc_id: str):
    """테스트 케이스 로드"""
    tc_file = DATA_DIR / f"{tc_id}.json"
    with open(tc_file, "r", encoding="utf-8") as f:
        return json.load(f)


def debug_tdd_test():
    """TDD 테스트 디버그 실행"""
    print("=" * 60)
    print("TDD 디버그 - s01_v01 테스트 케이스")
    print("=" * 60)

    try:
        # 1. 테스트 케이스 로드
        print("\n1. 테스트 케이스 로드 중...")
        tc = load_test_case("s01_v01")
        print(f"   ✓ 테스트 케이스 로드 완료: {tc['id']}")
        print(f"   - 이름: {tc['name']}")
        print(f"   - 초기 메시지: {tc['user_info']['base']['initial_message']}")

        # 2. LangGraph 그래프 생성
        print("\n2. LangGraph 그래프 생성 중...")
        from src.graph import create_graph

        graph = create_graph()
        print("   ✓ 그래프 생성 완료")

        # 3. LangGraph 어댑터 생성
        print("\n3. LangGraph 어댑터 생성 중...")
        from tests.infrastructure.adapter import LangGraphAdapter

        adapter = LangGraphAdapter(graph)
        print("   ✓ 어댑터 생성 완료")

        # 4. 대화 시작
        print("\n4. 대화 시작 중...")
        initial_message = tc["user_info"]["base"]["initial_message"]
        print(f"   - 초기 메시지: '{initial_message}'")

        step_result = adapter.start_conversation(initial_message)

        # 5. 결과 출력
        print("\n5. StepResult 상세 정보:")
        print(f"   - agent_question: {step_result.agent_question}")
        print(f"   - user_response: {step_result.user_response}")
        print(f"   - current_plan: {step_result.current_plan}")
        print(f"   - is_complete: {step_result.is_complete}")
        print(f"   - error: {step_result.error}")

        if step_result.error:
            print(f"\n   ✗ 오류 발생!")
            print(f"   오류 메시지: {step_result.error}")
        else:
            print(f"\n   ✓ 대화 시작 성공!")
            print(f"   Agent 질문: {step_result.agent_question}")

    except Exception as e:
        print(f"\n✗ 예외 발생!")
        print(f"\n예외 타입: {type(e).__name__}")
        print(f"예외 메시지: {str(e)}")
        print(f"\n전체 스택 트레이스:")
        print("-" * 60)
        traceback.print_exc()
        print("-" * 60)


if __name__ == "__main__":
    debug_tdd_test()
