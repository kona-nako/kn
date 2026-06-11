import streamlit as st

st.title("🏰 選択RPG")

# 初回のみシーンを設定
if "scene" not in st.session_state:
    st.session_state.scene = "start"

# スタートシーン
if st.session_state.scene == "start":
    st.write("あなたは森の入り口にいます。")

    if st.button("森へ進む"):
        st.session_state.scene = "forest"
        st.rerun()

    if st.button("村へ行く"):
        st.session_state.scene = "village"
        st.rerun()

# 森
elif st.session_state.scene == "forest":
    st.write("🌲 森の奥でモンスターに出会った！")

    if st.button("戦う"):
        st.session_state.scene = "battle"
        st.rerun()

    if st.button("逃げる"):
        st.session_state.scene = "start"
        st.rerun()

# 村
elif st.session_state.scene == "village":
    st.write("🏠 村人が話しかけてきた。")

    if st.button("話を聞く"):
        st.write("『森に宝があるらしいぞ！』")

    if st.button("森へ向かう"):
        st.session_state.scene = "forest"
        st.rerun()

# 戦闘
elif st.session_state.scene == "battle":
    st.write("⚔️ モンスターを倒した！")

    if st.button("宝箱を開ける"):
        st.session_state.scene = "treasure"
        st.rerun()

# 宝箱
elif st.session_state.scene == "treasure":
    st.success("🎉 伝説の剣を手に入れた！")
    st.write("ゲームクリア！")

    if st.button("最初から"):
        st.session_state.scene = "start"
        st.rerun()