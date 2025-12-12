import streamlit as st
import db_manager as db

st.title("💬 用户反馈与报错")
st.markdown("遇到 Bug 或者有功能建议？请告诉我们！")

with st.form("feedback_form"):
    # 选择反馈类型
    fb_type = st.selectbox("反馈类型", ["🐛 Bug 报错", "💡 功能建议", "📝 其他"])
    
    # 填写内容
    content = st.text_area("详细描述", height=150, placeholder="请详细描述你遇到的问题，或你想要的新功能...")
    
    submitted = st.form_submit_button("提交反馈", type="primary")
    
    if submitted:
        if not content:
            st.error("请填写描述内容！")
        else:
            try:
                # 调用数据库管家写入数据
                db.add_feedback(
                    username=st.session_state.username,
                    feedback_type=fb_type,
                    content=content
                )
                st.success("✅ 反馈已提交！感谢你的建议。")
            except Exception as e:
                st.error(f"提交失败，请联系管理员: {e}")