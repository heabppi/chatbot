from langchain_upstage import ChatUpstage
import pandas as pd
from config import load_environment, QUESTIONS
from utils.etf_description_01 import get_user_name
from utils.etf_description_01 import user_analysis_yesorno, user_analysis_etf, correct_answer_etf
from utils.investment_analysis_02 import match_user_input, determine_investment_type, current_options
from utils.portfolio_03 import calculate_portfolio_metrics, calculate_portfolio_volatility, adjust_portfolio_ratios
from utils.etf_analysis_04 import calculate_etf_sentiment_rank, recommend_top_etfs, analyze_etf_theme, get_ranges_by_invest_type
import plotly.graph_objects as go

# 환경 변수 로드
load_environment()
import streamlit as st
import time
import re

# 페이지 설정 (반드시 최상단에 위치)
st.set_page_config(page_title="ETF 추천 어시스턴트", layout="wide")
llm = ChatUpstage(model='solar-pro', api_key="####") #개인API

# ------------------ 초기화 및 플래그------------------#
#  세션 상태 초기화(질문)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "answers" not in st.session_state:
    st.session_state.answers = {}
# user_input 부분(아래)
if "user_name" not in st.session_state: # 이름
    st.session_state.user_name = None
if "user_ready" not in st.session_state: #
    st.session_state.user_ready = None
if "analysis_type" not in st.session_state:
    st.session_state.analysis_type = None
if "user_question" not in st.session_state:
    st.session_state.user_question = None
if "investment_type" not in st.session_state:
    st.session_state.investment_type = None
if "etf_rank" not in st.session_state:
    st.session_state.etf_rank = None
if "selected_themes" not in st.session_state:
    st.session_state.selected_themes = []
if "recommend_top_5_etf" not in st.session_state:
    st.session_state.recommend_top_5_etf = False
if "waiting_for_portfolio" not in st.session_state:
    st.session_state.waiting_for_portfolio = False
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "current_stage" not in st.session_state:
    st.session_state.current_stage = "name" 
# 처음 메시지를 보냈는지 여부를 관리하는 플래그(위)
if "asked_name" not in st.session_state:
    st.session_state.asked_name = False
if "etf_analysis" not in st.session_state:
    st.session_state.etf_analysis = False




# ------------------ title 및 chat style------------------#
# Initialize the page
st.title("📈📊 ETF 추천 chat-bot 🤖")

def render_messages():

    for message in st.session_state.messages[:-1]:
        content_with_emphasis = message["content"].replace("**", "<strong>")
        if message["role"] == "assistant":
            st.markdown(f"<div style='display: flex; justify-content: flex-start; margin: 5px 0;'>"
                        f"<div style='background-color: #f1f0f0; color: #000; padding: 10px 15px; border-radius: 15px 15px 15px 0; max-width: 70%; font-size: 14px; text-align: left;'>{content_with_emphasis}</div>"
                        f"</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='display: flex; justify-content: flex-end; margin: 5px 0;'>"
                        f"<div style='background-color: #dcf8c6; color: #000; padding: 10px 15px; border-radius: 15px 15px 0 15px; max-width: 70%; font-size: 14px; text-align: left; word-wrap: break-word;'>{content_with_emphasis}</div>"
                        f"</div>", unsafe_allow_html=True)
            time.sleep(1)

    last_message = st.session_state.messages[-1]
    
    placeholder = st.empty()  # 각 메시지의 출력 위치
    displayed_text = ""
    for char in last_message['content']:
        displayed_text += char
        content_with_emphasis = displayed_text.replace("**", "<strong>")  # Markdown 스타일을 HTML로 변환
        if last_message["role"] == "assistant":
            placeholder.markdown(f"<div style='display: flex; justify-content: flex-start; margin: 5px 0;'>"
                        f"<div style='background-color: #f1f0f0; color: #000; padding: 10px 15px; border-radius: 15px 15px 15px 0; max-width: 70%; font-size: 14px; text-align: left;'>{displayed_text}</div>"
                        f"</div>", unsafe_allow_html=True)
        else:
            placeholder.markdown(f"<div style='display: flex; justify-content: flex-end; margin: 5px 0;'>"
                        f"<div style='background-color: #dcf8c6; color: #000; padding: 10px 15px; border-radius: 15px 15px 0 15px; max-width: 70%; font-size: 14px; text-align: left; word-wrap: break-word;'>{displayed_text}</div>"
                        f"</div>", unsafe_allow_html=True)
        time.sleep(0.05)


