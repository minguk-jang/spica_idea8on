"""
Evaluator: 평가 로직 및 실패 분류
"""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, List, Optional


class FailureCategory(Enum):
    """실패 유형 분류"""
    PARSING_ERROR = "parsing_error"  # 사용자 입력 파싱 실패
    REDUNDANT_QUESTION = "redundant_question"  # 중복 질문
    MISSED_SLOT = "missed_slot"  # 슬롯 수집 누락
    WRONG_VALUE = "wrong_value"  # 잘못된 값 수집
    WRONG_INFERENCE = "wrong_inference"  # 잘못된 추론
    TURN_OVERFLOW = "turn_overflow"  # 턴 수 초과
    UNKNOWN = "unknown"  # 알 수 없는 실패


@dataclass
class EvaluationResult:
    """평가 결과"""
    success: bool
    final_plan: Dict[str, Any]
    ground_truth: Dict[str, Any]
    turn_count: int
    failure_category: Optional[FailureCategory] = None
    failure_detail: Optional[str] = None


def evaluate_plan(
    final_plan: Dict[str, Any],
    ground_truth: Dict[str, Any],
    turn_history: List[Dict[str, str]],
    max_turns: int = 15
) -> EvaluationResult:
    """
    최종 plan을 ground_truth와 비교하여 평가

    Args:
        final_plan: Agent가 수집한 최종 plan
        ground_truth: 기대되는 정답 plan
        turn_history: 턴별 질문/응답 히스토리
        max_turns: 최대 허용 턴 수

    Returns:
        평가 결과
    """
    turn_count = len(turn_history)

    # 턴 수 초과 확인
    if turn_count > max_turns:
        return EvaluationResult(
            success=False,
            final_plan=final_plan,
            ground_truth=ground_truth,
            turn_count=turn_count,
            failure_category=FailureCategory.TURN_OVERFLOW,
            failure_detail=f"최대 턴 수({max_turns})를 초과했습니다: {turn_count}턴"
        )

    # Plan 비교
    if plans_match(final_plan, ground_truth):
        return EvaluationResult(
            success=True,
            final_plan=final_plan,
            ground_truth=ground_truth,
            turn_count=turn_count
        )

    # 실패 원인 분류
    failure_cat, failure_detail = classify_failure(
        final_plan, ground_truth, turn_history
    )

    return EvaluationResult(
        success=False,
        final_plan=final_plan,
        ground_truth=ground_truth,
        turn_count=turn_count,
        failure_category=failure_cat,
        failure_detail=failure_detail
    )


def plans_match(plan: Dict[str, Any], ground_truth: Dict[str, Any]) -> bool:
    """
    두 plan이 일치하는지 확인

    Args:
        plan: 비교할 plan
        ground_truth: 정답 plan

    Returns:
        일치 여부
    """
    # 모든 ground_truth의 키가 plan에 있고 값이 일치하는지 확인
    for key, value in ground_truth.items():
        if key not in plan:
            return False
        if plan[key] != value:
            return False
    return True


def classify_failure(
    final_plan: Dict[str, Any],
    ground_truth: Dict[str, Any],
    turn_history: List[Dict[str, str]]
) -> tuple[FailureCategory, str]:
    """
    실패 원인 분류

    Args:
        final_plan: Agent가 수집한 최종 plan
        ground_truth: 기대되는 정답 plan
        turn_history: 턴별 질문/응답 히스토리

    Returns:
        (실패 카테고리, 상세 설명)
    """
    # 누락된 슬롯 확인
    missing_slots = []
    for key in ground_truth:
        if key not in final_plan:
            missing_slots.append(key)

    if missing_slots:
        return (
            FailureCategory.MISSED_SLOT,
            f"누락된 슬롯: {', '.join(missing_slots)}"
        )

    # 잘못된 값 확인
    wrong_values = []
    for key, expected_value in ground_truth.items():
        if key in final_plan and final_plan[key] != expected_value:
            wrong_values.append(f"{key}: {final_plan[key]} (기대값: {expected_value})")

    if wrong_values:
        return (
            FailureCategory.WRONG_VALUE,
            f"잘못된 값: {', '.join(wrong_values)}"
        )

    # 중복 질문 확인
    questions = [turn.get("question", "") for turn in turn_history]
    if len(questions) != len(set(questions)):
        return (
            FailureCategory.REDUNDANT_QUESTION,
            "동일한 질문을 반복했습니다"
        )

    return (FailureCategory.UNKNOWN, "알 수 없는 실패 원인")
