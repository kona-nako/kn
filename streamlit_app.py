import json
import os
import random
import string
import threading
import time

import streamlit as st

st.set_page_config(page_title="四字熟語バトル", page_icon="🀄", layout="centered")

# ============================================================
# 四字熟語バンク（正解判定はこの辞書に含まれているかどうかだけで行う）
#   ※ 文法をチェックする正規表現ロジックの代わりに、辞書照合を使う
# ============================================================
IDIOM_BANK = [
    "一石二鳥", "一期一会", "二人三脚", "四苦八苦", "七転八起",
    "温故知新", "電光石火", "十人十色", "一喜一憂", "自業自得",
    "我田引水", "花鳥風月", "春夏秋冬", "東西南北", "起承転結",
    "大器晩成", "一心不乱", "一日千秋", "千客万来", "三寒四温",
    "二束三文", "五里霧中", "一挙両得", "空前絶後", "油断大敵",
    "適材適所", "質実剛健", "意気投合", "東奔西走", "内憂外患",
    "一長一短", "大同小異", "半信半疑", "二転三転", "千変万化",
    "抱腹絶倒", "縦横無尽", "単刀直入", "前代未聞", "波瀾万丈",
]
IDIOM_SET = set(IDIOM_BANK)

AVAILABLE, SELECTED, USED = 0, 1, 2

DIFFICULTY_SETTINGS = {
    "かんたん": {"idiom_count": 2, "decoy_count": 2},
    "ふつう": {"idiom_count": 3, "decoy_count": 4},
    "むずかしい": {"idiom_count": 4, "decoy_count": 6},
}

AI_FIND_PROB = {"かんたん": 0.30, "ふつう": 0.60, "むずかしい": 0.95}


def is_valid_idiom(chars):
    """4文字がちょうど辞書に載っている四字熟語になっているかを判定する"""
    if len(chars) != 4:
        return False
    return "".join(chars) in IDIOM_SET


def build_hand(idiom_count, decoy_count):
    """
    idiom_count個の四字熟語をランダムに選んでバラバラにし、手札にする。
    decoy_count枚のダミー漢字も混ぜる。
    手札の中には必ず idiom_count 個ぶんの「正解の並び」が存在する。
    """
    targets = random.sample(IDIOM_BANK, idiom_count)
    tiles = []
    for idiom in targets:
        tiles.extend(list(idiom))

    used_chars = set("".join(targets))
    all_chars = set("".join(IDIOM_BANK))
    decoy_pool = list(all_chars - used_chars)
    random.shuffle(decoy_pool)
    decoys = decoy_pool[:decoy_count]
    tiles.extend(decoys)

    random.shuffle(tiles)
    return tiles, targets


def generate_hand(difficulty):
    cfg = DIFFICULTY_SETTINGS[difficulty]
    return build_hand(cfg["idiom_count"], cfg["decoy_count"])


def tier_message(found_count, max_count):
    if max_count <= 0:
        return ""
    ratio = found_count / max_count
    if ratio >= 1:
        return "🌟 パーフェクト！全部見つけました！"
    elif ratio >= 0.66:
        return "🔥 素晴らしい！"
    elif ratio >= 0.33:
        return "👍 いい感じ！"
    elif found_count > 0:
        return "🙂 まずまず！"
    else:
        return "💪 練習あるのみ！"


