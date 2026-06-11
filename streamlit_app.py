import streamlit as st
import random

st.title("📚 英単語クイズ")

questions = [
    {"english": "apple", "japanese": "りんご"},
    {"english": "dog", "japanese": "犬"},
    {"english": "book", "japanese": "本"},
]

# 初回のみ問題を選ぶ
if "question" not in st.session_state:
    st.session_state.question = random.choice(questions)

q = st.session_state.question

st.write(f"次の英単語の意味は？")
st.header(q["english"])

answer = st.text_input("答えを入力")

if st.button("答え合わせ"):
    if answer == q["japanese"]:
        st.success("正解！🎉")
    else:
        st.error(f"不正解。正解は「{q['japanese']}」です。")

if st.button("次の問題"):
    st.session_state.question = random.choice(questions)
    st.rerun()