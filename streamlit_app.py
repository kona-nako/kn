import streamlit as st
import random

st.title("✊✋✌️ じゃんけんゲーム")

# 手の一覧
hands = ["グー", "チョキ", "パー"]

# ユーザーの手を選択
user_hand = st.radio(
    "あなたの手を選んでください",
    hands
)

# 勝負ボタン
if st.button("じゃんけん！"):
    computer_hand = random.choice(hands)

    st.write(f"あなた: {user_hand}")
    st.write(f"コンピュータ: {computer_hand}")

    # 勝敗判定
    if user_hand == computer_hand:
        result = "あいこです！"
    elif (
        (user_hand == "グー" and computer_hand == "チョキ")
        or (user_hand == "チョキ" and computer_hand == "パー")
        or (user_hand == "パー" and computer_hand == "グー")
    ):
        result = "あなたの勝ち！🎉"
    else:
        result = "コンピュータの勝ち！🤖"

    st.success(result)