import streamlit as st
import pandas as pd
import google.generativeai as genai
import io

# ==========================================
# 1. 페이지 설정 및 제목
# ==========================================
st.set_page_config(page_title="팀 강점 디브리핑 생성기", layout="wide")

st.title("🧩 조직 강점 분석 & 디브리핑 생성기 (Powered by Gemini)")
st.markdown("""
이 도구는 갤럽 강점 데이터를 분석하여 **팀 전체 요약, 리더 코칭, 개인별 가이드**를 자동으로 생성해줍니다.
""")

# ==========================================
# 2. 사이드바: 설정 및 파일 업로드
# ==========================================
with st.sidebar:
    st.header("⚙️ 설정 및 입력")
    
    # API 키 입력받기 (Gemini용으로 텍스트 변경)
    api_key = st.text_input("Gemini API Key 입력", type="password", help="AI Studio에서 발급받은 키를 입력하세요.")
    
    # 엑셀 파일 업로드
    uploaded_file = st.file_uploader("강점 엑셀 파일 업로드 (.xlsx)", type=['xlsx'])
    
    st.info("""
    **[엑셀 양식 가이드]**
    첫 번째 줄(헤더)에 아래 단어가 정확히 있어야 합니다:
    
    | 이름 | 직급 | 테마1 | 테마2 | 테마3 | 테마4 | 테마5 |
    |---|---|---|---|---|---|---|
    | 김철수 | 팀장 | 화합 | 수집 | 집중 | 존재감 | 승부 |
    """)

# ==========================================
# 3. AI 분석 함수 (뇌 역할 - Gemini 규격으로 변경)
# ==========================================
def analyze_data(system_prompt, user_prompt, api_key):
    if not api_key:
        st.error("⚠️ Gemini API Key를 먼저 입력해주세요!")
        return None
    
    # Gemini API 설정
    genai.configure(api_key=api_key)
    
    try:
# 가장 추론 능력이 뛰어난 gemini-1.5-pro 모델 설정 및 시스템 프롬프트 부여
        model = genai.GenerativeModel(
            model_name="gemini-3.1-pro", # <- 여기를 변경하세요.
            system_instruction=system_prompt
        )
        
        # 모델 세팅 (온도 조절)
        generation_config = genai.GenerationConfig(
            temperature=0.7
        )
        
        # 콘텐츠 생성 요청
        response = model.generate_content(
            user_prompt,
            generation_config=generation_config
        )
        return response.text
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
        return None

# ==========================================
# 4. 메인 분석 로직
# ==========================================
if uploaded_file is not None:
    # 엑셀 읽기
    df = pd.read_excel(uploaded_file)
    
    st.divider()
    st.subheader("📋 업로드된 데이터 확인")
    st.dataframe(df.head())

    # 데이터 문자열로 변환 (AI에게 보내기 위해)
    data_text = df.to_markdown(index=False)

    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["🏢 팀 전체 분석", "👑 팀장(리더) 리포트", "👤 구성원 개별 리포트"])

    # ------------------------------------------------
    # TAB 1: 팀 전체 분석
    # ------------------------------------------------
    with tab1:
        st.write("팀의 전체적인 강점 분포와 페르소나를 분석합니다.")
        if st.button("팀 전체 리포트 생성하기", type="primary"):
            with st.spinner("AI가 팀 데이터를 분석 중입니다..."):
                
                sys_prompt = """
                당신은 20년 경력의 조직개발 컨설턴트입니다. 
                입력된 구성원 전체의 강점 데이터를 바탕으로 통찰력 있는 팀 분석 보고서를 작성하세요.
                톤앤매너: 전문적이고 명확하며, 비즈니스 인사이트가 담긴 말투.
                """
                
                user_req = f"""
                아래 데이터를 바탕으로 다음 목차의 보고서를 작성해줘.
                
                데이터:
                {data_text}

                [목차]
                1. 팀 전체 강점 카테고리별 분포 (실행/영향력/대인관계/전략적사고 4개 영역 비율 및 해석)
                2. 가장 많이 등장하는 핵심 테마 (Top 3~5) 및 그로 인한 팀의 특징
                3. 팀 전체 브리핑 (팀 페르소나 정의, 장점, 주의할 점/맹점)
                4. 팀 코칭 포인트 (리더가 이 팀을 이끌 때 주의할 점)
                """
                
                # 변수 api_key 추가 전달
                result = analyze_data(sys_prompt, user_req, api_key)
                if result:
                    st.markdown(result)

    # ------------------------------------------------
    # TAB 2: 팀장 분석
    # ------------------------------------------------
    with tab2:
        st.write("직급이 '팀장'인 사람을 찾아 심층 분석합니다.")
        # 팀장 찾기
        leaders = df[df['직급'].astype(str).str.contains('팀장|리더|그룹장')]
        
        if len(leaders) == 0:
            st.warning("직급에 '팀장' 또는 '리더'라고 적힌 사람이 없습니다.")
        else:
            leader_name = leaders.iloc[0]['이름']
            leader_data = leaders.iloc[0].to_markdown()

            if st.button(f"'{leader_name}' 팀장 리포트 생성하기"):
                with st.spinner("팀장님의 리더십 스타일을 분석 중입니다..."):
                    sys_prompt = "당신은 리더십 전문 코치입니다. 강점 기반의 리더십 분석 보고서를 작성하세요."
                    user_req = f"""
                    다음 리더의 강점 데이터를 분석해줘.
                    
                    리더 데이터:
                    {leader_data}
                    
                    [출력 양식]
                    1. 강점 테마 5개 요약 표 (순위, 카테고리, 테마명, 특징)
                    2. 업무 중 긍정적으로 발현될 수 있는 모습 (구체적 상황 예시)
                    3. 강점이 약점으로 드러날 경우의 유의점
                    4. 리더를 위한 셀프 코칭 포인트 (Self-Coaching)
                    """
                    result = analyze_data(sys_prompt, user_req, api_key)
                    if result:
                        st.markdown(result)

    # ------------------------------------------------
    # TAB 3: 개별 구성원 분석
    # ------------------------------------------------
    with tab3:
        st.write("구성원 한 명을 선택하여 상세 디브리핑을 생성합니다.")
        
        # 선택 박스
        selected_member = st.selectbox("분석할 팀원을 선택하세요:", df['이름'].unique())
        
        if st.button(f"'{selected_member}' 개인 리포트 생성"):
            # 해당 멤버 데이터만 추출
            member_row = df[df['이름'] == selected_member]
            member_data_str = member_row.to_markdown(index=False)
            
            with st.spinner(f"{selected_member}님을 분석 중입니다..."):
                sys_prompt = """
                당신은 갤럽 강점 코치입니다. 구성원의 강점을 긍정적이고 구체적으로 분석하세요.
                지나친 단정은 피하고, 성장을 위한 피드백을 포함하세요.
                """
                user_req = f"""
                다음 구성원의 강점 데이터를 분석해줘.
                
                구성원 데이터:
                {member_data_str}
                
                [출력 양식]
                1. 강점 테마 5개 요약 표
                2. 업무 중 긍정적으로 발현될 수 있는 모습 (3가지)
                3. 강점이 약점으로 드러날 경우의 유의점 (2가지)
                4. 강점 서머리 (한 줄 정의 및 해석)
                5. 성장을 위한 코칭 포인트
                """
                result = analyze_data(sys_prompt, user_req, api_key)
                if result:
                    st.markdown(result)
