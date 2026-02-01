"""
Planning Agent 통합 인터페이스
"""
from typing import Dict, Any, Optional
from langgraph.checkpoint.memory import MemorySaver
from .graph import create_graph
from .core.config import AgentConfig
from .core.state import AgentState


class PlanningAgent:
    """Planning Agent 클래스"""

    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Args:
            config: Agent 설정 (None인 경우 기본 설정 사용)
        """
        self.config = config or AgentConfig.default()
        self.graph = create_graph(self.config)
        self.checkpointer = MemorySaver()
        self.compiled = self.graph.compile(
            checkpointer=self.checkpointer,
            interrupt_before=['ask_user']
        )

    def run(self, initial_message: str, thread_id: str = 'default') -> Dict[str, Any]:
        """
        Agent 실행

        Args:
            initial_message: 초기 사용자 메시지
            thread_id: 스레드 ID (대화 세션 구분)

        Returns:
            실행 결과 상태
        """
        config = {'configurable': {'thread_id': thread_id}}

        initial_state: AgentState = {
            'messages': [{'role': 'user', 'content': initial_message}],
            'current_plan': {},
            'turn_count': 0
        }

        result = self.compiled.invoke(initial_state, config)
        return result

    def continue_conversation(
        self,
        user_response: str,
        thread_id: str = 'default'
    ) -> Dict[str, Any]:
        """
        대화 계속하기

        Args:
            user_response: 사용자 응답
            thread_id: 스레드 ID

        Returns:
            업데이트된 상태
        """
        config = {'configurable': {'thread_id': thread_id}}

        # 현재 상태 가져오기
        current_state = self.compiled.get_state(config)

        # 상태 업데이트
        updated_state = current_state.values.copy()
        updated_state['messages'].append({
            'role': 'user',
            'content': user_response
        })
        updated_state['turn_count'] = updated_state.get('turn_count', 0) + 1

        # 그래프 재개
        self.compiled.update_state(config, updated_state)
        result = self.compiled.invoke(None, config)

        return result

    def get_current_state(self, thread_id: str = 'default') -> Dict[str, Any]:
        """
        현재 상태 조회

        Args:
            thread_id: 스레드 ID

        Returns:
            현재 상태
        """
        config = {'configurable': {'thread_id': thread_id}}
        state = self.compiled.get_state(config)
        return state.values if state else {}

    def reset(self, thread_id: str = 'default'):
        """
        특정 스레드 초기화

        Args:
            thread_id: 스레드 ID
        """
        # MemorySaver는 메모리 기반이므로 새로운 checkpointer 생성
        self.checkpointer = MemorySaver()
        self.compiled = self.graph.compile(
            checkpointer=self.checkpointer,
            interrupt_before=['ask_user']
        )
