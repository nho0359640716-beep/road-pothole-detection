import streamlit as st

# =========================================================
# GIAO DIỆN CHUNG CHO TOÀN BỘ ỨNG DỤNG
# Màu: vàng vạch kẻ đường + xám bê tông, nền sáng.
# Chỉ cần sửa các biến trong :root để đổi màu toàn app.
# =========================================================

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');

:root{
  --bg:#F6F8F9; --card:#FFFFFF; --ink:#1F2428; --muted:#5C646B;
  --hero:#FFF4CC; --herosub:#5A5130;
  --line:#F2C230; --dash:#E0A800; --chip:#8A6A00;
  --track:#E6E9EB; --deep:#15181B; --edge:#DDE1E4;
}

/* Font: KHÔNG áp lên icon Material (nếu áp sẽ hiện chữ "keyboard_double_arrow...") */
html, body, .stApp,
.stApp *:not([data-testid="stIconMaterial"]):not([class*="material" i]):not(code):not(pre):not(pre *){
  font-family:'Be Vietnam Pro',sans-serif;
}
.stApp{background:var(--bg)}
.block-container{max-width:1280px;padding-top:4.5rem}
h1,h2,h3{color:var(--ink);letter-spacing:-.01em}
h1{font-weight:800}

/* ---------- Thanh công cụ trên cùng ---------- */
[data-testid="stHeader"]{
  background:rgba(255,255,255,.88);backdrop-filter:blur(8px);
  border-bottom:1px solid var(--edge);height:3.25rem;
}
[data-testid="stHeader"]::after{
  content:"";position:absolute;left:0;right:0;bottom:-1px;height:3px;
  background:repeating-linear-gradient(90deg,var(--dash) 0 28px,transparent 28px 48px);
}
[data-testid="stToolbar"] button,
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stExpandSidebarButton"]{border-radius:10px;color:var(--ink)}
[data-testid="stToolbar"] button:hover,
[data-testid="stSidebarCollapseButton"] button:hover,
[data-testid="stExpandSidebarButton"]:hover{background:var(--hero);color:var(--ink)}
[data-testid="stAppDeployButton"] button{border:1px solid var(--edge);font-weight:600;padding:.2rem .9rem}

/* ---------- Sidebar: nền nhựa đường + vạch kẻ vàng ---------- */
[data-testid="stSidebar"]{background:var(--deep);border-right:none;overflow-x:hidden}
[data-testid="stSidebar"]::after{content:"";position:absolute;right:0;top:0;bottom:0;width:4px;
  background:repeating-linear-gradient(180deg,var(--line) 0 22px,transparent 22px 44px)}
