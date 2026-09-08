import random
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

# 対戦モード（AI対戦・オンライン対戦）だけに適用する制限時間。
# 練習であるソロモードには時間制限を設けない。
# 難易度が上がるほど探すべき四字熟語の数が増えるため、時間も長くする。
TIME_LIMIT_SECONDS = {"かんたん": 60, "ふつう": 90, "むずかしい": 120}


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
def render_board(hand, prefix, confirm_label="✅ 四字熟語として確定する", time_limit_seconds=None):
    status_key = f"{prefix}_status"
    order_key = f"{prefix}_order"
    found_key = f"{prefix}_found"
    fail_key = f"{prefix}_fail"
    deadline_key = f"{prefix}_deadline"

    if status_key not in st.session_state:
        st.session_state[status_key] = [AVAILABLE] * len(hand)
        st.session_state[order_key] = []
        st.session_state[found_key] = []
        st.session_state[fail_key] = None

    if time_limit_seconds is not None and deadline_key not in st.session_state:
        st.session_state[deadline_key] = time.time() + time_limit_seconds

    status = st.session_state[status_key]
    order = st.session_state[order_key]
    found = st.session_state[found_key]

    # ---- 制限時間の表示（対戦モードのみ）----
    timed_out = False
    if time_limit_seconds is not None:
        remaining = st.session_state[deadline_key] - time.time()
        if remaining <= 0:
            remaining = 0
            timed_out = True
        mm, ss = divmod(int(remaining), 60)
        st.progress(min(1.0, max(0.0, remaining / time_limit_seconds)))
        st.write(f"⏳ 残り時間：{mm:02d}:{ss:02d}")
        if timed_out:
            st.error("⏰ 時間切れです！ここまでの結果で確定します。")

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
            if col.button(f"【{ch}】", key=f"{prefix}_btn_{i}", disabled=timed_out):
                order.remove(i)
                status[i] = AVAILABLE
                st.session_state[fail_key] = None
        else:
            if col.button(ch, key=f"{prefix}_btn_{i}", disabled=timed_out):
                order.append(i)
                status[i] = SELECTED
                st.session_state[fail_key] = None

    selected_word = "".join(hand[i] for i in order)
    st.write("**いま選んでいる文字**")
    st.info(selected_word if selected_word else "（まだ選んでいません）")

    c1, c2, c3 = st.columns(3)
    can_confirm = len(order) == 4
    if c1.button(confirm_label, key=f"{prefix}_confirm", disabled=(not can_confirm or timed_out)):
        if is_valid_idiom([hand[i] for i in order]):
            found.append(selected_word)
            for i in order:
                status[i] = USED
            order.clear()
            st.session_state[fail_key] = None
            st.success(f"「{selected_word}」は正しい四字熟語でした！")
        else:
            st.session_state[fail_key] = selected_word

    if c2.button("⬅️ 1文字戻す", key=f"{prefix}_undo", disabled=timed_out):
        if order:
            last = order.pop()
            status[last] = AVAILABLE
            st.session_state[fail_key] = None

    if c3.button("🔄 選択をリセット", key=f"{prefix}_clear", disabled=timed_out):
        for i in order:
            status[i] = AVAILABLE
        order.clear()
        st.session_state[fail_key] = None

    if st.session_state.get(fail_key):
        st.warning(f"「{st.session_state[fail_key]}」は四字熟語として認識されませんでした。")

    remaining_tiles = sum(1 for s in status if s == AVAILABLE)
    st.caption(f"残り未使用の漢字：{remaining_tiles}枚")

    finish_clicked = st.button("🏁 ここで終了する（お手上げ）", key=f"{prefix}_finish", disabled=timed_out)
    no_more_moves = remaining_tiles < 4 and len(order) < 4
    finished = finish_clicked or no_more_moves or timed_out

    # 制限時間中はカウントダウンのために1秒ごとに自動更新する
    if time_limit_seconds is not None and not finished:
        time.sleep(1)
        st.rerun()

    return found, finished


def clear_board_state(prefix):
    for key in [f"{prefix}_status", f"{prefix}_order", f"{prefix}_found", f"{prefix}_fail",
                f"{prefix}_deadline"]:
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
    c1, c2 = st.columns(2)
    if c1.button("🧑‍🎓 ソロモード\n(練習)", use_container_width=True):
        st.session_state.app_mode = "solo"
        st.rerun()
    if c2.button("🤖 AI対戦モード", use_container_width=True):
        st.session_state.app_mode = "ai"
        st.rerun()

    st.caption("💡 手札には必ず、選んだ難易度の個数ぶんの「正解の四字熟語」が隠れています。")


# ============================================================
# ソロモード
# ============================================================
def reset_solo():
    for key in ["solo_stage", "solo_hand", "solo_targets", "solo_difficulty", "solo_done"]:
        st.session_state.pop(key, None)
    clear_board_state("solo")


def run_solo_difficulty_select():
    """ソロモードに入って最初に表示する、難易度選択の画面。"""
    st.header("🧑‍🎓 ソロモード（練習）")
    st.caption("一人で好きなだけ練習できるモードです。時間制限はありません。"
               "まずは難易度を選んでください。")

    difficulty = st.radio("難易度", list(DIFFICULTY_SETTINGS.keys()),
                           horizontal=True, key="solo_diff_select")
    cfg = DIFFICULTY_SETTINGS[difficulty]
    st.write(f"・隠れている四字熟語：{cfg['idiom_count']}個　"
             f"・ダミー漢字：{cfg['decoy_count']}枚")

    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("▶️ この難易度で始める", key="solo_start", type="primary"):
        hand, targets = generate_hand(difficulty)
        st.session_state.solo_hand = hand
        st.session_state.solo_targets = targets
        st.session_state.solo_difficulty = difficulty
        st.session_state.solo_stage = "play"
        st.rerun()
    if c2.button("🏠 メニューに戻る", key="solo_menu_from_diff"):
        reset_solo()
        go_menu()
        st.rerun()


