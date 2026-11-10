import cv2
import numpy as np
import streamlit as st
import folium

from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation

from detector import detect
from database import add_report
from style import severity_label


NAMES = {
    "pothole": "Ổ gà",
    "manhole": "Nắp cống"
}


def render(show_title=True):
    if show_title:
        st.title("Nhận diện ổ gà từ ảnh")

    # Ngưỡng độ tin cậy
    conf = st.slider(
        "Ngưỡng độ tin cậy",
        0.10,
        0.90,
        0.25,
        0.05
    )

    # Tải ảnh lên
    f = st.file_uploader(
        "Tải ảnh đường lên",
        type=["jpg", "jpeg", "png"]
    )

    if f is None:
        st.info("Hãy tải một ảnh đường lên để bắt đầu.")
        return

    # Reset vị trí đã chọn khi đổi ảnh
    if st.session_state.get("location_for_file") != f.name:
        st.session_state["location_for_file"] = f.name
        st.session_state["selected_map_location"] = None

    # Đọc ảnh
    img = cv2.imdecode(
        np.frombuffer(f.getvalue(), np.uint8),
        cv2.IMREAD_COLOR
    )

    if img is None:
        st.error("Không đọc được ảnh này. Hãy thử file khác.")
        return

    # Hiển thị ảnh gốc
    c1, c2 = st.columns(2)

    c1.image(
        img,
        channels="BGR",
        caption="Ảnh gốc"
    )

    # Nhận diện
    if st.button("Bắt đầu nhận diện", type="primary"):
        with st.spinner("Đang nhận diện..."):
            try:
                out, n, items = detect(img, conf=conf)

            except Exception as e:
                st.error(f"Không thể nhận diện: {e}")
                return

        st.session_state["last_result"] = {
            "filename": f.name,
            "image": out,
            "count": n,
            "items": items,
        }

    # Lấy kết quả nhận diện
    res = st.session_state.get("last_result")

    if res and res["filename"] == f.name:

        c2.image(
            res["image"],
            channels="BGR",
            caption="Kết quả nhận diện"
        )

        if not res["items"]:
            st.info("Không phát hiện ổ gà trong ảnh này.")
            return

        st.success(f"Phát hiện {res['count']} ổ gà")

        # Thống kê
        confs = [i["conf"] for i in res["items"]]

        m1, m2, m3 = st.columns(3)

        m1.metric("Số ổ gà", res["count"])

        m2.metric(
            "Độ tin cậy trung bình",
            f"{sum(confs) / len(confs):.0%}"
        )

        m3.metric(
            "Mức độ ước tính",
            severity_label(res["count"])
        )

        st.caption(
            "Mức độ ước tính theo số ổ gà: 1 ổ là Nhẹ, "
            "2–3 ổ là Trung bình, từ 4 ổ là Nặng."
        )

        # Bảng kết quả
        st.dataframe(
            [
                {
                    "Loại": NAMES.get(i["class"], i["class"]),
                    "Độ tin cậy": f"{i['conf']:.0%}"
                }
                for i in res["items"]
            ],
            width="stretch"
        )

        st.divider()

        # ==================================
        # LẤY VỊ TRÍ GPS
        # ==================================

        st.subheader("📍 Vị trí ghi nhận")

        location = streamlit_geolocation()

        gps_lat = None
        gps_lon = None

        if location:
            gps_lat = location.get("latitude")
            gps_lon = location.get("longitude")

        if gps_lat is not None and gps_lon is not None:
            st.success("Đã lấy được vị trí GPS.")
            st.write(f"Latitude: {gps_lat}")
            st.write(f"Longitude: {gps_lon}")
        else:
            st.warning(
                "Chưa lấy được GPS. "
                "Bạn có thể chọn vị trí trực tiếp trên bản đồ."
            )

        st.divider()

        # ==================================
        # CHỌN VỊ TRÍ TRÊN BẢN ĐỒ
        # ==================================

        st.subheader("🗺️ Chọn vị trí ổ gà trên bản đồ")

        st.caption(
            "Nhấn vào vị trí cần ghi nhận trên bản đồ "
            "để đánh dấu vị trí ổ gà."
        )

        selected_location = st.session_state.get(
            "selected_map_location"
        )

        # Xác định tâm bản đồ
        if selected_location:
            map_center = [
                selected_location["lat"],
                selected_location["lng"]
            ]
            zoom = 16

        elif gps_lat is not None and gps_lon is not None:
            map_center = [gps_lat, gps_lon]
            zoom = 16

        else:
            # Vị trí mặc định tại Việt Nam
            map_center = [16.0, 106.0]
            zoom = 6

        # Tạo bản đồ OpenStreetMap
        location_map = folium.Map(
            location=map_center,
            zoom_start=zoom,
            control_scale=True
        )

        # Hiển thị marker GPS hiện tại
        if gps_lat is not None and gps_lon is not None:
            folium.Marker(
                location=[gps_lat, gps_lon],
                tooltip="Vị trí GPS hiện tại",
                popup="Vị trí GPS",
                icon=folium.Icon(
                    color="blue",
                    icon="info-sign"
                )
            ).add_to(location_map)

        # Hiển thị marker vị trí đã chọn
        if selected_location:
            folium.Marker(
                location=[
                    selected_location["lat"],
                    selected_location["lng"]
                ],
                tooltip="Vị trí ổ gà đã chọn",
                popup="Vị trí ghi nhận ổ gà",
                icon=folium.Icon(
                    color="red",
                    icon="warning"
                )
            ).add_to(location_map)

        # Hiển thị bản đồ và nhận tọa độ khi nhấn
        map_data = st_folium(
            location_map,
            width=None,
            height=450,
            key="select_location_map"
        )

        # Lấy tọa độ người dùng vừa nhấn
        if map_data and map_data.get("last_clicked"):

            clicked = map_data["last_clicked"]

            new_location = {
                "lat": clicked["lat"],
                "lng": clicked["lng"]
            }

            st.session_state["selected_map_location"] = new_location

            selected_location = new_location

        # Hiển thị tọa độ đã chọn
        if selected_location:

            st.success("Đã chọn vị trí ổ gà trên bản đồ!")

            st.write(
                f"**Vĩ độ (Latitude):** "
                f"{selected_location['lat']}"
            )

            st.write(
                f"**Kinh độ (Longitude):** "
                f"{selected_location['lng']}"
            )

            if st.button("🔄 Bỏ vị trí đã chọn"):
                st.session_state["selected_map_location"] = None
                st.rerun()

        else:
            st.info(
                "Bạn chưa chọn vị trí trên bản đồ. "
                "Nếu có GPS, hệ thống sẽ sử dụng tọa độ GPS."
            )

        # ==================================
        # XÁC ĐỊNH TỌA ĐỘ LƯU BÁO CÁO
        # ==================================

        if selected_location:
            lat = selected_location["lat"]
            lon = selected_location["lng"]

        else:
            lat = gps_lat
            lon = gps_lon

        st.divider()

        # ==================================
        # LƯU BÁO CÁO
        # ==================================

        if st.button("💾 Lưu báo cáo", type="primary"):

            try:
                report_id = add_report(
                    image=res["image"],
                    pothole_count=res["count"],
                    lat=lat,
                    lon=lon,
                )

                st.success(
                    f"Đã lưu báo cáo thành công! "
                    f"Mã báo cáo: {report_id}"
                )

            except Exception as e:
                st.error(f"Không thể lưu báo cáo: {e}")