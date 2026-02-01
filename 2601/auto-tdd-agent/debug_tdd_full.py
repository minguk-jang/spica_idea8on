"""
TDD 완전 디버그 스크립트 - 전체 흐름 확인
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


def debug_full_flow():
    """전체 흐름 디버그"""
    print("=" * 60)
    print("TDD 완전 디버그 - 전체 흐름 확인")
    print("=" * 60)

    try:
        # 1. 테스트 케이스 로드
        print("\n[Step 1] 테스트 케이스 로드")
        tc = load_test_case("s01_v01")
        print(f"   ✓ 테스트 케이스: {tc['id']}")

        # 2. LangGraph 설정
        print("\n[Step 2] LangGraph 설정")
        from src.graph import create_graph
        from langgraph.checkpoint.memory import MemorySaver

        graph = create_graph()
        checkpointer = MemorySaver()

        # WITHOUT interrupt - let it run fully
        print("   - 인터럽트 없이 그래프 컴파일")
        compiled_graph = graph.compile(checkpointer=checkpointer)

        # 3. 초기 상태 설정
        print("\n[Step 3] 초기 상태 설정")
        initial_message = tc["user_info"]["base"]["initial_message"]
        initial_state = {
            "messages": [{"role": "user", "content": initial_message}],
            "current_plan": {},
            "turn_count": 0,
        }
        print(f"   - 초기 메시지: '{initial_message}'")

        thread_id = "test_thread"
        config = {"configurable": {"thread_id": thread_id}}

        # 4. 그래프 실행
        print("\n[Step 4] 그래프 실행 (인터럽트 없음)")
        result = compiled_graph.invoke(initial_state, config)

        print(f"   - 결과 키: {list(result.keys())}")
        print(f"   - current_plan: {result.get('current_plan', {})}")
        print(f"   - turn_count: {result.get('turn_count', 'N/A')}")

        # 5. 메시지 확인
        messages = result.get("messages", [])
        print(f"\n[Step 5] 메시지 목록 (총 {len(messages)}개):")
        for i, msg in enumerate(messages):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            print(f"   [{i}] {role}: {content}")

        # 6. 체크포인터 상태
        print(f"\n[Step 6] 체크포인터 상태:")
        state = compiled_graph.get_state(config)
        print(f"   - 다음 노드: {state.next}")
        print(f"   - 완료 여부: {state.next == ()}")

        # 7. WITH interrupt - test the adapter behavior
        print("\n" + "=" * 60)
        print("[테스트 2] 인터럽트 포함 그래프 (어댑터 방식)")
        print("=" * 60)

        compiled_graph_with_interrupt = graph.compile(
            checkpointer=MemorySaver(), interrupt_before=["ask_user"]
        )

        print("\n   - 그래프 실행 (interrupt_before=['ask_user'])")
        result2 = compiled_graph_with_interrupt.invoke(initial_state, config)

        messages2 = result2.get("messages", [])
        print(f"   - 메시지 수: {len(messages2)}")
        print(f"   - 메시지: {messages2}")

        # 상태 확인
        state2 = compiled_graph_with_interrupt.get_state(config)
        print(f"\n   - 다음 노드: {state2.next}")
        print(f"   - ask_user 노드 실행 전에 중단됨: {state2.next == ('ask_user',)}")

        # 8. 상태 업데이트 후 계속 실행
        print("\n   - 상태 업데이트 후 계속 실행...")
        updated_state = state2.values.copy()
        updated_state["messages"].append(
            {"role": "user", "content": "제주도로 가고 싶어요"}
        )
        updated_state["turn_count"] = updated_state.get("turn_count", 0) + 1

        compiled_graph_with_interrupt.update_state(config, updated_state)
        result3 = compiled_graph_with_interrupt.invoke(None, config)

        messages3 = result3.get("messages", [])
        print(f"   - 업데이트 후 메시지 수: {len(messages3)}")
        for i, msg in enumerate(messages3):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            print(
                f"   [{i}] {role}: {content[:80]}{'...' if len(content) > 80 else ''}"
            )

        print("\n" + "=" * 60)
        print("디버그 완료!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ 예외 발생!")
        print(f"\n예외 타입: {type(e).__name__}")
        print(f"예외 메시지: {str(e)}")
        print(f"\n전체 스택 트레이스:")
        print("-" * 60)
        traceback.print_exc()
        print("-" * 60)


if __name__ == "__main__":
    debug_full_flow()
