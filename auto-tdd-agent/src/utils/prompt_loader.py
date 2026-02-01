"""
프롬프트 파일 로드 유틸리티
"""

from pathlib import Path
from typing import Dict, Any, Optional
import yaml


class PromptLoader:
    """프롬프트 템플릿 로더"""

    def __init__(self, prompts_dir: Optional[Path] = None):
        """
        Args:
            prompts_dir: 프롬프트 디렉토리 경로 (기본값: 프로젝트 루트의 prompts/)
        """
        if prompts_dir is None:
            prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        self.prompts_dir = prompts_dir

    def load_question_prompt(self, current_plan: Dict[str, Any]) -> str:
        """
        질문 생성 프롬프트 로드

        Args:
            current_plan: 현재 수집된 plan

        Returns:
            포맷팅된 프롬프트 문자열
        """
        prompt_file = self.prompts_dir / "question_generator.yaml"

        if not prompt_file.exists():
            # 기본 프롬프트 반환
            return f"""현재 수집된 여행 계획 정보:
{current_plan}

위 정보를 바탕으로 사용자에게 다음에 물어볼 질문을 생성하세요.
아직 수집되지 않은 필수 정보를 우선적으로 물어보세요."""

        with open(prompt_file, "r", encoding="utf-8") as f:
            template = yaml.safe_load(f)

        if "user_template" in template:
            return template["user_template"].format(current_plan=current_plan)

        return str(template)

    def load_parser_prompt(
        self, user_response: str, current_plan: Dict[str, Any] = None
    ) -> str:
        """
        파싱 프롬프트 로드

        Args:
            user_response: 사용자 응답
            current_plan: 현재 수집된 plan (선택적)

        Returns:
            포맷팅된 프롬프트 문자열
        """
        prompt_file = self.prompts_dir / "slot_updater.yaml"

        if not prompt_file.exists():
            # 기본 프롬프트 반환
            return f"""다음 사용자 응답에서 여행 계획 정보를 추출하세요:
"{user_response}"

JSON 형식으로 추출된 정보를 반환하세요. 예:
{{"destination": "제주도", "start_date": "2026-03-15"}}

정보가 없으면 빈 객체 {{}}를 반환하세요."""

        with open(prompt_file, "r", encoding="utf-8") as f:
            template = yaml.safe_load(f)

        if "user_template" in template:
            return template["user_template"].format(
                user_response=user_response, current_plan=current_plan or {}
            )

        return str(template)
