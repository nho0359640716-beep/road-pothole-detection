import streamlit as st

import page_image
import page_video
from style import page_header


def render():
    page_header(
        "Nhận diện ổ gà",
        "Tải ảnh hoặc video mặt đường, RoadAI sẽ đánh dấu từng ổ gà."
    )

    tab_image, tab_video = st.tabs(["🖼️ Ảnh", "🎥 Video"])

    with tab_image:
        page_image.render(show_title=False)

    with tab_video:
        page_video.render(show_title=False)
