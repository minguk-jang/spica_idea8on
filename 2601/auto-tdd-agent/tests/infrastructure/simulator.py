"""
ScenarioSimulator: 테스트 케이스 기반 사용자 응답 시뮬레이션
"""
import re
from typing import Dict, Any, Optional, List


class ScenarioSimulator:
    """규칙 기반 사용자 시뮬레이터"""

    def __init__(self, test_case: Dict[str, Any]):
        self.tc = test_case
        self.user_info = test_case["user_info"]
        self.response_rules = test_case.get("response_rules", {})
        self.ground_truth = test_case["ground_truth"]

        # 응답 전략
        self.reveal_strategy = self.response_rules.get("reveal_strategy", "all_at_once")
        self.clarification_behavior = self.response_rules.get("clarification_behavior", "cooperative")
        self.style = self.response_rules.get("style", "concise")

    def respond(self, agent_question: str) -> str:
        """
        Agent의 질문에 대해 규칙 기반 응답 생성

        Args:
            agent_question: Agent가 한 질문

        Returns:
            시뮬레이션된 사용자 응답
        """
        # 질문 의도 파악
        slot_intent = self._detect_slot_intent(agent_question)

        if not slot_intent:
            # 의도를 파악하지 못한 경우
            return self._apply_style("잘 이해하지 못했어요. 다시 설명해주세요.")

        # 슬롯별 값 반환
        value = self._get_slot_value(slot_intent)

        if value is None:
            return self._apply_style("그건 잘 모르겠어요.")

        return self._apply_style(str(value))

    def _detect_slot_intent(self, question: str) -> Optional[str]:
        """
        질문에서 어떤 슬롯을 묻는지 정규식으로 파악

        Args:
            question: Agent의 질문

        Returns:
            슬롯 이름 또는 None
        """
        # 간단한 키워드 매칭 (실제로는 더 정교한 로직 필요)
        patterns = {
            "destination": r"(어디|목적지|가고\s*싶|여행지)",
            "start_date": r"(언제|출발|시작|날짜)",
            "duration": r"(며칠|기간|얼마나)",
            "budget": r"(예산|비용|돈|얼마)",
            "companions": r"(누구|동행|함께)",
            "purpose": r"(목적|이유|왜)",
        }

        question_lower = question.lower()
        for slot, pattern in patterns.items():
            if re.search(pattern, question_lower):
                return slot

        return None

    def _get_slot_value(self, slot: str) -> Optional[Any]:
        """
        슬롯에 대한 값을 reveal_strategy에 따라 반환

        Args:
            slot: 슬롯 이름

        Returns:
            슬롯 값 또는 None
        """
        # base 정보에서 찾기
        if slot in self.user_info.get("base", {}):
            return self.user_info["base"][slot]

        # actual 정보에서 찾기 (reveal_strategy에 따라)
        if slot in self.user_info.get("actual", {}):
            if self.reveal_strategy == "all_at_once":
                return self.user_info["actual"][slot]
            elif self.reveal_strategy == "vague_first":
                # 첫 번째는 모호하게, 두 번째부터 명확하게 (간단한 구현)
                return self.user_info["actual"][slot]

        return None

    def _apply_style(self, response: str) -> str:
        """
        응답 스타일 적용

        Args:
            response: 원본 응답

        Returns:
            스타일이 적용된 응답
        """
        if self.style == "talkative":
            return f"{response} 그리고 정말 기대돼요!"
        elif self.style == "reluctant":
            return f"음... {response}"
        else:  # concise
            return response