## ------------------ 메인 로직 ------------------ ##

# 사용자 입력 받기
user_input = st.chat_input("답변을 입력하세요...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input.strip()})

# 0) 사용자 이름 요청 단계
if st.session_state.current_stage == "name":
    if not st.session_state.asked_name:
        st.session_state.messages.append({"role": "assistant", "content": "안녕하세요! 저는 테마별 ETF 추천 어시스턴트입니다. 이름을 알려주세요."})
        st.session_state.asked_name = True
    elif not st.session_state.user_name:
        st.session_state.user_name = get_user_name(llm, user_input)
        if st.session_state.user_name:
            st.session_state.messages.append({"role": "assistant", "content": f"{st.session_state.user_name}님 반갑습니다! ETF에 대해 궁금하신 점이 있으면 말씀해주세요."})
            st.session_state.current_stage = "etf_info"

# 1) 사용자 ETF 정보 요청 단계
elif st.session_state.current_stage == "etf_info":
    if user_input:
        etf_info = user_analysis_etf(llm, user_input)  # ETF 정보 분석 함수 호출
        if etf_info.lower() == "아니요":  # 사용자가 "아니요"라고 응답했을 경우
            st.session_state.messages.append({"role": "assistant", "content": "알겠습니다. 투자 성향 분석을 시작합니다!"})
            st.session_state.current_stage = "analysis"  # 투자 성향 분석 단계로 이동
            st.session_state.current_question = 0  # 질문 번호 초기화
        else:
            st.session_state.messages.append({"role": "assistant", "content": etf_info})  # ETF 정보 출력
            st.session_state.messages.append({"role": "assistant", "content": "더 궁금한 질문이 있으신가요?"})

# 2) 투자 성향 분석 단계
elif st.session_state.current_stage == "analysis" and st.session_state.current_question >= 0:
    if st.session_state.current_question < len(current_options):  # 질문이 남아 있는 경우
        current_key = list(current_options.keys())[st.session_state.current_question]
        print(11, current_key)
        current_options_list = current_options[current_key]
        print(22, current_options_list)

        # 사용자 입력 매칭
        matched_option = match_user_input(user_input, current_options_list)
        print(31, matched_option)
        print(32, matched_option)
        print(33, len(QUESTIONS))
        if matched_option:
            st.session_state.answers[current_key] = matched_option  # 사용자의 선택 저장
            st.session_state.current_question += 1
            print(44, st.session_state.current_question)
        else:
            st.session_state.messages.append({"role": "assistant", "content": "유효한 선택지를 입력해주세요."})

        # 다음 질문 출력 (중복 방지)
        if (
            st.session_state.current_question < len(QUESTIONS)  # 질문이 남아 있는 경우
            and all(
                QUESTIONS[st.session_state.current_question] != msg["content"]
                for msg in st.session_state.messages
    )
        ):
            st.session_state.messages.append({"role": "assistant", "content": QUESTIONS[st.session_state.current_question]})
    else:
        # 모든 질문 완료 -> 투자 성향 분석 결과 출력
        st.session_state.investment_type = determine_investment_type(st.session_state.answers)
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"투자 성향 분석 결과는 **{st.session_state.investment_type}**입니다."
        })
        st.session_state.messages.append({"role": "assistant", "content": f"{st.session_state.investment_type}의 수익률 및 리스크를 선택해주세요."})
        st.session_state.ranges = ranges = get_ranges_by_invest_type(st.session_state.investment_type)      
        # 옵션 생성 및 화면 출력
        st.session_state.options = [
            f"{idx + 1}. 수익률 : {option['return_range']}, 리스크 : {option['risk_range']}"
            for idx, option in enumerate(ranges)
        ]
        # 옵션을 메시지로 추가
        options_message = "\n\n".join(st.session_state.options)  # 리스트를 문자열로 변환
        st.session_state.messages.append({"role": "assistant", "content": options_message})
        st.session_state.current_stage = "select_invest_range"  # 다음 단계로 이동


