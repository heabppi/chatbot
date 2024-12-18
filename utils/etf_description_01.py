from config import AVAILABLE_THEMES
import httpx

# UTF-8로 헤더를 명시적으로 설정
headers = {
    "Content-Type": "application/json; charset=utf-8"
}

def get_user_name(llm, user_input):
    """
    사용자 입력에서 이름을 추출합니다.

    Parameters:
        llm (object): LLM 객체 (예: ChatUpstage)
        user_input (str): 사용자가 입력한 텍스트

    Returns:
        str: 사용자의 이름
    """

    prompt = f"""
    입력된 문장에서 님이나 호칭을 붙이지 말고 꼭 이름만 추출해 주세요. 다음과 같이 응답해 주세요:

    '{user_input}'님 안녕하세요! ETF에 대해 무엇이든 물어보세요.
    """

    # UTF-8로 인코딩 및 디코딩
    prompt = prompt.encode('utf-8').decode('utf-8')
    # LLM 호출
    response = llm.invoke(prompt)
    
    # AIMessage 객체에서 content만 추출
    if hasattr(response, "content"):
        return response.content.strip()
    else:
        return str(response).strip()


def user_analysis_yesorno(llm, user_input):
    prompt = f"""
    [아래]의 텍스트가 긍정인지 부정인지 판단하세요.
    상위 유망한 테마를 알려드릴까요?에 대한 리턴이며, 
    답변은 추가설명을 하지 않고 꼭 '긍정', '부정'으로만 리턴합니다.

    예시:
    긍정: 네, 좋아요, 괜찮아요, 좋아, 예, 필요해, 응, 좋아요, 알려줘, 알려주세요
    부정: 아니요, 아니, 싫어요, 잘 모르겠어요, 안 돼요
    
    [아래]
    {user_input}
    """
    extracted_name = llm.invoke(prompt).content
    print(user_input)
    print(extracted_name)
    return extracted_name.strip()

def correct_answer_etf(llm, user_input):
    prompt = f"""
    사용자가 아래와 같은 테마를 입력했습니다:
    "{user_input}"

    현재 지원하는 테마 리스트는 다음과 같습니다:
    {', '.join(AVAILABLE_THEMES)}

    사용자가 입력한 내용을 가장 잘 설명하거나 매칭되는 테마를 리스트에서 찾아 반환하세요.
    예를 들어서 '배터리'라고만 입력해도 '2차전지'로 알고, '5G'를 입력해도 '차세대통신'으로 관련이 있는 것으로 판단하세요.
    만약 어떤 테마와도 관련이 없으면 "아니요"라는 단어만 반환하세요.
    """
    response = llm.invoke(prompt).content.strip()

    if response == "아니요":
        return "아니요"
    elif response in AVAILABLE_THEMES:
        return response

def user_analysis_etf(llm, user_input):
    prompt = f"""
    지금부터 ETF에 대한 전문가입니다.
    [아래]의 텍스트는 'ETF에 대해서 궁금하신 점이 있으시다면 저에게 물어보세요!'에 대한 대답입니다.
    이 질문에 대한 대답을 자세하고 꼼꼼하게 초보자도 알아들을 수 있게 리턴하거나,
    [아래]의 텍스트가 '아니요'나 '없음' 같이 다음으로 넘어가고싶어 하는 말이라면꼭 '아니요'라는 단어만 리턴합니다.

    아니요 : 없음, 아니요, 다음으로 넘어고싶습니다, 궁금한거 없음, 다음 등

    [아래]
    {user_input}
    """
    extracted_response = llm.invoke(prompt).content.strip()
    return extracted_response

def get_user_theme_input():
    print("사용 가능한 ETF 테마 목록:")
    for i, theme in enumerate(AVAILABLE_THEMES, start=1):
        print(f"{i}. {theme}")

    try:
        theme_choice = int(input("원하는 ETF 테마 번호를 입력하세요: ")) - 1
        if 0 <= theme_choice < len(AVAILABLE_THEMES):
            return AVAILABLE_THEMES[theme_choice]
        else:
            print("잘못된 선택입니다. 다시 시도해주세요.")
            return get_user_theme_input()
    except ValueError:
        print("숫자를 입력해주세요.")
        return get_user_theme_input()
