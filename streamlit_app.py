import streamlit as st
import random


# =========================
# 基本設定
# =========================

st.set_page_config(
    page_title="Study Escape",
    page_icon="🗝️",
    layout="centered"
)


# =========================
# 問題データ
# =========================

stages = {

    "🏫 学校": [
        {
            "question": "5×8はいくつ？",
            "answer": "40",
            "hint": "九九を使います"
        },
        {
            "question": "『走る』の英単語は？",
            "answer": "run",
            "hint": "Rから始まります"
        },
        {
            "question": "日本の首都は？",
            "answer": "東京",
            "hint": "人口が最も多い都市です"
        }
    ],


    "🏰 古城": [
        {
            "question": "x+5=10 のxはいくつ？",
            "answer": "5",
            "hint": "5を移項します"
        },
        {
            "question": "太陽系で地球の隣の惑星は？",
            "answer": "火星",
            "hint": "赤い惑星です"
        },
        {
            "question": "英語で猫は？",
            "answer": "cat",
            "hint": "Cから始まります"
        }
    ],


    "🚀 宇宙船": [
        {
            "question": "水の化学式は？",
            "answer": "H2O",
            "hint": "水素と酸素からできます"
        },
        {
            "question": "江戸幕府を開いた人物は？",
            "answer": "徳川家康",
            "hint": "1603年に幕府を開きました"
        },
        {
            "question": "9×9はいくつ？",
            "answer": "81",
            "hint": "九九の最後です"
        }
    ]

}


# =========================
# セッション管理
# =========================

if "stage_index" not in st.session_state:
    st.session_state.stage_index = 0

if "question_index" not in st.session_state:
    st.session_state.question_index = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "started" not in st.session_state:
    st.session_state.started = False



stage_names = list(stages.keys())


# =========================
# タイトル
# =========================

st.title("🗝️ Study Escape")
st.subheader("知識で扉を開ける学習脱出ゲーム")


# =========================
# スタート画面
# =========================

if not st.session_state.started:

    st.write(
        """
        あなたは謎の施設に閉じ込められた。

        脱出するには、
        各部屋に隠された知識の試練を突破しなければならない。

        正しい答えを導き、出口を目指そう。
        """
    )


    if st.button("冒険開始"):

        st.session_state.started = True
        st.rerun()



# =========================
# ゲーム画面
# =========================

else:


    # 全クリア判定

    if st.session_state.stage_index >= len(stage_names):

        st.success("🎉 脱出成功！")

        st.write(
            f"""
            おめでとうございます。

            あなたの結果：

            正解数：
            {st.session_state.score} 問

            知識の迷宮から脱出しました！
            """
        )

        if st.button("もう一度挑戦"):

            st.session_state.clear()
            st.rerun()


    else:


        current_stage = stage_names[
            st.session_state.stage_index
        ]


        questions = stages[current_stage]


        current_question = questions[
            st.session_state.question_index
        ]


        # ステージ表示

        st.header(current_stage)


        st.progress(
            (st.session_state.question_index)
            /
            len(questions)
        )


        st.write(
            "出口を開くために問題を解こう"
        )


        # 問題

        st.subheader(
            current_question["question"]
        )


        answer = st.text_input(
            "答えを入力してください"
        )


        # ヒント

        if st.button("💡 ヒント"):

            st.info(
                current_question["hint"]
            )



        # 回答

        if st.button("🔓 回答する"):


            if answer.strip().lower() == \
               current_question["answer"].lower():


                st.success(
                    "正解！扉が開いた！"
                )


                st.session_state.score += 1


                st.session_state.question_index += 1


                # ステージ終了

                if (
                    st.session_state.question_index
                    >= len(questions)
                ):

                    st.session_state.stage_index += 1
                    st.session_state.question_index = 0


                st.rerun()


            else:


                st.error(
                    "不正解。もう一度考えてみよう。"
                )


# =========================
# 学習状況
# =========================

if st.session_state.started:

    st.sidebar.title("📊 学習記録")

    st.sidebar.write(
        f"正解数：{st.session_state.score}"
    )


    if st.session_state.stage_index < len(stage_names):

        st.sidebar.write(
            "現在："
            +
            stage_names[
                st.session_state.stage_index
            ]
        )