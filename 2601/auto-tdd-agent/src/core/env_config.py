"""
환경 변수 설정 로더
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


# 프로젝트 루트에서 .env 파일 로드
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"

if env_path.exists():
    load_dotenv(dotenv_path=env_path)


class EnvConfig:
    """환경 변수 설정"""

    # GLM API 설정
    GLM_API_KEY: str = os.getenv("GLM_API_KEY", "")
    GLM_MODEL: str = os.getenv("GLM_MODEL", "glm-4-flash")
    GLM_BASE_URL: str = os.getenv(
        "GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"
    )

    # Agent 설정
    MAX_TURNS: int = int(os.getenv("MAX_TURNS", "15"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))

    # 로깅 설정
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # 테스트 설정
    USE_IPC_LLM: bool = os.getenv("USE_IPC_LLM", "false").lower() == "true"

    @classmethod
    def validate(cls) -> bool:
        """
        필수 환경 변수가 설정되어 있는지 확인

        Returns:
            검증 성공 여부
        """
        if not cls.GLM_API_KEY or cls.GLM_API_KEY == "your_api_key_here":
            print("경고: GLM_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
            return False
        return True

    @classmethod
    def get_llm_config(cls) -> dict:
        """
        LLM 설정 딕셔너리 반환

        Returns:
            LLM 설정
        """
        return {
            "api_key": cls.GLM_API_KEY,
            "model": cls.GLM_MODEL,
            "base_url": cls.GLM_BASE_URL,
            "temperature": cls.TEMPERATURE,
        }