# ============================================================
# 共通UIパーツ：手札から四字熟語を探すUI
# ============================================================
def render_board(hand, prefix, confirm_label="✅ 四字熟語として確定する"):
    status_key = f"{prefix}_status"
    order_key = f"{prefix}_order"
    found_key = f"{prefix}_found"
    fail_key = f"{prefix}_fail"

    if status_key not in st.session_state:
        st.session_state[status_key] = [AVAILABLE] * len(hand)
        st.session_state[order_key] = []
        st.session_state[found_key] = []
        st.session_state[fail_key] = None

    status = st.session_state[status_key]
    order = st.session_state[order_key]
    found = st.session_state[found_key]

    st.write(f"**見つけた四字熟語：{len(found)}個**")
    if found:
        st.write("　".join(found))

    st.write("**手札（クリックした順に文字が並びます。選択中の字を押すと選択解除）**")
    cols = st.columns(6)
    for i, ch in enumerate(hand):
        col = cols[i % 6]
        if status[i] == USED:
            col.button(ch, key=f"{prefix}_btn_{i}", disabled=True)
        elif status[i] == SELECTED:
            if col.button(f"【{ch}】", key=f"{prefix}_btn_{i}"):
                order.remove(i)
                status[i] = AVAILABLE
                st.session_state[fail_key] = None
        else:
            if col.button(ch, key=f"{prefix}_btn_{i}"):
                order.append(i)
                status[i] = SELECTED
                st.session_state[fail_key] = None

    selected_word = "".join(hand[i] for i in order)
    st.write("**いま選んでいる文字**")
    st.info(selected_word if selected_word else "（まだ選んでいません）")

    c1, c2, c3 = st.columns(3)
    can_confirm = len(order) == 4
    if c1.button(confirm_label, key=f"{prefix}_confirm", disabled=not can_confirm):
        if is_valid_idiom([hand[i] for i in order]):
            found.append(selected_word)
            for i in order:
                status[i] = USED
            order.clear()
            st.session_state[fail_key] = None
            st.success(f"「{selected_word}」は正しい四字熟語でした！")
        else:
            st.session_state[fail_key] = selected_word

    if c2.button("⬅️ 1文字戻す", key=f"{prefix}_undo"):
        if order:
            last = order.pop()
            status[last] = AVAILABLE
            st.session_state[fail_key] = None

    if c3.button("🔄 選択をリセット", key=f"{prefix}_clear"):
        for i in order:
            status[i] = AVAILABLE
        order.clear()
        st.session_state[fail_key] = None

    if st.session_state.get(fail_key):
        st.warning(f"「{st.session_state[fail_key]}」は四字熟語として認識されませんでした。")

    remaining = sum(1 for s in status if s == AVAILABLE)
    st.caption(f"残り未使用の漢字：{remaining}枚")

    finish_clicked = st.button("🏁 ここで終了する（お手上げ）", key=f"{prefix}_finish")
    no_more_moves = remaining < 4 and len(order) < 4
    return found, (finish_clicked or no_more_moves)


def clear_board_state(prefix):
    for key in [f"{prefix}_status", f"{prefix}_order", f"{prefix}_found", f"{prefix}_fail"]:
        st.session_state.pop(key, None)


def show_idiom_legend():
    with st.expander("📖 四字熟語ヒント一覧（迷ったときに見てみよう）"):
        st.write("　".join(IDIOM_BANK))
        st.caption("手札の漢字は、上のリストの中からランダムに選ばれた四字熟語の文字と"
                   "ダミーの漢字を混ぜたものです。上のリストと同じ並びで4文字を選べれば正解になります。")


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
    st.title("🀄 四字熟語バトル")
    st.write("配られた漢字カードを組み合わせて、できるだけたくさんの四字熟語を作ろう！"
             "見つけた個数が多いほうの勝ちです。")
    show_idiom_legend()

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

    st.caption("💡 手札には必ず、選んだ難易度の個数ぶんの「正解の四字熟語」が隠れています。")


# ============================================================
# ソロモード
# ============================================================
def reset_solo():
    for key in ["solo_hand", "solo_targets", "solo_difficulty", "solo_done"]:
        st.session_state.pop(key, None)
    clear_board_state("solo")


