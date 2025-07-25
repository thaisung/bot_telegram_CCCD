from PIL import Image
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def import_text_mt(No,Full_name,Date_of_birth,Sex,Nationality,Place_of_origin,Place_of_residence,Date_of_expiry):
    # === Load ảnh gốc và tạo đối tượng vẽ ===
    image_path = "mt.png"  # ảnh CCCD gốc
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    # === 1. Thông tin và vị trí cần chèn số CCCD ===
    text = No
    position = (415, 290)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
    text_color = (0, 0, 0)  # Màu đen
    draw.text(position, text, font=load_font_Bold(35), fill=text_color)

    # === .2 Thông tin và vị trí cần chèn Họ và tên ===
    text = Full_name
    text = text.upper()
    position = (335, 358)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
    text_color = (0, 0, 0)  # Màu đen
    draw.text(position, text, font=load_font_Regular(26), fill=text_color)

    # === 3. Thông tin và vị trí cần chèn Ngay sinh ===
    text = Date_of_birth
    position = (545, 382)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
    text_color = (0, 0, 0)  # Màu đen
    draw.text(position, text, font=load_font_Regular(24), fill=text_color)

    # === 4. Thông tin và vị trí cần chèn Giới tính ===
    text = Sex
    position = (468, 414)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
    text_color = (0, 0, 0)  # Màu đen
    draw.text(position, text, font=load_font_Regular(24), fill=text_color)

    # === 5. Thông tin và vị trí cần chèn Quốc tịch ===
    text = Nationality
    position = (724, 412)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
    text_color = (0, 0, 0)  # Màu đen
    draw.text(position, text, font=load_font_Regular(24), fill=text_color)

    # === 6. Thông tin và vị trí cần chèn Quê quán ===
    text = Place_of_origin
    position = (337, 473)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
    text_color = (0, 0, 0)  # Màu đen
    draw.text(position, text, font=load_font_Regular(24), fill=text_color)

    # === 7. Thông tin và vị trí cần chèn Nơi thường chú ===
    text = Place_of_residence
    position = (335, 533)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
    text_color = (0, 0, 0)  # Màu đen
    draw.text(position, text, font=load_font_Regular(24), fill=text_color)

    # === 7. Thông tin và vị trí cần chèn Có giá trị dến ===
    text = Date_of_expiry
    position = (230, 520)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
    text_color = (0, 0, 0)  # Màu đen
    draw.text(position, text, font=load_font_Regular(19), fill=text_color)


    # ===  Lưu ảnh kết quả ===
    output_path = "cccd_text_mt.png"
    image.save(output_path)
    print(f"✅ Đã chèn chữ vào ảnh và lưu tại: {output_path}")