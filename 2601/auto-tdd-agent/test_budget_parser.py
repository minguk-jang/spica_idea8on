#!/usr/bin/env python3
"""
예산 추출 테스트 - 직접 ResponseParser 테스트
"""

import sys
import os

os.environ["USE_LLM"] = "false"
os.environ["USE_IPC_LLM"] = "false"

sys.path.insert(0, "/Users/mingukjang/git/spica_idea8on/2601/auto-tdd-agent")

from src.services.response_parser import ResponseParser

parser = ResponseParser(use_llm=False)

test_cases = [
    ("100만원", {"budget": "100만원"}),
    ("50만 원", {"budget": "50만원"}),
    ("10만원", {"budget": "10만원"}),
    ("친구 2명", {"companions": "친구 2명"}),
    ("휴양", {"purpose": "휴양"}),
    ("제주도", {"destination": "제주도"}),
]

print("=== ResponseParser 단위 테스트 ===\n")

all_passed = True
for text, expected in test_cases:
    result = parser.parse(text, {})

    print(f"Input: '{text}'")
    print(f"  Expected: {expected}")
    print(f"  Got:      {result}")

    # Check if expected keys are in result
    passed = True
    for key, value in expected.items():
        if key not in result or result[key] != value:
            passed = False
            all_passed = False

    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"  {status}")
    print()

print("=" * 40)
if all_passed:
    print("✓ 모든 테스트 통과!")
else:
    print("✗ 일부 테스트 실패")
