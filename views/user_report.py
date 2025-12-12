import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import db_manager as db

st.title("📊 个人能力诊断报告")

# 1. 从数据库获取数据
my_records = db.get_play_records(st.session_state.username)

if my_records.empty:
    st.info(f"Hi, {st.session_state.username}，你还没有提交过任何实战记录，无法生成报告。")
    st.stop()

# 2. 数据清洗 (Tags 拆分)
# 去除"常规段落"
valid_records = my_records[my_records['detected_tags'] != '常规段落'].copy()

# 如果没有任何包含Tag的记录
if valid_records.empty:
    st.warning("目前的记录中没有包含技术标签（都是常规段落），无法生成雷达图。")
else:
    # 拆分 Tags
    tags_expanded = valid_records.assign(tag=valid_records['detected_tags'].str.split(',')).explode('tag')
    tags_expanded['tag'] = tags_expanded['tag'].str.strip() # 去除空格

    # ================= 雷达图 =================
    st.header("1. 弱点雷达图")
    col1, col2 = st.columns([3, 2])

    with col1:
        # 统计每个Tag的失误总数
        tag_stats = tags_expanded.groupby('tag')['miss_count'].sum().reset_index()
        
        if not tag_stats.empty:
            # 简单算法：假设基准分100，每失误一次扣分 (为了演示效果)
            # 实际可以根据你的统计学模型调整
            max_miss = tag_stats['miss_count'].max()
            # 归一化反转：失误越多，分数越低
            tag_stats['score'] = 100 - (tag_stats['miss_count'] / max_miss * 80) 
            
            fig = go.Figure(data=go.Scatterpolar(
                r=tag_stats['score'],
                theta=tag_stats['tag'],
                fill='toself',
                name='当前能力'
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False,
                title="各维度技术能力评分 (分数越低表示该项越薄弱)"
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📉 失误原因分布")
        cause_counts = my_records['cause'].value_counts().reset_index()
        cause_counts.columns = ['原因', '次数']
        fig_pie = px.pie(cause_counts, values='次数', names='原因', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

# ================= 趋势图 =================
st.markdown("---")
st.header("2. 近期状态趋势")

# 按日期统计总失误
daily_stats = my_records.groupby('date_time')['miss_count'].sum().reset_index()
if not daily_stats.empty:
    fig_line = px.line(daily_stats, x="date_time", y="miss_count", 
                       title="每日总失误数变化", markers=True)
    st.plotly_chart(fig_line, use_container_width=True)