[data-testid="stSidebarContent"]{overflow-x:hidden}
[data-testid="stSidebar"] *:not([data-testid="stIconMaterial"]){color:#B7C0C6}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] *{color:#8E99A1}
[data-testid="stSidebarCollapseButton"] button,[data-testid="stSidebarCollapseButton"] button *{color:#fff!important}
.brand{display:flex;align-items:center;gap:10px;font-size:1.4rem;font-weight:800;margin:4px 0 2px;color:#fff}
[data-testid="stSidebar"] .brand{color:#fff}
.brand .dot{width:28px;height:28px;border-radius:8px;background:var(--line);display:grid;place-items:center}
.brand .dot::after{content:"";width:0;height:0;border-left:6px solid transparent;border-right:6px solid transparent;border-bottom:10px solid var(--deep)}
[data-testid="stSidebar"] [role="radiogroup"]{gap:2px}
[data-testid="stSidebar"] [role="radiogroup"] label{padding:10px 12px;border-radius:10px;width:100%;cursor:pointer}
[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child{display:none}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:#2A3036}
[data-testid="stSidebar"] [role="radiogroup"] label:hover *{color:#fff}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:var(--line)}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) *{color:var(--deep)!important;font-weight:700}
.model{margin-top:28px;background:#2A3036;border-radius:12px;padding:12px 14px;font-size:.8rem;line-height:1.5}
.model b{display:block;color:#fff;font-size:.88rem}
.model .live{display:inline-block;width:8px;height:8px;border-radius:50%;background:#3ED598;margin-right:7px}

/* ---------- Tiêu đề trang ---------- */
.ph{margin:0 0 20px}
.ph h1{font-size:2rem;font-weight:800;line-height:1.15;margin:0;padding:0;letter-spacing:-.02em}
.ph p{color:var(--muted);margin:4px 0 0;font-size:.98rem}
.panel-title{font-size:1.05rem;font-weight:700;margin:2px 0 8px;color:var(--ink)}
.note{color:var(--muted);font-size:.84rem;margin:2px 0 8px}

/* ---------- Dải số liệu (KPI) ---------- */
.kpi{display:grid;grid-template-columns:repeat(4,1fr);background:var(--deep);border-radius:14px;overflow:hidden;margin:0 0 18px}
.kpi > div{padding:20px 24px;border-right:1px dashed #4A535B}
.kpi > div:last-child{border-right:0}
.kpi b{display:block;font-size:2.5rem;font-weight:800;line-height:1.1;color:#fff;letter-spacing:-.02em}
.kpi span{color:#A9B3BA;font-size:.86rem}
.kpi .warn b{color:var(--line)}

/* ---------- Nhãn trạng thái / mức độ ---------- */
.pill{display:inline-block;padding:2px 11px;border-radius:999px;font-size:.8rem;font-weight:600;border:1px solid currentColor;white-space:nowrap}
.s0{color:#D64545}.s1{color:#2F6FDB}.s2{color:#25915F}
.sev{font-weight:600;white-space:nowrap}
.v0{color:#25915F}.v1{color:#B77700}.v2{color:#D64545}

/* ---------- Danh sách dòng ---------- */
.rows{display:grid}
.row2{display:flex;gap:12px;align-items:center;padding:12px 2px;border-top:1px solid var(--edge)}
.row2:first-child{border-top:0}
.row2 .id{font-weight:800;min-width:42px}
.row2 .t{flex:1;min-width:0}
.row2 .t b{display:block;font-weight:600}
.row2 .t span{font-size:.82rem;color:var(--muted)}

/* ---------- Nút bấm ---------- */
.stButton > button,[data-testid="stDownloadButton"] button{
  border-radius:10px;font-weight:600;min-height:40px;padding:.5rem 1.2rem;transition:background .15s ease;
}
[data-testid="stBaseButton-primary"]{background:var(--line);color:var(--ink);border:none}
[data-testid="stBaseButton-primary"]:hover{background:var(--dash);color:var(--ink)}
[data-testid="stBaseButton-secondary"]{background:#fff;border:1px solid var(--edge);color:var(--ink)}
[data-testid="stBaseButton-secondary"]:hover{border-color:var(--dash);color:var(--ink)}

/* ---------- Thẻ số liệu, bảng, ảnh, tải file ---------- */
[data-testid="stMetric"]{
  background:var(--card);border:1px solid var(--edge);border-radius:14px;padding:14px 18px;
}
[data-testid="stMetricLabel"]{color:var(--muted)}
[data-testid="stMetricValue"]{font-weight:700;color:var(--ink)}
[data-testid="stFileUploader"] section,[data-testid="stFileUploaderDropzone"]{
  border:2px dashed var(--dash);border-radius:14px;background:#FFFBEA;
}
[data-testid="stImage"] img{border-radius:12px}
[data-testid="stDataFrame"]{border:1px solid var(--edge);border-radius:12px;overflow:hidden}
[data-testid="stAlert"]{border-radius:12px}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:14px}
button[data-baseweb="tab"]{font-weight:600}
[data-testid="stPills"] button,[data-testid="stBaseButton-pills"],[data-testid="stBaseButton-pillsActive"]{border-radius:999px;font-weight:500}
[data-testid="stBaseButton-pillsActive"]{background:var(--deep);color:#fff;border-color:var(--deep)}
[data-testid="stBaseButton-pillsActive"] *{color:#fff!important}

/* ---------- Trang chủ ---------- */
/* Hero */
.hero{position:relative;overflow:hidden;display:grid;grid-template-columns:1.15fr 1fr;gap:36px;align-items:center;
background:var(--hero);border-radius:20px;padding:48px 48px 56px;color:var(--ink)}
.hero::after{content:"";position:absolute;left:0;right:0;bottom:0;height:6px;
background:repeating-linear-gradient(90deg,var(--dash) 0 36px,transparent 36px 64px)}
.chip{display:inline-block;border:1.5px solid var(--chip);color:var(--chip);font-weight:600;font-size:.8rem;
padding:4px 12px;border-radius:999px;margin-bottom:18px}
.hero h1{font-size:3.6rem;font-weight:800;line-height:1.05;margin:0 0 14px;padding:0;color:var(--ink);letter-spacing:-.02em}
.hero p{color:var(--herosub);font-size:1.1rem;line-height:1.6;max-width:34ch;margin:0}

/* Khung mô phỏng nhận diện */
.frame{position:relative;aspect-ratio:4/3;border-radius:12px;background:var(--deep);box-shadow:inset 0 0 0 1px #343A40}
.frame::before{content:"";position:absolute;left:12%;top:0;bottom:0;width:4px;opacity:.55;
background:repeating-linear-gradient(180deg,var(--line) 0 22px,transparent 22px 44px)}
.pit{position:absolute;left:32%;top:44%;width:36%;height:24%;border-radius:50%;background:#0A0C0E;
box-shadow:inset 0 6px 14px #000,0 0 0 5px #2E3338}
.box{position:absolute;left:25%;top:34%;width:50%;height:44%;border:2px solid var(--line);border-radius:3px}
.tag{position:absolute;top:-24px;left:-2px;background:var(--line);color:#23272B;font-weight:700;
font-size:.78rem;padding:3px 9px;border-radius:3px 3px 3px 0;white-space:nowrap}

.sec{font-size:1.5rem;font-weight:700;color:var(--ink);margin:48px 0 6px}
.sub{color:var(--muted);font-size:.92rem;margin:0 0 18px}

/* Các bước */
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:16px}
.step{position:relative;background:var(--card);border-radius:14px;padding:24px}
.step:not(:last-child)::after{content:"";position:absolute;top:40px;right:-24px;width:24px;border-top:3px dashed var(--line)}
.num{display:grid;place-items:center;width:34px;height:34px;border-radius:50%;background:var(--line);
color:#23272B;font-weight:700;margin-bottom:14px}
.step h3{font-size:1.2rem;font-weight:700;margin:0 0 6px;padding:0;color:var(--ink)}
.step p{color:var(--muted);font-size:.95rem;line-height:1.55;margin:0}

/* Chỉ số */
.stats{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:16px}
.stat{background:var(--card);border-radius:14px;padding:20px 22px}
.stat.lead{background:var(--hero)}
.stat .k{font-size:.85rem;font-weight:600;color:var(--muted)}
.stat .v{font-size:2.6rem;font-weight:700;line-height:1.15;margin:4px 0 0;color:var(--ink);letter-spacing:-.02em}
.stat.lead .v{font-size:3.2rem;color:var(--chip)}
.stat.lead .k,.stat.lead .d{color:var(--herosub)}
.bar{height:6px;border-radius:3px;background:var(--track);margin:12px 0 10px}
.stat.lead .bar{background:rgba(0,0,0,.09)}
.bar i{display:block;height:100%;border-radius:3px;background:var(--ink)}
.stat.lead .bar i{background:var(--dash)}
.stat .d{font-size:.8rem;line-height:1.45;color:var(--muted);margin:0}

@media (max-width:820px){
.hero,.steps,.stats{grid-template-columns:1fr}
.step::after{display:none}
.hero h1{font-size:2.6rem}
}

</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


# =========================================================
# HÀM TIỆN ÍCH DÙNG CHUNG CHO CÁC TRANG
# =========================================================

from html import escape

STATUS_CLASS = {"Chưa xử lý": "s0", "Đang xử lý": "s1", "Đã xử lý": "s2"}
SEVERITY_LABELS = ["Nhẹ", "Trung bình", "Nặng"]


def page_header(title, subtitle=""):
    """Tiêu đề trang thống nhất."""
    st.markdown(
        f'<div class="ph"><h1>{escape(title)}</h1><p>{escape(subtitle)}</p></div>',
        unsafe_allow_html=True,
    )


def severity_level(count):
    """Mức độ ước tính theo số ổ gà trong báo cáo (không lưu vào DB).
    0 = Nhẹ (1 ổ), 1 = Trung bình (2-3 ổ), 2 = Nặng (từ 4 ổ)."""
    count = int(count or 0)
    if count >= 4:
        return 2
    if count >= 2:
        return 1
    return 0


def severity_label(count):
    return SEVERITY_LABELS[severity_level(count)]


def severity_html(count):
    lv = severity_level(count)
    return f'<span class="sev v{lv}">● {SEVERITY_LABELS[lv]}</span>'


def status_pill(status):
    cls = STATUS_CLASS.get(status, "s1")
    return f'<span class="pill {cls}">{escape(str(status))}</span>'


def kpi_strip(items):
    """items: [(giá trị, nhãn, class_thêm_nếu_cần), ...]"""
    cells = "".join(
        f'<div class="{cls}"><b>{value}</b><span>{escape(label)}</span></div>'
        for value, label, cls in items
    )
    st.markdown(f'<div class="kpi">{cells}</div>', unsafe_allow_html=True)


def sidebar_brand():
    st.sidebar.markdown(
        '<div class="brand"><span class="dot"></span>RoadAI</div>',
        unsafe_allow_html=True,
    )
    st.sidebar.caption("Giám sát chất lượng mặt đường bằng YOLO")


def sidebar_model_box():
    st.sidebar.markdown(
        '<div class="model"><b><span class="live"></span>YOLO11n đang chạy</b>'
        "best.pt · ngưỡng mặc định 0,25</div>",
        unsafe_allow_html=True,
    )
