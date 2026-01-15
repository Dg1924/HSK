import streamlit as st
import pandas as pd
import requests
from streamlit_lottie import st_lottie

# ================== CẤU HÌNH TRANG ==================
st.set_page_config(
    page_title="HSK Vocabulary Trainer",
    page_icon="📘",
    layout="centered"
)

# ================== CSS TỐI GIẢN – HIỆN ĐẠI ==================
st.markdown("""
<style>
body {
    background-color: #f7f9fc;
}

.main-card {
    background: #ffffff;
    padding: 32px;
    border-radius: 20px;
    box-shadow: 0 14px 40px rgba(0,0,0,0.08);
    max-width: 720px;
    margin: auto;
}

.app-title {
    text-align: center;
    font-size: 30px;
    font-weight: 700;
    color: #1f3a8a;
    margin-bottom: 6px;
}

.subtitle {
    text-align: center;
    font-size: 15px;
    color: #6b7280;
    margin-bottom: 28px;
}

.meaning-box {
    text-align: center;
    font-size: 26px;
    font-weight: 600;
    color: #111827;
    margin-bottom: 24px;
}

input {
    font-size: 24px !important;
    text-align: center;
    padding: 10px !important;
}

.success-box {
    background: #ecfdf5;
    border-left: 6px solid #10b981;
    padding: 16px;
    border-radius: 14px;
    font-size: 18px;
    animation: fadeIn 0.5s ease-in-out;
}

.error-box {
    background: #fef2f2;
    border-left: 6px solid #ef4444;
    padding: 16px;
    border-radius: 14px;
    font-size: 18px;
    animation: shake 0.4s;
}

.example-box {
    background: #f1f5f9;
    padding: 16px;
    border-radius: 14px;
    margin-top: 14px;
    font-size: 16px;
}

@keyframes fadeIn {
    from {opacity: 0; transform: translateY(8px);}
    to {opacity: 1; transform: translateY(0);}
}

@keyframes shake {
    0% {transform: translateX(0);}
    25% {transform: translateX(-4px);}
    50% {transform: translateX(4px);}
    75% {transform: translateX(-4px);}
    100% {transform: translateX(0);}
}

button[title="View fullscreen"]{
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# ================== LOAD LOTTIE ==================
@st.cache_data
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_success_url = "https://assets10.lottiefiles.com/packages/lf20_yghbqt2z.json"
lottie_success_json = load_lottieurl(lottie_success_url)

# ================== LOAD DATA ==================
@st.cache_data
def load_data(sheet_name):
    try:
        df = pd.read_excel(
            "Tuvung.xlsx",
            sheet_name=sheet_name,
            usecols="B,D,E,G",
            header=0
        )
        df.columns = ['HanTu', 'Nghia', 'ViDu', 'NghiaViDu']
        df = df.dropna(subset=['HanTu'])
        return df
    except Exception as e:
        st.error(f"Lỗi đọc file: {e}")
        return pd.DataFrame()

# ================== SIDEBAR ==================
st.sidebar.markdown("### HSK Level")
hsk_level = st.sidebar.selectbox(
    "",
    ["HSK1", "HSK2", "HSK3", "HSK4", "HSK5", "HSK6"]
)

df = load_data(hsk_level)
if df.empty:
    st.warning("Không tìm thấy dữ liệu.")
    st.stop()

# ================== STATE ==================
if 'current_word' not in st.session_state:
    st.session_state.current_word = None
if 'show_result' not in st.session_state:
    st.session_state.show_result = False
if 'level' not in st.session_state:
    st.session_state.level = hsk_level
if 'input_key' not in st.session_state:
    st.session_state.input_key = 0

if st.session_state.level != hsk_level:
    st.session_state.level = hsk_level
    st.session_state.current_word = None
    st.session_state.show_result = False

def next_word():
    st.session_state.current_word = df.sample(1).iloc[0]
    st.session_state.show_result = False
    st.session_state.input_key += 1

if st.session_state.current_word is None:
    next_word()

# ================== GIAO DIỆN ==================
word = st.session_state.current_word
correct_answer = str(word['HanTu']).strip()
meaning = word['Nghia']
example_sent = word['ViDu'] if pd.notna(word['ViDu']) else ""
example_mean = word['NghiaViDu'] if pd.notna(word['NghiaViDu']) else ""

st.markdown("<div class='main-card'>", unsafe_allow_html=True)

st.markdown("<div class='app-title'>HSK Vocabulary Trainer</div>", unsafe_allow_html=True)
st.markdown(f"<div class='subtitle'>{hsk_level}</div>", unsafe_allow_html=True)

st.markdown(f"<div class='meaning-box'>{meaning}</div>", unsafe_allow_html=True)

with st.form("quiz_form"):
    user_input = st.text_input(
        "Chinese Character",
        key=f"input_{st.session_state.input_key}",
        placeholder="Type here"
    )
    submit_button = st.form_submit_button("Check")

if submit_button:
    st.session_state.show_result = True

# ================== RESULT ==================
if st.session_state.show_result:
    if user_input.strip() == correct_answer:
        col1, col2 = st.columns([1, 3])
        with col1:
            if lottie_success_json:
                st_lottie(lottie_success_json, height=110)
        with col2:
            st.markdown(
                f"<div class='success-box'>Correct answer: <b>{correct_answer}</b></div>",
                unsafe_allow_html=True
            )

        if example_sent:
            st.markdown(f"""
            <div class='example-box'>
                <b>Example</b><br>
                {example_sent}<br>
                <i>{example_mean}</i>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(
            "<div class='error-box'>Incorrect. Please try again.</div>",
            unsafe_allow_html=True
        )

# ================== NEXT ==================
st.write("")
col = st.columns([1, 1, 1])
with col[1]:
    if st.button("Next"):
        next_word()
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
