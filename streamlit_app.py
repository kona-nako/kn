import json
import os
import random
import re
import string
import threading
import time

import streamlit as st

st.set_page_config(page_title="えいたんご文づくりバトル", page_icon="🃏", layout="centered")

# ============================================================
# 単語バンク(品詞ごと)
# ============================================================
WORD_BANK = {
    "A": ["very", "always", "often", "sometimes", "never", "quickly", "slowly", "today"],   # 副詞
    "P": ["I", "You", "He", "She", "We", "They", "It"],                                      # 代名詞
    "B": ["am", "is", "are"],                                                                 # be動詞
    "N": ["not"],                                                                             # 否定語
    "D": ["a", "an", "the", "my", "your", "his", "her", "this", "that"],                       # 限定詞
    "J": ["big", "small", "happy", "good", "bad", "red", "blue", "new", "old", "fast",
          "cute", "nice"],                                                                    # 形容詞
    "O": ["dog", "cat", "book", "apple", "water", "ball", "school", "friend", "music",
          "movie", "house", "car", "pizza", "coffee", "tea", "game", "picture"],               # 名詞
    "V": ["like", "love", "want", "have", "eat", "play", "see", "go", "run", "read",
          "watch", "make", "buy", "study"],                                                   # 動詞
    "R": ["in", "on", "at", "with", "to", "for"],                                              # 前置詞
    "C": ["and", "but", "because"],                                                            # 接続詞
}

POS_LABEL = {
    "A": "副詞", "P": "代名詞", "B": "be動詞", "N": "否定語", "D": "限定詞",
    "J": "形容詞", "O": "名詞", "V": "動詞", "R": "前置詞", "C": "接続詞",
}

WORD_TO_POS = {}
for _pos, _words in WORD_BANK.items():
    for _w in _words:
        WORD_TO_POS[_w] = _pos


def get_word(pos):
    return random.choice(WORD_BANK[pos])


# ============================================================
# 簡易英文法(正規表現ベースのルールベース判定)
#   1つの節(クローズ) = [副詞]? 代名詞 [副詞]?
#        (be動詞 [否定]? [副詞]? (形容詞 | [限定詞]?形容詞*名詞)
#         | 動詞 [否定]? [限定詞]?形容詞*名詞 [副詞]?)
#        (前置詞 [限定詞]?形容詞*名詞)?
#   文 = 節 (接続詞 節)?
# ============================================================
_CLAUSE = r"A?PA?(?:BN?A?(?:J|D?J*O)|VN?D?J*OA?)(?:RD?J*O)?"
FULL_PATTERN = re.compile(rf"{_CLAUSE}(?:C{_CLAUSE})?")


def is_grammatical(words):
    if not words:
        return False
    try:
        codes = "".join(WORD_TO_POS[w] for w in words)
    except KeyError:
        return False
    m = FULL_PATTERN.fullmatch(codes)
    return m is not None


# ============================================================
# 10語のカードセットを生成する(必ず正解の並びが存在するようにする)
# ============================================================
FALLBACK_SOLUTION = ["I", "like", "the", "big", "dog", "because", "She", "have", "a", "cat"]
FALLBACK_CLAUSE1_LEN = 5


def build_clause(target_len, tries=500):
    for _ in range(tries):
        tokens = []
        lead_adv = random.random() < 0.30
        mid_adv = random.random() < 0.25
        verb_type = random.choice(["be", "do"])
        neg = random.random() < 0.15
        use_pp = random.random() < 0.35
        pp_det = random.random() < 0.6
        pp_adj = random.choice([0, 0, 1])

        if lead_adv:
            tokens.append(get_word("A"))
        tokens.append(get_word("P"))
        if mid_adv:
            tokens.append(get_word("A"))

        if verb_type == "be":
            tokens.append(get_word("B"))
            if neg:
                tokens.append("not")
            be_adv = random.random() < 0.2
            if be_adv:
                tokens.append(get_word("A"))
            use_adj_only = random.random() < 0.45
            if use_adj_only:
                tokens.append(get_word("J"))
            else:
                if random.random() < 0.7:
                    tokens.append(get_word("D"))
                for _ in range(random.choice([0, 0, 1, 1, 2])):
                    tokens.append(get_word("J"))
                tokens.append(get_word("O"))
        else:
            tokens.append(get_word("V"))
            if neg:
                tokens.append("not")
            if random.random() < 0.7:
                tokens.append(get_word("D"))
            for _ in range(random.choice([0, 0, 1, 1, 2])):
                tokens.append(get_word("J"))
            tokens.append(get_word("O"))
            if random.random() < 0.2:
                tokens.append(get_word("A"))

        if use_pp:
            tokens.append(get_word("R"))
            if pp_det:
                tokens.append(get_word("D"))
            for _ in range(pp_adj):
                tokens.append(get_word("J"))
            tokens.append(get_word("O"))

        if len(tokens) == target_len:
            return tokens
    return None


