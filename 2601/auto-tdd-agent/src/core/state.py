"""
Agent 상태 정의
"""
from typing import TypedDict, List
from .types import MessageDict, PlanDict


class AgentState(TypedDict):
    """Agent 상태 정의"""
    messages: List[MessageDict]  # 대화 히스토리
    current_plan: PlanDict  # 현재 수집된 슬롯 정보
    turn_count: int  # 턴 카운터
