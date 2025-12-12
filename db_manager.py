import streamlit as st
from sqlalchemy import text

# 1. 获取数据库连接
def get_connection():
    # Streamlit 会自动读取 secrets.toml 里的配置
    return st.connection("mysql", type="sql")

# ================= 用户管理 =================
def get_user(username):
    """根据用户名查找用户"""
    conn = get_connection()
    # ttl=0 表示不缓存，确保每次都查最新数据
    df = conn.query("SELECT * FROM users WHERE username = :u", params={"u": username}, ttl=0)
    return df

def create_user(username, password_hash):
    """注册新用户"""
    conn = get_connection()
    with conn.session as s:
        s.execute(
            text("INSERT INTO users (username, password, role) VALUES (:u, :p, 'user')"),
            {"u": username, "p": password_hash}
        )
        s.commit()

# ================= 1. 谱面库管理 =================
def get_all_charts():
    conn = get_connection()
    # ttl=0 表示不缓存，每次都强制去数据库查最新的
    return conn.query("SELECT * FROM charts", ttl=0)

def add_chart(song_name, difficulty, filename):
    conn = get_connection()
    with conn.session as s:
        s.execute(
            text("INSERT INTO charts (song_name, difficulty, chart_image_path) VALUES (:n, :d, :p)"),
            {"n": song_name, "d": difficulty, "p": filename}
        )
        s.commit()

def delete_chart(song_id):
    conn = get_connection()
    with conn.session as s:
        s.execute(text("DELETE FROM charts WHERE song_id = :id"), {"id": song_id})
        s.commit()

# ================= 2. 标注管理 =================
def get_annotations(chart_id=None):
    conn = get_connection()
    sql = "SELECT * FROM annotations"
    params = {}
    if chart_id:
        sql += " WHERE chart_id = :id"
        params = {"id": chart_id}
    return conn.query(sql, params=params, ttl=0)

def add_annotation(data_dict):
    conn = get_connection()
    with conn.session as s:
        s.execute(
            text("""
                INSERT INTO annotations 
                (chart_id, chart_name, difficulty, start_section, end_section, tags, desc_text, expert_rating, annotator)
                VALUES (:chart_id, :chart_name, :difficulty, :start_section, :end_section, :tags, :desc, :expert_rating, :annotator)
            """),
            data_dict
        )
        s.commit()

def delete_annotation(ann_id):
    conn = get_connection()
    with conn.session as s:
        s.execute(text("DELETE FROM annotations WHERE annotation_id = :id"), {"id": ann_id})
        s.commit()

# ================= 3. 打歌记录管理 =================
def get_user_records(username):
    conn = get_connection()
    return conn.query("SELECT * FROM play_records WHERE username = :u", params={"u": username}, ttl=0)

def add_play_record(data_dict):
    conn = get_connection()
    with conn.session as s:
        s.execute(
            text("""
                INSERT INTO play_records 
                (username, chart_name, miss_section, miss_count, cause, detected_tags, notes)
                VALUES (:u, :cn, :ms, :mc, :cause, :tags, :notes)
            """),
            data_dict
        )
        s.commit()

def delete_play_record(rec_id):
    conn = get_connection()
    with conn.session as s:
        s.execute(text("DELETE FROM play_records WHERE record_id = :id"), {"id": rec_id})
        s.commit()

# ================= 4. 【新功能】用户反馈 =================
def add_feedback(username, feedback_type, content):
    conn = get_connection()
    with conn.session as s:
        s.execute(
            text("INSERT INTO user_feedback (username, feedback_type, content) VALUES (:u, :t, :c)"),
            {"u": username, "t": feedback_type, "c": content}
        )
        s.commit()