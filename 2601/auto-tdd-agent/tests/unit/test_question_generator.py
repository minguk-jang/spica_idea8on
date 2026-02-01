"""
QuestionGenerator 단위 테스트
"""
import pytest
from src.services.question_generator import QuestionGenerator


def test_question_generation_empty_plan():
    """빈 plan에서 첫 질문 생성 테스트"""
    generator = QuestionGenerator()
    question = generator.generate({})

    assert question is not None
    assert len(question) > 0
    # 첫 번째 필수 슬롯인 destination에 대한 질문
    assert '어디' in question or '목적지' in question


def test_question_generation_partial_plan():
    """부분 plan에서 다음 질문 생성 테스트"""
    generator = QuestionGenerator()
    plan = {'destination': '제주도'}
    question = generator.generate(plan)

    # 다음 필수 슬롯인 start_date에 대한 질문
    assert '언제' in question or '출발' in question or '날짜' in question


def test_question_generation_all_required_complete():
    """모든 필수 슬롯이 채워진 경우 선택 슬롯 질문"""
    generator = QuestionGenerator()
    plan = {
        'destination': '제주도',
        'start_date': '2026-03-15',
        'duration': '3박 4일'
    }
    question = generator.generate(plan)

    # 선택 슬롯 질문
    assert '예산' in question or '누구' in question or '목적' in question


def test_question_generation_all_complete():
    """모든 슬롯이 채워진 경우 완료 메시지"""
    generator = QuestionGenerator()
    plan = {
        'destination': '제주도',
        'start_date': '2026-03-15',
        'duration': '3박 4일',
        'budget': '50만원',
        'companions': '가족',
        'purpose': '휴양'
    }
    question = generator.generate(plan)

    assert '완료' in question
