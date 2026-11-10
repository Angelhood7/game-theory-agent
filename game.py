import streamlit as st
import numpy as np
import matplotlib.pyplot as plt


# -------------------------- 策略库定义 --------------------------
def always_cooperate(history):
    return 'C'


def always_defect(history):
    return 'D'


def tit_for_tat(history):
    if len(history) == 0:
        return 'C'
    return history[-1][1]


def grim_trigger(history):
    if len(history) == 0:
        return 'C'
    # 对方只要背叛过一次，永远背叛
    for round in history:
        if round[1] == 'D':
            return 'D'
    return 'C'


def tit_for_two_tats(history):
    # 一报还两报：对方连续背叛两次才报复
    if len(history) < 2:
        return 'C'
    if history[-1][1] == 'D' and history[-2][1] == 'D':
        return 'D'
    return 'C'


def random_strategy(history):
    return np.random.choice(['C', 'D'])


strategy_dict = {
    "一报还一报 (Tit-for-Tat)": tit_for_tat,
    "永远合作": always_cooperate,
    "永远背叛": always_defect,
    "冷酷触发 (Grim Trigger)": grim_trigger,
    "一报还两报 (宽容版)": tit_for_two_tats,
    "随机策略": random_strategy
}


# -------------------------- 博弈核心逻辑 --------------------------
def play_game(strategy_a_func, strategy_b_func, rounds, payoff):
    history = []
    score_a = 0
    score_b = 0
    score_a_list = []
    score_b_list = []

    for i in range(rounds):
        # 双方各自根据历史决策
        move_a = strategy_a_func(history)
        # 构造对方视角的历史
        history_b = [(b, a) for a, b in history]
        move_b = strategy_b_func(history_b)

        # 计算收益
        if move_a == 'C' and move_b == 'C':
            sa, sb = payoff['R'], payoff['R']
        elif move_a == 'C' and move_b == 'D':
            sa, sb = payoff['S'], payoff['T']
        elif move_a == 'D' and move_b == 'C':
            sa, sb = payoff['T'], payoff['S']
        else:
            sa, sb = payoff['P'], payoff['P']

        score_a += sa
        score_b += sb
        score_a_list.append(score_a)
        score_b_list.append(score_b)
        history.append((move_a, move_b))

    return history, score_a, score_b, score_a_list, score_b_list


# -------------------------- 策略特性分析 --------------------------
def analyze_strategy(name, func):
    features = {}
    # 善良性：第一步是否合作
    features["善良性"] = "是" if func([]) == 'C' else "否"

    # 报复性：对方背叛后是否会反击
    test_history = [('C', 'D')]
    features["报复性"] = "是" if func(test_history) == 'D' else "否"

    # 宽容性：对方背叛后重新合作是否能恢复合作
    test_history2 = [('C', 'D'), ('D', 'C'), ('C', 'C')]
    features["宽容性"] = "是" if func(test_history2) == 'C' else "否"

    # 清晰性：规则是否明确可预测
    clear_set = ["一报还一报 (Tit-for-Tat)", "永远合作", "永远背叛", "冷酷触发 (Grim Trigger)"]
    features["清晰性"] = "高" if name in clear_set else "中/低"

    return features


# -------------------------- 页面UI --------------------------
st.set_page_config(page_title="囚徒困境合作演化仿真智能体", layout="wide")
st.title("🔄 迭代囚徒困境合作演化策略仿真智能体")
st.caption("基于Axelrod & Hamilton (1981)《合作的进化》经典理论 | 博弈论课程教学工具")

with st.expander("📖 智能体简介", expanded=True):
    st.markdown("""
    本智能体以**重复囚徒困境博弈**为核心场景，复现Axelrod锦标赛的经典研究框架。
    内置6种经典博弈策略，支持自定义博弈轮数与收益矩阵，可直观对比不同策略的演化结果，
    验证「合作如何在自利个体中自发涌现」的核心命题，辅助理解重复博弈、无名氏定理与演化稳定策略等知识点。
    """)

# 侧边栏参数设置
with st.sidebar:
    st.header("⚙️ 参数设置")
    rounds = st.slider("博弈轮数", min_value=10, max_value=200, value=100, step=10)

    st.subheader("收益矩阵 (T > R > P > S)")
    T = st.number_input("诱惑收益 T (背叛对方合作)", value=5.0, min_value=0.0)
    R = st.number_input("合作收益 R (双方合作)", value=3.0, min_value=0.0)
    P = st.number_input("背叛收益 P (双方背叛)", value=1.0, min_value=0.0)
    S = st.number_input("傻子收益 S (合作对方背叛)", value=0.0, min_value=0.0)
    payoff = {'T': T, 'R': R, 'P': P, 'S': S}

    st.subheader("选择对战策略")
    strategy_a_name = st.selectbox("策略A", list(strategy_dict.keys()), index=0)
    strategy_b_name = st.selectbox("策略B", list(strategy_dict.keys()), index=2)

    run_btn = st.button("▶️ 开始仿真", type="primary", use_container_width=True)

# 主区域
col1, col2 = st.columns([2, 1])

if run_btn:
    strategy_a_func = strategy_dict[strategy_a_name]
    strategy_b_func = strategy_dict[strategy_b_name]

    history, score_a, score_b, score_a_list, score_b_list = play_game(
        strategy_a_func, strategy_b_func, rounds, payoff
    )

    with col1:
        st.subheader("📈 累计得分演化曲线")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(range(1, rounds + 1), score_a_list, label=strategy_a_name, linewidth=2)
        ax.plot(range(1, rounds + 1), score_b_list, label=strategy_b_name, linewidth=2)
        ax.set_xlabel("博弈轮次")
        ax.set_ylabel("累计收益")
        ax.legend()
        ax.grid(alpha=0.3)
        st.pyplot(fig)

        st.subheader("📋 前20轮对战详情")
        detail_data = []
        for i in range(min(20, rounds)):
            detail_data.append({
                "轮次": i + 1,
                "策略A": history[i][0],
                "策略B": history[i][1],
                "A收益": score_a_list[i] - (score_a_list[i - 1] if i > 0 else 0),
                "B收益": score_b_list[i] - (score_b_list[i - 1] if i > 0 else 0)
            })
        st.dataframe(detail_data, use_container_width=True)

    with col2:
        st.subheader("🏆 最终结果")
        st.metric(label=f"{strategy_a_name} 总收益", value=f"{score_a:.1f}")
        st.metric(label=f"{strategy_b_name} 总收益", value=f"{score_b:.1f}")

        st.subheader("🧩 策略特性分析 (Axelrod四标准)")
        feat_a = analyze_strategy(strategy_a_name, strategy_a_func)
        feat_b = analyze_strategy(strategy_b_name, strategy_b_func)

        st.markdown(f"**{strategy_a_name}**")
        for k, v in feat_a.items():
            st.text(f"  {k}: {v}")

        st.markdown(f"**{strategy_b_name}**")
        for k, v in feat_b.items():
            st.text(f"  {k}: {v}")

st.divider()
st.caption(
    "参考文献：Axelrod, R., & Hamilton, W. D. (1981). The evolution of cooperation. Science, 211(4489), 1390-1396.")
