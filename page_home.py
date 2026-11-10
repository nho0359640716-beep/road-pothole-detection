import streamlit as st

# Số liệu mô hình: sửa tại đây
METRICS = [
    ("mAP50", 0.826, "Độ chính xác tổng thể khi khoanh vùng ổ gà"),
    ("mAP50-95", 0.463, "Độ khớp của khung với các ngưỡng IoU chặt hơn"),
    ("Precision", 0.815, "Trong số ổ gà báo ra, bao nhiêu là đúng"),
    ("Recall", 0.740, "Trong số ổ gà thật, bao nhiêu được tìm thấy"),
]

def render_home():
    hero = (
        '<div class="hero"><div>'
        '<span class="chip">YOLO11n</span>'
        "<h1>RoadAI</h1>"
        "<p>Phát hiện ổ gà trên mặt đường bằng AI và định vị trên bản đồ.</p>"
        "</div>"
        '<div class="frame"><div class="pit"></div>'
        '<div class="box"><span class="tag">ổ gà 0.83</span></div></div>'
        "</div>"
    )

    steps = (
        '<div class="sec">Cách dùng</div><div class="steps">'
        '<div class="step"><div class="num">1</div><h3>Tải lên</h3>'
        "<p>Chọn ảnh hoặc video mặt đường có ổ gà.</p></div>"
        '<div class="step"><div class="num">2</div><h3>Nhận diện</h3>'
        "<p>YOLO tìm ổ gà, đếm số lượng và cho biết độ tin cậy.</p></div>"
        '<div class="step"><div class="num">3</div><h3>Báo cáo</h3>'
        "<p>Chọn vị trí trên bản đồ, lưu và theo dõi trạng thái xử lý.</p></div>"
        "</div>"
    )

    cards = ""
    for i, (name, value, hint) in enumerate(METRICS):
        cls = "stat lead" if i == 0 else "stat"
        cards += (
            f'<div class="{cls}"><div class="k">{name}</div>'
            f'<div class="v">{value:.3f}</div>'
            f'<div class="bar"><i style="width:{value * 100:.1f}%"></i></div>'
            f'<p class="d">{hint}</p></div>'
        )
    perf = (
        '<div class="sec">Hiệu năng mô hình</div>'
        '<p class="sub">YOLO11n, huấn luyện 100 epoch, ảnh đầu vào 416×416</p>'
        f'<div class="stats">{cards}</div>'
    )

    st.markdown(hero + steps + perf, unsafe_allow_html=True)


def render():
    render_home()


if __name__ == "__main__":
    st.set_page_config(page_title="RoadAI", page_icon="🛣️", layout="wide")
    render()