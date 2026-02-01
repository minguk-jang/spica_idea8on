"""
데이터 검증 로직
"""
import re
from typing import Any
from ..core.config import AgentConfig


class PlanValidator:
    """Plan 검증 로직"""

    def __init__(self, config: AgentConfig):
        """
        Args:
            config: Agent 설정
        """
        self.config = config

    def validate_slot_type(self, slot_name: str, value: Any) -> bool:
        """
        슬롯 타입 검증

        Args:
            slot_name: 슬롯 이름
            value: 검증할 값

        Returns:
            검증 성공 여부
        """
        expected_type = self.config.slot_types.get(slot_name)

        if expected_type == 'date':
            return self._is_valid_date(value)
        elif expected_type == 'string':
            return isinstance(value, str) and len(value) > 0
        elif expected_type == 'number':
            return isinstance(value, (int, float))

        # 타입이 정의되지 않은 경우 통과
        return True

    def _is_valid_date(self, value: str) -> bool:
        """
        날짜 형식 검증

        Args:
            value: 검증할 날짜 문자열

        Returns:
            유효한 날짜 형식인지 여부
        """
        if not isinstance(value, str):
            return False

        # YYYY-MM-DD 형식 검증
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        return bool(re.match(pattern, value))

    def validate_plan_completeness(self, plan: dict) -> tuple[bool, list]:
        """
        Plan 완성도 검증

        Args:
            plan: 검증할 plan

        Returns:
            (완성 여부, 누락된 필수 슬롯 목록)
        """
        missing_slots = []

        for slot in self.config.required_slots:
            if slot not in plan or not plan[slot]:
                missing_slots.append(slot)

        is_complete = len(missing_slots) == 0
        return is_complete, missing_slots
