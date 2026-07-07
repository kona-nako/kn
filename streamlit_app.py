import streamlit as st
import time
from PIL import Image


# ==========================
# 基本設定
# ==========================

st.set_page_config(
    page_title="Typing Battle",
    page_icon="⚔️",
    layout="wide"
)


# ==========================
# 敵データ
# ==========================

enemies = [

    {
        "name": "スライム",
        "hp": 100,
        "time": 30,
        "text": "apple",
        "image": "images/slime.png"
    },


    {
        "name": "ゴブリン",
        "hp": 300,
        "time": 25,
        "text": "python programming",
        "image": "images/goblin.png"
    },


    {
        "name": "ゴーレム",
        "hp": 700,
        "time": 20,
        "text": "knowledge is power",
        "image": "images/golem.png"
    },


    {
        "name": "ドラゴン",
        "hp": 1500,
        "time": 15,
        "text": "continuous practice improves typing skill",
        "image": "images/dragon.png"
    }

]


# ==========================
# 状態保存
# ==========================

if "enemy_index" not in st.session_state:
    st.session_state.enemy_index = 0

if "enemy_hp" not in st.session_state:
    st.session_state.enemy_hp = enemies[0]["hp"]

if "playing" not in st.session_state:
    st.session_state.playing = False

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "combo" not in st.session_state:
    st.session_state.combo = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "wins" not in st.session_state:
    st.session_state.wins = 0



# ==========================
# HPバー
# ==========================

def hp_bar(current, maximum):

    percent = int(
        current / maximum * 100
    )

    st.markdown(
        f"""
        <div style="
        background:#333;
        border-radius:10px;
        height:30px;
        width:100%;
        ">

        <div style="
        background:#e53935;
        width:{percent}%;
        height:30px;
        border-radius:10px;
        text-align:center;
        color:white;
        font-weight:bold;
        ">

        {current}/{maximum}

        </div>

        </div>
        """,
        unsafe_allow_html=True
    )



# ==========================
# タイトル
# ==========================

st.title("⚔️ Typing Battle")

st.write(
"""
⌨️ タイピングで敵を攻撃しよう！

正確に入力するほど攻撃力アップ。
ミスすると時間を失います。
"""
)



# ==========================
# クリア
# ==========================

if st.session_state.enemy_index >= len(enemies):

    st.balloons()

    st.success(
        "🏆 全モンスター撃破！"
    )

    st.write(
        f"""
        最終スコア：
        {st.session_state.score}

        撃破数：
        {st.session_state.wins}
        """
    )


    if st.button("もう一度遊ぶ"):

        st.session_state.clear()
        st.rerun()



else:


    enemy = enemies[
        st.session_state.enemy_index
    ]


    # ==========================
    # 戦闘画面
    # ==========================

    left, right = st.columns(2)


    with left:

        st.subheader(
            enemy["name"]
        )


        try:

            image = Image.open(
                enemy["image"]
            )

            st.image(
                image,
                width=250
            )

        except:

            st.warning(
                "画像がありません"
            )


        hp_bar(
            st.session_state.enemy_hp,
            enemy["hp"]
        )



    with right:


        st.subheader(
            "🧙 プレイヤー"
        )


        st.write(
            "⚔️ 攻撃力：正確性で変化"
        )

        st.write(
            f"🔥 コンボ：{st.session_state.combo}"
        )

        st.write(
            f"🏆 スコア：{st.session_state.score}"
        )



    st.divider()



    # ==========================
    # 戦闘開始
    # ==========================

    if not st.session_state.playing:


        st.info(
            f"""
            制限時間：
            {enemy['time']}秒

            攻撃ワード：

            {enemy['text']}
            """
        )


        if st.button("⚔️ 戦闘開始"):

            st.session_state.start_time = time.time()

            st.session_state.playing = True

            st.rerun()



    else:


        elapsed = (
            time.time()
            -
            st.session_state.start_time
        )


        remaining = (
            enemy["time"]
            -
            int(elapsed)
        )


        st.metric(
            "⏳ 残り時間",
            f"{remaining}秒"
        )


        if remaining <= 0:


            st.error(
                "💀 時間切れ！敗北"
            )


            if st.button("再挑戦"):

                st.session_state.playing = False
                st.session_state.combo = 0
                st.rerun()



        else:


            st.subheader(
                "攻撃入力"
            )


            answer = st.text_input(
                "ここに入力"
            )


            if st.button("🔥 攻撃"):


                target = enemy["text"]


                # 正確率計算

                correct = 0

                for a,b in zip(
                    answer,
                    target
                ):

                    if a == b:

                        correct += 1


                accuracy = (
                    correct /
                    len(target)
                )


                # 攻撃計算

                if answer == target:


                    st.session_state.combo += 1


                else:


                    st.session_state.combo = 0



                combo_bonus = (
                    1 +
                    st.session_state.combo
                    *
                    0.2
                )


                damage = int(
                    100 *
                    accuracy *
                    combo_bonus
                )


                if answer != target:

                    enemy["time"] -= 3


                    st.warning(
                        "ミス！時間減少"
                    )

                else:

                    st.success(
                        f"""
                        ⚔️ 攻撃成功！

                        ダメージ：
                        {damage}
                        """
                    )


                st.session_state.enemy_hp -= damage

                st.session_state.score += damage



                # 撃破

                if st.session_state.enemy_hp <= 0:


                    st.balloons()


                    st.success(
                        f"{enemy['name']}撃破！"
                    )


                    st.session_state.enemy_index += 1

                    st.session_state.wins += 1


                    if (
                        st.session_state.enemy_index
                        <
                        len(enemies)
                    ):

                        next_enemy = enemies[
                            st.session_state.enemy_index
                        ]

                        st.session_state.enemy_hp = (
                            next_enemy["hp"]
                        )


                    st.session_state.playing = False


                st.rerun()