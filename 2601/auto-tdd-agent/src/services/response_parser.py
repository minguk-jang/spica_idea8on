"""
응답 파싱 서비스
"""

import re
import json
from typing import Dict, Any
from ..utils.prompt_loader import PromptLoader
from ..utils.llm_client import get_llm_client


class ResponseParser:
    """응답 파싱 서비스"""

    def __init__(self, use_llm: bool = False):
        """
        초기화

        Args:
            use_llm: LLM 사용 여부 (False인 경우 규칙 기반)
        """
        self.prompt_loader = PromptLoader()
        self.use_llm = use_llm
        self.llm = None

        if use_llm:
            try:
                self.llm = get_llm_client(temperature=0.0)
            except ValueError as e:
                print(f"경고: LLM 초기화 실패 - {e}")
                print("규칙 기반 모드로 전환합니다.")
                self.use_llm = False

    def parse(
        self, user_response: str, current_plan: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        사용자 응답에서 슬롯 정보 추출

        Args:
            user_response: 사용자 응답
            current_plan: 현재 수집된 plan (선택적)

        Returns:
            추출된 슬롯 정보 딕셔너리
        """
        if self.use_llm and self.llm:
            return self._parse_with_llm(user_response, current_plan)
        else:
            return self._parse_with_rules(user_response)

    def _parse_with_llm(
        self, user_response: str, current_plan: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        LLM을 사용하여 응답 파싱

        Args:
            user_response: 사용자 응답
            current_plan: 현재 수집된 plan (선택적)

        Returns:
            추출된 슬롯 정보
        """
        prompt = self.prompt_loader.load_parser_prompt(user_response, current_plan)

        try:
            response = self.llm.invoke(prompt)
            # IPC 클라이언트는 문자열을 반환, ChatOpenAI는 객체를 반환
            if isinstance(response, str):
                content = response.strip()
            else:
                content = response.content.strip()

            # 코드 블록 제거 (```json ... ``` 형식)
            if content.startswith("```"):
                # 첫 번째 줄 제거 (```json)
                lines = content.split("\n")
                if len(lines) > 2:
                    content = "\n".join(lines[1:-1])  # 중간 내용만 추출
                else:
                    content = content.replace("```json", "").replace("```", "").strip()

            # JSON 파싱
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                print(f"경고: JSON 파싱 실패 - {content}")
                return self._parse_with_rules(user_response)
        except Exception as e:
            print(f"경고: LLM 호출 실패 - {e}")
            return self._parse_with_rules(user_response)

    def _parse_with_rules(self, user_response: str) -> Dict[str, Any]:
        """
        규칙 기반으로 응답 파싱

        Args:
            user_response: 사용자 응답

        Returns:
            추출된 슬롯 정보
        """
        extracted = {}

        # 목적지 추출
        destination = self._extract_destination(user_response)
        if destination:
            extracted["destination"] = destination

        # 날짜 추출
        start_date = self._extract_date(user_response)
        if start_date:
            extracted["start_date"] = start_date

        # 기간 추출
        duration = self._extract_duration(user_response)
        if duration:
            extracted["duration"] = duration

        # 예산 추출
        budget = self._extract_budget(user_response)
        if budget:
            extracted["budget"] = budget

        # 동반자 추출
        companions = self._extract_companions(user_response)
        if companions:
            extracted["companions"] = companions

        # 여행 목적 추출
        purpose = self._extract_purpose(user_response)
        if purpose:
            extracted["purpose"] = purpose

        return extracted

    def _extract_destination(self, text: str) -> str:
        """
        목적지 추출

        Args:
            text: 입력 텍스트

        Returns:
            추출된 목적지 또는 None
        """
        # 간단한 패턴 매칭 (실제로는 LLM 사용 권장)
        patterns = [
            r"(제주도?|부산|서울|강릉|경주|전주|여수|속초|대구|광주|인천|대전)",
            r"([가-힣]{2,})(?:로|에|으로)\s*(?:가|여행)",  # 최소 2글자 이상
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                destination = match.group(1)
                # "일", "월" 같은 단일 글자나 시간 관련 단어 제외
                if len(destination) >= 2 and destination not in [
                    "오늘",
                    "내일",
                    "모레",
                ]:
                    return destination

        return None

    def _extract_date(self, text: str) -> str:
        """
        날짜 추출

        Args:
            text: 입력 텍스트

        Returns:
            YYYY-MM-DD 형식의 날짜 또는 None
        """
        # YYYY-MM-DD 형식
        pattern = r"(\d{4})-(\d{1,2})-(\d{1,2})"
        match = re.search(pattern, text)

        if match:
            year, month, day = match.groups()
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        # "3월 15일" 형식 (현재 연도 기준)
        pattern = r"(\d{1,2})월\s*(\d{1,2})일"
        match = re.search(pattern, text)

        if match:
            month, day = match.groups()
            # 현재는 2026년으로 가정
            return f"2026-{month.zfill(2)}-{day.zfill(2)}"

        return None

    def _extract_duration(self, text: str) -> str:
        """
        기간 추출

        Args:
            text: 입력 텍스트

        Returns:
            추출된 기간 또는 None
        """
        # "3박 4일" 형식
        pattern = r"(\d+)박\s*(\d+)일"
        match = re.search(pattern, text)

        if match:
            nights, days = match.groups()
            return f"{nights}박 {days}일"

        # "3일" 형식
        pattern = r"(\d+)일"
        match = re.search(pattern, text)

        if match:
            days = match.group(1)
            return f"{days}일"

        return None

    def _extract_budget(self, text: str) -> str:
        """
        예산 추출

        Args:
            text: 입력 텍스트

        Returns:
            추출된 예산 또는 None
        """
        # "50만원" 또는 "50만 원" 형식 (공백 유무 모두 처리)
        pattern = r"(\d+)\s*만\s*원?"
        match = re.search(pattern, text)

        if match:
            amount = match.group(1)
            return f"{amount}만원"

        # "100만원" 형식 (공백 없음)
        pattern = r"(\d+만원)"
        match = re.search(pattern, text)

        if match:
            return match.group(1)

        return None

    def _extract_companions(self, text: str) -> str:
        """
        동반자 추출

        Args:
            text: 입력 텍스트

        Returns:
            추출된 동반자 정보 또는 None
        """
        # 동반자 관련 키워드 패턴
        patterns = [
            r"(혼자|혼자서|나 혼자|혼자 여행)",
            r"(친구\s*\d*명?|친구랑|친구와|친구들?)",
            r"(가족|부모님|아이들?|아들|딸|형제|자매)",
            r"(연인|남자친구|여자친구|배우자|부부)",
            r"(동료|회사\s*동료|직장\s*동료)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        return None

    def _extract_purpose(self, text: str) -> str:
        """
        여행 목적 추출

        Args:
            text: 입력 텍스트

        Returns:
            추출된 여행 목적 또는 None
        """
        # 여행 목적 키워드 패턴
        # 주의: "여행"은 일반적인 단어이므로 별도로 처리
        patterns = [
            r"(휴양|휴식|쉬|힐링|재충전)",
            r"(관광|구경|볼거리|관람|탐방)",
            r"(먹방|맛집|음식|미식|먹을거리)",
            r"(액티비티|체험|모험|스포츠|서핑|등산|자전거)",
            r"(문화|역사|박물관|미술관|전시|공연)",
            r"(쇼핑|쇼핑하|구매|사고\s*싶)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        # "여행"은 다른 목적 키워드가 없을 때만 매칭 (최후의 수단)
        # "여행"이 문장 중간에 있고 "계획", "준비" 등과 함께 있으면 제외
        if re.search(r"여행", text):
            # "계획", "준비", "가자", "갈" 등이 있으면 greeting으로 간주
            if re.search(r"(계획|준비|도와|가자|갈|가고|갈거|여행을|여행 계획)", text):
                return None
            # 순수하게 "휴양 여행", "관광 여행" 등으로 쓰인 경우만 허용
            if re.search(r"(휴양\s*여행|관광\s*여행|먹방\s*여행|문화\s*여행)", text):
                match = re.search(r"(휴양|관광|먹방|문화)", text)
                if match:
                    return match.group(1)

        return None
