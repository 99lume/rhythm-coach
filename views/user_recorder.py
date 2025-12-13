import streamlit as st
import pandas as pd
import db_manager as db

st.title("📊 我的游玩记录")

# 读取用户
current_user = st.session_state.get("username", None)
if not current_user:
    st.error("请先登录")
    st.stop()

# 读取谱面列表
charts_df = db.get_all_charts()
if charts_df.empty:
    st.warning("⚠️ 谱面库空")
    st.stop()

# ============================ 侧边栏筛选区域 ============================
with st.sidebar:
    st.header("🎛️ 筛选曲目")

    # ① 搜索歌名
    search_text = st.text_input("搜索歌名", placeholder="输入关键词…")

    # ② 难度筛选
    all_diff = sorted(charts_df["difficulty"].unique())
    selected_diff = st.multiselect("难度", all_diff, default=all_diff)

    # ③ 等级筛选（单一等级）
    all_lv = sorted(charts_df["level"].dropna().unique().tolist())
    selected_lv = st.selectbox(
        "选择等级 Lv", ["全部"] + [str(lv) for lv in all_lv]
    )

    # ④ 等级排序方式
    sort_mode = st.radio(
        "等级排序方式",
        ["默认", "从低到高 (升序)", "从高到低 (降序)"]
    )

# ============================ 筛选逻辑 ============================

filtered = charts_df[
    charts_df["difficulty"].isin(selected_diff) &
    charts_df["song_name"].str.contains(search_text, case=False, na=False)
]

if selected_lv != "全部":
    filtered = filtered[filtered["level"] == int(selected_lv)]

# 排序
if sort_mode == "从低到高 (升序)":
    filtered = filtered.sort_values(by="level", ascending=True)
elif sort_mode == "从高到低 (降序)":
    filtered = filtered.sort_values(by="level", ascending=False)

# 空过滤提示
if filtered.empty:
    st.warning("没有符合条件的谱面，请调整筛选条件。")
    st.stop()

# ============================ 下拉选择曲目 ============================
chart_options = filtered.apply(
    lambda x: f"ID:{x['song_id']} | {x['song_name']} ({x['difficulty']}, Lv{x['level']})",
    axis=1
)

selected_label = st.selectbox("选择你游玩的谱面", chart_options)

selected_row = filtered[
    chart_options == selected_label
].iloc[0]

chart_id = selected_row["song_id"]
song_name = selected_row["song_name"]
difficulty = selected_row["difficulty"]
level = selected_row["level"]

st.success(f"🎵 当前选择：{song_name} ({difficulty}, Lv{level})")

# ============================ 记录技术练习表单 ============================
st.markdown("---")
st.subheader("📝 记录我的练习")

with st.form("record_form"):
    col1, col2 = st.columns(2)

    # 记录练习次数
    practice_count = col1.number_input("练习次数", min_value=0, step=1)

    # 记录失误段落
    miss_section = st.number_input("失误段落", min_value=1, step=1, help="请输入失误的段落编号")

    # 选择失误原因
    all_reasons = ["读谱没看清", "手速跟不上", "节奏难以把控", "手滑/断触", "耐力耗尽", "初见杀", "不熟悉这类配置", "其他"]
    cause = st.selectbox("失误原因", all_reasons)

    # 备注
    comment = st.text_area("备注（可选）", height=80)

    submitted = st.form_submit_button("保存练习记录")

    if submitted:
        try:
            db.add_play_record({
                "username": current_user,
                "chart_id": chart_id,
                "song_name": song_name,
                "difficulty": difficulty,
                "level": level,
                "practice_count": practice_count,
                "miss_section": miss_section,
                "cause": cause,
                "comment": comment
            })
            st.success("🎉 已成功记录练习情况")
            st.rerun()
        except Exception as e:
            st.error(f"保存失败: {e}")

# ============================ 我的历史记录 ============================
st.markdown("---")
st.subheader("📜 我的历史记录")

records = db.get_play_records(current_user)

if not records.empty:
    st.dataframe(
        records[["song_name", "difficulty", "level", "practice_count", "miss_section", "cause", "comment", "play_time"]],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("暂无记录")
