"""
LLM 클라이언트 (GLM API 또는 IPC 사용)
"""

import os
from typing import Optional, Union
from langchain_openai import ChatOpenAI
from ..core.env_config import EnvConfig
from .ipc_llm_client import IPCLLMClient, get_ipc_llm_client


def get_llm_client(
    temperature: Optional[float] = None,
) -> Union[ChatOpenAI, IPCLLMClient]:
    """
    LLM 클라이언트 생성

    USE_IPC_LLM 환경 변수가 설정된 경우 IPC 클라이언트를 사용하고,
    그렇지 않으면 GLM API 클라이언트를 사용합니다.

    Args:
        temperature: 생성 온도 (None인 경우 환경 변수 값 사용)

    Returns:
        ChatOpenAI 또는 IPCLLMClient 인스턴스
    """
    # IPC 모드 확인 (EnvConfig 또는 환경 변수)
    use_ipc = (
        EnvConfig.USE_IPC_LLM or os.environ.get("USE_IPC_LLM", "").lower() == "true"
    )

    if use_ipc:
        return get_ipc_llm_client()

    # 환경 변수 검증
    if not EnvConfig.validate():
        raise ValueError("GLM_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

    config = EnvConfig.get_llm_config()

    return ChatOpenAI(
        model=config["model"],
        api_key=config["api_key"],
        base_url=config["base_url"],
        temperature=temperature if temperature is not None else config["temperature"],
    )
