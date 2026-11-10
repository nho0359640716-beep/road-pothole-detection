import sqlite3
import base64
from pathlib import Path
from datetime import date, timedelta
from html import escape

import cv2
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

from database import DB_PATH, update_report_status
from style import (
    page_header, kpi_strip, severity_html, severity_label, status_pill
)


# =========================================================
# 1. CẤU HÌNH CHUNG
# =========================================================

STATUSES = [
    "Chưa xử lý",
    "Đang xử lý",
    "Đã xử lý"
]

STATUS_ICONS = {
    "Chưa xử lý": "🔴",
    "Đang xử lý": "🔵",
    "Đã xử lý": "🟢"
}

# Màu marker folium (folium chỉ hỗ trợ tên màu có sẵn)
STATUS_FOLIUM_COLORS = {
    "Chưa xử lý": "red",
    "Đang xử lý": "blue",
    "Đã xử lý": "green"
}


# =========================================================
# 2. ĐỌC DATABASE
# =========================================================

def load_reports():

    conn = sqlite3.connect(DB_PATH)

    try:

        reports = conn.execute("""
            SELECT
                id,
                image_path,
                pothole_count,
                created_at,
                lat,
                lon,
                status
            FROM reports
            ORDER BY id DESC
        """).fetchall()

        return reports

    finally:
        conn.close()


def delete_report(report_id, image_path):
    """Xóa báo cáo trong DB và file ảnh đi kèm."""

    conn = sqlite3.connect(DB_PATH)

    try:

        conn.execute(
            "DELETE FROM reports WHERE id = ?",
            (report_id,)
        )

        conn.commit()

        if image_path:

            image_file = Path(image_path)

            if image_file.exists():
                image_file.unlink()

    except Exception:

        conn.rollback()
        raise

    finally:
        conn.close()


def valid_coords(lat, lon):
    """Trả về (lat, lon) dạng float nếu hợp lệ, ngược lại None."""

    try:

        latitude = float(lat)
        longitude = float(lon)

    except (ValueError, TypeError):
        return None

    if -90 <= latitude <= 90 and -180 <= longitude <= 180:
        return latitude, longitude

    return None


# =========================================================
# 3. TRANG QUẢN LÝ BÁO CÁO (bảng bên trái, chi tiết bên phải)
# =========================================================

def render_detail(report):
    """Khung chi tiết của báo cáo đang chọn."""

    (
        report_id,
        image_path,
        count,
        created_at,
        lat,
        lon,
        status
    ) = report

    with st.container(border=True):

        st.markdown(
            f'<div class="panel-title">Báo cáo #{report_id}</div>'
            f'<div class="note">{escape(str(created_at))}</div>'
            f'<div>{status_pill(status)} &nbsp; '
            f'{count} ổ gà · {severity_html(count)}</div>',
            unsafe_allow_html=True
        )

        tab_image, tab_gps = st.tabs([
            "🖼️ Ảnh nhận diện",
            "📍 Vị trí"
        ])

        with tab_image:

            if image_path and Path(image_path).exists():

                img = cv2.imread(str(image_path))

                if img is not None:
                    st.image(img, channels="BGR", width="stretch")
                else:
                    st.error("Không thể đọc ảnh báo cáo.")

            elif image_path:
                st.warning("Không tìm thấy file ảnh báo cáo.")

            else:
                st.info("Báo cáo không có đường dẫn ảnh.")

        with tab_gps:

            coords = valid_coords(lat, lon)

            if coords:

                latitude, longitude = coords

                st.caption(
                    f"Vĩ độ {latitude:.6f} · Kinh độ {longitude:.6f}"
                )

                mini_map = folium.Map(
                    location=[latitude, longitude],
                    zoom_start=15
                )

                folium.Marker(
                    location=[latitude, longitude],
                    tooltip=f"Báo cáo #{report_id}",
                    icon=folium.Icon(
                        color=STATUS_FOLIUM_COLORS.get(status, "blue")
                    )
                ).add_to(mini_map)

                st_folium(
                    mini_map,
                    width=None,
                    height=300,
                    key=f"gps_map_{report_id}",
                    returned_objects=[]
                )

            elif lat is not None or lon is not None:
                st.warning("Tọa độ GPS không hợp lệ.")

            else:
                st.info("Báo cáo này chưa có tọa độ GPS.")

        # ---------------- Cập nhật trạng thái ----------------

        st.markdown("**Cập nhật trạng thái**")

        c1, c2 = st.columns([2, 1])

        selected_status = c1.selectbox(
            "Trạng thái mới",
            STATUSES,
            index=STATUSES.index(status) if status in STATUSES else 0,
            key=f"status_{report_id}",
            label_visibility="collapsed"
        )

        if c2.button(
            "Cập nhật",
            key=f"update_{report_id}",
            type="primary",
            width="stretch"
        ):

            try:

                update_report_status(report_id, selected_status)

                st.toast(f"Đã cập nhật báo cáo #{report_id}")

                st.rerun()

            except Exception as e:

                st.error(f"Lỗi cập nhật trạng thái: {e}")

        # ---------------- Xóa báo cáo ----------------

        delete_key = f"delete_confirm_{report_id}"

        if not st.session_state.get(delete_key, False):

            if st.button("🗑️ Xóa báo cáo", key=f"delete_{report_id}"):

                st.session_state[delete_key] = True
                st.rerun()

        else:

            st.warning(
                f"Bạn có chắc chắn muốn xóa báo cáo #{report_id}?"
            )

            d1, d2 = st.columns(2)

            if d1.button(
                "Xác nhận xóa",
                key=f"confirm_delete_{report_id}",
                width="stretch"
            ):

                try:

                    delete_report(report_id, image_path)

                    st.session_state.pop(delete_key, None)

                    # Đổi key bảng để bỏ lựa chọn của dòng đã xóa
                    st.session_state["report_table_v"] = (
                        st.session_state.get("report_table_v", 0) + 1
                    )

                    st.toast(f"Đã xóa báo cáo #{report_id}")

                    st.rerun()

                except Exception as e:

                    st.error(f"Lỗi xóa báo cáo: {e}")

            if d2.button(
                "Hủy",
                key=f"cancel_delete_{report_id}",
                width="stretch"
            ):

                st.session_state[delete_key] = False
                st.rerun()


