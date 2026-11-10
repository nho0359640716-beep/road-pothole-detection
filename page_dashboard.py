import sqlite3
import pandas as pd
import streamlit as st

from database import DB_PATH
from style import (
    page_header, kpi_strip, severity_html, status_pill
)


def get_dashboard_data():
    conn = sqlite3.connect(DB_PATH)

    try:
        # Tổng quan
        summary_query = """
            SELECT
                COUNT(*) AS total_reports,
                COALESCE(SUM(pothole_count), 0) AS total_potholes,
                SUM(CASE WHEN status = 'Chưa xử lý' THEN 1 ELSE 0 END)
                    AS pending,
                SUM(CASE WHEN status = 'Đang xử lý' THEN 1 ELSE 0 END)
                    AS processing,
                SUM(CASE WHEN status = 'Đã xử lý' THEN 1 ELSE 0 END)
                    AS completed
            FROM reports
        """

        summary = pd.read_sql_query(summary_query, conn)

        # Thống kê theo trạng thái
        status_query = """
            SELECT status, COUNT(*) AS total
            FROM reports
            GROUP BY status
        """

        status_data = pd.read_sql_query(status_query, conn)

        # Thống kê theo ngày
        daily_query = """
            SELECT
                DATE(created_at) AS date,
                COUNT(*) AS total_reports,
                SUM(pothole_count) AS total_potholes
            FROM reports
            GROUP BY DATE(created_at)
            ORDER BY DATE(created_at)
        """

        daily_data = pd.read_sql_query(daily_query, conn)

        # Báo cáo gần đây
        recent_query = """
            SELECT
                id,
                created_at,
                pothole_count,
                status,
                lat,
                lon
            FROM reports
            ORDER BY id DESC
            LIMIT 10
        """

        recent_data = pd.read_sql_query(recent_query, conn)

        return summary, status_data, daily_data, recent_data

    finally:
        conn.close()


def get_urgent_reports(limit=5):
    """Báo cáo chưa xong, xếp theo số ổ gà giảm dần (mức độ nặng trước)."""
    conn = sqlite3.connect(DB_PATH)

    try:
        return conn.execute("""
            SELECT id, created_at, pothole_count, status, lat, lon
            FROM reports
            WHERE status != 'Đã xử lý'
            ORDER BY pothole_count DESC, id DESC
            LIMIT ?
        """, (limit,)).fetchall()

    finally:
        conn.close()


STATUS_ORDER = ["Chưa xử lý", "Đang xử lý", "Đã xử lý"]
STATUS_COLORS = ["#D64545", "#2F6FDB", "#25915F"]


def donut_html(counts):
    """Biểu đồ tròn trạng thái bằng SVG, không cần thư viện thêm."""
    total = sum(counts) or 1
    radius = 52
    circ = 2 * 3.14159265 * radius
    offset = 0
    arcs = ""

    for value, color in zip(counts, STATUS_COLORS):
        length = value / total * circ
        arcs += (
            f'<circle r="{radius}" cx="70" cy="70" fill="none" '
            f'stroke="{color}" stroke-width="22" '
            f'stroke-dasharray="{length:.2f} {circ - length:.2f}" '
            f'stroke-dashoffset="{-offset:.2f}" '
            f'transform="rotate(-90 70 70)"/>'
        )
        offset += length

    legend = "".join(
        f'<div style="margin:6px 0"><span style="display:inline-block;'
        f'width:10px;height:10px;border-radius:3px;background:{c};'
        f'margin-right:8px"></span>{name}: <b>{v}</b></div>'
        for name, v, c in zip(STATUS_ORDER, counts, STATUS_COLORS)
    )

    return (
        '<div style="display:flex;align-items:center;gap:24px;padding:8px 4px">'
        f'<svg width="140" height="140" viewBox="0 0 140 140">{arcs}</svg>'
        f'<div>{legend}</div></div>'
    )


