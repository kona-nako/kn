import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="ケアレスミス分析", page_icon="📊")

st.title("📊 ケアレスミス分析アプリ")

st.write("問題を解いた結果を入力すると、ケアレスミス率を分析します。")

# セッションにデータ保存
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "問題",
        "正誤",
        "ミス種類"
    ])

# 入力フォーム
with st.form("input_form"):
    problem = st.text_input("問題名")
    result = st.selectbox("結果", ["正解", "不正解"])

    mistake = st.selectbox(
        "ミスの種類",
        [
            "なし",
            "ケアレスミス",
            "計算ミス",
            "知識不足",
            "時間不足",
            "問題文の読み間違い"
        ]
    )

    submit = st.form_submit_button("追加")

if submit:
    new = pd.DataFrame({
        "問題":[problem],
        "正誤":[result],
        "ミス種類":[mistake]
    })

    st.session_state.data = pd.concat(
        [st.session_state.data, new],
        ignore_index=True
    )

df = st.session_state.data

st.subheader("入力データ")

st.dataframe(df, use_container_width=True)

if len(df) > 0:

    total = len(df)

    careless = len(df[df["ミス種類"]=="ケアレスミス"])

    rate = careless / total * 100

    st.metric("ケアレスミス率", f"{rate:.1f}%")

    st.metric("問題数", total)

    st.metric("ケアレスミス", careless)

    # 円グラフ
    st.subheader("ケアレスミス割合")

    fig, ax = plt.subplots()

    ax.pie(
        [careless, total-careless],
        labels=["ケアレスミス","その他"],
        autopct="%1.1f%%",
        startangle=90
    )

    ax.axis("equal")

    st.pyplot(fig)

    # 棒グラフ
    st.subheader("ミスの種類")

    count = df["ミス種類"].value_counts()

    fig2, ax2 = plt.subplots()

    ax2.bar(count.index, count.values)

    plt.xticks(rotation=30)

    st.pyplot(fig2)

    # コメント
    st.subheader("AIコメント（簡易版）")

    if rate < 10:
        st.success("ケアレスミスは少ないです。この調子で続けましょう！")

    elif rate < 30:
        st.warning("少しケアレスミスがあります。見直しを意識すると得点アップが期待できます。")

    else:
        st.error("ケアレスミスが多めです。見直し時間を確保し、問題文を丁寧に読む習慣をつけましょう。")