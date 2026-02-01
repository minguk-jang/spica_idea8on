"""
Agent 설정 관리
"""
from pathlib import Path
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class AgentConfig:
    """Agent 설정"""
    required_slots: List[str] = field(default_factory=list)
    optional_slots: List[str] = field(default_factory=list)
    slot_types: Dict[str, str] = field(default_factory=dict)
    max_turns: int = 15

    @classmethod
    def from_schema_file(cls, schema_path: Path) -> 'AgentConfig':
        """
        plan_schema.json에서 설정 로드

        Args:
            schema_path: 스키마 파일 경로

        Returns:
            AgentConfig 인스턴스
        """
        if not schema_path.exists():
            # 기본 설정 반환
            return cls(
                required_slots=["destination", "start_date", "duration"],
                optional_slots=["budget", "companions", "purpose"],
                slot_types={
                    "destination": "string",
                    "start_date": "date",
                    "duration": "string",
                    "budget": "string",
                    "companions": "string",
                    "purpose": "string"
                }
            )

        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)

        return cls(
            required_slots=schema.get('required_slots', []),
            optional_slots=schema.get('optional_slots', []),
            slot_types=schema.get('slot_types', {}),
            max_turns=schema.get('max_turns', 15)
        )

    @classmethod
    def default(cls) -> 'AgentConfig':
        """
        기본 설정 반환

        Returns:
            기본 AgentConfig 인스턴스
        """
        return cls(
            required_slots=["destination", "start_date", "duration"],
            optional_slots=["budget", "companions", "purpose"],
            slot_types={
                "destination": "string",
                "start_date": "date",
                "duration": "string",
                "budget": "string",
                "companions": "string",
                "purpose": "string"
            }
        )
