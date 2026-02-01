"""
질문 생성 노드
"""

import os

from ..core.state import AgentState
from ..services.question_generator import QuestionGenerator


def ask_user(state: AgentState) -> AgentState:
    """
    사용자에게 질문하는 노드

    Args:
        state: 현재 상태

    Returns:
        업데이트된 상태
    """
    # 질문 생성 서비스 사용 (환경 변수에 따라 LLM 사용 여부 결정)
    use_llm = os.environ.get("USE_LLM", "true").lower() == "true"
    generator = QuestionGenerator(use_llm=use_llm)
    question = generator.generate(state["current_plan"])

    # 메시지 히스토리에 추가
    state["messages"].append({"role": "assistant", "content": question})

    return state
