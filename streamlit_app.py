import streamlit as st
import time
import random

st.set_page_config(page_title="高速学習アプリ", layout="wide")

GAME_LIMIT = 30
QUESTION_LIMIT = 5

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
if "started" not in st.session_state:
    st.session_state.started = False

if "score" not in st.session_state:
    st.session_state.score = 0

if "wrong" not in st.session_state:
    st.session_state.wrong = 0

if "question" not in st.session_state:
    st.session_state.question = random.choice(QUESTIONS)

if "radio_id" not in st.session_state:
    st.session_state.radio_id = 0

# -------------------------
# スタート前画面
# -------------------------
if not st.session_state.started:

    st.title("🍣 高速学習アプリ")

    st.markdown("## 制限時間：30秒")
    st.markdown("### 1問5秒以内に答えよう！")

    if st.button("▶ スタート！", use_container_width=True):

        st.session_state.started = True
        st.session_state.game_start = time.time()
        st.session_state.question_start = time.time()
        st.rerun()

    st.stop()

# -------------------------
# タイマー
# -------------------------
game_elapsed = time.time() - st.session_state.game_start
question_elapsed = time.time() - st.session_state.question_start

game_remaining = max(0, GAME_LIMIT - int(game_elapsed))
question_remaining = max(0, QUESTION_LIMIT - int(question_elapsed))

# -------------------------
# 次の問題
# -------------------------
def next_question():
    st.session_state.question = random.choice(QUESTIONS)
    st.session_state.question_start = time.time()
    st.session_state.radio_id += 1
    st.rerun()

# -------------------------
# ゲーム終了
# -------------------------
if game_elapsed >= GAME_LIMIT:

    st.title("🎉 ゲーム終了")

    st.success(f"正解：{st.session_state.score}")
    st.error(f"不正解：{st.session_state.wrong}")

    if st.button("もう一度遊ぶ"):

        for key in list(st.session_state.keys()):
            del st.session_state[key]

        st.rerun()

    st.stop()

# -------------------------
# 問題時間終了
# -------------------------
if question_elapsed >= QUESTION_LIMIT:
    st.session_state.wrong += 1
    next_question()

# -------------------------
# 上部タイマー
# -------------------------
st.title("🍣 高速学習アプリ")

# ゲームタイマー
st.metric("⏰ ゲーム残り時間", f"{game_remaining} 秒")
st.progress(game_remaining / GAME_LIMIT)

# 少し余白
st.write("")

# 問題タイマー
st.metric("⌛ この問題の残り時間", f"{question_remaining} 秒")
st.progress(question_remaining / QUESTION_LIMIT)

st.write("")

# 正解・不正解
col1, col2 = st.columns(2)

with col1:
    st.metric("⭕ 正解", st.session_state.score)

with col2:
    st.metric("❌ 不正解", st.session_state.wrong)

st.divider()

# -------------------------
# 問題表示
# -------------------------
q = st.session_state.question

st.subheader(q["question"])

answer = st.radio(
    "答えを選んでください",
    q["choices"],
    key=f"radio_{st.session_state.radio_id}"
)

if st.button("回答", use_container_width=True):

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