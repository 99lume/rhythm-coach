import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import db_manager as db

# ================= 样式优化 =================
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    footer {visibility: hidden;}
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        min-width: 350px !important;
    }
</style>
""", unsafe_allow_html=True)

# ================= HTML/JS 图片查看器 (URL版) =================
def display_html_viewer(image_url, height=850):
    """
    直接使用云端 URL 显示图片，无需本地读取
    """
    try:
        html_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ margin: 0; padding: 0; background-color: #ffffff; overflow: hidden; }}
                #container {{
                    width: 100vw; height: {height}px;
                    display: flex; justify-content: center; align-items: center;
                    overflow: hidden; cursor: grab;
                    border: 1px solid #e0e0e0; border-radius: 8px;
                }}
                #container:active {{ cursor: grabbing; }}
                #target-img {{
                    max-width: 95%; max-height: 95%;
                    transition: transform 0.05s linear; transform-origin: 0 0;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                }}
                .controls {{
                    position: absolute; top: 10px; right: 20px; z-index: 100;
                    background: rgba(0,0,0,0.6); padding: 5px 10px; border-radius: 20px;
                    color: white; font-family: sans-serif; font-size: 12px; pointer-events: none;
                }}
            </style>
        </head>
        <body>
            <div class="controls">🖱️ 滚轮缩放 | ✋ 左键拖拽 | 双击复位</div>
            <div id="container">
                <img id="target-img" src="{image_url}" draggable="false">
            </div>
            <script>
                const container = document.getElementById('container');
                const img = document.getElementById('target-img');
                let scale = 1; let panning = false;
                let pointX = 0; let pointY = 0; let startX = 0; let startY = 0;
                function setTransform() {{ img.style.transform = `translate(${{pointX}}px, ${{pointY}}px) scale(${{scale}})`; }}
                container.onmousedown = function (e) {{ e.preventDefault(); startX = e.clientX - pointX; startY = e.clientY - pointY; panning = true; }};
                container.onmouseup = function (e) {{ panning = false; }};
                container.onmouseleave = function (e) {{ panning = false; }};
                container.onmousemove = function (e) {{ e.preventDefault(); if (!panning) return; pointX = (e.clientX - startX); pointY = (e.clientY - startY); setTransform(); }};
                container.onwheel = function (e) {{ e.preventDefault(); const xs = (e.clientX - pointX) / scale; const ys = (e.clientY - pointY) / scale; const delta = -e.deltaY; (delta > 0) ? (scale *= 1.1) : (scale /= 1.1); if (scale < 0.1) scale = 0.1; pointX = e.clientX - xs * scale; pointY = e.clientY - ys * scale; setTransform(); }};
                container.ondblclick = function(e) {{ scale = 1; pointX = 0; pointY = 0; img.style.transform = `translate(0px, 0px) scale(1)`; }};
            </script>
        </body>
        </html>
        """
        components.html(html_code, height=height + 20)
    except Exception as e:
        st.error(f"加载失败: {e}")

# ================= 主程序逻辑 =================

# 1. 从数据库加载谱面列表
charts_df = db.get_all_charts()

if charts_df.empty:
    st.warning("⚠️ 谱面库为空，请联系管理员上传谱面。")
    st.stop()

TECH_TAGS = [
    "交互 (Trill)", "楼梯 (Stairs)", "纵连 (Jack)", "大跨度 (Jump)", 
    "多押 (Chord)", "变速 (Soflan)", "读谱难 (Reading)", 
    "耐力 (Stamina)", "锁手 (Tech)", "各显神通 (Gimmick)"
]

current_user = st.session_state.get("username", "Unknown")
current_role = st.session_state.get("role", "user")

# ================= 侧边栏：控制台 =================
with st.sidebar:
    st.header("🎛️ 标注控制台")
    st.caption(f"当前身份: {current_user}")
    
    # --- 1. 谱面选择 ---
    st.markdown("### 1. 谱面选择")
    chart_options = charts_df.apply(lambda x: f"{x['song_name']} ({x['difficulty']})", axis=1)
    selected_label = st.selectbox("工作曲目", chart_options, label_visibility="collapsed")
    
    # 获取选中行数据
    selected_row = charts_df[charts_df.apply(lambda x: f"{x['song_name']} ({x['difficulty']})", axis=1) == selected_label].iloc[0]
    current_chart_id = int(selected_row['song_id'])
    current_chart_name = selected_row['song_name']
    
    # 关键：直接获取 URL
    image_url = selected_row['chart_image_path']

    st.markdown("---")
    
    # --- 2. 录入表单 ---
    st.markdown("### 2. 新增标注")
    with st.form("annotation_form"):
        st.caption("👈 请在左侧大图中查看小节号")
        c1, c2 = st.columns(2)
        start_sec = c1.number_input("起始 #", min_value=1, value=1)
        end_sec = c2.number_input("结束 #", min_value=1, value=1)
        
        selected_tags = st.multiselect("技术特征*", options=TECH_TAGS)
        expert_rating = st.slider("难度 (1-5)", 1, 5, 3)
        desc = st.text_area("描述", height=70, placeholder="备注...") # height >= 68
        
        if st.form_submit_button("💾 保存标注", type="primary"):
            if end_sec < start_sec:
                st.error("结束 < 起始")
            elif not selected_tags:
                st.error("未选标签")
            else:
                # 写入数据库
                try:
                    db.add_annotation({
                        "chart_id": current_chart_id,
                        "chart_name": current_chart_name,
                        "difficulty": selected_row['difficulty'],
                        "start_section": start_sec,
                        "end_section": end_sec,
                        "tags": ",".join(selected_tags),
                        "desc": desc,
                        "expert_rating": expert_rating,
                        "annotator": current_user
                    })
                    st.success("已保存到云端")
                    st.rerun()
                except Exception as e:
                    st.error(f"保存失败: {e}")

    # --- 3. 历史记录 (从数据库读取) ---
    st.markdown("---")
    st.markdown("### 3. 社区标注记录")
    
    # 从数据库查当前歌曲的标注
    current_anns = db.get_annotations(chart_id=current_chart_id)
    
    if not current_anns.empty:
        st.caption(f"共 {len(current_anns)} 条 (由社区成员贡献)")
        # 倒序显示
        for idx, row in current_anns[::-1].iterrows():
            contributor = row['annotator'] if row['annotator'] else '未知'
            
            label = f"#{row['start_section']}-{row['end_section']} {row['tags'].split(',')[0]} (by {contributor})"
            
            with st.expander(label):
                st.write(f"**贡献者**: {contributor}")
                st.write(f"**标签**: {row['tags']}")
                st.write(f"**描述**: {row['desc_text']}") # 注意：数据库字段名叫 desc_text
                st.write(f"**难度**: {'⭐'*int(row['expert_rating'])}")
                
                # 删除权限控制
                can_delete = (current_role == 'admin') or (str(contributor) == str(current_user))
                
                if can_delete:
                    if st.button("🗑️ 删除", key=f"del_{row['annotation_id']}"):
                        db.delete_annotation(row['annotation_id'])
                        st.success("删除成功")
                        st.rerun()
                else:
                    st.caption("🔒 仅标注者可删除")
    else:
        st.info("暂无标注")

# ================= 主界面：大图展示 =================
if image_url:
    display_html_viewer(image_url, height=850)
else:
    st.error("❌ 图片链接无效")