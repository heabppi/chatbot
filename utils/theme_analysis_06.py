from serpapi import GoogleSearch
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from config import SERPAPI_KEY, UPSTAGE_API_KEY, ETF_DESCRIPTIONS
from langchain_upstage import ChatUpstage
import os
from dotenv import load_dotenv

def load_environment():
    """
    환경 변수 로드 함수
    .env 파일에서 환경 변수를 읽어와 시스템 환경 변수로 설정합니다.
    """
    load_dotenv()

# 환경 변수 설정
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "your-default-serpapi-key")
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY", "your-default-upstage-key")

class ETFAnsweringSystem:
    def __init__(self, theme):
        self.theme = theme
        self.llm = ChatUpstage(model='solar-pro', api_key = UPSTAGE_API_KEY)  # OpenAI LLM 설정
        self.prompt_template = PromptTemplate(
            input_variables=["context"],
            template="""
            뉴스 타이틀을 바탕으로 해당 테마에 대한 전망을 예측해주세요.
            
            뉴스 타이틀:
            {context}
            """
        )

    def get_google_search(self):
        search_keyword = self.theme  # 테마 이름만 사용
        params = {
            "api_key": SERPAPI_KEY,
            "engine": "google_news",
            "hl": "ko",
            "gl": "kr",
            "q": search_keyword
        }

        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            news_json_result = results.get('news_results', [])
            if not news_json_result:
                return f"'{search_keyword}'에 대한 관련 뉴스를 찾을 수 없습니다."
            news_list = [news['title'] for news in news_json_result if 'title' in news]
            return "\n".join(news_list)
        except Exception as e:
            return f"Google Search 실행 중 오류 발생: {str(e)}"

    def answer_question(self):
        context = self.get_google_search()
        if not context:
            return "관련 뉴스를 찾을 수 없습니다."

        try:
            chain = LLMChain(prompt=self.prompt_template, llm=self.llm)
            result = chain.run(context=context)
            print(context)
            return result
        except Exception as e:
            return f"LLMChain 실행 중 오류 발생: {str(e)}"

    def get_theme_details(self):
        description = ETF_DESCRIPTIONS[self.theme.replace(" ETF", "")]["description"]  # 원래 테마로 접근
        return f"테마 설명: {description}\n"