import pandas as pd
import numpy as np
from config import ETF_DESCRIPTIONS
from utils.theme_analysis_06 import ETFAnsweringSystem
import streamlit as st

@st.cache_data
def load_etf_data(investment_type):
    """
    투자 성향에 따라 적합한 ETF 데이터를 로드합니다.

    Parameters:
        investment_type (str): 투자 성향 ("안정형", "중립형", "공격형")

    Returns:
        pandas.DataFrame: ETF 데이터프레임
    """
    file_map = {
        "안정형": "data/merged_conservative_with_details_new.csv",
        "중립형": "data/merged_balanced_with_details_new.csv",
        "공격형": "data/merged_aggressive_with_details_new.csv",
    }
    file_path = file_map.get(investment_type)
    if not file_path:
        raise ValueError("잘못된 투자 성향입니다.")
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"'{file_path}' 파일을 찾을 수 없습니다. 경로를 확인하세요.")

## ETF 테마 순위 계산 (윤지님)
def calculate_etf_sentiment_rank(data):
    group_column = '테마'
    cagr_column = 'CAGR'
    volatility_column = '변동성'
    correlation = 0.5

    grouped = data.groupby(group_column)
    results = []

    for theme, group in grouped:
        num_assets = len(group)
        weights = np.full(num_assets, 1 / num_assets)

        # 공분산 행렬 생성
        cov_matrix = np.zeros((num_assets, num_assets))
        for i in range(num_assets):
            for j in range(num_assets):
                if i == j:
                    cov_matrix[i, j] = group[volatility_column].iloc[i] ** 2
                else:
                    cov_matrix[i, j] = correlation * group[volatility_column].iloc[i] * group[volatility_column].iloc[j]

        # 테마별 지표 계산
        theme_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
        theme_cagr = np.sum(weights * group[cagr_column])
        theme_sharp = theme_cagr / theme_volatility

        # 결과 저장
        results.append({
            group_column: theme,
            '테마 변동성': theme_volatility,
            '테마 CAGR': theme_cagr,
            '테마 샤프지수': theme_sharp
        })

    portfolio_results = pd.DataFrame(results)
    portfolio_results = portfolio_results.sort_values(by='테마 샤프지수', ascending=False).reset_index(drop=True)

    ranked_themes = portfolio_results[(portfolio_results['테마 CAGR'] > 0.03) & (portfolio_results['테마 샤프지수'] > 0)]

    return ranked_themes

def recommend_top_etfs(user_type, selected_themes, top_n=5):
    """선택한 테마에 따라 ETF를 추천합니다."""
    etf_data = load_etf_data(user_type)
    if etf_data is None:
        return {"error": "ETF 데이터를 로드하지 못했습니다."}

    recommendations = {}
    for theme in selected_themes:
        filtered_data = etf_data[etf_data['테마_x'] == theme]
        if filtered_data.empty:
            recommendations[theme] = f"'{theme}' 테마에 대한 데이터가 없습니다."
        else:
            top_etfs = filtered_data.sort_values(by='최종 환산 점수', ascending=False).head(top_n)
            etf_details = []
            for _, row in top_etfs.iterrows():
                etf_details.append({
                    "ETF 코드": row['ETF 코드'],
                    "ETF 이름": row['ETF 이름'],
                    "소개": row['소개'],
                    "투자포인트": row['투자포인트'],
                    "현재가": row['현재가_x']
                })
            recommendations[theme] = etf_details
    return recommendations


def match_theme(input_theme):
    """사용자가 입력한 테마를 ETF_DESCRIPTIONS의 키와 매칭."""
    for theme_key in ETF_DESCRIPTIONS.keys():
        if input_theme.strip() in theme_key:
            return theme_key
    return None  # 매칭되지 않을 경우 None 반환

def analyze_etf_theme(themes):
    """테마 기반 ETF 분석 함수."""
    input_theme = themes[0]
    matched_theme = match_theme(input_theme)

    if not matched_theme:
        # 매칭 실패 시 오류 메시지 반환
        return input_theme, None, f"'{input_theme}' 테마를 찾을 수 없습니다. 다시 입력해주세요."

    # 매칭된 테마로 ETFAnsweringSystem 초기화
    qa_system = ETFAnsweringSystem(matched_theme)
    
    try:
        # 테마 설명 및 뉴스 전망 가져오기
        theme_details = qa_system.get_theme_details()
        result = qa_system.answer_question()
        return matched_theme, theme_details, result
    except KeyError as e:
        # ETF_DESCRIPTIONS 키 오류 처리
        return matched_theme, None, f"'{matched_theme}' 테마에 대한 정보를 찾을 수 없습니다. 오류: {str(e)}"
    
def get_ranges_by_invest_type(invest_type):
    if invest_type == "안정형":
        return [
            {"return_range": "2%", "risk_range": "2%"},
            {"return_range": "4%", "risk_range": "4%"},
            {"return_range": "5%", "risk_range": "5%"},
        ]
    elif invest_type == "중립형":
        return [
            {"return_range": "7%", "risk_range": "10%"},
            {"return_range": "9%", "risk_range": "12.5%"},
            {"return_range": "10%", "risk_range": "15%"},
        ]
    elif invest_type == "공격형":
        return [
            {"return_range": "12%", "risk_range": "24%"},
            {"return_range": "15%", "risk_range": "30%"},
            {"return_range": "15% 이상", "risk_range": "30% 이상"},
        ]
    else:
        return []