def combine_sentence():
    for _ in range(300):
        len1 = random.randint(3, 6)
        len2 = 9 - len1
        c1 = build_clause(len1)
        if c1 is None:
            continue
        c2 = build_clause(len2)
        if c2 is None:
            continue
        conj = get_word("C")
        return c1 + [conj] + c2, len1
    return FALLBACK_SOLUTION[:], FALLBACK_CLAUSE1_LEN


def generate_hand():
    """(手札10枚, 正解の並び10語, 節1の語数) を返す"""
    solution, clause1_len = combine_sentence()
    hand = solution[:]
    tries = 0
    while True:
        random.shuffle(hand)
        tries += 1
        if hand != solution or tries > 5:
            break
    return hand, solution, clause1_len


def tier_message(n):
    if n >= 10:
        return "🌟 パーフェクト！10枚すべて使いました！"
    elif n >= 8:
        return "🔥 素晴らしい！"
    elif n >= 6:
        return "👍 いい感じ！"
    elif n >= 4:
        return "🙂 まずまず！"
    else:
        return "💪 練習あるのみ！"


# ============================================================
# 共通UIパーツ:手札から文を組み立てるUI
# ============================================================
def render_hand_builder(hand, prefix, show_hint, confirm_label="✅ この文で確定する"):
    used_key, order_key = f"{prefix}_used", f"{prefix}_order"
    if used_key not in st.session_state:
        st.session_state[used_key] = [False] * len(hand)
        st.session_state[order_key] = []

    used = st.session_state[used_key]
    order = st.session_state[order_key]

    st.write("**手札(クリックした順番に文になります)**")
    cols = st.columns(5)
    for i, w in enumerate(hand):
        col = cols[i % 5]
        label = w if not show_hint else f"{w}［{POS_LABEL[WORD_TO_POS[w]]}］"
        if col.button(label, key=f"{prefix}_btn_{i}", disabled=used[i]):
            order.append(i)
            used[i] = True
            st.rerun()

    words = [hand[i] for i in order]
    valid = is_grammatical(words) if words else False

    st.write("**いま作っている文**")
    st.info(" ".join(words) if words else "（まだ単語を選んでいません）")
    if words:
        if valid:
            st.success(f"✅ 文法的に正しい文になっています！（{len(words)}語）")
        else:
            st.warning("⏳ まだ文法的に正しくありません。続けるか、並び替えてみましょう。")

    c1, c2 = st.columns(2)
    if c1.button("⬅️ 1つ戻す", key=f"{prefix}_undo"):
        if order:
            last = order.pop()
            used[last] = False
            st.rerun()
    if c2.button("🔄 最初からやり直す", key=f"{prefix}_reset"):
        st.session_state[used_key] = [False] * len(hand)
        st.session_state[order_key] = []
        st.rerun()

    confirmed = st.button(confirm_label, key=f"{prefix}_confirm",
                           disabled=len(words) == 0, type="primary")
    return words, valid, confirmed


def clear_builder_state(prefix):
    for key in [f"{prefix}_used", f"{prefix}_order"]:
        st.session_state.pop(key, None)


# ============================================================
# 品詞レジェンド
# ============================================================
def show_pos_legend():
    with st.expander("📖 品詞の凡例(ヒント表示をONにすると各カードに表示されます)"):
        st.write(" / ".join(f"**{label}**" for code, label in POS_LABEL.items()))
        st.caption("文法チェックは「代名詞＋動詞＋名詞」「be動詞＋形容詞／名詞」「前置詞句」"
                   "「接続詞でつないだ2つの文」などのよく使う文型に基づく簡易判定です。"
                   "主語と動詞の一致(He is / He are の区別)など高度な文法までは判定していません。")