def render():
    page_header(
        "Tổng quan mặt đường",
        "Số liệu từ các báo cáo ổ gà đã lưu trong hệ thống."
    )

    summary, status_data, daily_data, recent_data = (
        get_dashboard_data()
    )

    # =========================
    # THỐNG KÊ TỔNG QUAN
    # =========================

    total_reports = int(summary.iloc[0]["total_reports"])
    total_potholes = int(summary.iloc[0]["total_potholes"])
    pending = int(summary.iloc[0]["pending"] or 0)
    processing = int(summary.iloc[0]["processing"] or 0)
    completed = int(summary.iloc[0]["completed"] or 0)

    done_pct = round(completed / total_reports * 100) if total_reports else 0

    kpi_strip([
        (total_reports, "Báo cáo", ""),
        (total_potholes, "Ổ gà phát hiện", ""),
        (pending + processing, "Cần xử lý", "warn"),
        (f"{done_pct}%", "Đã xử lý xong", ""),
    ])

    if total_reports == 0:
        st.info(
            "Chưa có báo cáo nào. Vào mục Nhận diện, "
            "tải ảnh lên và lưu báo cáo để bắt đầu."
        )
        return

    # =========================
    # BIỂU ĐỒ THEO NGÀY + TRẠNG THÁI
    # =========================

    left, right = st.columns([1.6, 1])

    with left:
        with st.container(border=True):
            st.markdown(
                '<div class="panel-title">Thống kê theo ngày</div>',
                unsafe_allow_html=True
            )

            if not daily_data.empty:
                daily = daily_data.copy()
                daily["date"] = pd.to_datetime(daily["date"])
                daily = daily.set_index("date")

                tab_pothole, tab_report = st.tabs(
                    ["Số ổ gà", "Số báo cáo"]
                )

                with tab_pothole:
                    st.bar_chart(
                        daily[["total_potholes"]],
                        color="#F5B800",
                        height=260
                    )

                with tab_report:
                    st.bar_chart(
                        daily[["total_reports"]],
                        color="#15181B",
                        height=260
                    )
            else:
                st.info("Chưa có dữ liệu thống kê theo ngày.")

    with right:
        with st.container(border=True):
            st.markdown(
                '<div class="panel-title">Theo trạng thái</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                donut_html([pending, processing, completed]),
                unsafe_allow_html=True
            )

            st.caption(f"Tổng cộng {total_reports} báo cáo.")

    # =========================
    # NÊN XỬ LÝ TRƯỚC
    # =========================

    with st.container(border=True):
        st.markdown(
            '<div class="panel-title">Nên xử lý trước</div>'
            '<div class="note">Xếp theo mức độ nghiêm trọng, '
            'sau đó theo báo cáo mới nhất.</div>',
            unsafe_allow_html=True
        )

        urgent = get_urgent_reports()

        if urgent:
            rows = ""

            for rid, created_at, count, status, lat, lon in urgent:
                where = (
                    f"{float(lat):.5f}, {float(lon):.5f}"
                    if lat is not None and lon is not None
                    else "Chưa có tọa độ GPS"
                )

                rows += (
                    f'<div class="row2"><div class="id">#{rid}</div>'
                    f'<div class="t"><b>{count} ổ gà</b>'
                    f'<span>{created_at} · {where}</span></div>'
                    f'{severity_html(count)}{status_pill(status)}</div>'
                )

            st.markdown(
                f'<div class="rows">{rows}</div>',
                unsafe_allow_html=True
            )
        else:
            st.success("Tất cả báo cáo đã được xử lý.")

    # =========================
    # BÁO CÁO GẦN ĐÂY
    # =========================

    with st.expander("10 báo cáo gần đây", expanded=False):
        if not recent_data.empty:
            recent = recent_data.copy()
            recent.columns = [
                "Mã báo cáo",
                "Thời gian",
                "Số ổ gà",
                "Trạng thái",
                "Vĩ độ",
                "Kinh độ"
            ]

            st.dataframe(
                recent,
                width="stretch",
                hide_index=True
            )
        else:
            st.info("Chưa có báo cáo nào trong hệ thống.")
