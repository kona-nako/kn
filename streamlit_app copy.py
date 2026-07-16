import streamlit as st
import time
import random

st.set_page_config(page_title="高速学習アプリ", layout="wide")

# -------------------------
# モード別のタイマー設定（秒）
# -------------------------
MODE_SETTINGS = {
    "かんたん": {"game_limit": 30, "question_limit": 5},
    "ふつう": {"game_limit": 45, "question_limit": 10},
    "むずかしい": {"game_limit": 60, "question_limit": 15},
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
    {
        "question": "日本の国旗の色は？",
        "choices": ["赤と白", "青と白", "緑と白", "黄色と白"],
        "answer": "赤と白"
    },
    {
        "question": "1週間は何日？",
        "choices": ["6日", "7日", "8日", "9日"],
        "answer": "7日"
    },
    {
        "question": "英語で『猫』は？",
        "choices": ["Dog", "Cat", "Bird", "Fish"],
        "answer": "Cat"
    },
    {
        "question": "5 + 5 = ?",
        "choices": ["8", "9", "10", "11"],
        "answer": "10"
    },
    {
        "question": "日本の国花は？",
        "choices": ["桜", "バラ", "ひまわり", "チューリップ"],
        "answer": "桜"
    },
    {
        "question": "富士山がある県は？",
        "choices": ["静岡県", "北海道", "沖縄県", "青森県"],
        "answer": "静岡県"
    },
    {
        "question": "1ダースは何個？",
        "choices": ["10個", "12個", "15個", "20個"],
        "answer": "12個"
    },
    {
        "question": "英語で『青』は？",
        "choices": ["Red", "Blue", "Green", "Yellow"],
        "answer": "Blue"
    },
    {
        "question": "10 - 3 = ?",
        "choices": ["6", "7", "8", "9"],
        "answer": "7"
    },
    {
        "question": "日本の国技は？",
        "choices": ["相撲", "柔道", "剣道", "空手"],
        "answer": "相撲"
    },
    {
        "question": "1年で一番暑い季節は？",
        "choices": ["春", "夏", "秋", "冬"],
        "answer": "夏"
    },
    {
        "question": "英語で『ありがとう』は？",
        "choices": ["Sorry", "Please", "Thank you", "Hello"],
        "answer": "Thank you"
    },
    {
        "question": "2 × 6 = ?",
        "choices": ["10", "11", "12", "13"],
        "answer": "12"
    },
    {
        "question": "バナナの色は？",
        "choices": ["黄色", "赤", "青", "紫"],
        "answer": "黄色"
    },
    {
        "question": "日本の通貨単位は？",
        "choices": ["円", "ドル", "ユーロ", "ウォン"],
        "answer": "円"
    },
    {
        "question": "1時間は何分？",
        "choices": ["50分", "60分", "70分", "80分"],
        "answer": "60分"
    },
    {
        "question": "英語で『学校』は？",
        "choices": ["House", "School", "Park", "Store"],
        "answer": "School"
    },
    {
        "question": "9 + 8 = ?",
        "choices": ["15", "16", "17", "18"],
        "answer": "17"
    },
    {
        "question": "海の水はどんな味？",
        "choices": ["甘い", "しょっぱい", "苦い", "酸っぱい"],
        "answer": "しょっぱい"
    },
    {
        "question": "日本で一番高い山は？",
        "choices": ["富士山", "浅間山", "槍ヶ岳", "白山"],
        "answer": "富士山"
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
    {
        "question": "12 × 12 = ?",
        "choices": ["122", "132", "144", "154"],
        "answer": "144"
    },
    {
        "question": "日本国憲法が施行されたのは何年？",
        "choices": ["1945年", "1946年", "1947年", "1950年"],
        "answer": "1947年"
    },
    {
        "question": "英語で『重要な』は？",
        "choices": ["Important", "Interesting", "Impossible", "Immediate"],
        "answer": "Important"
    },
    {
        "question": "三角形の内角の和は？",
        "choices": ["90度", "180度", "270度", "360度"],
        "answer": "180度"
    },
    {
        "question": "光の速さは秒速約何km？",
        "choices": ["3万km", "30万km", "300万km", "3000万km"],
        "answer": "30万km"
    },
    {
        "question": "日本で一番長い川は？",
        "choices": ["信濃川", "利根川", "石狩川", "淀川"],
        "answer": "信濃川"
    },
    {
        "question": "7の倍数はどれ？",
        "choices": ["21", "22", "23", "24"],
        "answer": "21"
    },
    {
        "question": "英語で『決定する』は？",
        "choices": ["Decide", "Design", "Desire", "Deny"],
        "answer": "Decide"
    },
    {
        "question": "平方根の記号は？",
        "choices": ["√", "∑", "∫", "π"],
        "answer": "√"
    },
    {
        "question": "江戸幕府を開いたのは？",
        "choices": ["徳川家康", "織田信長", "豊臣秀吉", "源頼朝"],
        "answer": "徳川家康"
    },
    {
        "question": "200 ÷ 5 = ?",
        "choices": ["30", "35", "40", "45"],
        "answer": "40"
    },
    {
        "question": "英語で『経済』は？",
        "choices": ["Economy", "Ecology", "Energy", "Equity"],
        "answer": "Economy"
    },
    {
        "question": "DNAの二重らせん構造を発見したのは？",
        "choices": ["ワトソンとクリック", "アインシュタイン", "ダーウィン", "メンデル"],
        "answer": "ワトソンとクリック"
    },
    {
        "question": "日本の内閣総理大臣を選ぶのは？",
        "choices": ["国会", "天皇", "最高裁判所", "国民投票"],
        "answer": "国会"
    },
    {
        "question": "15%の割引で1000円の商品はいくら？",
        "choices": ["750円", "800円", "850円", "900円"],
        "answer": "850円"
    },
    {
        "question": "英語で『環境』は？",
        "choices": ["Environment", "Equipment", "Enrollment", "Experiment"],
        "answer": "Environment"
    },
    {
        "question": "世界で一番大きい大陸は？",
        "choices": ["アジア", "アフリカ", "北アメリカ", "ヨーロッパ"],
        "answer": "アジア"
    },
    {
        "question": "二進法で10は10進法でいくつ？",
        "choices": ["1", "2", "3", "4"],
        "answer": "2"
    },
    {
        "question": "日本の三権分立の三権は？",
        "choices": ["立法・行政・司法", "経済・政治・文化", "教育・医療・農業", "内閣・国会・裁判所"],
        "answer": "立法・行政・司法"
    },
    {
        "question": "英語で『比較する』は？",
        "choices": ["Compare", "Compete", "Complete", "Compose"],
        "answer": "Compare"
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
    {
        "question": "微分方程式 dy/dx = y の一般解は？",
        "choices": ["y=Ce^x", "y=Cx", "y=Csin(x)", "y=C/x"],
        "answer": "y=Ce^x"
    },
    {
        "question": "相対性理論を提唱したのは？",
        "choices": ["アインシュタイン", "ニュートン", "ボーア", "ハイゼンベルク"],
        "answer": "アインシュタイン"
    },
    {
        "question": "英語で『にもかかわらず』は？",
        "choices": ["Nevertheless", "Furthermore", "Therefore", "Meanwhile"],
        "answer": "Nevertheless"
    },
    {
        "question": "明治時代に制定された憲法は？",
        "choices": ["大日本帝国憲法", "日本国憲法", "五箇条の御誓文", "教育勅語"],
        "answer": "大日本帝国憲法"
    },
    {
        "question": "log₁₀100 = ?",
        "choices": ["1", "2", "3", "10"],
        "answer": "2"
    },
    {
        "question": "DNAを構成する塩基は何種類？",
        "choices": ["2種類", "3種類", "4種類", "5種類"],
        "answer": "4種類"
    },
    {
        "question": "世界恐慌が始まったのは何年？",
        "choices": ["1919年", "1929年", "1939年", "1949年"],
        "answer": "1929年"
    },
    {
        "question": "英語で『必然的な』は？",
        "choices": ["Inevitable", "Invisible", "Incredible", "Indefinite"],
        "answer": "Inevitable"
    },
    {
        "question": "二次関数 y=x²-4x+3 の頂点の座標は？",
        "choices": ["(2,-1)", "(1,-1)", "(2,1)", "(-2,-1)"],
        "answer": "(2,-1)"
    },
    {
        "question": "産業革命が起こった国は？",
        "choices": ["イギリス", "フランス", "ドイツ", "アメリカ"],
        "answer": "イギリス"
    },
    {
        "question": "化学式C6H12O6が表す物質は？",
        "choices": ["グルコース", "エタノール", "酢酸", "メタン"],
        "answer": "グルコース"
    },
    {
        "question": "英語で『持続可能な』は？",
        "choices": ["Sustainable", "Suspicious", "Substantial", "Subsequent"],
        "answer": "Sustainable"
    },
    {
        "question": "三権分立を提唱した思想家は？",
        "choices": ["モンテスキュー", "ルソー", "ロック", "ヴォルテール"],
        "answer": "モンテスキュー"
    },
    {
        "question": "積分∫x dx の答えは？",
        "choices": ["x²/2 + C", "x²+C", "2x+C", "x+C"],
        "answer": "x²/2 + C"
    },
    {
        "question": "冷戦の対立構造は？",
        "choices": ["アメリカとソ連", "日本と中国", "イギリスとフランス", "ドイツとイタリア"],
        "answer": "アメリカとソ連"
    },
    {
        "question": "英語で『矛盾』は？",
        "choices": ["Contradiction", "Contribution", "Construction", "Continuation"],
        "answer": "Contradiction"
    },
    {
        "question": "オームの法則の式は？",
        "choices": ["V=IR", "V=I/R", "V=I+R", "V=IR²"],
        "answer": "V=IR"
    },
    {
        "question": "平安時代に書かれた作品は？",
        "choices": ["源氏物語", "万葉集", "古事記", "日本書紀"],
        "answer": "源氏物語"
    },
    {
        "question": "英語で『独立した』は？",
        "choices": ["Independent", "Interdependent", "Indifferent", "Intelligent"],
        "answer": "Independent"
    },
    {
        "question": "三角関数でsin30°の値は？",
        "choices": ["1/2", "√2/2", "√3/2", "1"],
        "answer": "1/2"
    },
]

MODE_QUESTIONS = {
    "かんたん": QUESTIONS_BEGINNER,
    "ふつう": QUESTIONS_INTERMEDIATE,
    "むずかしい": QUESTIONS_ADVANCED,
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
    st.session_state.mode = "かんたん"

if "selected_mode" not in st.session_state:
    st.session_state.selected_mode = "かんたん"

if "remaining_questions" not in st.session_state:
    st.session_state.remaining_questions = []

# -------------------------
# 問題を1問取り出す（出題済みは山が尽きるまで出さない）
# -------------------------
def draw_question(mode_name):
    if not st.session_state.remaining_questions:
        pool = MODE_QUESTIONS[mode_name][:]
        random.shuffle(pool)
        st.session_state.remaining_questions = pool
    return st.session_state.remaining_questions.pop()

# -------------------------
# スタート前画面
# -------------------------
if not st.session_state.started:

    st.title("高速学習アプリ")

    st.markdown("### モードを選んでね")

    # 各モードボタンの塗りつぶし色・文字色・選択中の枠線を動的に生成
    mode_colors = {
        "かんたん": "#2ecc71",   # 緑
        "ふつう": "#f1c40f",   # 黄
        "むずかしい": "#e74c3c",   # 赤
    }
    mode_text_colors = {
        "かんたん": "#ffffff",
        "ふつう": "#3d3400",
        "むずかしい": "#ffffff",
    }
    mode_keys = {
        "かんたん": "mode_container_beginner",
        "ふつう": "mode_container_intermediate",
        "むずかしい": "mode_container_advanced",
    }

    button_css = "<style>"
    for m_name, m_key in mode_keys.items():
        button_css += f"""
        .st-key-{m_key} {{
            background-color: {mode_colors[m_name]};
            border-radius: 20px;
            padding: 32px 16px 36px 16px;
            display: flex;
            flex-direction: column;
            align-items: stretch;
            min-height: 260px;
            justify-content: center;
        }}
        .st-key-{m_key} div[data-testid="stButton"] button {{
            width: 100%;
            background-color: transparent;
            border: none;
            box-shadow: none;
            font-size: 2.6rem;
            font-weight: 900;
            letter-spacing: 0.05em;
            color: {mode_text_colors[m_name]};
            white-space: normal;
            word-break: break-word;
            padding: 8px 0;
            line-height: 1.3;
        }}
        .st-key-{m_key} div[data-testid="stButton"] button p {{
            font-size: 2.6rem;
            font-weight: 900;
        }}
        .st-key-{m_key} div[data-testid="stButton"] button:hover {{
            background-color: rgba(255, 255, 255, 0.15);
            color: {mode_text_colors[m_name]};
        }}
        .st-key-{m_key} .mode-info {{
            font-size: 1.15rem;
            font-weight: 400;
            color: {mode_text_colors[m_name]};
            text-align: center;
            line-height: 1.5;
            margin-top: 8px;
        }}
        """
    button_css += "</style>"
    st.markdown(button_css, unsafe_allow_html=True)

    def start_game(mode_name):
        st.session_state.mode = mode_name
        st.session_state.game_limit = MODE_SETTINGS[mode_name]["game_limit"]
        st.session_state.question_limit = MODE_SETTINGS[mode_name]["question_limit"]
        # 出題プールをシャッフルして作り直す（＝出題済みは尽きるまで出さない）
        pool = MODE_QUESTIONS[mode_name][:]
        random.shuffle(pool)
        st.session_state.remaining_questions = pool
        st.session_state.question = draw_question(mode_name)
        st.session_state.started = True
        st.session_state.game_start = time.time()
        st.session_state.question_start = time.time()
        st.rerun()

    btn_col1, btn_col2, btn_col3 = st.columns(3)
    btn_cols = {"かんたん": btn_col1, "ふつう": btn_col2, "むずかしい": btn_col3}

    for m_name, m_key in mode_keys.items():
        with btn_cols[m_name]:
            with st.container(key=m_key):
                settings = MODE_SETTINGS[m_name]
                if st.button(
                    m_name,
                    key=f"{m_key}_btn",
                    use_container_width=True,
                ):
                    start_game(m_name)

                st.markdown(
                    f"""
                    <div class="mode-info">
                        制限時間：{settings['game_limit']}秒<br>
                        1問：{settings['question_limit']}秒以内
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

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
    st.session_state.question = draw_question(st.session_state.mode)
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