#!/usr/bin/env python3
"""
ResponseParser 디버깅 스크립트
"""

import sys

sys.path.insert(0, "/Users/mingukjang/git/spica_idea8on/2601/auto-tdd-agent")

# 규칙 기반 모드
import os

os.environ["USE_LLM"] = "false"

from src.services.response_parser import ResponseParser

parser = ResponseParser(use_llm=False)

# 테스트 케이스
test_inputs = [
    ("제주도", "destination"),
    ("2026-03-15", "start_date"),
    ("3박 4일", "duration"),
    ("100만원", "budget"),
    ("친구 2명", "companions"),
    ("휴양", "purpose"),
]

print("=== ResponseParser Debug ===\n")

for text, expected_slot in test_inputs:
    result = parser.parse(text, {})

    print(f"Input: '{text}'")
    print(f"  Expected slot: {expected_slot}")
    print(f"  Parsed result: {result}")

    if expected_slot in result:
        print(f"  ✓ SUCCESS: {expected_slot} = {result[expected_slot]}")
    else:
        print(f"  ✗ FAILED: {expected_slot} not found")
    print()

# 개별 함수 테스트
print("\n=== Individual Function Test ===\n")

test_functions = [
    ("_extract_budget", ["100만원", "100만 원", "50만원", "10만원"]),
    ("_extract_companions", ["친구 2명", "가족", "혼자", "연인"]),
    ("_extract_purpose", ["휴양", "관광", "먹방", "여행"]),
]

for func_name, test_cases in test_functions:
    func = getattr(parser, func_name)
    print(f"{func_name}():")
    for text in test_cases:
        result = func(text)
        status = "✓" if result else "✗"
        print(f"  {status} '{text}' -> {result}")
    print()
