import streamlit as st
import time


st.set_page_config(
    page_title="Type Escape",
    page_icon="⌨️"
)


st.title("⌨️ Type Escape")
st.write("正確な入力で時間を守れ！")


sentences = [
    "apple",
    "computer",
    "knowledge",
    "study hard",
    "python programming"
]


if "start" not in st.session_state:
    st.session_state.start = False

if "time" not in st.session_state:
    st.session_state.time = 30

if "score" not in st.session_state:
    st.session_state.score = 0


if not st.session_state.start:

    if st.button("ゲーム開始"):

        st.session_state.start = True
        st.session_state.start_time = time.time()

        st.rerun()



else:


    elapsed = time.time() - st.session_state.start_time

    remaining = (
        st.session_state.time
        -
        int(elapsed)
    )


    st.metric(
        "残り時間",
        f"{remaining}秒"
    )


    if remaining <= 0:

        st.error("時間切れ")

        st.write(
            f"スコア：{st.session_state.score}"
        )

        st.session_state.start = False



    else:


        target = sentences[
            st.session_state.score
            %
            len(sentences)
        ]


        st.subheader(target)


        answer = st.text_input(
            "入力してください"
        )


        if st.button("判定"):


            if answer == target:

                st.success(
                    "正確！ +2秒"
                )

                st.session_state.score += 1

                st.session_state.time += 2


            else:

                st.error(
                    "ミス！ -3秒"
                )

                st.session_state.time -= 3


            st.rerun()