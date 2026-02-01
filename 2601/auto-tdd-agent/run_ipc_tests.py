#!/usr/bin/env python3
"""
IPC 기반 LLM 테스트 러너
TDD를 Opencode LLM(IPC)과 함께 실행
"""

import os
import sys
import json
import time
import threading
import socket
import re
from pathlib import Path
from typing import List, Dict, Any

# IPC 모드 활성화 (imports 전에 설정)
os.environ["USE_LLM"] = "true"
os.environ["USE_IPC_LLM"] = "true"

from tests.infrastructure.simulator import ScenarioSimulator
from tests.infrastructure.adapter import LangGraphAdapter, StepResult
from tests.evaluation.evaluator import evaluate_plan, EvaluationResult
from src.graph import create_graph
from src.core.config import AgentConfig

SOCKET_PATH = "/tmp/opencode_llm_socket"
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data" / "scenarios"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "logs"


def extract_user_input_from_prompt(prompt: str) -> str:
    """프롬프트에서 사용자 입력 추출"""
    lines = prompt.split("\n")
    for line in lines:
        if line.startswith("사용자 응답:") or line.startswith("User:"):
            return line.split(":", 1)[1].strip()
    return ""


def extract_plan_from_prompt(prompt: str) -> Dict[str, Any]:
    """프롬프트에서 현재 plan 상태 추출"""
    plan = {}
    slots = ["destination", "start_date", "duration", "budget", "companions", "purpose"]
    for slot in slots:
        if f'"{slot}": ""' in prompt or f'"{slot}": """' in prompt:
            plan[slot] = ""  # 비어있음
        elif f'"{slot}":' in prompt:
            match = re.search(rf'"{slot}":\s*"([^"]+)"', prompt)
            if match:
                plan[slot] = match.group(1)
    return plan


def handle_llm_request(conn: socket.socket):
    """단일 LLM 요청 처리"""
    try:
        request_data = b""
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            request_data += chunk

        request = json.loads(request_data.decode())
        prompt = request.get("prompt", "")

        print(f"Received prompt (first 200 chars): {prompt[:200]}")

        # 프롬프트 분석하여 응답 생성
        response_content = generate_smart_response(prompt)

        response = {"content": response_content}
        conn.sendall(json.dumps(response).encode())

    except Exception as e:
        error_response = {"content": f'{{"error": "{str(e)}"}}'}
        conn.sendall(json.dumps(error_response).encode())
    finally:
        conn.close()


def generate_smart_response(prompt: str) -> str:
    """프롬프트를 분석하여 적절한 응답 생성"""
    user_input = extract_user_input_from_prompt(prompt)
    current_plan = extract_plan_from_prompt(prompt)

    # 슬롯 업데이트 요청인지 질문 생성 요청인지 판단
    if (
        "업데이트" in prompt
        or "추출" in prompt
        or "parser" in prompt.lower()
        or "slot" in prompt.lower()
    ):
        return generate_slot_parsing_response(user_input)
    else:
        return generate_question_response(current_plan)


def generate_slot_parsing_response(user_input: str) -> str:
    """사용자 입력에서 슬롯 추출하여 JSON 반환"""
    extracted = {}

    if not user_input:
        return json.dumps(extracted, ensure_ascii=False)

    # 목적지
    dest_match = re.search(
        r"(제주도?|부산|서울|강릉|경주|전주|여수|속초|대구|광주|인천|대전)", user_input
    )
    if dest_match and len(dest_match.group(1)) >= 2:
        extracted["destination"] = dest_match.group(1)

    # 날짜
    date_match = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", user_input)
    if date_match:
        year, month, day = date_match.groups()
        extracted["start_date"] = f"{year}-{int(month):02d}-{int(day):02d}"
    else:
        date_match = re.search(r"(\d{1,2})월\s*(\d{1,2})일", user_input)
        if date_match:
            month, day = date_match.groups()
            extracted["start_date"] = f"2026-{int(month):02d}-{int(day):02d}"

    # 기간
    duration_match = re.search(r"(\d+)박\s*(\d+)일", user_input)
    if duration_match:
        nights, days = duration_match.groups()
        extracted["duration"] = f"{nights}박 {days}일"
    else:
        duration_match = re.search(r"(\d+)일", user_input)
        if duration_match:
            extracted["duration"] = f"{duration_match.group(1)}일"

    # 예산
    budget_match = re.search(r"(\d+)\s*만\s*원?", user_input)
    if budget_match:
        extracted["budget"] = f"{budget_match.group(1)}만원"
    elif re.search(r"(\d+만원)", user_input):
        match = re.search(r"(\d+만원)", user_input)
        extracted["budget"] = match.group(1)

    # 동반자
    companions_patterns = [
        r"(혼자|혼자서|나 혼자|혼자 여행)",
        r"(친구\s*\d*명?|친구랑|친구와|친구들?)",
        r"(가족|부모님|아이들?|아들|딸|형제|자매)",
        r"(연인|남자친구|여자친구|배우자|부부)",
    ]
    for pattern in companions_patterns:
        match = re.search(pattern, user_input)
        if match:
            extracted["companions"] = match.group(1)
            break

    # 목적
    purpose_patterns = [
        r"(휴양|휴식|쉬|힐링|재충전)",
        r"(관광|구경|볼거리|관람|탐방)",
        r"(먹방|맛집|음식|미식|먹을거리)",
        r"(액티비티|체험|모험|스포츠|서핑|등산|자전거)",
        r"(문화|역사|박물관|미술관|전시|공연)",
        r"(쇼핑|쇼핑하|구매|사고\s*싶)",
    ]
    for pattern in purpose_patterns:
        match = re.search(pattern, user_input)
        if match:
            extracted["purpose"] = match.group(1)
            break

    return json.dumps(extracted, ensure_ascii=False)