def run_solo_play():
    st.header("🧑‍🎓 ソロモード（練習）")
    st.caption(f"難易度：{st.session_state.solo_difficulty}"
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
        missed = [t for t in st.session_state.solo_targets if t not in found]
        if missed:
            st.warning("見つけられなかったのはこの四字熟語！　" + "　".join(missed))
        else:
            st.success("すべての四字熟語を見つけました！")

    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("🎲 難易度を選び直す", key="solo_new"):
        reset_solo()
        st.rerun()
    if c2.button("🏠 メニューに戻る", key="solo_menu"):
        reset_solo()
        go_menu()
        st.rerun()


def run_solo():
    stage = st.session_state.get("solo_stage", "difficulty")
    if stage == "difficulty":
        run_solo_difficulty_select()
    else:
        run_solo_play()


# ============================================================
# AI対戦モード
# ============================================================
def reset_ai():
    for key in ["ai_stage", "ai_hand", "ai_targets", "ai_difficulty",
                "ai_opponent_targets", "ai_result"]:
        st.session_state.pop(key, None)
    clear_board_state("aibattle")


def ai_play(difficulty, targets):
    prob = AI_FIND_PROB[difficulty]
    return [idiom for idiom in targets if random.random() < prob]


def run_ai_difficulty_select():
    """AI対戦モードに入って最初に表示する、難易度選択の画面。"""
    st.header("🤖 AI対戦モード")
    st.caption("まずは難易度を選んでください。難易度が上がるほど、探すべき四字熟語の数と"
               "制限時間の両方が増えます。")

    difficulty = st.radio("難易度", list(DIFFICULTY_SETTINGS.keys()),
                           horizontal=True, key="ai_diff_select")
    cfg = DIFFICULTY_SETTINGS[difficulty]
    st.write(f"・隠れている四字熟語：{cfg['idiom_count']}個　"
             f"・ダミー漢字：{cfg['decoy_count']}枚　"
             f"・制限時間：{TIME_LIMIT_SECONDS[difficulty]}秒")

    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("▶️ この難易度で対戦を始める", key="ai_start", type="primary"):
        hand, targets = generate_hand(difficulty)
        st.session_state.ai_hand = hand
        st.session_state.ai_targets = targets
        st.session_state.ai_difficulty = difficulty

        _, opp_targets = generate_hand(difficulty)
        st.session_state.ai_opponent_targets = opp_targets

        st.session_state.ai_stage = "play"
        st.rerun()
    if c2.button("🏠 メニューに戻る", key="ai_menu_from_diff"):
        reset_ai()
        go_menu()
        st.rerun()


def run_ai_play():
    st.header("🤖 AI対戦モード")
    time_limit = TIME_LIMIT_SECONDS[st.session_state.ai_difficulty]

    # ラウンドがまだ終わっていない間だけ、時間制限つきの盤面を描画する。
    # （終わった後もこのブロックを描画し続けると、内部の自動更新タイマーが
    #   　動き続けて「メニューに戻る」などのボタン操作が効かなくなるため）
    if "ai_result" not in st.session_state:
        st.caption(f"難易度：{st.session_state.ai_difficulty}　"
                   f"⏱️ 制限時間：{time_limit}秒（難易度が上がるほど長くなります）")

        found, finished = render_board(
            st.session_state.ai_hand, "aibattle",
            confirm_label="✅ 四字熟語として確定して勝負する",
            time_limit_seconds=time_limit,
        )

        if finished:
            # お手上げ・手詰まり・時間切れ、いずれの場合もここでタイマーを止めて確定する
            ai_found = ai_play(st.session_state.ai_difficulty, st.session_state.ai_opponent_targets)
            st.session_state.ai_result = (list(found), ai_found)
            st.rerun()

    if "ai_result" in st.session_state:
        player_found, ai_found = st.session_state.ai_result
        player_missed = [t for t in st.session_state.ai_targets if t not in player_found]
        ai_missed = [t for t in st.session_state.ai_opponent_targets if t not in ai_found]

        st.divider()
        st.subheader("🏁 結果")
        c1, c2 = st.columns(2)
        with c1:
            st.write("**あなた**")
            st.write("　".join(player_found) if player_found else "（なし）")
            st.metric("見つけた数", len(player_found))
            if player_missed:
                st.warning("見つけられなかったのはこの四字熟語！　" + "　".join(player_missed))
            else:
                st.success("すべて見つけました！")
        with c2:
            st.write(f"**🤖 AI（{st.session_state.ai_difficulty}）**")
            st.write("　".join(ai_found) if ai_found else "（なし）")
            st.metric("見つけた数", len(ai_found))
            if ai_missed:
                st.caption("AIが見つけられなかった四字熟語：" + "　".join(ai_missed))

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


def run_ai():
    stage = st.session_state.get("ai_stage", "difficulty")
    if stage == "difficulty":
        run_ai_difficulty_select()
    else:
        run_ai_play()


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
else:
    st.session_state.app_mode = "menu"
    st.rerun()