# 3-1) 투자 범위(수익률 및 리스크) 선택
elif st.session_state.current_stage == "select_invest_range":
    
    # 입력값 처리
    if user_input:
        # 정규 표현식으로 숫자만 추출
        extracted_number = re.findall(r'\d+', user_input)
        selected_index = int(extracted_number[0]) - 1  # 번호를 인덱스로 변환
        print(selected_index)
                
        # 인덱스 유효성 검사
        if 0 <= selected_index < len(st.session_state.options):
            selected_option = st.session_state.options[selected_index]  # 선택된 옵션
            # 선택된 옵션에서 수익률과 리스크 추출
            return_match = re.search(r"수익률\s*:\s*([0-9~%\s]+)", selected_option)
            risk_match = re.search(r"리스크\s*:\s*([0-9~%\s]+)", selected_option)

            if return_match and risk_match:
                return_range = return_match.group(1).strip()  # 수익률 값 추출
                risk_range = risk_match.group(1).strip()      # 리스크 값 추출

                # 결과 저장
                st.session_state.selected_range = selected_option
                st.session_state.return_range = return_range  # 수익률 저장
                st.session_state.risk_range = risk_range      # 리스크 저장

                # 성공 메시지 출력
                st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"**선택하신 옵션**: {selected_option}"
                })
                st.success(f"선택하신 옵션:\n수익률: {return_range}, 리스크: {risk_range}")

                # 다음 단계로 이동
                st.session_state.current_stage = "theme_ranking"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "상위 유망 테마를 알려드릴까요?"  # 이제 여기에서 다음 단계로!!!!!!!!!
                })

            else:
                st.error("옵션에서 수익률과 리스크를 찾을 수 없습니다.")


# 4) 상위 테마 리스트 제공 단계
elif st.session_state.current_stage == "theme_ranking":
    answer = user_analysis_yesorno(llm, user_input)  # 사용자의 긍정/부정 응답 분석
    if answer == '긍정':
        data = pd.read_csv("data/cal_data.csv")  # 테마 데이터 로드
        etf_rank = calculate_etf_sentiment_rank(data)  # 테마 순위 계산
        all_themes = etf_rank['테마']
        all_themes_display = "\n".join([f"{idx + 1}. {theme}" for idx, theme in enumerate(all_themes)])

        # 테마 순위 출력
        st.session_state.messages.append({"role": "assistant", "content": f"**유망 테마 순위**\n\n{all_themes_display}"})
        st.session_state.messages.append({"role": "assistant", "content": "알고 싶은 테마가 있으신가요? (테마를 입력해주세요)"})
        st.session_state.current_stage = "theme_info"  # 다음 단계로 이동

# 4) 테마 설명 및 실시간 뉴스 제공
elif st.session_state.current_stage == "theme_info":
    if user_input:
        themes = [theme.strip() for theme in user_input.split(",")]
        selected_theme, theme_details, news_summary = analyze_etf_theme(themes)
        if theme_details and news_summary:
            st.session_state.messages.append({"role": "assistant", "content": f"**{selected_theme} 테마 설명:**\n\n{theme_details}\n\n**실시간 뉴스 요약:**\n\n{news_summary}"})
            st.session_state.messages.append({"role": "assistant", "content": "더 알고 싶으신 테마가 있으신가요? (테마를 입력해주세요.)"})
        elif user_analysis_yesorno(llm, user_input) == "부정":
            st.session_state.messages.append({"role": "assistant", "content": "이제, 투자 희망 테마를 입력해주세요!"})
            st.session_state.current_stage = "etf_recommendation"

# 5) 테마 설명 및 실시간 뉴스 제공
elif st.session_state.current_stage == "theme_info":
    if user_input:
        themes = [theme.strip() for theme in user_input.split(",")]
        selected_theme, theme_details, news_summary = analyze_etf_theme(themes)
        if theme_details and news_summary:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"**{selected_theme} 테마 설명:**\n\n{theme_details}\n\n**실시간 뉴스 요약: **\n\n{news_summary}"
            })
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "더 알고 싶으신 테마가 있으신가요? (테마를 입력해주세요.)"
            })
                      
            
    if user_analysis_yesorno(llm, user_input) == "부정":
        st.session_state.messages.append({"role": "assistant", "content": "이제, 투자 희망 테마를 입력해주세요!"})
        st.session_state.current_stage = "etf_recommendation"


# 6) ETF 추천 단계
elif st.session_state.current_stage == "etf_recommendation":
    if user_input:
        selected_themes = [theme.strip() for theme in user_input.split(",")]
        etf_recommendations = recommend_top_etfs(st.session_state.investment_type, selected_themes)

        for theme, etfs in etf_recommendations.items():
            if isinstance(etfs, list):
                etf_list = "\n\n".join([f"**ETF 코드**: {etf['ETF 코드']}\n**ETF 이름**: {etf['ETF 이름']}\n**현재가**: {etf['현재가']} 원" for etf in etfs])
                st.session_state.messages.append({"role": "assistant", "content": f"**{theme} 추천 ETF:**\n\n{etf_list}"})
            else:
                st.session_state.messages.append({"role": "assistant", "content": etfs})

        st.session_state.messages.append({"role": "assistant", "content": "ETF 코드를 입력해주세요!"})
        st.session_state.current_stage = "portfolio_start"
    
    else:
        # 입력 필드
        user_input = st.text_input("테마를 다시 입력해주세요:")

