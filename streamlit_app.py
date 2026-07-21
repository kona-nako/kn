import streamlit as st
import time
import random

st.set_page_config(page_title="高速学習アプリ", layout="wide")

# -------------------------
# モード別のタイマー設定（秒）
# -------------------------
MODE_SETTINGS = {
    "初級モード": {"game_limit": 30, "question_limit": 5},
    "中級モード": {"game_limit": 45, "question_limit": 10},
    "高級モード": {"game_limit": 60, "question_limit": 15},
}

# -------------------------
# 難易度別の問題セット
# -------------------------
QUESTIONS_BEGINNER = [
    {
        "question": "日本の首都は？",
        "choices": ["大阪", "東京", "福岡", "札幌"],
        "answer": "東京"
    },
    {