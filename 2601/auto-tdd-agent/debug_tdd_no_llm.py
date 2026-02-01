"""
TDD 디버그 스크립트 - 규칙 기반 모드 (LLM 없음)
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


def debug_without_llm():
    """LLM 없이 규칙 기반으로 디버그"""
    print("=" * 60)
    print("TDD 디버그 - 규칙 기반 모드 (LLM 없음)")
    print("=" * 60)

    try:
        # 1. 테스트 케이스 로드
        print("\n[Step 1] 테스트 케이스 로드")
        tc = load_test_case("s01_v01")
        print(f"   ✓ 테스트 케이스: {tc['id']}")

        # 2. 규칙 기반 파서 테스트
        print("\n[Step 2] ResponseParser 테스트 (규칙 기반)")
        from src.services.response_parser import ResponseParser

        parser = ResponseParser(use_llm=False)  # 규칙 기반

        # 테스트 메시지로 파싱 테스트
        test_messages = [
            "여행 계획을 도와주세요.",
            "제주도로 가고 싶어요",
            "2026-03-15에 출발합니다",
            "3박 4일로 갈 거예요",
            "100만원 예산입니다",
        ]

        for msg in test_messages:
            result = parser.parse(msg, {})
            print(f"   - '{msg}' -> {result}")

        # 3. 규칙 기반 질문 생성 테스트
        print("\n[Step 3] QuestionGenerator 테스트 (규칙 기반)")
        from src.services.question_generator import QuestionGenerator

        generator = QuestionGenerator(use_llm=False)  # 규칙 기반

        # 다양한 plan 상태로 테스트
        test_plans = [
            {},  # 아무것도 없음
            {"destination": "제주도"},  # 목적지만 있음
            {"destination": "제주도", "start_date": "2026-03-15"},  # 2개
            {
                "destination": "제주도",
                "start_date": "2026-03-15",
                "duration": "3박 4일",
            },  # 필수 완료
            {
                "destination": "제주도",
                "start_date": "2026-03-15",
                "duration": "3박 4일",
                "budget": "100만원",
            },  # 4개
        ]

        for plan in test_plans:
            question = generator.generate(plan)
            print(f"   - Plan: {plan}")
            print(f"     질문: '{question}'")

        # 4. 그래프 실행 (규칙 기반)
        print("\n[Step 4] 그래프 실행 (규칙 기반)")
        from src.graph import create_graph
        from langgraph.checkpoint.memory import MemorySaver
        from src.core.config import AgentConfig
        from src.core.state import AgentState

        # 수동으로 상태 관리하며 테스트
        initial_message = tc["user_info"]["base"]["initial_message"]
        print(f"   - 초기 메시지: '{initial_message}'")

        # 상태 초기화
        state = {
            "messages": [{"role": "user", "content": initial_message}],
            "current_plan": {},
            "turn_count": 0,
        }

        # process_input 수동 실행
        print("\n[Step 5] process_input 노드 실행")
        from src.nodes.process_node import process_input

        state = process_input(state)
        print(f"   - 처리 후 current_plan: {state['current_plan']}")
        print(f"   - 메시지 수: {len(state['messages'])}")

        # ask_user 수동 실행
        print("\n[Step 6] ask_user 노드 실행")
        from src.nodes.question_node import ask_user

        state = ask_user(state)
        print(f"   - 질문 생성 후 current_plan: {state['current_plan']}")
        print(f"   - 메시지 수: {len(state['messages'])}")

        # 메시지 확인
        for i, msg in enumerate(state["messages"]):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            print(f"   [{i}] {role}: {content}")

        # 5. 라우터 테스트
        print("\n[Step 7] 라우터 테스트")
        from src.nodes.router import should_continue
        from src.core.config import AgentConfig

        schema_path = PROJECT_ROOT / "data" / "plan_schema.json"
        config = AgentConfig.from_schema_file(schema_path)

        result = should_continue(state, config)
        print(f"   - 라우터 결과: {result}")
        print(f"   - should_continue: {result == 'ask_user'}")
        print(f"   - should_end: {result == 'end'}")

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
        raise


if __name__ == "__main__":
    debug_without_llm()
