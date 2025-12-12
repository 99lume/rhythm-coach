import cloudinary
import cloudinary.uploader
import streamlit as st

def upload_image_to_cloud(file_obj, filename_tag):
    """
    将图片文件上传到 Cloudinary 图床
    :param file_obj: Streamlit 上传的文件对象
    :param filename_tag: 给图片起个标签（通常用歌名）
    :return: 图片的 HTTPS 链接 (URL)
    """
    # 1. 配置 Cloudinary (从 secrets.toml 读取)
    try:
        cloudinary.config( 
            cloud_name = st.secrets["cloudinary"]["cloud_name"], 
            api_key    = st.secrets["cloudinary"]["api_key"], 
            api_secret = st.secrets["cloudinary"]["api_secret"],
            secure = True
        )
    except KeyError:
        st.error("❌ 缺少 Cloudinary 配置！请检查 .streamlit/secrets.toml")
        return None

    # 2. 执行上传
    try:
        # folder="rhythm_charts" 会自动在云端建一个文件夹，方便管理
        response = cloudinary.uploader.upload(
            file_obj, 
            public_id=filename_tag, 
            folder="rhythm_charts", 
            resource_type="image"
        )
        # 返回安全的 https 链接
        return response['secure_url']
    
    except Exception as e:
        st.error(f"❌ 图片上传失败: {e}")
        return None