# ============================================================
# セッション状態の初期化
# ============================================================
if "app_mode" not in st.session_state:
    st.session_state.app_mode = "menu"


def go_menu():
    st.session_state.app_mode = "menu"


# ============================================================
# メニュー画面
# ============================================================
def run_menu():
    st.title("🃏 えいたんご文づくりバトル")
    st.write("配られた英単語カードを並べ替えて、できるだけ長い(そして文法的に正しい)英文を作ろう！")
    show_pos_legend()

    st.divider()
    c1, c2, c3 = st.columns(3)
    if c1.button("🧑‍🎓 ソロモード\n(練習)", use_container_width=True):
        st.session_state.app_mode = "solo"
        st.rerun()
    if c2.button("🤖 AI対戦モード", use_container_width=True):
        st.session_state.app_mode = "ai"
        st.rerun()
    if c3.button("🌐 オンライン対戦モード", use_container_width=True):
        st.session_state.app_mode = "online"
        st.rerun()

    st.caption("💡 手札の10枚には必ず「10枚全部を使った正しい英文」の並び方が存在します。"
               "ただし見つけるのはかなり難しいので、まずは短い文から挑戦してみましょう。")


# ============================================================
# ソロモード
# ============================================================
def reset_solo():
    for key in ["solo_hand", "solo_solution", "solo_clause1_len", "solo_result"]:
        st.session_state.pop(key, None)
    clear_builder_state("solo")


def run_solo():
    st.header("🧑‍🎓 ソロモード（練習）")
    st.caption("一人で好きなだけ練習できるモードです。文法チェックの結果を見ながら挑戦しましょう。")

    if "solo_hand" not in st.session_state:
        hand, solution, clause1_len = generate_hand()
        st.session_state.solo_hand = hand
        st.session_state.solo_solution = solution
        st.session_state.solo_clause1_len = clause1_len

    show_hint = st.checkbox("💡 品詞のヒントを表示する", key="solo_hint")
    words, valid, confirmed = render_hand_builder(
        st.session_state.solo_hand, "solo", show_hint, confirm_label="✅ この文で確定する"
    )

    if confirmed:
        st.session_state.solo_result = (words, valid)

    if "solo_result" in st.session_state:
        r_words, r_valid = st.session_state.solo_result
        st.divider()
        st.subheader("結果")
        st.write(" ".join(r_words))
        if r_valid:
            st.success(f"文法的に正しい文です！ {len(r_words)}語使用 {tier_message(len(r_words))}")
        else:
            st.error("まだ文法的に正しくありません。単語の並びを見直して再挑戦してみましょう。")

    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("🎲 新しいカードを引く", key="solo_new"):
        reset_solo()
        st.rerun()
    if c2.button("🏠 メニューに戻る", key="solo_menu"):
        reset_solo()
        go_menu()
        st.rerun()


# ============================================================
# AI対戦モード
# ============================================================
def reset_ai():
    for key in ["aim_player_hand", "aim_player_solution", "aim_player_clause1_len",
                "aim_ai_solution", "aim_ai_clause1_len", "ai_result"]:
        st.session_state.pop(key, None)
    clear_builder_state("ai")


def ai_play(difficulty):
    solution = st.session_state.aim_ai_solution
    clause1_len = st.session_state.aim_ai_clause1_len

    mistake_chance = {"かんたん": 0.35, "ふつう": 0.12, "むずかしい": 0.0}[difficulty]
    full_chance = {"かんたん": 0.05, "ふつう": 0.55, "むずかしい": 1.0}[difficulty]

    if random.random() < full_chance:
        words = solution[:]
    else:
        words = solution[:clause1_len]

    if random.random() < mistake_chance:
        words = words[:]
        random.shuffle(words)

    valid = is_grammatical(words)
    return words, valid


