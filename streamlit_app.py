import streamlit as st
import time
import random


# =========================
# 設定
# =========================

st.set_page_config(
    page_title="Typing Battle",
    page_icon="⚔️"
)


# =========================
# 敵データ
# =========================

enemies = [
    {
        "name": "スライム",
        "hp": 100,
        "time": 30,
        "text": "apple"
    },

    {
        "name": "ゴブリン",
        "hp": 300,
        "time": 25,
        "text": "python programming"
    },

    {
        "name": "ゴーレム",
        "hp": 700,
        "time": 20,
        "text": "knowledge is power"
    },

    {
        "name": "ドラゴン",
        "hp": 1500,
        "time": 15,
        "text": "continuous practice improves typing skill"
    }
]


# =========================
# 初期化
# =========================

if "enemy_level" not in st.session_state:
    st.session_state.enemy_level = 0

if "enemy_hp" not in st.session_state:
    st.session_state.enemy_hp = enemies[0]["hp"]

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "combo" not in st.session_state:
    st.session_state.combo = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "playing" not in st.session_state:
    st.session_state.playing = False



# =========================
# タイトル
# =========================

st.title("⚔️ Typing Battle")

st.write(
    "正確なタイピングで敵を倒せ！"
)


# =========================
# クリア判定
# =========================

if st.session_state.enemy_level >= len(enemies):

    st.success(
        "🎉 全ての敵を倒しました！"
    )

    st.write(
        f"総スコア：{st.session_state.score}"
    )


    if st.button("最初から"):

        st.session_state.clear()
        st.rerun()



else:


    enemy = enemies[
        st.session_state.enemy_level
    ]


    # =====================
    # 敵表示
    # =====================

    st.header(
        f"👹 {enemy['name']}"
    )


    st.progress(
        st.session_state.enemy_hp
        /
        enemy["hp"]
    )


    st.write(
        f"敵HP：{st.session_state.enemy_hp}"
    )


    # =====================
    # 開始
    # =====================

    if not st.session_state.playing:


        st.write(
            f"""
            制限時間：
            {enemy['time']}秒

            攻撃文：

            **{enemy['text']}**
            """
        )


        if st.button("戦闘開始"):

            st.session_state.start_time = time.time()

            st.session_state.playing = True

            st.rerun()



    else:


        # =====================
        # 時間計算
        # =====================

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
            "残り時間",
            f"{remaining}秒"
        )


        if remaining <= 0:


            st.error(
                "時間切れ！敗北..."
            )


            if st.button("再挑戦"):

                st.session_state.playing = False
                st.rerun()


        else:


            # =================
            # 入力
            # =================

            answer = st.text_input(
                "攻撃入力"
            )


            if st.button("⚔️ 攻撃"):


                target = enemy["text"]


                # -----------------
                # 正確率計算
                # -----------------

                correct = 0


                for a,b in zip(
                    answer,
                    target
                ):

                    if a == b:
                        correct += 1


                accuracy = (
                    correct
                    /
                    len(target)
                )


                # -----------------
                # ダメージ計算
                # -----------------

                if answer == target:


                    st.session_state.combo += 1


                    damage = int(
                        100
                        *
                        accuracy
                        *
                        (
                            1
                            +
                            st.session_state.combo
                            *
                            0.2
                        )
                    )


                    st.success(
                        f"""
                        PERFECT!

                        攻撃力：
                        {damage}

                        コンボ：
                        {st.session_state.combo}
                        """
                    )


                else:


                    damage = int(
                        50
                        *
                        accuracy
                    )


                    st.session_state.combo = 0


                    st.warning(
                        """
                        ミス！

                        時間 -3秒
                        """
                    )


                    enemy["time"] -= 3



                # HP減少

                st.session_state.enemy_hp -= damage

                st.session_state.score += damage


                # 敵撃破

                if st.session_state.enemy_hp <= 0:


                    st.balloons()


                    st.success(
                        f"{enemy['name']}を倒した！"
                    )


                    st.session_state.enemy_level += 1


                    if (
                        st.session_state.enemy_level
                        <
                        len(enemies)
                    ):

                        next_enemy = enemies[
                            st.session_state.enemy_level
                        ]


                        st.session_state.enemy_hp = (
                            next_enemy["hp"]
                        )


                    st.session_state.playing = False



                st.rerun()