"""
Plan 상태 관리 서비스
"""
from typing import Dict, Any, List
from ..core.config import AgentConfig


class PlanManager:
    """Plan 업데이트 관리 서비스"""

    def __init__(self, config: AgentConfig = None):
        """
        Args:
            config: Agent 설정 (None인 경우 기본 설정 사용)
        """
        self.config = config or AgentConfig.default()

    def update(
        self,
        current_plan: Dict[str, Any],
        extracted_slots: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        현재 plan을 추출된 슬롯으로 업데이트

        Args:
            current_plan: 현재 plan
            extracted_slots: 추출된 슬롯 정보

        Returns:
            업데이트된 plan
        """
        updated_plan = current_plan.copy()

        # 새로운 슬롯 정보 병합
        for key, value in extracted_slots.items():
            if value:  # 값이 있는 경우만 업데이트
                updated_plan[key] = value

        return updated_plan

    def is_complete(self, plan: Dict[str, Any]) -> bool:
        """
        Plan이 완성되었는지 확인

        Args:
            plan: 검증할 plan

        Returns:
            완성 여부
        """
        return all(
            slot in plan and plan[slot]
            for slot in self.config.required_slots
        )

    def get_missing_slots(self, plan: Dict[str, Any]) -> List[str]:
        """
        누락된 필수 슬롯 목록 반환

        Args:
            plan: 검증할 plan

        Returns:
            누락된 슬롯 목록
        """
        missing = []

        for slot in self.config.required_slots:
            if slot not in plan or not plan[slot]:
                missing.append(slot)

        return missing

    def get_next_slot_to_collect(self, plan: Dict[str, Any]) -> str:
        """
        다음에 수집할 슬롯 결정

        Args:
            plan: 현재 plan

        Returns:
            다음 슬롯 이름 또는 None
        """
        # 필수 슬롯 우선
        for slot in self.config.required_slots:
            if slot not in plan or not plan[slot]:
                return slot

        # 선택 슬롯
        for slot in self.config.optional_slots:
            if slot not in plan or not plan[slot]:
                return slot

        return None