def run_ai():
    st.header("🤖 AI対戦モード")
    st.caption("AIも同じルールで10枚のカードから文を作って勝負します。")

    difficulty = st.radio("AIの強さ", ["かんたん", "ふつう", "むずかしい"],
                           horizontal=True, key="ai_diff")

    if "aim_player_hand" not in st.session_state:
        hand, solution, clause1_len = generate_hand()
        st.session_state.aim_player_hand = hand
        st.session_state.aim_player_solution = solution
        st.session_state.aim_player_clause1_len = clause1_len

        ai_hand, ai_solution, ai_clause1_len = generate_hand()
        st.session_state.aim_ai_solution = ai_solution
        st.session_state.aim_ai_clause1_len = ai_clause1_len

    show_hint = st.checkbox("💡 品詞のヒントを表示する", key="ai_hint")
    words, valid, confirmed = render_hand_builder(
        st.session_state.aim_player_hand, "ai", show_hint,
        confirm_label="✅ この文で確定して勝負する"
    )

    if confirmed:
        ai_words, ai_valid = ai_play(difficulty)
        st.session_state.ai_result = (words, valid, ai_words, ai_valid, difficulty)

    if "ai_result" in st.session_state:
        pw, pv, aw, av, used_diff = st.session_state.ai_result
        st.divider()
        st.subheader("🏁 結果")
        ps = len(pw) if pv else 0
        ascore = len(aw) if av else 0

        c1, c2 = st.columns(2)
        with c1:
            st.write("**あなた**")
            st.write(" ".join(pw))
            st.metric("スコア", ps)
            if not pv:
                st.caption("⚠️ 文法的に正しくないためスコア0")
        with c2:
            st.write(f"**🤖 AI（{used_diff}）**")
            st.write(" ".join(aw))
            st.metric("スコア", ascore)
            if not av:
                st.caption("⚠️ AIの文も文法的に正しくありませんでした")

        if ps > ascore:
            st.balloons()
            st.success("🎉 あなたの勝ち！")
        elif ascore > ps:
            st.error("🤖 AIの勝ち！")
        else:
            st.warning("引き分け！")

    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("🎲 新しい対戦", key="ai_new"):
        reset_ai()
        st.rerun()
    if c2.button("🏠 メニューに戻る", key="ai_menu"):
        reset_ai()
        go_menu()
        st.rerun()


# ============================================================
# オンライン対戦モード(同じサーバーに接続している人同士)
# ============================================================
ROOM_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "battle_rooms.json")
_ROOM_LOCK = threading.Lock()


def load_rooms():
    with _ROOM_LOCK:
        if not os.path.exists(ROOM_FILE):
            return {}
        try:
            with open(ROOM_FILE, "r", encoding="utf-8") as f:
                rooms = json.load(f)
        except Exception:
            return {}
        now = time.time()
        cleaned = {k: v for k, v in rooms.items() if now - v.get("created_at", now) < 3 * 3600}
        if len(cleaned) != len(rooms):
            with open(ROOM_FILE, "w", encoding="utf-8") as f:
                json.dump(cleaned, f, ensure_ascii=False)
        return cleaned


def save_rooms(rooms):
    with _ROOM_LOCK:
        with open(ROOM_FILE, "w", encoding="utf-8") as f:
            json.dump(rooms, f, ensure_ascii=False)


def new_room_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=4))


def reset_online():
    for key in ["online_stage", "online_role", "online_code", "online_hand"]:
        st.session_state.pop(key, None)
    clear_builder_state("online")


