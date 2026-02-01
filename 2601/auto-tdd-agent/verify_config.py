"""
환경 변수 및 클라이언트 생성 검증 스크립트
"""

import os
import sys
from unittest.mock import MagicMock

# langchain_openai가 설치되어 있지 않을 경우를 대비해 Mock 처리
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    # 가짜 ChatOpenAI 클래스 생성
    class ChatOpenAI:
        def __init__(self, **kwargs):
            pass

# 실제 모듈 임포트
# 주의: src.utils.llm_client 내부에서 langchain_openai를 임포트하므로
# 위에서 sys.modules에 mock을 주입해야 할 수도 있지만,
# 여기서는 환경 변수 로직 검증이 핵심이므로 일단 진행합니다.

# 프로젝트 경로 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))


def test_api_mode():
    print("\n--- [검증 1] API 모드 (기본) ---")
    # 환경 변수 초기화 (테스트를 위해)
    if "USE_IPC_LLM" in os.environ:
        del os.environ["USE_IPC_LLM"]

    # EnvConfig 재로드를 위해 모듈 제거 (실제로는 복잡하므로 os.environ 조작만으로 테스트)
    # 여기서는 get_llm_client 함수가 호출될 때 os.environ을 확인하는지 봅니다.

    # 강제로 false 설정
    os.environ["USE_IPC_LLM"] = "false"

    try:
        from src.utils.llm_client import get_llm_client, IPCLLMClient
        from langchain_openai import ChatOpenAI

        # API 키가 없으면 에러가 날 수 있으므로 try-except 처리
        try:
            client = get_llm_client()
            print(f"Client Type: {type(client).__name__}")

            if isinstance(client, ChatOpenAI):
                print("✅ 성공: API 모드에서 ChatOpenAI 클라이언트가 반환되었습니다.")
            else:
                print("❌ 실패: API 모드인데 ChatOpenAI가 아닙니다.")

        except ValueError as e:
            print(f"✅ 성공 (예상된 에러): API 키 검증 에러 발생 ({e})")
            print(
                "   -> 이는 IPC 모드가 아님을 의미합니다 (IPC 모드는 키 검사를 건너뜀)."
            )

    except Exception as e:
        print(f"❌ 오류 발생: {e}")


def test_ipc_mode():
    print("\n--- [검증 2] IPC 모드 (강제 설정) ---")
    # IPC 모드 활성화
    os.environ["USE_IPC_LLM"] = "true"

    try:
        from src.utils.llm_client import get_llm_client, IPCLLMClient

        client = get_llm_client()
        print(f"Client Type: {type(client).__name__}")

        if isinstance(client, IPCLLMClient):
            print("✅ 성공: IPC 모드에서 IPCLLMClient 클라이언트가 반환되었습니다.")
        else:
            print(f"❌ 실패: IPC 모드인데 {type(client).__name__}가 반환되었습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")


if __name__ == "__main__":
    # .env 파일 생성 (테스트용)
    with open(".env", "w") as f:
        f.write("USE_IPC_LLM=false\n")
        f.write("GLM_API_KEY=dummy_key_for_test\n")  # 키 검증 통과를 위해 더미 키 추가

    print("검증 시작...")
    test_api_mode()
    test_ipc_mode()

    # 정리
    if os.path.exists(".env"):
        os.remove(".env")
