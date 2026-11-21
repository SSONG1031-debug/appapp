import streamlit as st
from openai import OpenAI
import random
import re
import difflib

# ==========================================
# 1. OpenAI API 키 직접 입력
# ==========================================
OPENAI_API_KEY = "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"
client = OpenAI(api_key=OPENAI_API_KEY)

# ==========================================
# 2. 초등학교 6학년 수준 영어 문장 리스트
# ==========================================
SENTENCES = [
    "I went to the park with my friends yesterday.",
    "What are you going to do this weekend?",
    "She is taller than her younger brother.",
    "How often do you brush your teeth?",
    "I have a headache and a runny nose.",
    "Can you tell me how to get to the museum?",
    "Go straight two blocks and turn left.",
    "My favorite season is autumn because the weather is cool.",
    "I want to be a scientist in the future.",
    "Whose umbrella is this on the desk?",
    "We should save water and recycle paper.",
    "Did you enjoy your summer vacation in Busan?",
    "I usually wake up at seven thirty in the morning.",
    "Why are you so excited about the school trip?",
    "Let's meet in front of the library at three o'clock."
]

# ==========================================
# 3. 텍스트 정규화 및 단어 비교 함수
# ==========================================
def clean_word(word):
    """비교를 위해 소문자로 바꾸고 문장부호를 제거합니다."""
    return re.sub(r"[^\w']", "", word.lower())

def evaluate_pronunciation(target_sentence, spoken_text):
    """목표 문장과 인식된 음성을 단어 단위로 비교해 HTML과 정확도를 반환합니다."""
    target_words_orig = target_sentence.split()
    target_words_clean = [clean_word(w) for w in target_words_orig]
    spoken_words_clean = [clean_word(w) for w in spoken_text.split()]

    # SequenceMatcher로 단어 순서가 밀려도 정확하게 매칭
    matcher = difflib.SequenceMatcher(None, target_words_clean, spoken_words_clean)
    
    colored_words = []
    correct_count = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for i in range(i1, i2):
                colored_words.append(
                    f"<span style='color: #1E88E5; font-weight: bold;'>{target_words_orig[i]}</span>"
                )
                correct_count += 1
        elif tag in ("replace", "delete"):
            for i in range(i1, i2):
                colored_words.append(
                    f"<span style='color: #E53935; font-weight: bold; text-decoration: underline;'>{target_words_orig[i]}</span>"
                )

    accuracy = int((correct_count / len(target_words_orig)) * 100) if target_words_orig else 0
    result_html = " ".join(colored_words)
    return result_html, accuracy

# ==========================================
# 4. Streamlit 웹앱 UI 구성
# ==========================================
st.set_page_config(page_title="영어 말하기 평가", page_icon="🎙️", layout="centered")

st.title("🎙️ 초등 6학년 영어 말하기 평가")
st.write("제시된 문장을 보고 마이크 버튼을 눌러 또박또박 읽어보세요.")

# 세션 상태 초기화 (현재 문장 유지용)
if "current_sentence" not in st.session_state:
    st.session_state.current_sentence = random.choice(SENTENCES)
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0

# 새 문장 뽑기 버튼
if st.button("🔄 새로운 문장 뽑기", use_container_width=True):
    new_sentence = random.choice(SENTENCES)
    while new_sentence == st.session_state.current_sentence and len(SENTENCES) > 1:
        new_sentence = random.choice(SENTENCES)
    st.session_state.current_sentence = new_sentence
    st.session_state.audio_key += 1  # 녹음기 초기화
    st.rerun()

# 제시 문장 출력 박스
st.markdown(
    f"""
    <div style="
        background-color: #F0F2F6;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        font-size: 26px;
        font-weight: bold;
        color: #262730;
        margin: 15px 0;
    ">
        {st.session_state.current_sentence}
    </div>
    """,
    unsafe_allow_html=True
)

# 마이크 녹음 위젯
audio_value = st.audio_input(
    "마이크를 누르고 문장을 읽은 뒤, 정지 버튼을 눌러주세요.",
    key=f"audio_{st.session_state.audio_key}"
)

# 녹음이 완료되면 OpenAI API로 음성 인식 및 평가 수행
if audio_value is not None:
    if OPENAI_API_KEY == "여기에_본인의_OPENAI_API_KEY를_입력하세요" or not OPENAI_API_KEY:
        st.error("코드 상단의 `OPENAI_API_KEY` 변수에 실제 API 키를 입력해주세요.")
    else:
        with st.spinner("발음을 분석하고 있습니다..."):
            try:
                # OpenAI Whisper API 호출 (영어 인식 고정)
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=("student_audio.wav", audio_value.getvalue(), "audio/wav"),
                    language="en"
                )
                spoken_text = transcription.text.strip()

                # 발음 평가 및 색상 적용
                result_html, accuracy = evaluate_pronunciation(
                    st.session_state.current_sentence, spoken_text
                )

                st.divider()
                st.subheader("📊 평가 결과")

                # 색상 표시된 문장 출력
                st.markdown(
                    f"""
                    <div style="
                        background-color: #FFFFFF;
                        border: 2px solid #E0E0E0;
                        padding: 20px;
                        border-radius: 12px;
                        text-align: center;
                        font-size: 26px;
                        margin-bottom: 15px;
                    ">
                        {result_html}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # 정확도 및 피드백
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric("정확도", f"{accuracy}%")
                with col2:
                    if accuracy == 100:
                        st.success("완벽해요! 모든 단어를 정확하게 발음했습니다.")
                    elif accuracy >= 70:
                        st.info("잘했어요! 빨간색으로 표시된 단어를 한 번 더 연습해 보세요.")
                    else:
                        st.warning("조금 더 천천히, 또박또박 다시 읽어볼까요?")

                # AI가 실제로 들은 문장 참고용 표시
                with st.expander("🔍 AI가 인식한 내 발음 보기"):
                    st.write(f"**인식된 문장:** {spoken_text}")

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
