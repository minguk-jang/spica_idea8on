"""
Agent 라이브 테스트 스크립트

실제 GLM API를 호출하여 Agent가 작동하는지 확인합니다.
"""
from src.agent import PlanningAgent
from src.core.env_config import EnvConfig


def main():
    print("=" * 60)
    print("Planning Agent 라이브 테스트")
    print("=" * 60)
    print()

    # 환경 변수 확인
    if not EnvConfig.validate():
        print("❌ GLM_API_KEY가 설정되지 않았습니다.")
        print("💡 .env 파일을 열어 API 키를 설정하세요.")
        return

    print("✓ API Key 설정 확인")
    print(f"✓ Model: {EnvConfig.GLM_MODEL}")
    print()

    # Agent 생성
    try:
        agent = PlanningAgent()
        print("✓ Agent 초기화 완료")
        print()
    except Exception as e:
        print(f"❌ Agent 초기화 실패: {e}")
        return

    # 대화 시작
    print("대화를 시작합니다...")
    print("-" * 60)

    try:
        # 첫 턴
        result = agent.run("여행 계획 도와주세요", thread_id="test_live")
        print(f"Agent: {result['messages'][-1]['content']}")
        print()

        # 두 번째 턴
        result = agent.continue_conversation("제주도로 가고 싶어요", thread_id="test_live")
        print(f"User: 제주도로 가고 싶어요")
        print(f"Agent: {result['messages'][-1]['content']}")
        print(f"현재 Plan: {result.get('current_plan', {})}")
        print()

        # 세 번째 턴
        result = agent.continue_conversation("3월 15일에 출발할 거예요", thread_id="test_live")
        print(f"User: 3월 15일에 출발할 거예요")
        print(f"Agent: {result['messages'][-1]['content']}")
        print(f"현재 Plan: {result.get('current_plan', {})}")
        print()

        # 네 번째 턴
        result = agent.continue_conversation("3박 4일로 계획하고 있어요", thread_id="test_live")
        print(f"User: 3박 4일로 계획하고 있어요")
        print(f"Agent: {result['messages'][-1]['content']}")
        print(f"현재 Plan: {result.get('current_plan', {})}")
        print()

        print("-" * 60)
        print("✅ 테스트 완료!")
        print(f"최종 Plan: {result.get('current_plan', {})}")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
