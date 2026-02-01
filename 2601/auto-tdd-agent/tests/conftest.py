"""
Pytest 설정 및 공통 Fixtures
"""
import pytest
from pathlib import Path
import sys

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_plan():
    """샘플 plan fixture"""
    return {
        'destination': '제주도',
        'start_date': '2026-03-15',
        'duration': '3박 4일'
    }


@pytest.fixture
def empty_state():
    """빈 상태 fixture"""
    return {
        'messages': [],
        'current_plan': {},
        'turn_count': 0
    }


@pytest.fixture
def sample_config():
    """샘플 설정 fixture"""
    from src.core.config import AgentConfig
    return AgentConfig.default()