def render():

    page_header(
        "Báo cáo",
        "Quản lý và theo dõi tiến độ xử lý từng điểm ổ gà."
    )

    # -----------------------------------------------------
    # ĐỌC DỮ LIỆU
    # -----------------------------------------------------

    try:

        reports = load_reports()

    except Exception as e:

        st.error(f"Không thể đọc database: {e}")
        return

    # -----------------------------------------------------
    # TÌM KIẾM VÀ LỌC (một hàng)
    # -----------------------------------------------------

    with st.container(border=True):

        c1, c2, c3, c4 = st.columns([1.2, 1, 1, 1])

        search_id = c1.text_input(
            "Mã báo cáo",
            placeholder="Ví dụ: 1, 2, 3..."
        )

        selected_filter = c2.selectbox(
            "Trạng thái xử lý",
            ["Tất cả"] + STATUSES
        )

        start_date = c3.date_input(
            "Từ ngày",
            value=date.today() - timedelta(days=30)
        )

        end_date = c4.date_input(
            "Đến ngày",
            value=date.today()
        )

    if start_date > end_date:

        st.error("Ngày bắt đầu không được lớn hơn ngày kết thúc.")
        return

    # -----------------------------------------------------
    # LỌC BÁO CÁO
    # -----------------------------------------------------

    filtered_reports = []

    for report in reports:

        report_id = report[0]
        created_at = report[3]
        status = report[6]

        if search_id.strip():

            if search_id.strip() not in str(report_id):
                continue

        if selected_filter != "Tất cả":

            if status != selected_filter:
                continue

        try:

            report_date = date.fromisoformat(str(created_at)[:10])

            if not start_date <= report_date <= end_date:
                continue

        except (ValueError, TypeError):

            continue

        filtered_reports.append(report)

    # -----------------------------------------------------
    # THỐNG KÊ
    # -----------------------------------------------------

    total_reports = len(filtered_reports)

    total_potholes = sum(int(r[2] or 0) for r in filtered_reports)

    pending = sum(1 for r in filtered_reports if r[6] == "Chưa xử lý")
    processing = sum(1 for r in filtered_reports if r[6] == "Đang xử lý")
    completed = sum(1 for r in filtered_reports if r[6] == "Đã xử lý")

    kpi_strip([
        (total_reports, "Báo cáo", ""),
        (pending, "Chưa xử lý", "warn"),
        (processing, "Đang xử lý", ""),
        (completed, "Đã xử lý", ""),
    ])

    if not filtered_reports:

        st.info("Không tìm thấy báo cáo phù hợp.")
        return

    # -----------------------------------------------------
    # BẢNG (trái) + CHI TIẾT (phải)
    # -----------------------------------------------------

    left, right = st.columns([1.35, 1])

    table = pd.DataFrame([
        {
            "Mã": r[0],
            "Thời gian": str(r[3]),
            "Số ổ gà": int(r[2] or 0),
            "Mức độ": severity_label(r[2]),
            "Trạng thái": f"{STATUS_ICONS.get(r[6], '⚪')} {r[6]}",
            "GPS": "Có" if valid_coords(r[4], r[5]) else "Chưa có",
        }
        for r in filtered_reports
    ])

    with left:

        st.caption(
            f"{total_reports} báo cáo · {total_potholes} ổ gà. "
            "Chọn một dòng để xem chi tiết."
        )

        table_key = f"report_table_{st.session_state.get('report_table_v', 0)}"

        event = st.dataframe(
            table,
            hide_index=True,
            width="stretch",
            height=560,
            on_select="rerun",
            selection_mode="single-row",
            key=table_key
        )

    selected_rows = event.selection.rows

    with right:

        if selected_rows and selected_rows[0] < len(filtered_reports):

            render_detail(filtered_reports[selected_rows[0]])

        else:

            with st.container(border=True):

                st.markdown(
                    '<div class="panel-title">Chi tiết báo cáo</div>',
                    unsafe_allow_html=True
                )

                st.info(
                    "Chọn một dòng trong bảng để xem ảnh, vị trí "
                    "và cập nhật trạng thái."
                )


