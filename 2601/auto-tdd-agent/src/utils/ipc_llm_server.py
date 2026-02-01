"""
IPC LLM 서버 - Assistant가 LLM 요청을 처리하는 서버
"""

import json
import socket
import os
import sys

SOCKET_PATH = "/tmp/opencode_llm_socket"


def start_ipc_server():
    """IPC 서버 시작 및 LLM 요청 처리"""
    # 기존 소켓 파일 제거
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

    # 소켓 생성
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(1)

    print(f"IPC LLM Server started at {SOCKET_PATH}")
    print("Waiting for LLM requests...")
    print("(Press Ctrl+C to stop)")

    try:
        while True:
            # 연결 수락
            conn, _ = server.accept()

            try:
                # 요청 수신
                request_data = b""
                while True:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    request_data += chunk

                # 요청 파싱
                request = json.loads(request_data.decode())
                prompt = request.get("prompt", "")
                temperature = request.get("temperature", 0.7)

                # 콘솔에 프롬프트 출력 (Assistant가 볼 수 있도록)
                print("\n" + "=" * 60)
                print("LLM REQUEST RECEIVED:")
                print("=" * 60)
                print(f"Prompt: {prompt[:200]}...")
                print(f"Temperature: {temperature}")
                print("=" * 60)

                # Assistant에게 응답을 기다림
                print("\nWaiting for Assistant response...")
                print("(Please provide response via stdin)")

                # 사용자 입력 받기 (Assistant가 직접 응답 입력)
                response_content = input("\nEnter LLM response: ")

                # 응답 전송
                response = {"content": response_content}
                conn.sendall(json.dumps(response).encode())

            except Exception as e:
                print(f"Error handling request: {e}")
                error_response = {"content": f"Error: {str(e)}"}
                conn.sendall(json.dumps(error_response).encode())
            finally:
                conn.close()

    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        server.close()
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)


if __name__ == "__main__":
    start_ipc_server()
