"""
TDD 심화 디버그 스크립트 - 그래프 내부 상태 확인
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


def debug_tdd_detailed():
    """TDD 테스트 상세 디버그 실행"""
    print("=" * 60)
    print("TDD 심화 디버그 - 그래프 내부 상태 확인")
    print("=" * 60)

    try:
        # 1. 테스트 케이스 로드
        print("\n1. 테스트 케이스 로드 중...")
        tc = load_test_case("s01_v01")
        print(f"   ✓ 테스트 케이스 로드 완료: {tc['id']}")

        # 2. LangGraph 그래프 생성
        print("\n2. LangGraph 그래프 생성 중...")
        from src.graph import create_graph
        from langgraph.checkpoint.memory import MemorySaver

        graph = create_graph()
        checkpointer = MemorySaver()
        compiled_graph = graph.compile(
            checkpointer=checkpointer, interrupt_before=["ask_user"]
        )
        print("   ✓ 그래프 컴파일 완료")

        # 3. 초기 상태로 그래프 실행
        print("\n3. 그래프 실행 중...")
        initial_message = tc["user_info"]["base"]["initial_message"]
        print(f"   - 초기 메시지: '{initial_message}'")

        initial_state = {
            "messages": [{"role": "user", "content": initial_message}],
            "current_plan": {},
            "turn_count": 0,
        }

        print(
            f"   - 초기 상태: {json.dumps(initial_state, ensure_ascii=False, indent=4)}"
        )

        thread_id = "test_thread"
        config = {"configurable": {"thread_id": thread_id}}

        print(f"   - 설정: {config}")

        # 그래프 실행
        result = compiled_graph.invoke(initial_state, config)

        print("\n4. 그래프 실행 결과:")
        print(f"   - 결과 키: {list(result.keys())}")
        print(f"   - current_plan: {result.get('current_plan', {})}")
        print(f"   - turn_count: {result.get('turn_count', 'N/A')}")

        # 메시지 상세 확인
        messages = result.get("messages", [])
        print(f"\n5. 메시지 목록 (총 {len(messages)}개):")
        for i, msg in enumerate(messages):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            print(
                f"   [{i}] {role}: {content[:100]}{'...' if len(content) > 100 else ''}"
            )

        # 마지막 에이전트 메시지 찾기
        agent_messages = [msg for msg in messages if msg.get("role") == "assistant"]
        print(f"\n6. Agent 메시지 수: {len(agent_messages)}")
        if agent_messages:
            print(
                f"   - 마지막 Agent 메시지: {agent_messages[-1].get('content', '')[:100]}"
            )
        else:
            print("   - Agent 메시지가 없습니다!")

        # 체크포인터 상태 확인
        print("\n7. 체크포인터 상태 확인:")
        try:
            state = compiled_graph.get_state(config)
            print(
                f"   - 상태 값 키: {list(state.values.keys()) if state.values else 'None'}"
            )
            print(f"   - 다음 노드: {state.next if hasattr(state, 'next') else 'N/A'}")
        except Exception as e:
            print(f"   - 상태 확인 실패: {e}")

    except Exception as e:
        print(f"\n✗ 예외 발생!")
        print(f"\n예외 타입: {type(e).__name__}")
        print(f"예외 메시지: {str(e)}")
        print(f"\n전체 스택 트레이스:")
        print("-" * 60)
        traceback.print_exc()
        print("-" * 60)


if __name__ == "__main__":
    debug_tdd_detailed()
