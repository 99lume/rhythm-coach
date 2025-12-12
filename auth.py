import streamlit as st
import hashlib
import db_manager as db  # 引入刚才写的数据库管家

def hash_password(password):
    return hashlib.sha256(str(password).encode()).hexdigest()

def login_page():
    st.header("🔐 用户登录 (云端版)")
    
    tab1, tab2 = st.tabs(["登录", "注册新用户"])
    
    # --- 登录逻辑 ---
    with tab1:
        with st.form("login_form"):
            username = st.text_input("用户名")
            password = st.text_input("密码", type="password")
            submitted = st.form_submit_button("登录", type="primary")
            
            if submitted:
                # 1. 去数据库查找这个用户
                user_df = db.get_user(username)
                
                if not user_df.empty:
                    # 2. 检查密码是否匹配
                    stored_password = user_df.iloc[0]['password']
                    input_hash = hash_password(password)
                    
                    if stored_password == input_hash:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.role = user_df.iloc[0]['role']
                        st.success("登录成功！")
                        st.rerun()
                    else:
                        st.error("密码错误")
                else:
                    st.error("用户不存在")

    # --- 注册逻辑 ---
    with tab2:
        with st.form("register_form"):
            new_user = st.text_input("设置用户名")
            new_pass = st.text_input("设置密码", type="password")
            confirm_pass = st.text_input("确认密码", type="password")
            reg_submitted = st.form_submit_button("注册")
            
            if reg_submitted:
                # 1. 检查用户名是否已存在
                existing_user = db.get_user(new_user)
                
                if not existing_user.empty:
                    st.error("该用户名已被注册")
                elif new_pass != confirm_pass:
                    st.error("两次密码不一致")
                elif not new_user or not new_pass:
                    st.error("不能为空")
                else:
                    # 2. 写入数据库
                    try:
                        db.create_user(new_user, hash_password(new_pass))
                        st.success("注册成功！请返回登录页登录。")
                    except Exception as e:
                        st.error(f"注册失败: {e}")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.rerun()