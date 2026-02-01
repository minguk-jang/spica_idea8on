"""
ResponseParser 단위 테스트
"""
import pytest
from src.services.response_parser import ResponseParser


def test_parse_destination():
    """목적지 파싱 테스트"""
    parser = ResponseParser()
    response = "제주도로 가고 싶어요"
    result = parser.parse(response)

    assert 'destination' in result
    assert result['destination'] == '제주도'


def test_parse_date_format_yyyy_mm_dd():
    """YYYY-MM-DD 형식 날짜 파싱 테스트"""
    parser = ResponseParser()
    response = "2026-03-15에 출발할 예정이에요"
    result = parser.parse(response)

    assert 'start_date' in result
    assert result['start_date'] == '2026-03-15'


def test_parse_date_format_korean():
    """한국어 형식 날짜 파싱 테스트"""
    parser = ResponseParser()
    response = "3월 15일에 출발할 거예요"
    result = parser.parse(response)

    assert 'start_date' in result
    assert result['start_date'] == '2026-03-15'


def test_parse_duration():
    """기간 파싱 테스트"""
    parser = ResponseParser()
    response = "3박 4일로 계획하고 있어요"
    result = parser.parse(response)

    assert 'duration' in result
    assert result['duration'] == '3박 4일'


def test_parse_budget():
    """예산 파싱 테스트"""
    parser = ResponseParser()
    response = "예산은 50만원 정도 생각하고 있어요"
    result = parser.parse(response)

    assert 'budget' in result
    assert result['budget'] == '50만원'


def test_parse_multiple_slots():
    """여러 슬롯 동시 파싱 테스트"""
    parser = ResponseParser()
    response = "제주도로 3월 15일에 3박 4일로 가려고 해요"
    result = parser.parse(response)

    assert 'destination' in result
    assert 'start_date' in result
    assert 'duration' in result


def test_parse_no_information():
    """정보가 없는 응답 파싱 테스트"""
    parser = ResponseParser()
    response = "잘 모르겠어요"
    result = parser.parse(response)

    assert len(result) == 0
