import streamlit as st
import pandas as pd
import time
import db_manager as db       # 引入数据库管家
import image_utils as img_host # 引入刚才写的图床工具

st.title("⚙️ 谱面库管理 (云端版)")
st.markdown("**管理员专用：在此上传新谱面，图片将自动托管至 CDN。**")

# --- 区域 1：上传新谱面 ---
with st.expander("📤 上传新谱面", expanded=True):
    with st.form("upload_chart_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            song_name = st.text_input("🎵 歌曲名称", placeholder="例如：Freedom Dive")
        with col2:
            difficulty = st.selectbox("⭐ 难度等级", ["Easy", "Normal", "Hard", "Expert", "Master"])
        
        uploaded_file = st.file_uploader("🖼️ 选择谱面长图", type=["png", "jpg", "jpeg"])
        
        submitted = st.form_submit_button("🚀 上传并保存")
        
        if submitted:
            if not (song_name and uploaded_file):
                st.error("请填写完整信息（歌名 + 图片）！")
            else:
                try:
                    with st.spinner("☁️ 正在将图片传输到 Cloudinary 服务器..."):
                        # 1. 生成一个干净的文件名标签 (去除特殊字符)
                        timestamp = int(time.time())
                        clean_name = "".join([c for c in song_name if c.isalnum() or c in (' ','-','_')]).strip()
                        file_tag = f"{clean_name}_{difficulty}_{timestamp}"
                        
                        # 2. 上传图片 -> 获取 URL
                        image_url = img_host.upload_image_to_cloud(uploaded_file, file_tag)
                        
                        if image_url:
                            # 3. 将 URL 和信息存入数据库
                            db.add_chart(song_name, difficulty, image_url)
                            
                            st.success(f"✅ 上传成功！")
                            st.caption(f"图片链接: {image_url}") # 调试用，让你看到生成的链接
                            time.sleep(1.5)
                            st.rerun()
                        else:
                            st.error("图片上传失败，请重试。")
                            
                except Exception as e:
                    st.error(f"系统错误: {e}")

# --- 区域 2：当前谱面库列表 ---
st.markdown("---")
st.subheader("📋 云端谱面库")

# 从数据库获取列表
df_charts = db.get_all_charts()

if not df_charts.empty:
    # 显示表格
    st.dataframe(
        df_charts[['song_id', 'song_name', 'difficulty', 'upload_time']], 
        use_container_width=True, 
        hide_index=True
    )
    
    # 删除功能
    with st.expander("🗑️ 删除谱面"):
        with st.form("delete_form"):
            # 制作选项列表：ID - 歌名 - 难度
            options = df_charts.apply(
                lambda x: f"ID:{x['song_id']} | {x['song_name']} ({x['difficulty']})", axis=1
            )
            selected_del = st.selectbox("选择要删除的谱面", options)
            
            if st.form_submit_button("确认删除", type="primary"):
                try:
                    # 解析 ID
                    del_id = int(selected_del.split("|")[0].replace("ID:", "").strip())
                    
                    # 从数据库删除
                    db.delete_chart(del_id)
                    
                    st.success("已从数据库移除记录。")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"删除失败: {e}")
else:
    st.info("谱面库为空，请在上方上传第一张谱面。")