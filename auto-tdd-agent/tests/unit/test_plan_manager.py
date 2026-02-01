"""
PlanManager 단위 테스트
"""
import pytest
from src.services.plan_manager import PlanManager


def test_plan_update():
    """Plan 업데이트 테스트"""
    manager = PlanManager()
    current = {'destination': '제주도'}
    extracted = {'start_date': '2026-03-15'}
    updated = manager.update(current, extracted)

    assert updated['destination'] == '제주도'
    assert updated['start_date'] == '2026-03-15'


def test_plan_update_empty_value():
    """빈 값은 업데이트되지 않는지 테스트"""
    manager = PlanManager()
    current = {'destination': '제주도'}
    extracted = {'start_date': None, 'duration': ''}
    updated = manager.update(current, extracted)

    assert updated['destination'] == '제주도'
    assert 'start_date' not in updated
    assert 'duration' not in updated


def test_plan_is_complete():
    """Plan 완성 확인 테스트"""
    manager = PlanManager()
    complete_plan = {
        'destination': '제주도',
        'start_date': '2026-03-15',
        'duration': '3박 4일'
    }
    assert manager.is_complete(complete_plan) == True


def test_plan_is_incomplete():
    """Plan 미완성 확인 테스트"""
    manager = PlanManager()
    incomplete_plan = {
        'destination': '제주도',
        'start_date': '2026-03-15'
        # duration 누락
    }
    assert manager.is_complete(incomplete_plan) == False


def test_get_missing_slots():
    """누락된 슬롯 목록 반환 테스트"""
    manager = PlanManager()
    partial_plan = {
        'destination': '제주도'
    }
    missing = manager.get_missing_slots(partial_plan)

    assert 'start_date' in missing
    assert 'duration' in missing
    assert 'destination' not in missing


def test_get_next_slot_to_collect():
    """다음 수집할 슬롯 결정 테스트"""
    manager = PlanManager()
    plan = {'destination': '제주도'}
    next_slot = manager.get_next_slot_to_collect(plan)

    # 필수 슬롯 중 첫 번째 누락된 슬롯 반환
    assert next_slot == 'start_date'


def test_get_next_slot_when_required_complete():
    """필수 슬롯이 모두 수집되면 선택 슬롯 반환"""
    manager = PlanManager()
    plan = {
        'destination': '제주도',
        'start_date': '2026-03-15',
        'duration': '3박 4일'
    }
    next_slot = manager.get_next_slot_to_collect(plan)

    # 선택 슬롯 중 첫 번째 반환
    assert next_slot in ['budget', 'companions', 'purpose']


def test_get_next_slot_when_all_complete():
    """모든 슬롯이 수집되면 None 반환"""
    manager = PlanManager()
    plan = {
        'destination': '제주도',
        'start_date': '2026-03-15',
        'duration': '3박 4일',
        'budget': '50만원',
        'companions': '가족',
        'purpose': '휴양'
    }
    next_slot = manager.get_next_slot_to_collect(plan)

    assert next_slot is None
