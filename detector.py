
from ultralytics import YOLO

model = YOLO("best.pt")

def detect(image_bgr, conf=0.25):
    r = model.predict(
        source=image_bgr,
        conf=conf,
        iou=0.45,
        imgsz=640,
        max_det=300,
        verbose=False
    )[0]

    annotated = r.plot()

    items = []

    for b in r.boxes:
        items.append({
            "class": model.names[int(b.cls)],
            "conf": round(float(b.conf), 3),
            "box": [round(v) for v in b.xyxy[0].tolist()],
        })

    n_pothole = sum(
        1 for i in items
        if i["class"] == "pothole"
    )

    return annotated, n_pothole, items
