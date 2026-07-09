import streamlit as st
import time
import random

# ==========================
# 初期設定
# ==========================
st.set_page_config(
    page_title="高速学習アプリ",
    layout="wide"
)

LIMIT = 10  # 制限時間（秒）

# ==========================
# 問題データ
# ==========================
QUESTIONS = [
    {
        "question": "日本の首都は？",
        "choices": ["大阪", "東京", "福岡", "札幌"],
        "answer": "東京"
    },
    {
        "question": "5 × 8 = ?",
        "choices": ["30", "35", "40", "45"],
        "answer": "40"
    },
    {
        "question": "水の化学式は？",
        "choices": ["CO2", "H2O", "O2", "NaCl"],
        "answer": "H2O"
    },
    {
        "question": "英語で『犬』は？",
        "choices": ["Cat", "Bird", "Dog", "Fish"],
        "answer": "Dog"
    },
    {
        "question": "100 ÷ 4 = ?",
        "choices": ["20", "25", "30", "40"],
        "answer": "25"
    },
]

# ==========================
# session_state
# ==========================
if "score" not in st.session_state:
    st.session_state.score = 0

if "wrong" not in st.session_state:
    st.session_state.wrong = 0

if "question" not in st.session_state:
    st.session_state.question = random.choice(QUESTIONS)

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

if "answered" not in st.session_state:
    st.session_state.answered = False

# ==========================
# 新しい問題
# ==========================
def next_question():
    st.session_state.question = random.choice(QUESTIONS)
    st.session_state.start_time = time.time()
    st.session_state.answered = False
    st.rerun()

# ==========================
# 残り時間
# ==========================
elapsed = time.time() - st.session_state.start_time
remain = max(0, LIMIT - elapsed)

# 時間切れ
if remain <= 0:
    st.session_state.wrong += 1
    next_question()

# ==========================
# タイトル
# ==========================
st.title("🍣 回転ずし式 学力トレーニング")

col1, col2 = st.columns([3,1])

with col2:
    st.metric("残り時間", f"{remain:.1f} 秒")
    st.metric("正解", st.session_state.score)
    st.metric("不正解", st.session_state.wrong)

with col1:

    q = st.session_state.question

    st.subheader(q["question"])

    answer = st.radio(
        "答えを選んでください",
        q["choices"],
        key="radio"
    )

    if st.button("回答する"):

        if answer == q["answer"]:
            st.success("正解！")
            st.session_state.score += 1
        else:
            st.error(f"不正解（正解：{q['answer']}）")
            st.session_state.wrong += 1

        time.sleep(0.8)
        next_question()

# ==========================
# プログレスバー
# ==========================
progress = remain / LIMIT
st.progress(progress)

# ==========================
# 自動更新
# ==========================
time.sleep(0.2)
st.rerun()