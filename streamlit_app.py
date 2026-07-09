import streamlit as st
import time
import random

st.set_page_config(page_title="高速学習アプリ", layout="wide")

GAME_LIMIT = 30      # ゲーム全体（秒）
QUESTION_LIMIT = 5   # 1問（秒）

# -------------------------
# 問題
# -------------------------
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

# -------------------------
# 初期化
# -------------------------
if "game_start" not in st.session_state:
    st.session_state.game_start = time.time()

if "question_start" not in st.session_state:
    st.session_state.question_start = time.time()

if "score" not in st.session_state:
    st.session_state.score = 0

if "wrong" not in st.session_state:
    st.session_state.wrong = 0

if "question" not in st.session_state:
    st.session_state.question = random.choice(QUESTIONS)

if "radio_index" not in st.session_state:
    st.session_state.radio_index = 0


# -------------------------
# 次の問題
# -------------------------
def next_question():
    st.session_state.question = random.choice(QUESTIONS)
    st.session_state.question_start = time.time()
    st.session_state.radio_index += 1
    st.rerun()


# -------------------------
# タイマー計算
# -------------------------
game_elapsed = time.time() - st.session_state.game_start
question_elapsed = time.time() - st.session_state.question_start

game_remaining = max(0, GAME_LIMIT - game_elapsed)
question_remaining = max(0, QUESTION_LIMIT - question_elapsed)

# -------------------------
# ゲーム終了
# -------------------------
if game_remaining <= 0:

    st.title("🎉 ゲーム終了")

    st.success(f"正解：{st.session_state.score}")
    st.error(f"不正解：{st.session_state.wrong}")

    if st.button("もう一度遊ぶ"):

        for k in list(st.session_state.keys()):
            del st.session_state[k]

        st.rerun()

    st.stop()

# -------------------------
# 問題タイムアウト
# -------------------------
if question_remaining <= 0:
    st.session_state.wrong += 1
    next_question()

# -------------------------
# 画面
# -------------------------
st.title("高速学習アプリ")

col1, col2 = st.columns([3,1])

with col2:

    st.metric("ゲーム残り", f"{game_remaining:.1f} 秒")
    st.progress(game_remaining / GAME_LIMIT)

    st.metric("問題残り", f"{question_remaining:.1f} 秒")
    st.progress(question_remaining / QUESTION_LIMIT)

    st.metric("正解", st.session_state.score)
    st.metric("不正解", st.session_state.wrong)

with col1:

    q = st.session_state.question

    st.subheader(q["question"])

    answer = st.radio(
        "選択してください",
        q["choices"],
        key=f"radio_{st.session_state.radio_index}"
    )

    if st.button("回答"):

        if answer == q["answer"]:
            st.session_state.score += 1
            st.success("正解！")
        else:
            st.session_state.wrong += 1
            st.error(f"不正解！（正解：{q['answer']}）")

        time.sleep(0.5)
        next_question()

# -------------------------
# 自動更新
# -------------------------
time.sleep(0.2)
st.rerun()