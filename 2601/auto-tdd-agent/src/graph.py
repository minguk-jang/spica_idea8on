"""
LangGraph 그래프 조립
"""
from pathlib import Path
from langgraph.graph import StateGraph, END
from .core.state import AgentState
from .core.config import AgentConfig
from .nodes.question_node import ask_user
from .nodes.process_node import process_input
from .nodes.router import should_continue


def create_graph(config: AgentConfig = None) -> StateGraph:
    """
    Agent 그래프 생성

    Args:
        config: Agent 설정 (None인 경우 기본 설정 사용)

    Returns:
        StateGraph 인스턴스
    """
    if config is None:
        # 스키마 파일에서 설정 로드 시도
        schema_path = Path(__file__).parent.parent / 'data' / 'plan_schema.json'
        if schema_path.exists():
            config = AgentConfig.from_schema_file(schema_path)
        else:
            config = AgentConfig.default()

    workflow = StateGraph(AgentState)

    # 노드 추가
    workflow.add_node('ask_user', ask_user)
    workflow.add_node('process_input', process_input)

    # 엣지 추가
    workflow.set_entry_point('process_input')
    workflow.add_edge('process_input', 'ask_user')
    workflow.add_conditional_edges(
        'ask_user',
        lambda state: should_continue(state, config),
        {
            'ask_user': 'process_input',
            END: END
        }
    )

    return workflow
