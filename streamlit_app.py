import random
import streamlit as st

st.set_page_config(page_title="えいたんご文づくりバトル", page_icon="🃏", layout="centered")

# ------------------------------------------------------------
# 単語カードの山(デッキ)を作る
# ------------------------------------------------------------
BASE_WORDS = {
    "代名詞": ["I", "You", "He", "She", "We", "They", "It"],
    "動詞": ["am", "is", "are", "like", "love", "want", "have", "eat", "play",
             "see", "go", "run", "read", "watch", "make", "buy", "study"],
    "名詞": ["dog", "cat", "book", "apple", "water", "ball", "school", "friend",
             "music", "movie", "house", "car", "pizza", "coffee", "tea", "game", "picture"],
    "冠詞": ["a", "an", "the"],
    "形容詞": ["big", "small", "happy", "good", "bad", "red", "blue", "new", "old",
               "fast", "cute", "nice"],
    "副詞": ["very", "always", "often", "sometimes", "never", "quickly", "slowly", "today"],
    "前置詞": ["in", "on", "at", "with", "to", "for"],
    "接続詞": ["and", "but", "because"],
    "その他": ["not", "my", "your", "his", "her", "this", "that"],
}

# よく使う単語は複数枚デッキに入れて、文を作りやすくする
EXTRA_COPIES = {
    "a": 3, "the": 3, "is": 3, "I": 3, "and": 2, "You": 2,
    "like": 2, "my": 2, "have": 2, "the ": 0,
}

HAND_SIZE = 10


def build_deck():
    deck = []
    for words in BASE_WORDS.values():
        deck.extend(words)
    for word, n in EXTRA_COPIES.items():
        if n > 1:
            deck.extend([word] * (n - 1))
    return deck


DECK = build_deck()

# ------------------------------------------------------------
# セッション状態の初期化
# ------------------------------------------------------------
def reset_game():
    st.session_state.phase = "setup"
    for key in ["hand1", "hand2", "used1", "used2", "order1", "order2",
                "name1", "name2"]:
        st.session_state.pop(key, None)


if "phase" not in st.session_state:
    reset_game()


def deal_hand():
    return random.sample(DECK, HAND_SIZE)


def word_grid(hand, used_key, order_key, disabled_all=False):
    """手札をボタンのグリッドで表示し、押されたら order に追加する"""
    used = st.session_state[used_key]
    cols = st.columns(5)
    for i, word in enumerate(hand):
        col = cols[i % 5]
        already_used = used[i]
        if col.button(word, key=f"{used_key}_{i}", disabled=already_used or disabled_all):
            st.session_state[order_key].append(i)
            used[i] = True
            st.rerun()


def undo_last(used_key, order_key):
    if st.session_state[order_key]:
        last_idx = st.session_state[order_key].pop()
        st.session_state[used_key][last_idx] = False


def reset_sentence(hand_key, used_key, order_key):
    n = len(st.session_state[hand_key])
    st.session_state[used_key] = [False] * n
    st.session_state[order_key] = []


def player_turn(player_no):
    hand_key, used_key, order_key, name_key = (
        f"hand{player_no}", f"used{player_no}", f"order{player_no}", f"name{player_no}",
    )
    name = st.session_state[name_key]

    st.header(f"🎴 {name} のターン")
    st.caption("配られた10枚のカードから、できるだけ長い英文になるように単語をクリックして並べよう。"
               "すべての単語を使わなくてもOK。")

    st.subheader("手札(クリックした順に文になります)")
    word_grid(st.session_state[hand_key], used_key, order_key)

    order = st.session_state[order_key]
    sentence_words = [st.session_state[hand_key][i] for i in order]
    sentence_text = " ".join(sentence_words)

    st.subheader("いま作っている文")
    st.info(sentence_text if sentence_text else "（まだ単語を選んでいません）")
    st.write(f"使った単語数: **{len(order)}** / {HAND_SIZE}")

    c1, c2, c3 = st.columns(3)
    if c1.button("⬅️ 1つ戻す", key=f"undo_{player_no}"):
        undo_last(used_key, order_key)
        st.rerun()
    if c2.button("🔄 リセット", key=f"reset_{player_no}"):
        reset_sentence(hand_key, used_key, order_key)
        st.rerun()
    if c3.button("✅ 文を確定する", key=f"confirm_{player_no}", disabled=len(order) == 0):
        if player_no == 1:
            st.session_state.phase = "p2_turn"
        else:
            st.session_state.phase = "result"
        st.rerun()


# ------------------------------------------------------------
# 画面(フェーズ)ごとの表示
# ------------------------------------------------------------
st.title("🃏 えいたんご文づくりバトル")

if st.session_state.phase == "setup":
    st.write("英単語カードを10枚引いて、対戦相手とできるだけ長い英文を作って勝負するゲームです。")
    name1 = st.text_input("プレイヤー1の名前", value="プレイヤー1")
    name2 = st.text_input("プレイヤー2の名前", value="プレイヤー2")

    if st.button("🎲 カードを配る", type="primary"):
        st.session_state.name1 = name1
        st.session_state.name2 = name2
        st.session_state.hand1 = deal_hand()
        st.session_state.hand2 = deal_hand()
        st.session_state.used1 = [False] * HAND_SIZE
        st.session_state.used2 = [False] * HAND_SIZE
        st.session_state.order1 = []
        st.session_state.order2 = []
        st.session_state.phase = "p1_turn"
        st.rerun()

elif st.session_state.phase == "p1_turn":
    player_turn(1)

elif st.session_state.phase == "p2_turn":
    st.success(f"{st.session_state.name1} の文が確定しました。次は {st.session_state.name2} の番です。")
    player_turn(2)

elif st.session_state.phase == "result":
    name1, name2 = st.session_state.name1, st.session_state.name2
    words1 = [st.session_state.hand1[i] for i in st.session_state.order1]
    words2 = [st.session_state.hand2[i] for i in st.session_state.order2]
    sentence1, sentence2 = " ".join(words1), " ".join(words2)
    score1, score2 = len(words1), len(words2)

    st.header("🏁 結果発表")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader(name1)
        st.info(sentence1)
        st.metric("単語数", score1)
    with c2:
        st.subheader(name2)
        st.info(sentence2)
        st.metric("単語数", score2)

    if score1 > score2:
        st.balloons()
        st.success(f"🎉 {name1} の勝ち！")
    elif score2 > score1:
        st.balloons()
        st.success(f"🎉 {name2} の勝ち！")
    else:
        st.warning("引き分け！")

    st.caption("※ このアプリは文法の正しさまでは自動判定していません。"
               "お互いの文が英語として自然かどうかは、先生や辞書、翻訳アプリなどで確認してみましょう。")

    if st.button("🔁 もう一度遊ぶ"):
        reset_game()
        st.rerun()