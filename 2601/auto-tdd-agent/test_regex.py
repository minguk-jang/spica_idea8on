#!/usr/bin/env python3
"""
정규식 패턴 테스트
"""

import re

# Budget patterns
test_cases = [
    "100만원",
    "100만 원",
    "50만원",
    "50만 원",
]

print("=== Budget Pattern Test ===")
for text in test_cases:
    # Pattern 1: "50만원" 또는 "50만 원" 형식 (공백 유무 모두 처리)
    pattern1 = r"(\d+)\s*만\s*원?"
    match1 = re.search(pattern1, text)

    # Pattern 2: "100만원" 형식 (공백 없음)
    pattern2 = r"(\d+만원)"
    match2 = re.search(pattern2, text)

    result = None
    if match1:
        result = f"{match1.group(1)}만원"
    elif match2:
        result = match2.group(1)

    print(f"'{text}' -> {result}")

print("\n=== Companions Pattern Test ===")
companions_cases = [
    "친구 2명",
    "친구랑",
    "가족",
    "혼자",
    "연인",
]

patterns = [
    r"(혼자|혼자서|나 혼자|혼자 여행)",
    r"(친구\s*\d*명?|친구랑|친구와|친구들?)",
    r"(가족|부모님|아이들?|아들|딸|형제|자매)",
    r"(연인|남자친구|여자친구|배우자|부부)",
    r"(동료|회사\s*동료|직장\s*동료)",
]

for text in companions_cases:
    result = None
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            result = match.group(1)
            break
    print(f"'{text}' -> {result}")

print("\n=== Purpose Pattern Test ===")
purpose_cases = [
    "휴양",
    "관광",
    "먹방",
    "여행",  # 주의: 여행은 목적지 질문에도 매칭될 수 있음
]

purpose_patterns = [
    r"(휴양|휴식|쉬|힐링|재충전)",
    r"(관광|구경|볼거리|여행|관람|탐방)",
    r"(먹방|맛집|음식|미식|먹을거리)",
    r"(액티비티|체험|모험|스포츠|서핑|등산|자전거)",
    r"(문화|역사|박물관|미술관|전시|공연)",
    r"(쇼핑|쇼핑하|구매|사고\s*싶)",
]

for text in purpose_cases:
    result = None
    for pattern in purpose_patterns:
        match = re.search(pattern, text)
        if match:
            result = match.group(1)
            break
    print(f"'{text}' -> {result}")
