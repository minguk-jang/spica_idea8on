"""
IPC 기반 LLM 클라이언트
테스트 프로세스에서 Assistant로 LLM 요청을 전달
"""

import json
import socket
import os
from typing import Optional, Dict, Any
from pathlib import Path

SOCKET_PATH = "/tmp/opencode_llm_socket"


class IPCLLMClient:
    """IPC를 통해 Assistant에게 LLM 요청을 보내는 클라이언트"""

    def __init__(self, socket_path: str = SOCKET_PATH):
        self.socket_path = socket_path

    def invoke(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Assistant에게 LLM 요청 보내고 응답 받기

        Args:
            prompt: LLM에 보낼 프롬프트
            temperature: 생성 온도

        Returns:
            LLM 응답 텍스트
        """
        print(f"[DEBUG] IPC Client: invoke() called")
        print(f"[DEBUG] IPC Client: socket path = {self.socket_path}")

        # 요청 데이터 준비
        request = {"type": "llm_request", "prompt": prompt, "temperature": temperature}
        print(f"[DEBUG] IPC Client: request prepared: {request}")

        # 소켓 연결
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        print(f"[DEBUG] IPC Client: socket created (AF_UNIX)")
        try:
            print(f"[DEBUG] IPC Client: attempting to connect to {self.socket_path}...")
            client.connect(self.socket_path)
            print(f"[DEBUG] IPC Client: connected successfully!")

            # 요청 전송
            request_json = json.dumps(request)
            print(f"[DEBUG] IPC Client: sending request ({len(request_json)} bytes)...")
            client.sendall(request_json.encode())
            print(f"[DEBUG] IPC Client: request sent, shutting down write side...")
            client.shutdown(socket.SHUT_WR)

            # 응답 수신
            print(f"[DEBUG] IPC Client: waiting for response...")
            response_data = b""
            while True:
                chunk = client.recv(4096)
                if not chunk:
                    print(f"[DEBUG] IPC Client: no more data received")
                    break
                response_data += chunk
                print(
                    f"[DEBUG] IPC Client: received chunk ({len(chunk)} bytes), total: {len(response_data)} bytes"
                )

            # 응답 파싱
            print(f"[DEBUG] IPC Client: parsing response...")
            response = json.loads(response_data.decode())
            print(
                f"[DEBUG] IPC Client: response parsed successfully, content length: {len(response.get('content', ''))}"
            )
            return response.get("content", "")

        finally:
            print(f"[DEBUG] IPC Client: closing socket...")
            client.close()
            print(f"[DEBUG] IPC Client: socket closed")


def get_ipc_llm_client() -> IPCLLMClient:
    """IPC LLM 클라이언트 인스턴스 생성"""
    return IPCLLMClient()