# 7) 포트폴리오 작성 단계
elif st.session_state.current_stage == "portfolio_start":
    if user_input:
        st.session_state.selected_etfs = [int(code.strip()) for code in user_input.split(",")]
        # 선택한 ETF 데이터에서 수익률(CAGR)과 변동성 계산
        # portfolio_metrics = calculate_portfolio_metrics(st.session_state.selected_etfs, st.session_state.investment_type)
            
        # if portfolio_metrics:
        bond_cagr = 0.0376  # 채권 수익률
        bond_volatility = 0.0785  # 채권 변동성

        df = pd.read_csv('data/cal_data.csv', index_col = 0).set_index('코드')
        select_df = df.loc[st.session_state.selected_etfs, ['CAGR', '변동성']]
        bond = {'CAGR' : bond_cagr, '변동성' : bond_volatility}
        select_df.loc['채권'] = bond
        returns = select_df['CAGR'].to_list()
        volatility = select_df['변동성'].to_list()

        # st.session_state.return_range = int(re.sub(r"[^0-9]", "", st.session_state.return_range))
        # st.session_state.risk_range = int(re.sub(r"[^0-9]", "", st.session_state.risk_range))
        adjust_portfolio_result = adjust_portfolio_ratios(
            int(st.session_state.return_range.split('%')[0]) / 100,
            int(st.session_state.risk_range.split('%')[0]) / 100,
            returns,
            volatility,
            st.session_state.selected_etfs
        )
        st.session_state.portfolio_summary = select_df.index, adjust_portfolio_result


        # 포트폴리오 구성 결과 출력
        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                f"**최적 포트폴리오 구성:**\n"
                f"- 예상 수익률: {adjust_portfolio_result['return'] * 100:.2f}%\n"
                f"- 예상 변동성: {adjust_portfolio_result['volatility'] * 100:.2f}%"
            )
        })    

        print("여기서 실패")

        # 추가 질문: 포트폴리오 생성 여부
        st.session_state.messages.append({"role": "assistant", "content": "이 포트폴리오로 진행하시겠습니까? (네/아니요)"})
        st.session_state.current_stage = "portfolio_followup"

    else:
        st.session_state.messages.append({"role": "assistant", "content": "선택한 ETF 데이터를 찾을 수 없습니다. 다시 입력해주세요."})
        

# 9) 최적 포트폴리오 결과 화면
elif st.session_state.current_stage == "portfolio_followup":
    if user_input.lower() in ["네", "예", "응"]:
        ETF_NAME, PORTFOLIO_RESULT = st.session_state.portfolio_summary
        

        # 파이 차트와 샤프 지수 비교 차트를 세션 상태에 저장
        # st.session_state.pie_chart = render_pie_chart(ETF_NAME, PORTFOLIO_RESULT['weights'])
        # st.session_state.sharpe_chart = render_sharpe_chart(portfolio_sharpe, etf_sharpe)

        # 결과 페이지로 자동 표시
        st.session_state.current_stage = "results"  # 페이지 상태 변경

# 메시지 출력
render_messages()

# 결과 페이지
if st.session_state.current_stage == "results":
    st.title("📊 최적 포트폴리오 결과")

    # 포트폴리오 요약 표시
    ETF_NAME, portfolio_summary = st.session_state.portfolio_summary

    st.markdown("### **포트폴리오 요약**")
    st.markdown(f"- **수익률**: {portfolio_summary['return'] * 100:.2f}%")
    st.markdown(f"- **변동성**: {portfolio_summary['volatility'] * 100:.2f}%")

    st.markdown("### **포트폴리오 비중**")
    for idx, name in enumerate(ETF_NAME):
        st.markdown(f"- **{name} 비율**: {portfolio_summary['weights'][idx] * 100:.2f}%")

    st.markdown("### **ETF와 채권 비율**")
    labels = ETF_NAME
    sizes = portfolio_summary['weights'] * 100
    fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, hole=0)])
    fig.update_layout(
        title='ETF와 채권 비율',
        width=500,  # 그래프 너비 설정
        height=500  # 그래프 높이 설정
    )

    st.plotly_chart(fig)


