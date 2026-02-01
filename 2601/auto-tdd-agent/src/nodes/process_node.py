"""
입력 처리 노드
"""

import os

from ..core.state import AgentState
from ..services.response_parser import ResponseParser
from ..services.plan_manager import PlanManager


def process_input(state: AgentState) -> AgentState:
    """
    사용자 입력을 처리하는 노드

    Args:
        state: 현재 상태

    Returns:
        업데이트된 상태
    """
    # 마지막 사용자 메시지 추출
    user_message = None
    for msg in reversed(state["messages"]):
        if msg.get("role") == "user":
            user_message = msg.get("content")
            break

    if user_message:
        # 응답 파싱 (환경 변수에 따라 LLM 사용 여부 결정)
        use_llm = os.environ.get("USE_LLM", "true").lower() == "true"
        parser = ResponseParser(use_llm=use_llm)
        extracted_slots = parser.parse(user_message, state["current_plan"])

        # Plan 업데이트
        plan_manager = PlanManager()
        state["current_plan"] = plan_manager.update(
            state["current_plan"], extracted_slots
        )

    return state
