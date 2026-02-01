"""
그래프 전체 실행 통합 테스트
"""

import pytest
from src.graph import create_graph
from src.core.state import AgentState


def test_graph_creation():
    """그래프 생성 테스트"""
    graph = create_graph()
    assert graph is not None


def test_graph_compilation():
    """그래프 컴파일 테스트"""
    graph = create_graph()
    compiled = graph.compile()
    assert compiled is not None


def test_graph_single_turn():
    """그래프 단일 턴 실행 테스트"""
    from langgraph.checkpoint.memory import MemorySaver

    graph = create_graph()
    checkpointer = MemorySaver()
    compiled = graph.compile(checkpointer=checkpointer, interrupt_after=["ask_user"])

    initial_state: AgentState = {
        "messages": [{"role": "user", "content": "여행 계획 도와주세요"}],
        "current_plan": {},
        "turn_count": 0,
    }

    config = {"configurable": {"thread_id": "test_single"}}
    result = compiled.invoke(initial_state, config)

    # 결과 검증
    assert "messages" in result
    assert len(result["messages"]) > 1  # 사용자 메시지 + Agent 응답
    assert "current_plan" in result
    assert "turn_count" in result


def test_graph_multi_turn():
    """그래프 다중 턴 실행 테스트"""
    from langgraph.checkpoint.memory import MemorySaver

    graph = create_graph()
    checkpointer = MemorySaver()
    compiled = graph.compile(checkpointer=checkpointer, interrupt_before=["ask_user"])

    config = {"configurable": {"thread_id": "test"}}

    # 첫 턴
    initial_state: AgentState = {
        "messages": [{"role": "user", "content": "제주도로 여행 가고 싶어요"}],
        "current_plan": {},
        "turn_count": 0,
    }

    result1 = compiled.invoke(initial_state, config)
    assert "messages" in result1

    # 두 번째 턴
    current_state = compiled.get_state(config)
    updated_state = current_state.values.copy()
    updated_state["messages"].append(
        {"role": "user", "content": "3월 15일에 출발할 거예요"}
    )
    updated_state["turn_count"] = updated_state.get("turn_count", 0) + 1

    compiled.update_state(config, updated_state)
    result2 = compiled.invoke(None, config)

    # Plan이 업데이트되었는지 확인
    assert "current_plan" in result2
    # 최소한 하나의 정보는 수집되어야 함
    assert len(result2.get("current_plan", {})) > 0
