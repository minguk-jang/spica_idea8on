"""
질문 생성 서비스
"""

from typing import Dict, Any, Optional
from ..utils.prompt_loader import PromptLoader
from ..utils.llm_client import get_llm_client


class QuestionGenerator:
    """질문 생성 서비스"""

    def __init__(self, use_llm: bool = False):
        """
        초기화

        Args:
            use_llm: LLM 사용 여부 (False인 경우 규칙 기반)
        """
        self.prompt_loader = PromptLoader()
        self.use_llm = use_llm
        self.llm = None

        if use_llm:
            try:
                self.llm = get_llm_client()
            except ValueError as e:
                print(f"경고: LLM 초기화 실패 - {e}")
                print("규칙 기반 모드로 전환합니다.")
                self.use_llm = False

    def generate(self, current_plan: Dict[str, Any]) -> str:
        """
        현재 plan을 바탕으로 다음 질문 생성

        Args:
            current_plan: 현재 수집된 plan

        Returns:
            생성된 질문
        """
        if self.use_llm and self.llm:
            return self._generate_with_llm(current_plan)
        else:
            return self._generate_with_rules(current_plan)

    def _generate_with_llm(self, current_plan: Dict[str, Any]) -> str:
        """
        LLM을 사용하여 질문 생성

        Args:
            current_plan: 현재 수집된 plan

        Returns:
            생성된 질문
        """
        prompt = self.prompt_loader.load_question_prompt(current_plan)

        try:
            response = self.llm.invoke(prompt)
            # IPC 클라이언트는 문자열을 반환, ChatOpenAI는 객체를 반환
            if isinstance(response, str):
                return response.strip()
            else:
                return response.content.strip()
        except Exception as e:
            print(f"경고: LLM 호출 실패 - {e}")
            print("규칙 기반 모드로 전환합니다.")
            return self._generate_with_rules(current_plan)

    def _generate_with_rules(self, current_plan: Dict[str, Any]) -> str:
        """
        규칙 기반으로 질문 생성

        Args:
            current_plan: 현재 수집된 plan

        Returns:
            생성된 질문
        """
        # 수집되지 않은 필수 슬롯 확인
        required_slots = ["destination", "start_date", "duration"]

        for slot in required_slots:
            if slot not in current_plan:
                return self._generate_slot_question(slot)

        # 모든 필수 슬롯이 수집되면 선택 슬롯 확인
        optional_slots = ["budget", "companions", "purpose"]

        for slot in optional_slots:
            if slot not in current_plan:
                return self._generate_slot_question(slot)

        # 모든 정보가 수집되면 완료 메시지
        return "여행 계획이 완료되었습니다."

    def _generate_slot_question(self, slot: str) -> str:
        """
        슬롯별 질문 생성

        Args:
            slot: 슬롯 이름

        Returns:
            질문 문자열
        """
        questions = {
            "destination": "어디로 여행을 가고 싶으신가요?",
            "start_date": "언제 출발하실 예정인가요?",
            "duration": "여행 기간은 며칠인가요?",
            "budget": "예산은 얼마 정도 생각하고 계신가요?",
            "companions": "누구와 함께 가시나요?",
            "purpose": "여행의 목적은 무엇인가요?",
        }

        return questions.get(slot, "추가 정보를 알려주세요.")
