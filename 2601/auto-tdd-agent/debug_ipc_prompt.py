#!/usr/bin/env python3
"""
IPC 디버깅 - 프롬프트 덤프
"""

import os
import sys
import json
import threading
import socket
from pathlib import Path

# IPC 모드 활성화
os.environ["USE_LLM"] = "true"
os.environ["USE_IPC_LLM"] = "true"

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, "/Users/mingukjang/git/spica_idea8on/2601/auto-tdd-agent")

from tests.infrastructure.simulator import ScenarioSimulator
from tests.infrastructure.adapter import LangGraphAdapter
from src.graph import create_graph

SOCKET_PATH = "/tmp/opencode_llm_socket"


def handle_llm_request(conn: socket.socket):
    try:
        request_data = b""
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            request_data += chunk

        request = json.loads(request_data.decode())
        prompt = request.get("prompt", "")

        print("\n" + "=" * 40)
        print("RECEIVED PROMPT:")
        print("=" * 40)
        print(prompt)
        print("=" * 40 + "\n")

        # 빈 응답 전송 (디버깅용)
        response = {"content": "{}"}
        conn.sendall(json.dumps(response).encode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def start_ipc_server():
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(1)

    # 한 번의 요청만 처리하고 종료
    conn, _ = server.accept()
    handle_llm_request(conn)
    server.close()
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)


def run_test():
    # 서버 시작
    server_thread = threading.Thread(target=start_ipc_server)
    server_thread.daemon = True
    server_thread.start()
    time.sleep(1)

    # 테스트 케이스 로드
    tc_path = "/Users/mingukjang/git/spica_idea8on/2601/auto-tdd-agent/data/scenarios/s01_v01.json"
    with open(tc_path, "r", encoding="utf-8") as f:
        tc = json.load(f)

    graph = create_graph()
    adapter = LangGraphAdapter(graph)

    # 첫 턴 실행 (질문 생성) -> LLM 요청 발생 -> 프롬프트 출력
    adapter.start_conversation("여행 계획을 도와주세요.")


import time

run_test()
