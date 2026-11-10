import cv2
from datetime import datetime

import sqlite3
from pathlib import Path

# Xác định thư mục chứa source code
BASE_DIR = Path(__file__).resolve().parent

# Thư mục lưu database
DATA_DIR = BASE_DIR / "data"

# Thư mục lưu database
IMAGE_DIR = DATA_DIR / "report_images"

# Đường dẫn file SQLite
DB_PATH = DATA_DIR / "roadai.db"
    
def init_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT NOT NULL,
            pothole_count INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            lat REAL,
            lon REAL,
            status TEXT NOT NULL DEFAULT 'Chưa xử lý'
        )
    """)

    conn.commit()

    conn.close()

    print("Khởi tạo database và bảng reports thành công!")


def add_report(image, pothole_count, lat=None, lon=None,
               status="Chưa xử lý"):

    # Tạo tên ảnh theo thời gian
    filename = datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".jpg"

    # Đường dẫn lưu ảnh
    image_path = IMAGE_DIR / filename

    # Lưu ảnh đã nhận diện
    success = cv2.imwrite(str(image_path), image)

    if not success:
        raise Exception("Không thể lưu ảnh báo cáo!")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO reports (
                image_path,
                pothole_count,
                created_at,
                lat,
                lon,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(image_path),
            pothole_count,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            lat,
            lon,
            status
        ))

        report_id = cursor.lastrowid

        conn.commit()

        return report_id

    except Exception:
        conn.rollback()

        if image_path.exists():
            image_path.unlink()

        raise

    finally:
        conn.close()
        
        

def update_report_status(report_id, status):
    allowed_statuses = [
        "Chưa xử lý",
        "Đang xử lý",
        "Đã xử lý"
    ]

    if status not in allowed_statuses:
        raise ValueError("Trạng thái không hợp lệ!")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE reports
            SET status = ?
            WHERE id = ?
        """, (status, report_id))

        if cursor.rowcount == 0:
            raise ValueError("Không tìm thấy báo cáo!")

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

        
if __name__ == "__main__":
    init_db()