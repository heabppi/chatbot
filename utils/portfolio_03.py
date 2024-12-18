import pandas as pd
import numpy as np
import streamlit as st
from scipy.optimize import minimize

@st.cache_data
def load_etf_data(investment_type):
    """투자 성향에 따라 적합한 ETF 데이터를 로드합니다."""
    file_map = {
        "안정형": "data/merged_conservative_with_details_new.csv",
        "중립형": "data/merged_balanced_with_details_new.csv",
        "공격형": "data/merged_aggressive_with_details_new.csv",
    }
    print('로드 성공')
    file_path = file_map[investment_type]
    print(file_path)
    try:
        etf_data = pd.read_csv(file_path)
        return etf_data
    except FileNotFoundError:
        st.error(f"'{file_path}' 파일을 찾을 수 없습니다. 경로를 확인하세요.")
        return None
    
def calculate_portfolio_metrics(selected_etfs, investment_type):
    """선택된 ETF의 포트폴리오 메트릭을 계산합니다."""
    etf_data = load_etf_data(investment_type)
    print(11, etf_data)
    if etf_data is None:
        return None

    # ETF 데이터를 필터링하여 선택된 ETF만 가져오기
    etf_data['ETF 코드'] = etf_data['ETF 코드'].astype(str).str.strip()
    selected_etfs = [code.strip() for code in selected_etfs if code.strip()]
    filtered_data = etf_data[etf_data['ETF 코드'].isin(selected_etfs)]
    
    if filtered_data.empty:
        st.warning("선택된 ETF 데이터가 없습니다. ETF 코드를 다시 확인해주세요.")
        return None

    # 평균 CAGR(수익률)과 변동성 계산
    avg_cagr = filtered_data['CAGR'].mean()
    avg_volatility = filtered_data['변동성'].mean()

    return {
        "selected_etfs": filtered_data[['ETF 코드', 'ETF 이름', 'CAGR', '변동성']].reset_index(drop=True),
        "avg_cagr": avg_cagr,
        "avg_volatility": avg_volatility
    }

def calculate_portfolio_volatility(etf_volatility, bond_volatility, etf_ratio, bond_ratio, correlation=0.2):
    """ETF와 채권 포트폴리오의 변동성을 계산합니다."""
    portfolio_variance = (
        (etf_ratio * etf_volatility) ** 2 +
        (bond_ratio * bond_volatility) ** 2 +
        2 * etf_ratio * bond_ratio * correlation * etf_volatility * bond_volatility
    )
    return np.sqrt(portfolio_variance) * 100

def filter_correlation(corr_df, selected_codes):
    selected_codes = list(set([str(code).strip() for code in selected_codes])) 

    if '채권' not in selected_codes:
        selected_codes.append('채권')

    # corr_df의 인덱스와 컬럼을 문자열로 변환하여 비교
    corr_df.index = corr_df.index.astype(str)
    corr_df.columns = corr_df.columns.astype(str)

    # corr_df의 인덱스와 컬럼에 존재하는 코드들만 필터링
    available_codes = [code for code in selected_codes if code in corr_df.index and code in corr_df.columns]
    
    print("사용 코드:", available_codes)

    # 하나라도 선택된 게 있으면 돌아가기
    if available_codes:
        filtered_corr = corr_df.loc[available_codes, available_codes]
        print("해당 상관관계:")
        print(filtered_corr)
        return filtered_corr
    else:
        print("매칭되는 코드가 없습니다.")
        return pd.DataFrame()  # 매칭되는 코드가 없으면 빈 데이터프레임 반환

def adjust_portfolio_ratios(target_return, target_volatility, returns, volatility, ETF_NAME):
    n = len(returns)
    print(f'ETF 이름 : {ETF_NAME}')
    # 중요도 가중치 (0~1 사이, 예: 수익률 우선 0.7, 변동성 중요도 0.3)
    lambda_weight = 0.7
    corr_df = pd.read_csv('data/ETF_corr_renamed.csv', index_col=0)
    corr_matrix = filter_correlation(corr_df, ETF_NAME)

    # 공분산행렬 계산
    cov_matrix = np.outer(volatility, volatility) * corr_matrix

    # 초기 가중치 추정값 (균등 분배)
    initial_weights = [1.0/n] * n
    
    # 포트폴리오 기대수익률 계산 함수
    def portfolio_return(weights):
        return np.dot(weights, returns)

    # 포트폴리오 변동성 계산 함수
    def portfolio_volatility(weights):
        return np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))

    # 최적화 목표 함수
    def objective_function(weights):
        ret_diff = portfolio_return(weights) - target_return
        vol_diff = portfolio_volatility(weights) - target_volatility
        return lambda_weight * (ret_diff**2) + (1 - lambda_weight) * (vol_diff**2)

    # 가중치 합이 1을 만족하는 함수
    def weight_constraint(weights):
        return np.sum(weights) - 1

    # 제약 조건 설정
    constraints = [
        {"type": "eq", "fun": weight_constraint}  # 가중치 합 = 1
    ]

    # 가중치의 경계 (0 <= w_i <= 1)
    bounds = [(0, 1) for _ in range(n)]

    # 최적화 실행
    result = minimize(objective_function, initial_weights, bounds=bounds, constraints=constraints)
    optimized_weights = result.x
    optimized_return = portfolio_return(optimized_weights)
    optimized_volatility = portfolio_volatility(optimized_weights)

    optimized_result = {
        'weights' : optimized_weights,
        'return'  : optimized_return,
        'volatility' : optimized_volatility
    }

    return optimized_result











