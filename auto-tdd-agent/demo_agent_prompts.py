"""
Agent Live Demo - LLM 프롬프트 출력용 Mock 테스트

실제 API 호출 없이 Agent가 LLM에 보내는 프롬프트를 출력합니다.
"""

import sys
from typing import Dict, Any, Optional
from dataclasses import dataclass


# Mock LLM 클라이언트 클래스
@dataclass
class MockLLMResponse:
    content: str


class MockLLMClient:
    """LLM 프롬프트 출력용 Mock 클라이언트"""

    def __init__(self, mock_responses: Optional[Dict[str, str]] = None):
        self.mock_responses = mock_responses or {}
        self.call_count = 0

    def invoke(self, prompt: str) -> MockLLMResponse:
        """
        LLM 호출 대신 프롬프트를 출력
        """
        self.call_count += 1

        print("\n" + "=" * 60)
        print(f"📝 LLM 프롬프트 호출 #{self.call_count}")
        print("=" * 60)
        print("\n📤 전송된 프롬프트:\n")
        print(prompt)
        print("-" * 60)

        # 간단한 키워드 매칭으로 응답 생성
        response = self._generate_mock_response(prompt)

        print("\n📥 모의 LLM 응답:\n")
        print(response)
        print("=" * 60)

        return MockLLMResponse(content=response)

    def _generate_mock_response(self, prompt: str) -> str:
        """프롬프트 내용을 기반으로 간단한 응답 생성"""

        # 질문 생성 프롬프트인 경우
        if "destination" in prompt and "start_date" in prompt and "duration" in prompt:
            if (
                "destination" in prompt.lower()
                or "여행 계획" in prompt
                or "current_plan" in prompt
            ):
                if "destination" in str(prompt).lower() and "{}" in str(prompt):
                    return "어디로 여행을 가고 싶으신가요?"
                elif "start_date" in str(prompt).lower() and "destination" in str(
                    prompt
                ):
                    return "언제 출발하실 예정인가요?"
                elif "duration" in str(prompt).lower():
                    return "여행 기간은 며칠인가요?"
                elif "budget" in str(prompt).lower():
                    return "예산은 얼마 정도 생각하고 계신가요?"
                else:
                    return "여행 계획이 완료되었습니다!"

        # 슬롯 업데이트(파싱) 프롬프트인 경우
        if "제주도" in prompt or "여행" in prompt:
            if "제주도" in prompt and "여행" in prompt:
                return '{"destination": "제주도"}'
            elif "3월 15일" in prompt or "3월15일" in prompt:
                return '{"start_date": "2026-03-15"}'
            elif "3박 4일" in prompt or "3박4일" in prompt:
                return '{"duration": "3박 4일"}'

        return "여행 계획이 완료되었습니다!"


# 모의 LLM 주입을 위한 패치
from src.utils import prompt_loader, llm_client
from src.services import question_generator, response_parser

# 원래 함수들 저장
_original_get_llm = llm_client.get_llm_client
_original_question_generator_init = question_generator.QuestionGenerator.__init__
_original_response_parser_init = response_parser.ResponseParser.__init__

# Mock LLM 인스턴스 생성
mock_llm = MockLLMClient()


# get_llm_client 패치
def mock_get_llm_client(temperature=None):
    return mock_llm


llm_client.get_llm_client = mock_get_llm_client


# QuestionGenerator 패치
def mock_question_generator_init(self, use_llm=True):
    self.prompt_loader = prompt_loader.PromptLoader()
    self.use_llm = True
    self.llm = mock_llm


question_generator.QuestionGenerator.__init__ = mock_question_generator_init


# ResponseParser 패치
def mock_response_parser_init(self, use_llm=True):
    self.prompt_loader = prompt_loader.PromptLoader()
    self.use_llm = True
    self.llm = mock_llm


response_parser.ResponseParser.__init__ = mock_response_parser_init


# 이제 Agent 임포트 및 실행
from src.agent import PlanningAgent
from src.core.env_config import EnvConfig


def main():
    print("\n" + "=" * 60)
    print("🤖 Planning Agent 라이브 Mock 테스트")
    print("=" * 60)
    print("\n이 스크립트는 실제 API를 호출하지 않고,")
    print("Agent가 LLM에 보내는 프롬프트를 출력합니다.\n")

    # Agent 생성 (이제 Mock LLM 사용)
    try:
        agent = PlanningAgent()
        print("✓ Agent 초기화 완료 (Mock LLM 사용)")
        print()
    except Exception as e:
        print(f"❌ Agent 초기화 실패: {e}")
        return

    # 대화 시작
    print("대화를 시작합니다...")
    print("-" * 60)

    # 첫 턴
    print("\n[Turn 1] User: 여행 계획 도와주세요")
    result = agent.run("여행 계획 도와주세요", thread_id="test_mock")
    print(f"\n[Turn 1] Agent: {result['messages'][-1]['content']}")

    # 두 번째 턴
    print("\n" + "-" * 60)
    print("\n[Turn 2] User: 제주도로 가고 싶어요")
    result = agent.continue_conversation("제주도로 가고 싶어요", thread_id="test_mock")
    print(f"\n[Turn 2] Agent: {result['messages'][-1]['content']}")
    print(f"[Turn 2] 현재 Plan: {result.get('current_plan', {})}")

    # 세 번째 턴
    print("\n" + "-" * 60)
    print("\n[Turn 3] User: 3월 15일에 출발할 거예요")
    result = agent.continue_conversation(
        "3월 15일에 출발할 거예요", thread_id="test_mock"
    )
    print(f"\n[Turn 3] Agent: {result['messages'][-1]['content']}")
    print(f"[Turn 3] 현재 Plan: {result.get('current_plan', {})}")

    # 네 번째 턴
    print("\n" + "-" * 60)
    print("\n[Turn 4] User: 3박 4일로 계획하고 있어요")
    result = agent.continue_conversation(
        "3박 4일로 계획하고 있어요", thread_id="test_mock"
    )
    print(f"\n[Turn 4] Agent: {result['messages'][-1]['content']}")
    print(f"[Turn 4] 현재 Plan: {result.get('current_plan', {})}")

    print("\n" + "=" * 60)
    print(f"✅ 테스트 완료!")
    print(f"총 LLM 호출 횟수: {mock_llm.call_count}")
    print(f"최종 Plan: {result.get('current_plan', {})}")
    print("=" * 60)


if __name__ == "__main__":
    main()
