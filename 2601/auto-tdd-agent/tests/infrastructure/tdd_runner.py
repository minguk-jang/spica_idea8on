"""
TDD 실행 메인 스크립트
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any

# TDD에서는 규칙 기반 모드로 실행 (LLM 없이) - imports 전에 설정
os.environ["USE_LLM"] = "false"
os.environ["USE_IPC_LLM"] = "false"

from tests.infrastructure.simulator import ScenarioSimulator
from tests.infrastructure.adapter import LangGraphAdapter, StepResult
from tests.evaluation.evaluator import evaluate_plan, EvaluationResult

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "scenarios"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "logs"


def load_all_tcs() -> List[Dict[str, Any]]:
    """
    data/scenarios 디렉토리에서 모든 테스트 케이스 로드

    Returns:
        테스트 케이스 리스트
    """
    test_cases = []

    if not DATA_DIR.exists():
        print(f"경고: {DATA_DIR} 디렉토리가 존재하지 않습니다.")
        return test_cases

    for tc_file in sorted(DATA_DIR.glob("*.json")):
        try:
            with open(tc_file, "r", encoding="utf-8") as f:
                tc = json.load(f)
                test_cases.append(tc)
        except Exception as e:
            print(f"경고: {tc_file} 로드 실패: {e}")

    return test_cases


def run_single_tc(tc: Dict[str, Any], max_turns: int = 15) -> EvaluationResult:
    """
    단일 테스트 케이스 실행

    Args:
        tc: 테스트 케이스
        max_turns: 최대 턴 수

    Returns:
        평가 결과
    """
    # Agent 그래프 생성
    from src.graph import create_graph

    graph = create_graph()

    # 어댑터 및 시뮬레이터 초기화
    adapter = LangGraphAdapter(graph)
    simulator = ScenarioSimulator(tc)

    # 대화 히스토리
    turn_history = []

    # 초기 메시지
    initial_message = tc["user_info"]["base"].get(
        "initial_message", "여행 계획을 도와주세요."
    )

    # 대화 시작
    step_result = adapter.start_conversation(initial_message)

    if step_result.error:
        return EvaluationResult(
            success=False,
            final_plan={},
            ground_truth=tc["ground_truth"],
            turn_count=0,
            failure_category=None,
            failure_detail=f"시작 오류: {step_result.error}",
        )

    # 대화 루프
    for turn in range(max_turns):
        if step_result.is_complete:
            break

        if not step_result.agent_question:
            # Agent가 질문을 하지 않음
            break

        # 시뮬레이터로 응답 생성
        user_response = simulator.respond(step_result.agent_question)

        # 히스토리 저장
        turn_history.append(
            {
                "turn": turn + 1,
                "question": step_result.agent_question,
                "response": user_response,
            }
        )

        # 대화 계속
        step_result = adapter.continue_conversation(user_response)

        if step_result.error:
            return EvaluationResult(
                success=False,
                final_plan=step_result.current_plan or {},
                ground_truth=tc["ground_truth"],
                turn_count=len(turn_history),
                failure_category=None,
                failure_detail=f"실행 오류: {step_result.error}",
            )

    # 평가
    final_plan = step_result.current_plan or {}
    result = evaluate_plan(final_plan, tc["ground_truth"], turn_history, max_turns)

    # 로그 저장
    save_log(tc["id"], result, turn_history)

    return result


def save_log(tc_id: str, result: EvaluationResult, turn_history: List[Dict[str, str]]):
    """
    테스트 결과를 로그 파일로 저장

    Args:
        tc_id: 테스트 케이스 ID
        result: 평가 결과
        turn_history: 턴 히스토리
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    log_data = {
        "test_case_id": tc_id,
        "success": result.success,
        "turn_count": result.turn_count,
        "final_plan": result.final_plan,
        "ground_truth": result.ground_truth,
        "failure_category": result.failure_category.value
        if result.failure_category
        else None,
        "failure_detail": result.failure_detail,
        "turn_history": turn_history,
    }

    log_file = OUTPUT_DIR / f"{tc_id}.json"
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

    print(f"로그 저장: {log_file}")


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("Planning Agent TDD 실행")
    print("=" * 60)
    print("[설정] 규칙 기반 모드로 실행 (LLM 미사용)")
    print()

    # 테스트 케이스 로드
    test_cases = load_all_tcs()

    if not test_cases:
        print("실행할 테스트 케이스가 없습니다.")
        return

    print(f"\n총 {len(test_cases)}개의 테스트 케이스를 발견했습니다.\n")

    # 결과 수집
    results = []

    for tc in test_cases:
        print(f"[{tc['id']}] {tc['name']} 실행 중...")

        try:
            result = run_single_tc(tc)
            results.append((tc, result))

            status = "✓ 성공" if result.success else "✗ 실패"
            print(f"  {status} ({result.turn_count}턴)")

            if not result.success and result.failure_detail:
                print(f"  실패 원인: {result.failure_detail}")

        except Exception as e:
            print(f"  ✗ 예외 발생: {e}")
            results.append((tc, None))

        print()

    # 요약 출력
    print("=" * 60)
    print("요약")
    print("=" * 60)

    success_count = sum(1 for _, r in results if r and r.success)
    total_count = len(results)

    print(f"성공: {success_count}/{total_count}")
    print(f"실패: {total_count - success_count}/{total_count}")

    # 실패 케이스별 분류
    if success_count < total_count:
        print("\n실패 케이스:")
        for tc, result in results:
            if not result or not result.success:
                failure_cat = (
                    result.failure_category.value
                    if result and result.failure_category
                    else "unknown"
                )
                print(f"  - {tc['id']}: {failure_cat}")


if __name__ == "__main__":
    main()
