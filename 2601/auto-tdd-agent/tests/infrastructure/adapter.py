"""
LangGraphAdapter: LangGraph와 테스트 프레임워크 연결
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver


@dataclass
class StepResult:
    """각 스텝의 실행 결과"""

    agent_question: Optional[str] = None
    user_response: Optional[str] = None
    current_plan: Dict[str, Any] = None
    is_complete: bool = False
    error: Optional[str] = None


class LangGraphAdapter:
    """LangGraph와 테스트를 연결하는 어댑터"""

    def __init__(self, graph: StateGraph):
        """
        Args:
            graph: LangGraph StateGraph 인스턴스
        """
        self.checkpointer = MemorySaver()
        self.compiled_graph = graph.compile(
            checkpointer=self.checkpointer,
            interrupt_after=["ask_user"],  # ask_user 노드 실행 후 중단
        )
        self.thread_id = "test_thread"
        self.config = {"configurable": {"thread_id": self.thread_id}}

    def start_conversation(self, initial_message: str) -> StepResult:
        """
        대화 시작

        Args:
            initial_message: 사용자의 첫 메시지

        Returns:
            첫 번째 스텝 결과
        """
        try:
            # 초기 상태로 그래프 실행
            initial_state = {
                "messages": [{"role": "user", "content": initial_message}],
                "current_plan": {},
                "turn_count": 0,
            }

            # 그래프 실행 (interrupt까지)
            result = self.compiled_graph.invoke(initial_state, self.config)

            # Agent의 질문 추출
            agent_question = self._extract_last_agent_message(result)

            return StepResult(
                agent_question=agent_question,
                current_plan=result.get("current_plan", {}),
                is_complete=False,
            )
        except Exception as e:
            return StepResult(error=str(e))

    def continue_conversation(self, user_response: str) -> StepResult:
        """
        대화 계속하기

        Args:
            user_response: 사용자 응답

        Returns:
            다음 스텝 결과
        """
        try:
            # 현재 상태 가져오기
            current_state = self.compiled_graph.get_state(self.config)

            # 사용자 응답 추가
            updated_state = current_state.values.copy()
            updated_state["messages"].append({"role": "user", "content": user_response})
            updated_state["turn_count"] = updated_state.get("turn_count", 0) + 1

            # 그래프 재개
            self.compiled_graph.update_state(self.config, updated_state)
            result = self.compiled_graph.invoke(None, self.config)

            # 완료 여부 확인 (간단한 휴리스틱)
            is_complete = self._check_completion(result)

            if is_complete:
                return StepResult(
                    current_plan=result.get("current_plan", {}), is_complete=True
                )

            # Agent의 다음 질문 추출
            agent_question = self._extract_last_agent_message(result)

            return StepResult(
                agent_question=agent_question,
                user_response=user_response,
                current_plan=result.get("current_plan", {}),
                is_complete=False,
            )
        except Exception as e:
            return StepResult(error=str(e))

    def _extract_last_agent_message(self, state: Dict[str, Any]) -> Optional[str]:
        """
        상태에서 Agent의 마지막 메시지 추출

        Args:
            state: 그래프 상태

        Returns:
            Agent의 마지막 메시지
        """
        messages = state.get("messages", [])
        for msg in reversed(messages):
            if msg.get("role") == "assistant":
                return msg.get("content")
        return None

    def _check_completion(self, state: Dict[str, Any]) -> bool:
        """
        대화 완료 여부 확인

        Args:
            state: 그래프 상태

        Returns:
            완료 여부
        """
        # 간단한 휴리스틱: 메시지가 "계획이 완료되었습니다" 등을 포함하는지
        messages = state.get("messages", [])
        if messages:
            last_msg = messages[-1].get("content", "")
            if "완료" in last_msg or "complete" in last_msg.lower():
                return True
        return False
