"""
TDD 최종 디버그 보고서
========================

실행된 테스트: s01_v01
초기 메시지: "여행 계획을 도와주세요"

[문제 분석]
===========

1. 문제 원인:
   - src/nodes/process_node.py:29에서 ResponseParser(use_llm=True)로 설정
   - src/nodes/question_node.py:20에서 QuestionGenerator(use_llm=True)로 설정
   
   이로 인해 그래프 실행 시 LLM을 호출하려고 시도하지만, 
   LLM이 응답하지 않거나 설정되지 않아 타임아웃 발생

2. 규칙 기반 모드 테스트 결과 (정상 작동):
   ✓ ResponseParser가 초기 메시지에서 정보 추출 (빈 결과 - 정상)
   ✓ QuestionGenerator가 첫 질문 생성: "어디로 여행을 가시고 언제 출발하시나요?"
   ✓ 그래프 노드들이 정상적으로 상태 업데이트
   ✓ 메시지 히스토리에 assistant 메시지 추가됨
   
3. 인터럽트 모드 테스트 결과:
   - interrupt_before=["ask_user"] 설정 시:
     * process_input 노드는 실행됨 (하지만 LLM 호출로 인해 타임아웃)
     * ask_user 노드는 실행되지 않음 (인터럽트로 인해 중단)
     * 결과: agent_question이 None

[상세 실행 결과]
================

1. ResponseParser 테스트:
   - '여행 계획을 도와주세요.' -> {}
   - '제주도로 가고 싶어요' -> {'destination': '제주도'}
   - '2026-03-15에 출발합니다' -> {'start_date': '2026-03-15'}
   - '3박 4일로 갈 거예요' -> {'duration': '3박 4일'}
   - '100만원 예산입니다' -> {'budget': '100만원'}

2. QuestionGenerator 테스트:
   - Plan: {} -> '어디로 여행을 가고 싶으신가요?'
   - Plan: {'destination': '제주도'} -> '언제 출발하실 예정인가요?'
   - Plan: +start_date -> '여행 기간은 며칠인가요?'
   - Plan: +duration -> '예산은 얼마 정도 생각하고 계신가요?'
   - Plan: +budget -> '누구와 함께 가시나요?'

3. 그래프 실행 흐름:
   - 초기 상태: messages=[user: "여행 계획을 도와주세요"], current_plan={}, turn_count=0
   - process_input 실행: current_plan={} (정보 없음)
   - ask_user 실행: messages에 assistant 메시지 추가
   - 결과 메시지: "어디로 여행을 가시고 언제 출발하시나요?"

[해결 방법]
===========

옵션 1: LLM 설정 확인
   - .env 파일에 LLM API 키가 올바르게 설정되어 있는지 확인
   - LLM 서버/서비스가 실행 중인지 확인

옵션 2: 규칙 기반 모드로 전환 (테스트용)
   - process_node.py:29를 ResponseParser(use_llm=False)로 변경
   - question_node.py:20를 QuestionGenerator(use_llm=False)로 변경

옵션 3: LLM 클라이언트의 타임아웃 설정
   - LLM 호출에 타임아웃을 추가하여 무한 대기 방지

[결론]
======
TDD 테스트가 실패하는 이유는 노드들이 LLM을 사용하도록 설정되어 있지만
LLM이 응답하지 않아 타임아웃되기 때문입니다.
규칙 기반 모드로 전환하거나 LLM 설정을 확인해야 합니다.
"""

print(__doc__)
