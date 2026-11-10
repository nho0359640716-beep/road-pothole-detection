import sqlite3

import streamlit as st

import page_home
import page_detect
import page_history
import page_dashboard

from style import inject_css, sidebar_brand, sidebar_model_box
from database import init_db, DB_PATH


# =========================
# CẤU HÌNH ỨNG DỤNG
# =========================

st.set_page_config(
    page_title="RoadAI",
    page_icon="🛣️",
    layout="wide"
)

inject_css()


# =========================
# KHỞI TẠO DATABASE
# =========================

init_db()


# =========================
# ĐIỀU HƯỚNG
# Khóa (key) giữ cố định để đổi số huy hiệu không làm mất trang đang chọn.
# =========================

PAGES = {
    "dashboard": ("📊", "Tổng quan", page_dashboard.render),
    "detect": ("🔍", "Nhận diện", page_detect.render),
    "map": ("🗺️", "Bản đồ", page_history.render_map),
    "reports": ("📋", "Báo cáo", page_history.render),
    "about": ("ℹ️", "Giới thiệu", page_home.render),
}


def count_pending():
    """Số báo cáo chưa xử lý, hiện bên cạnh mục Báo cáo."""
    try:
        conn = sqlite3.connect(DB_PATH)
        try:
            return conn.execute(
                "SELECT COUNT(*) FROM reports WHERE status = 'Chưa xử lý'"
            ).fetchone()[0]
        finally:
            conn.close()
    except Exception:
        return 0


def menu_label(key):
    icon, name, _ = PAGES[key]
    label = f"{icon}  {name}"
    if key == "reports":
        n = count_pending()
        if n:
            label += f"   ({n})"
    return label


# =========================
# SIDEBAR
# =========================

sidebar_brand()

choice = st.sidebar.radio(
    "Menu",
    list(PAGES),
    format_func=menu_label,
    label_visibility="collapsed"
)

sidebar_model_box()


# =========================
# HIỂN THỊ TRANG
# =========================

PAGES[choice][2]()