def run_online():
    st.header("🌐 オンライン対戦モード")
    st.warning("⚠️ このモードは「同じサーバー（同じPCで開いた別タブ、同じWi-Fi内、"
               "同じ場所にデプロイされたアプリ）」に接続している人同士でのみ対戦できます。"
               "全く離れた場所の相手とインターネット越しにマッチングする機能は、"
               "別途の会員サーバーが必要になるため今回は非対応です（その場合はAI対戦モードをお使いください）。")

    stage = st.session_state.get("online_stage", "menu")

    if stage == "menu":
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("部屋を作る")
            host_name = st.text_input("あなたの名前", value="ホスト", key="online_host_name")
            if st.button("🆕 部屋を作成する", key="online_create"):
                code = new_room_code()
                hand1, sol1, cl1 = generate_hand()
                hand2, sol2, cl2 = generate_hand()
                rooms = load_rooms()
                rooms[code] = {
                    "name1": host_name, "name2": None,
                    "hand1": hand1, "hand2": hand2,
                    "words1": None, "words2": None,
                    "ready1": False, "ready2": False,
                    "created_at": time.time(),
                }
                save_rooms(rooms)
                st.session_state.online_stage = "room"
                st.session_state.online_role = "host"
                st.session_state.online_code = code
                st.session_state.online_hand = hand1
                st.rerun()
        with c2:
            st.subheader("部屋に入る")
            guest_name = st.text_input("あなたの名前", value="ゲスト", key="online_guest_name")
            code_in = st.text_input("部屋コード(4文字)", key="online_code_input").upper().strip()
            if st.button("🚪 参加する", key="online_join"):
                rooms = load_rooms()
                if code_in not in rooms:
                    st.error("その部屋コードは見つかりませんでした。")
                elif rooms[code_in]["name2"] is not None:
                    st.error("この部屋はすでに満員です。")
                else:
                    rooms[code_in]["name2"] = guest_name
                    save_rooms(rooms)
                    st.session_state.online_stage = "room"
                    st.session_state.online_role = "guest"
                    st.session_state.online_code = code_in
                    st.session_state.online_hand = rooms[code_in]["hand2"]
                    st.rerun()

        st.divider()
        if st.button("🏠 メニューに戻る", key="online_tomenu_menu"):
            go_menu()
            st.rerun()
        return

    # ---- room stage ----
    code = st.session_state.online_code
    role = st.session_state.online_role
    rooms = load_rooms()
    room = rooms.get(code)

    if room is None:
        st.error("部屋が見つかりませんでした（時間切れで削除された可能性があります）。")
        if st.button("メニューに戻る", key="online_gone"):
            reset_online()
            st.rerun()
        return

    st.info(f"部屋コード: **{code}**" + ("　この番号を相手に伝えてください。" if role == "host" else ""))
    opp_name = room["name2"] if role == "host" else room["name1"]
    st.write(f"対戦相手: {opp_name if opp_name else '（参加を待っています…）'}")

    ready_key = "ready1" if role == "host" else "ready2"
    words_key = "words1" if role == "host" else "words2"

    if not room[ready_key]:
        show_hint = st.checkbox("💡 品詞のヒントを表示する", key="online_hint")
        words, valid, confirmed = render_hand_builder(
            st.session_state.online_hand, "online", show_hint,
            confirm_label="✅ この文で確定して提出する"
        )
        if confirmed:
            fresh_rooms = load_rooms()
            fresh_room = fresh_rooms.get(code)
            if fresh_room:
                fresh_room[words_key] = words
                fresh_room[ready_key] = True
                save_rooms(fresh_rooms)
                st.rerun()
    else:
        st.success("提出済みです。相手の提出を待っています…")
        if st.button("🔄 相手の状況を確認する", key="online_check"):
            st.rerun()

    rooms = load_rooms()
    room = rooms.get(code) or {}
    if room.get("ready1") and room.get("ready2"):
        st.divider()
        st.subheader("🏁 結果")
        w1, w2 = room["words1"], room["words2"]
        v1, v2 = is_grammatical(w1), is_grammatical(w2)
        s1 = len(w1) if v1 else 0
        s2 = len(w2) if v2 else 0

        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**{room['name1']}**")
            st.write(" ".join(w1))
            st.metric("スコア", s1)
            if not v1:
                st.caption("⚠️ 文法的に正しくないためスコア0")
        with c2:
            st.write(f"**{room['name2']}**")
            st.write(" ".join(w2))
            st.metric("スコア", s2)
            if not v2:
                st.caption("⚠️ 文法的に正しくないためスコア0")

        if s1 > s2:
            st.success(f"🎉 {room['name1']} の勝ち！")
        elif s2 > s1:
            st.success(f"🎉 {room['name2']} の勝ち！")
        else:
            st.warning("引き分け！")

    st.divider()
    if st.button("🏠 退室してメニューに戻る", key="online_leave"):
        reset_online()
        go_menu()
        st.rerun()


# ============================================================
# ルーティング
# ============================================================
mode = st.session_state.app_mode
if mode == "menu":
    run_menu()
elif mode == "solo":
    run_solo()
elif mode == "ai":
    run_ai()
elif mode == "online":
    run_online()
else:
    st.session_state.app_mode = "menu"
    st.rerun()