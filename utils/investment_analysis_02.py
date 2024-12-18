import re

# 투자 성향 질문 선택지 정의
current_options = {
    "목적": [
        "1. 생활비나 긴급자금 등 필수 자금을 안전하게 관리", 
        "2. 결혼, 내 집 마련 등 특정 목표 자금을 안정적으로 모음", 
        "3. 목표 자금 마련 + 적정 수준의 자산 증식", 
        "4. 장기적인 자산 증식과 재산 형성", 
        "5. 고수익을 통한 빠른 자산 증식"
    ],
    "손실/수익률": [
        "1. 원금 손실 절대 불가", 
        "2. 원금 보전 중요, 약간의 손실 감수 가능", 
        "3. 10% 이내 손실 감수 가능", 
        "4. 20% 이상 손실 감수 가능", 
        "5. 원금 초과 손실 감수"
    ],
    "투자 비중": [
        "1. 총 자산의 10% 이하", 
        "2. 10% ~ 30%", 
        "3. 30% ~ 50%", 
        "4. 50% ~ 70%", 
        "5. 70% 이상"
    ]
}


def match_user_input(user_input, options):
    user_input = user_input.strip()  # 공백 제거
    if user_input.isdigit():
        number = int(user_input)
        if 1 <= number <= len(options):
            return str(number)
    return None

def determine_investment_type(answers):
    scores = {
        "목적": {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5},
        "손실/수익률": {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5},
        "투자 비중": {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5},
    }
    total_score = sum(scores[key][answers[key]] for key in answers if key in scores)
    if total_score <= 8:
        return "안정형"
    elif 9 <= total_score <= 11:
        return "중립형"
    else:
        return "공격형"
