import streamlit as st
import pandas as pd
import time
import db_manager as db

st.title(f"📝 {st.session_state.username} 的实战记录")
st.caption("数据实时同步至云端数据库。")

# 1. 获取基础数据
charts_df = db.get_all_charts()
all_anns = db.get_annotations() # 获取所有标注用于匹配

if charts_df.empty:
    st.warning("暂无谱面数据。")
    st.stop()

# ----------------- 左侧：输入区域 -----------------
col_input, col_history = st.columns([1, 1.2])

with col_input:
    st.subheader("➕ 新增记录")
    with st.container(border=True):
        # 选择歌曲
        chart_name = st.selectbox("1. 选择歌曲", charts_df['song_name'].unique())
        
        # 智能分析提示
        current_patterns = pd.DataFrame()
        if not all_anns.empty:
            current_patterns = all_anns[all_anns['chart_name'] == chart_name]
        
        with st.form("record_form"):
            col1, col2 = st.columns(2)
            with col1:
                miss_section = st.number_input("失误段落 #", min_value=1, step=1)
            with col2:
                miss_count = st.number_input("失误数", min_value=1, step=1)
            
            cause = st.selectbox("失误原因", ["读谱没看清", "手速跟不上", "节奏乱了", "手滑/断触", "耐力耗尽", "初见杀"])
            notes = st.text_input("备注 (可选)")
            
            # 智能匹配逻辑
            detected_tags_list = ["常规段落"]
            if not current_patterns.empty:
                matched = current_patterns[
                    (current_patterns['start_section'] <= miss_section) & 
                    (current_patterns['end_section'] >= miss_section)
                ]
                if not matched.empty:
                    raw_tags = matched.iloc[0]['tags']
                    detected_tags_list = raw_tags.split(',') if raw_tags else []
                    st.info(f"💡 系统分析：此段落包含 **{' + '.join(detected_tags_list)}** 难点")
            
            if st.form_submit_button("🚀 提交记录", type="primary"):
                try:
                    db.add_play_record({
                        "u": st.session_state.username,
                        "cn": chart_name,
                        "ms": miss_section,
                        "mc": miss_count,
                        "cause": cause,
                        "tags": ",".join(detected_tags_list),
                        "notes": notes
                    })
                    st.success("✅ 已保存到云端")
                    st.rerun()
                except Exception as e:
                    st.error(f"保存失败: {e}")

# ----------------- 右侧：历史记录 -----------------
with col_history:
    st.subheader("📜 我的云端记录")
    
    # 从数据库获取记录
    my_records = db.get_user_records(st.session_state.username)
    
    if not my_records.empty:
        # 倒序遍历
        for index, row in my_records[::-1].iterrows():
            rec_title = f"{row['date_time']} | {row['chart_name']} (段落 #{row['miss_section']})"
            
            with st.expander(rec_title, expanded=False):
                c1, c2, c3 = st.columns([2, 2, 1])
                with c1:
                    st.write(f"**失误:** {row['miss_count']}")
                    st.write(f"**原因:** {row['cause']}")
                with c2:
                    st.write(f"**标签:** {row['detected_tags']}")
                with c3:
                    st.write("")
                    if st.button("🗑️ 删除", key=f"del_{row['record_id']}"):
                        db.delete_play_record(row['record_id'])
                        st.success("已删除")
                        st.rerun()
    else:
        st.info("暂无记录。")