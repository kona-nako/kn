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
        "question": "3 + 4 = ?",
        "choices": ["6", "7", "8", "9"],
        "answer": "7"
    },
    {
        "question": "英語で『犬』は？",
        "choices": ["Cat", "Bird", "Dog", "Fish"],
        "answer": "Dog"
    },
    {
        "question": "1年は何ヶ月？",
        "choices": ["10ヶ月", "11ヶ月", "12ヶ月", "13ヶ月"],
        "answer": "12ヶ月"
    },
    {
        "question": "りんごの色は？",
        "choices": ["青", "赤", "紫", "黒"],
        "answer": "赤"
    },
]

QUESTIONS_INTERMEDIATE = [
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
        "question": "100 ÷ 4 = ?",
        "choices": ["20", "25", "30", "40"],
        "answer": "25"
    },
    {
        "question": "明治維新が起きたのは何世紀？",
        "choices": ["17世紀", "18世紀", "19世紀", "20世紀"],
        "answer": "19世紀"
    },
    {
        "question": "英語で『速い』は？",
        "choices": ["Slow", "Fast", "Quiet", "Heavy"],
        "answer": "Fast"
    },
]

QUESTIONS_ADVANCED = [
    {
        "question": "二次方程式 x² - 5x + 6 = 0 の解は？",
        "choices": ["x=1,4", "x=2,3", "x=-2,-3", "x=1,6"],
        "answer": "x=2,3"
    },
    {
        "question": "光合成で使われる気体は？",
        "choices": ["酸素", "窒素", "二酸化炭素", "水素"],
        "answer": "二酸化炭素"
    },
    {
        "question": "フランス革命が始まったのは何年？",
        "choices": ["1689年", "1776年", "1789年", "1804年"],
        "answer": "1789年"
    },
    {
        "question": "英語で『しかしながら』は？",