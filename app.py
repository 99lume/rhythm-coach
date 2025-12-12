import streamlit as st
from auth import login_page, logout

# 页面配置必须在所有代码之前
st.set_page_config(page_title="RhythmCoach", page_icon="🎮", layout="wide")

# 初始化 Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# --- 1. 如果未登录，只显示登录页 ---
if not st.session_state.logged_in:
    login_page()
    st.stop() # 停止执行后续代码

# --- 2. 定义页面路由 ---
# 这里引用 views 文件夹里的文件路径
pages = {}

# 所有用户都能看到的页面
common_pages = [
    st.Page("views/public_marking.py", title="谱面标注 (公共)", icon="📍"),
    st.Page("views/user_recorder.py", title="我的打歌记录", icon="📝"),
    st.Page("views/user_report.py", title="能力诊断报告", icon="📊"),
    st.Page("views/user_feedback.py", title="反馈与报错", icon="💬"),
]

# 只有管理员能看到的页面
admin_pages = [
    st.Page("views/admin_manager.py", title="谱面库管理 (Admin)", icon="⚙️"),
]

# --- 3. 根据角色构建导航 ---
if st.session_state.role == "admin":
    # 管理员看所有
    pg = st.navigation({
        "管理后台": admin_pages,
        "用户功能": common_pages
    })
else:
    # 普通用户只能看用户功能
    pg = st.navigation({
        "功能菜单": common_pages
    })

# --- 4. 侧边栏显示用户信息 ---
with st.sidebar:
    st.write(f"👤 当前用户: **{st.session_state.username}**")
    if st.button("退出登录"):
        logout()

# --- 5. 运行选中的页面 ---
pg.run()