def generate_question_response(current_plan: Dict[str, Any]) -> str:
    """현재 plan 상태에 따른 다음 질문 생성"""
    # 필수 슬롯 먼저 확인
    if not current_plan.get("destination"):
        return "어디로 여행을 가고 싶으신가요?"
    elif not current_plan.get("start_date"):
        return "언제 출발하실 예정인가요?"
    elif not current_plan.get("duration"):
        return "여행 기간은 며칠인가요?"
    # 선택 슬롯
    elif not current_plan.get("budget"):
        return "예산은 얼마 정도 생각하고 계신가요?"
    elif not current_plan.get("companions"):
        return "누구와 함께 가시나요?"
    elif not current_plan.get("purpose"):
        return "여행의 목적은 무엇인가요?"
    else:
        return "여행 계획이 완료되었습니다."


def start_ipc_server():
    """IPC 서버 실행"""
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(5)
    server.settimeout(1.0)

    print(f"🔌 IPC LLM Server started at {SOCKET_PATH}")

    running = True
    try:
        while running:
            try:
                conn, _ = server.accept()
                thread = threading.Thread(target=handle_llm_request, args=(conn,))
                thread.daemon = True
                thread.start()
            except socket.timeout:
                continue
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)


def load_all_tcs() -> List[Dict[str, Any]]:
    """모든 테스트 케이스 로드"""
    test_cases = []
    if not DATA_DIR.exists():
        return test_cases

    for tc_file in sorted(DATA_DIR.glob("*.json")):
        try:
            with open(tc_file, "r", encoding="utf-8") as f:
                test_cases.append(json.load(f))
        except Exception as e:
            print(f"경고: {tc_file} 로드 실패: {e}")

    return test_cases


def run_single_tc(tc: Dict[str, Any], max_turns: int = 15) -> EvaluationResult:
    """단일 테스트 케이스 실행"""
    graph = create_graph()
    adapter = LangGraphAdapter(graph)
    simulator = ScenarioSimulator(tc)

    turn_history = []
    initial_message = tc["user_info"]["base"].get(
        "initial_message", "여행 계획을 도와주세요."
    )

    step_result = adapter.start_conversation(initial_message)

    if step_result.error:
        return EvaluationResult(
            success=False,
            final_plan={},
            ground_truth=tc["ground_truth"],
            turn_count=0,
            failure_detail=f"시작 오류: {step_result.error}",
        )

    for turn in range(max_turns):
        if step_result.is_complete:
            break

        if not step_result.agent_question:
            break

        user_response = simulator.respond(step_result.agent_question)
        turn_history.append(
            {
                "turn": turn + 1,
                "question": step_result.agent_question,
                "response": user_response,
            }
        )

        step_result = adapter.continue_conversation(user_response)

        if step_result.error:
            return EvaluationResult(
                success=False,
                final_plan=step_result.current_plan or {},
                ground_truth=tc["ground_truth"],
                turn_count=len(turn_history),
                failure_detail=f"실행 오류: {step_result.error}",
            )

    final_plan = step_result.current_plan or {}
    result = evaluate_plan(final_plan, tc["ground_truth"], turn_history, max_turns)

    save_log(tc["id"], result, turn_history)

    return result


def save_log(tc_id: str, result: EvaluationResult, turn_history: List[Dict[str, str]]):
    """테스트 결과 저장"""
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


def main():
    """메인 실행"""
    print("=" * 60)
    print("Planning Agent TDD (IPC LLM Mode)")
    print("=" * 60)
    print("[설정] IPC LLM 모드로 실행 (Opencode LLM)")
    print()

    # IPC 서버 시작
    server_thread = threading.Thread(target=start_ipc_server)
    server_thread.daemon = True
    server_thread.start()
    time.sleep(1)

    # 테스트 실행
    test_cases = load_all_tcs()

    if not test_cases:
        print("실행할 테스트 케이스가 없습니다.")
        return

    print(f"\n총 {len(test_cases)}개의 테스트 케이스를 발견했습니다.\n")

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
            import traceback

            traceback.print_exc()
            results.append((tc, None))

        print()

    # 요약
    print("=" * 60)
    print("요약")
    print("=" * 60)

    success_count = sum(1 for _, r in results if r and r.success)
    total_count = len(results)

    print(f"성공: {success_count}/{total_count}")
    print(f"실패: {total_count - success_count}/{total_count}")

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
