import os
import tempfile
import cv2
import streamlit as st
from detector import detect


def render(show_title=True):
    if show_title:
        st.title("Nhận diện ổ gà từ video")
    step = st.slider("Chỉ xử lý 1 khung mỗi N khung (số lớn thì nhanh hơn)", 1, 10, 3)
    f = st.file_uploader("Tải video lên", type=["mp4", "mov", "avi"])

    if f is None:
        st.info("Hãy tải một video ngắn (10-30 giây) để bắt đầu.")
        return

    st.video(f.getvalue())

    if st.button("Bắt đầu nhận diện", type="primary"):
        try:
            import imageio
        except ImportError:
            st.error("Thiếu thư viện. Chạy: pip install imageio imageio-ffmpeg")
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(f.name)[1]) as tmp:
            tmp.write(f.getvalue())
            in_path = tmp.name

        cap = cv2.VideoCapture(in_path)
        if not cap.isOpened():
            st.error("Không mở được video này.")
            return

        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        out_path = in_path + "_out.mp4"
        writer = imageio.get_writer(out_path, fps=fps / step, codec="libx264",
                                    macro_block_size=None)
        bar = st.progress(0.0, text="Đang xử lý video...")
        idx, processed, max_n, best, confs = 0, 0, 0, None, []

        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if idx % step == 0:
                out, n, items = detect(frame)
                h, w = out.shape[:2]
                out = out[: h // 2 * 2, : w // 2 * 2]
                writer.append_data(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))
                processed += 1
                confs += [i["conf"] for i in items if i["class"] == "pothole"]
                if n > max_n:
                    max_n, best = n, out
            idx += 1
            if idx % 5 == 0:
                bar.progress(min(idx / total, 1.0))

        cap.release()
        writer.close()
        bar.progress(1.0, text="Xong")

        with open(out_path, "rb") as fh:
            video_bytes = fh.read()
        st.session_state["video_result"] = {
            "name": f.name, "video": video_bytes, "frames": processed,
            "max_n": max_n, "best": best,
            "avg_conf": (sum(confs) / len(confs)) if confs else 0,
        }

    res = st.session_state.get("video_result")
    if res and res["name"] == f.name:
        st.success("Đã nhận diện xong")
        st.video(res["video"])
        m1, m2, m3 = st.columns(3)
        m1.metric("Số khung đã xử lý", res["frames"])
        m2.metric("Nhiều nhất trong 1 khung", res["max_n"])
        m3.metric("Độ tin cậy trung bình", f"{res['avg_conf']:.0%}")
        if res["best"] is not None:
            st.image(res["best"], channels="BGR", caption="Khung có nhiều ổ gà nhất")
        else:
            st.info("Không phát hiện ổ gà nào trong video.")