def run_solo():
    st.header("🧑‍🎓 ソロモード（練習）")
    st.caption("一人で好きなだけ練習できるモードです。")

    if "solo_hand" not in st.session_state:
        difficulty = st.session_state.get("solo_diff_select", "ふつう")
        hand, targets = generate_hand(difficulty)
        st.session_state.solo_hand = hand
        st.session_state.solo_targets = targets
        st.session_state.solo_difficulty = difficulty

    st.write(f"難易度：**{st.session_state.solo_difficulty}**"
             f"（正解は{len(st.session_state.solo_targets)}個隠れています）")

    found, finished = render_board(st.session_state.solo_hand, "solo")

    if finished:
        st.session_state.solo_done = True

    if st.session_state.get("solo_done"):
        st.divider()
        st.subheader("結果")
        max_count = len(st.session_state.solo_targets)
        st.write(f"見つけた四字熟語：{len(found)}個 / 正解{max_count}個中")
        st.write(tier_message(len(found), max_count))
        st.caption("正解だった四字熟語：" + "　".join(st.session_state.solo_targets))

    st.divider()
    st.radio("次のカードの難易度", list(DIFFICULTY_SETTINGS.keys()),
             horizontal=True, key="solo_diff_select")
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
    for key in ["ai_hand", "ai_targets", "ai_difficulty", "ai_opponent_targets", "ai_result"]:
        st.session_state.pop(key, None)
    clear_board_state("aibattle")


def ai_play(difficulty, targets):
    prob = AI_FIND_PROB[difficulty]
    return [idiom for idiom in targets if random.random() < prob]


def run_ai():
    st.header("🤖 AI対戦モード")
    st.caption("AIも同じ仕組みの手札から四字熟語を探して勝負します。")

    difficulty = st.radio("難易度（自分とAI共通）", list(DIFFICULTY_SETTINGS.keys()),
                           horizontal=True, key="ai_diff_select")

    if "ai_hand" not in st.session_state:
        hand, targets = generate_hand(difficulty)
        st.session_state.ai_hand = hand
        st.session_state.ai_targets = targets
        st.session_state.ai_difficulty = difficulty

        _, opp_targets = generate_hand(difficulty)
        st.session_state.ai_opponent_targets = opp_targets

    found, finished = render_board(
        st.session_state.ai_hand, "aibattle",
        confirm_label="✅ 四字熟語として確定して勝負する",
    )

    if finished and "ai_result" not in st.session_state:
        ai_found = ai_play(st.session_state.ai_difficulty, st.session_state.ai_opponent_targets)
        st.session_state.ai_result = (list(found), ai_found)

    if "ai_result" in st.session_state:
        player_found, ai_found = st.session_state.ai_result
        st.divider()
        st.subheader("🏁 結果")
        c1, c2 = st.columns(2)
        with c1:
            st.write("**あなた**")
            st.write("　".join(player_found) if player_found else "（なし）")
            st.metric("見つけた数", len(player_found))
        with c2:
            st.write(f"**🤖 AI（{st.session_state.ai_difficulty}）**")
            st.write("　".join(ai_found) if ai_found else "（なし）")
            st.metric("見つけた数", len(ai_found))

        if len(player_found) > len(ai_found):
            st.balloons()
            st.success("🎉 あなたの勝ち！")
        elif len(ai_found) > len(player_found):
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
# オンライン対戦モード（同じサーバーに接続している人同士）
# ============================================================
ROOM_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "idiom_battle_rooms.json")
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
    clear_board_state("online")


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
            difficulty = st.radio("難易度", list(DIFFICULTY_SETTINGS.keys()),
                                   horizontal=True, key="online_host_diff")
            if st.button("🆕 部屋を作成する", key="online_create"):
                code = new_room_code()
                hand1, _ = generate_hand(difficulty)
                hand2, _ = generate_hand(difficulty)
                rooms = load_rooms()
                rooms[code] = {
                    "name1": host_name, "name2": None,
                    "hand1": hand1, "hand2": hand2,
                    "found1": None, "found2": None,
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
    found_key_room = "found1" if role == "host" else "found2"

    if not room[ready_key]:
        found, finished = render_board(
            st.session_state.online_hand, "online",
            confirm_label="✅ 四字熟語として確定して提出する",
        )
        if finished:
            fresh_rooms = load_rooms()
            fresh_room = fresh_rooms.get(code)
            if fresh_room:
                fresh_room[found_key_room] = list(found)
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
        f1, f2 = room["found1"], room["found2"]
        s1, s2 = len(f1), len(f2)

        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**{room['name1']}**")
            st.write("　".join(f1) if f1 else "（なし）")
            st.metric("見つけた数", s1)
        with c2:
            st.write(f"**{room['name2']}**")
            st.write("　".join(f2) if f2 else "（なし）")
            st.metric("見つけた数", s2)

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