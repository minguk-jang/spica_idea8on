"""
라우팅 로직
"""

from langgraph.graph import END
from ..core.state import AgentState
from ..core.config import AgentConfig
from ..services.plan_manager import PlanManager


def should_continue(state: AgentState, config: AgentConfig = None) -> str:
    """
    대화를 계속할지 결정하는 조건 함수

    Args:
        state: 현재 상태
        config: Agent 설정 (None인 경우 기본 설정 사용)

    Returns:
        다음 노드 이름 또는 END
    """
    if config is None:
        config = AgentConfig.default()

    # 턴 수 초과 체크
    if state.get("turn_count", 0) > config.max_turns:
        return END

    # Plan 완성도 확인 (필수 슬롯 + 선택 슬롯 모두)
    plan_manager = PlanManager(config)
    current_plan = state.get("current_plan", {})

    # 필수 슬롯 확인
    required_complete = plan_manager.is_complete(current_plan)

    # 선택 슬롯 확인
    optional_complete = all(
        slot in current_plan and current_plan[slot] for slot in config.optional_slots
    )

    # 필수 + 선택 모두 완료되면 END
    if required_complete and optional_complete:
        return END

    return "ask_user"
