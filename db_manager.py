import streamlit as st
import pandas as pd
from sqlalchemy import text

# =========================================================
# 1. 获取数据库连接
# =========================================================
def get_connection():
    return st.connection("mysql", type="sql")

# =========================================================
# 2. 用户管理
# =========================================================
def get_user(username):
    conn = get_connection()
    return conn.query(
        "SELECT * FROM users WHERE username = :u",
        params={"u": username},
        ttl=0
    )

def create_user(username, password_hash):
    conn = get_connection()
    with conn.session as s:
        s.execute(
            text("INSERT INTO users (username, password, role) VALUES (:u, :p, 'user')"),
            {"u": username, "p": password_hash}
        )
        s.commit()

# =========================================================
# 3. 谱面库管理
# =========================================================
def get_all_charts():
    conn = get_connection()
    return conn.query("SELECT * FROM charts", ttl=0)

def add_chart(song_name, difficulty, level, filename):
    conn = get_connection()
    with conn.session as s:
        s.execute(
            text("""
                INSERT INTO charts (song_name, difficulty, level, chart_image_path)
                VALUES (:n, :d, :l, :p)
            """),
            {"n": song_name, "d": difficulty, "l": level, "p": filename}
        )
        s.commit()

def delete_chart(song_id):
    conn = get_connection()
    with conn.session as s:
        s.execute(text("DELETE FROM charts WHERE song_id = :id"), {"id": song_id})
        s.commit()

# =========================================================
# 4. 标注管理
# =========================================================
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
                (chart_id, chart_name, difficulty, start_section, end_section,
                 tags, desc_text, expert_rating, annotator)
                VALUES (:chart_id, :chart_name, :difficulty, :start_section,
                        :end_section, :tags, :desc, :expert_rating, :annotator)
            """),
            data_dict
        )
        s.commit()

def delete_annotation(ann_id):
    conn = get_connection()
    with conn.session as s:
        s.execute(text("DELETE FROM annotations WHERE annotation_id = :id"), {"id": ann_id})
        s.commit()

# =========================================================
# 5. 游玩记录管理（新版：score + rating + comment）
# =========================================================

def add_play_record(data):
    """
    新版打歌记录（score + rating + comment + level）
    """
    conn = get_connection()
    with conn.session as s:
        s.execute(
            text("""
                INSERT INTO play_records (username, chart_id, song_name, difficulty, level,
                                          score, rating, comment)
                VALUES (:username, :chart_id, :song_name, :difficulty, :level,
                        :score, :rating, :comment)
            """),
            data
        )
        s.commit()

def get_play_records(username):
    """
    获取用户评分记录（倒序）
    """
    try:
        conn = get_connection()
        query = """
            SELECT record_id, username, chart_id, song_name, difficulty, level,
                   score, rating, comment, play_time
            FROM play_records
            WHERE username = :u
            ORDER BY play_time DESC
        """
        df = conn.query(query, params={"u": username}, ttl=0)
        return df
    except Exception as e:
        print("Error get_play_records:", e)
        return pd.DataFrame()

def delete_play_record(record_id):
    conn = get_connection()
    with conn.session as s:
        s.execute(
            text("DELETE FROM play_records WHERE record_id = :id"),
            {"id": record_id}
        )
        s.commit()

# =========================================================
# 6. 旧版「miss 统计」系统（保留）
# =========================================================
def add_old_play_record(data_dict):
    """
    旧版 miss 记录（保留以兼容旧功能）
    """
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

def get_old_play_records(username):
    conn = get_connection()
    return conn.query(
        "SELECT * FROM play_records WHERE username = :u AND score IS NULL",
        params={"u": username},
        ttl=0
    )

# =========================================================
# 7. 用户反馈
# =========================================================
def add_feedback(username, feedback_type, content):
    conn = get_connection()
    with conn.session as s:
        s.execute(
            text("""
                INSERT INTO user_feedback (username, feedback_type, content)
                VALUES (:u, :t, :c)
            """),
            {"u": username, "t": feedback_type, "c": content}
        )
        s.commit()

def get_play_records(username):
    """获取用户的游玩记录（按时间倒序）"""
    try:
        conn = get_connection()
        query = """
            SELECT record_id, username, chart_id, song_name, difficulty, level,
                   score, rating, comment, play_time
            FROM play_records
            WHERE username = :u
            ORDER BY play_time DESC
        """
        df = conn.query(query, params={"u": username}, ttl=0)
        return df
    except Exception as e:
        print("Error get_play_records:", e)
        return pd.DataFrame()
