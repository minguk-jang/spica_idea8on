"""
테스트 스크립트: IPC slot parsing 디버깅
"""

import sys

sys.path.insert(0, "/Users/mingukjang/git/spica_idea8on/2601/auto-tdd-agent")

from src.utils.ipc_llm_client import IPCLLMClient


def test_slot_parsing():
    # IPC LLM 클라이언트 생성
    client = IPCLLMClient()

    # slot_updater.yaml 템플릿 기반 프롬프트 구성
    current_plan = "{}"
    user_response = "제주도"

    prompt = f"""현재까지 수집된 계획:
{current_plan}

사용자 응답:
"{user_response}"

위 사용자 응답에서 다음 정보를 추출하세요:
- destination: 여행 목적지 (예: "제주도", "부산")
- start_date: 출발 날짜 (YYYY-MM-DD 형식, 예: "2026-03-15")
- duration: 여행 기간 (예: "3박 4일", "5일")
- budget: 예산 (예: "50만원", "100만원")
- companions: 동행자 (예: "가족", "친구", "혼자")
- purpose: 여행 목적 (예: "휴양", "관광", "업무")

주의사항:
1. 사용자 응답에 명시적으로 나타난 정보만 추출하세요
2. "거기", "그때" 같은 대명사는 current_plan을 참고하여 해석하세요
3. 날짜는 반드시 YYYY-MM-DD 형식으로 변환하세요 (현재 연도: 2026)
4. 추출된 정보만 포함한 JSON 객체를 반환하세요
5. 정보가 없으면 빈 객체 {{}}를 반환하세요

출력 형식 (JSON만):
"""

    print("=" * 60)
    print("프롬프트:")
    print("=" * 60)
    print(prompt)
    print()
    print("=" * 60)
    print("IPC LLM 요청 전송 중...")
    print("=" * 60)

    try:
        response = client.invoke(prompt, temperature=0.0)
        print("\n응답:")
        print("=" * 60)
        print(response)
        print("=" * 60)
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_slot_parsing()
