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
        "choices": ["Therefore", "However", "Moreover", "Because"],
        "answer": "However"
    },
    {
        "question": "円の面積を求める公式は？",
        "choices": ["πr", "2πr", "πr²", "πd"],
        "answer": "πr²"
    },
]

MODE_QUESTIONS = {
    "初級モード": QUESTIONS_BEGINNER,
    "中級モード": QUESTIONS_INTERMEDIATE,
    "高級モード": QUESTIONS_ADVANCED,
}

# -------------------------
# 右端固定タイマー用CSS
# -------------------------
st.markdown(
    """
    <style>
    .fixed-timer-panel {
        position: fixed;
        top: 100px;
        right: 20px;
        width: 220px;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 16px;
    }
    .timer-box {
        background-color: rgba(38, 39, 48, 0.9);
        border: 1px solid rgba(250, 250, 250, 0.2);
        border-radius: 8px;
        padding: 12px 16px;
    }
    .timer-label {
        font-size: 0.9rem;
        color: rgba(250, 250, 250, 0.7);
        margin-bottom: 4px;
    }
    .timer-value {
        font-size: 1.8rem;
        font-weight: 600;
        color: #fafafa;
        margin-bottom: 8px;
    }
    .timer-progress-track {
        width: 100%;
        height: 8px;
        background-color: rgba(250, 250, 250, 0.2);
        border-radius: 4px;
        overflow: hidden;
    }
    .timer-progress-fill {
        height: 100%;
        border-radius: 4px;
        background-color: #ff4b4b;
        transition: width 0.2s linear;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# 初期化
# -------------------------
if "started" not in st.session_state:
    st.session_state.started = False

if "score" not in st.session_state:
    st.session_state.score = 0

if "wrong" not in st.session_state:
    st.session_state.wrong = 0

if "radio_id" not in st.session_state:
    st.session_state.radio_id = 0

if "mode" not in st.session_state:
    st.session_state.mode = "初級モード"

if "selected_mode" not in st.session_state:
    st.session_state.selected_mode = "初級モード"

# -------------------------
# スタート前画面
# -------------------------
if not st.session_state.started:

    st.title("🍣 高速学習アプリ")

    st.markdown("### モードを選んでね")

    # 各モードボタンの塗りつぶし色と、選択中を示す枠線を動的に生成
    mode_colors = {
        "初級モード": "#2ecc71",   # 緑
        "中級モード": "#f1c40f",   # 黄
        "高級モード": "#e74c3c",   # 赤
    }
    mode_text_colors = {
        "初級モード": "#ffffff",
        "中級モード": "#3d3400",
        "高級モード": "#ffffff",
    }
    mode_keys = {
        "初級モード": "mode_container_beginner",
        "中級モード": "mode_container_intermediate",
        "高級モード": "mode_container_advanced",
    }

    button_css = "<style>"
    for m_name, m_key in mode_keys.items():
        is_selected = st.session_state.selected_mode == m_name
        border_style = "5px solid #ffffff" if is_selected else "5px solid transparent"
        button_css += f"""
        .st-key-{m_key} div[data-testid="stButton"] button {{
            height: 160px;
            width: 100%;
            font-size: 1.6rem;
            font-weight: 700;
            border-radius: 16px;
            white-space: normal;
            background-color: {mode_colors[m_name]};
            color: {mode_text_colors[m_name]};
            border: {border_style};
        }}
        .st-key-{m_key} div[data-testid="stButton"] button:hover {{
            background-color: {mode_colors[m_name]};
            color: {mode_text_colors[m_name]};
            opacity: 0.85;
        }}
        """
    button_css += "</style>"
    st.markdown(button_css, unsafe_allow_html=True)

    btn_col1, btn_col2, btn_col3 = st.columns(3)

    with btn_col1:
        with st.container(key=mode_keys["初級モード"]):
            if st.button("🟢\n初級モード", key="mode_btn_beginner", use_container_width=True):
                st.session_state.selected_mode = "初級モード"
                st.rerun()

    with btn_col2:
        with st.container(key=mode_keys["中級モード"]):
            if st.button("🟡\n中級モード", key="mode_btn_intermediate", use_container_width=True):
                st.session_state.selected_mode = "中級モード"
                st.rerun()

    with btn_col3:
        with st.container(key=mode_keys["高級モード"]):
            if st.button("🔴\n高級モード", key="mode_btn_advanced", use_container_width=True):
                st.session_state.selected_mode = "高級モード"
                st.rerun()

    selected_mode = st.session_state.selected_mode
    selected_settings = MODE_SETTINGS[selected_mode]
    st.markdown(f"## 制限時間：{selected_settings['game_limit']}秒")
    st.markdown(f"### 1問{selected_settings['question_limit']}秒以内に答えよう！")

    if st.button("▶ スタート！", use_container_width=True):

        st.session_state.mode = selected_mode
        st.session_state.game_limit = MODE_SETTINGS[selected_mode]["game_limit"]
        st.session_state.question_limit = MODE_SETTINGS[selected_mode]["question_limit"]
        st.session_state.question = random.choice(MODE_QUESTIONS[selected_mode])
        st.session_state.started = True
        st.session_state.game_start = time.time()
        st.session_state.question_start = time.time()
        st.rerun()

    st.stop()

# -------------------------
# 現在のモードの問題セット
# -------------------------
current_questions = MODE_QUESTIONS[st.session_state.mode]

# -------------------------
# タイマー
# -------------------------
game_elapsed = time.time() - st.session_state.game_start
question_elapsed = time.time() - st.session_state.question_start

game_limit = st.session_state.game_limit
question_limit = st.session_state.question_limit

game_remaining = max(0, game_limit - int(game_elapsed))
question_remaining = max(0, question_limit - int(question_elapsed))

game_pct = int((game_remaining / game_limit) * 100)
question_pct = int((question_remaining / question_limit) * 100)

# -------------------------
# 次の問題
# -------------------------
def next_question():
    st.session_state.question = random.choice(current_questions)
    st.session_state.question_start = time.time()
    st.session_state.radio_id += 1
    st.rerun()

# -------------------------
# ゲーム終了
# -------------------------
if game_elapsed >= game_limit:

    st.title("🎉 ゲーム終了")

    st.markdown(f"#### モード：{st.session_state.mode}")
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
if question_elapsed >= question_limit:
    st.session_state.wrong += 1
    next_question()

# -------------------------
# 右端固定タイマー・スコアパネル（縦並び）
# -------------------------
st.markdown(
    f"""
    <div class="fixed-timer-panel">
        <div class="timer-box">
            <div class="timer-label">⏰ ゲーム残り時間</div>
            <div class="timer-value">{game_remaining} 秒</div>
            <div class="timer-progress-track">
                <div class="timer-progress-fill" style="width: {game_pct}%;"></div>
            </div>
        </div>
        <div class="timer-box">
            <div class="timer-label">⌛ この問題の残り時間</div>
            <div class="timer-value">{question_remaining} 秒</div>
            <div class="timer-progress-track">
                <div class="timer-progress-fill" style="width: {question_pct}%;"></div>
            </div>
        </div>
        <div class="timer-box">
            <div class="timer-label">⭕ 正解</div>
            <div class="timer-value">{st.session_state.score}</div>
        </div>
        <div class="timer-box">
            <div class="timer-label">❌ 不正解</div>
            <div class="timer-value">{st.session_state.wrong}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# 上部タイトル
# -------------------------
st.title("🍣 高速学習アプリ")
st.caption(f"モード：{st.session_state.mode}")

st.write("")

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