# =========================================================
# 4. BẢN ĐỒ GIÁM SÁT Ổ GÀ
# =========================================================

def popup_html(report):
    """Nội dung popup cho marker (giữ ảnh nhận diện)."""

    (
        report_id,
        image_path,
        pothole_count,
        created_at,
        lat,
        lon,
        status
    ) = report

    image_html = ""

    if image_path:

        path = Path(image_path)

        if path.exists():

            try:

                encoded = base64.b64encode(
                    path.read_bytes()
                ).decode("utf-8")

                image_html = (
                    f'<img src="data:image/jpeg;base64,{encoded}" '
                    'style="width:200px;max-width:100%;'
                    'border-radius:8px;margin-top:8px;">'
                )

            except Exception:

                image_html = "<p>Không đọc được ảnh.</p>"

        else:

            image_html = "<p>Không tìm thấy ảnh.</p>"

    return f"""
    <div style="width:230px;font-family:Arial;font-size:13px;">
        <h4>🚧 Báo cáo #{report_id}</h4>
        <b>Số ổ gà:</b> {pothole_count}<br>
        <b>Mức độ:</b> {severity_label(pothole_count)}<br>
        <b>Thời gian:</b> {created_at}<br>
        <b>Trạng thái:</b> {escape(str(status))}<br>
        <b>Vĩ độ:</b> {lat}<br>
        <b>Kinh độ:</b> {lon}<br>
        {image_html}
    </div>
    """


def render_map():

    page_header(
        "Bản đồ ổ gà",
        "Theo dõi vị trí và trạng thái xử lý các báo cáo ổ gà."
    )

    try:

        reports = [
            r for r in load_reports()
            if valid_coords(r[4], r[5])
        ]

    except Exception as e:

        st.error(f"Lỗi đọc database: {e}")
        return

    if not reports:

        st.info(
            "Chưa có báo cáo GPS. "
            "Hãy lưu báo cáo từ trang nhận diện."
        )

        return

    # -----------------------------------------------------
    # LỌC THEO TRẠNG THÁI
    # -----------------------------------------------------

    counts = {s: sum(1 for r in reports if r[6] == s) for s in STATUSES}

    options = ["Tất cả"] + STATUSES

    selected = st.pills(
        "Lọc trạng thái",
        options,
        default="Tất cả",
        format_func=lambda s: (
            f"{s} ({len(reports)})" if s == "Tất cả"
            else f"{STATUS_ICONS[s]} {s} ({counts[s]})"
        ),
        key="map_filter",
        label_visibility="collapsed"
    )

    if selected in (None, "Tất cả"):
        shown = reports
    else:
        shown = [r for r in reports if r[6] == selected]

    if not shown:

        st.info("Không có điểm nào ở trạng thái này.")
        return

    # -----------------------------------------------------
    # BẢN ĐỒ (trái) + DANH SÁCH (phải)
    # -----------------------------------------------------

    map_col, list_col = st.columns([2, 1])

    with map_col:

        try:

            points = [valid_coords(r[4], r[5]) for r in shown]

            road_map = folium.Map(
                location=list(points[0]),
                zoom_start=13,
                control_scale=True,
                tiles="OpenStreetMap"
            )

            for report, (lat, lon) in zip(shown, points):

                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(
                        popup_html(report),
                        max_width=280
                    ),
                    tooltip=(
                        f"Báo cáo #{report[0]} | "
                        f"{report[2]} ổ gà | {report[6]}"
                    ),
                    icon=folium.Icon(
                        color=STATUS_FOLIUM_COLORS.get(report[6], "blue"),
                        icon="warning",
                        prefix="glyphicon"
                    )
                ).add_to(road_map)

            # Tự động thu phóng để thấy hết các điểm
            if len(set(points)) > 1:

                road_map.fit_bounds(
                    [
                        [min(p[0] for p in points), min(p[1] for p in points)],
                        [max(p[0] for p in points), max(p[1] for p in points)]
                    ],
                    padding=(30, 30)
                )

            st_folium(
                road_map,
                width=None,
                height=600,
                key=f"roadai_map_{selected}",
                returned_objects=[]
            )

        except Exception as e:

            st.error(f"Lỗi hiển thị bản đồ: {e}")

    with list_col:

        with st.container(border=True, height=600):

            st.markdown(
                f'<div class="panel-title">{len(shown)} điểm ghi nhận</div>',
                unsafe_allow_html=True
            )

            rows = ""

            for r in shown:

                rows += (
                    f'<div class="row2"><div class="id">#{r[0]}</div>'
                    f'<div class="t"><b>{r[2]} ổ gà</b>'
                    f'<span>{escape(str(r[3]))}</span></div>'
                    f'{severity_html(r[2])}{status_pill(r[6])}</div>'
                )

            st.markdown(
                f'<div class="rows">{rows}</div>',
                unsafe_allow_html=True
            )
