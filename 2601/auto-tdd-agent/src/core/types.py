"""
공통 타입 정의
"""
from typing import Dict, Any
from enum import Enum


class SlotType(Enum):
    """슬롯 타입 정의"""
    DESTINATION = "destination"
    START_DATE = "start_date"
    DURATION = "duration"
    BUDGET = "budget"
    COMPANIONS = "companions"
    PURPOSE = "purpose"


# 메시지 타입
MessageDict = Dict[str, str]  # {"role": str, "content": str}

# Plan 타입
PlanDict = Dict[str, Any]  # 슬롯 데이터
