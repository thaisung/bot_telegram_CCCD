import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import datetime
import unicodedata

def load_font_Regular(size):
    font_path = "font-text/LiberationSans-Regular.ttf"  # Đường dẫn tới font
    font = ImageFont.truetype(font_path, size)
    return font

def load_font_Bold(size):
    font_path = "font-text/LiberationSans-Bold.ttf"  # Đường dẫn tới font
    font = ImageFont.truetype(font_path, size)
    return font


def import_text_ms(No,Full_name,Date_of_birth,Sex,Nationality,Place_of_origin,Place_of_residence,Date_of_expiry,Date_month_year):
    # === Load ảnh gốc và tạo đối tượng vẽ ===
    image_path = "MMSS.png"  # ảnh CCCD gốc
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    # === 1. Thông tin và vị trí cần chèn Cư trú ===
    text = Place_of_origin
    position = (178, 240)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
    text_color = (0, 0, 0)  # Màu đen
    draw.text(position, text, font=load_font_Regular(24), fill=text_color)

    # === 2. Thông tin và vị trí cần chèn Nơi đăng ký khai sinh ===
    text = Place_of_residence
    position = (178, 318)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
    text_color = (0, 0, 0)  # Màu đen
    draw.text(position, text, font=load_font_Regular(24), fill=text_color)


    # === 3. Chèn Ngày tháng năm cấp ===
    text = Date_month_year
    position = (499, 387)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
    text_color = (0, 0, 0)  # Màu đen
    draw.text(position, text, font=load_font_Regular(24), fill=text_color)

    # === 4. Thông tin và vị trí cần chèn Có giá trị dến ===
    text = Date_of_expiry
    position = (494, 447)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
    text_color = (0, 0, 0)  # Màu đen
    draw.text(position, text, font=load_font_Regular(24), fill=text_color)


    # Ghi mã vạch //////////////////////////////////////////////////////////////

    # === 1. Chuyển ngày sang MRZ format ===
    def to_mrz_date(date_str):
        dt = datetime.datetime.strptime(date_str, "%d/%m/%Y")
        return dt.strftime("%y%m%d")

    # === 2. Chuẩn hóa tên: LAST<<MIDDLE<FIRST ===
    def remove_accents(input_str):
        input_str = input_str.replace("Đ", "D").replace("đ", "d")
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        return ''.join([c for c in nfkd_form if not unicodedata.combining(c) and c.isascii()])

    def normalize_name(name):
        """Chuẩn MRZ: HỌ<<TÊN_ĐỆM<TÊN và bỏ dấu"""
        name = remove_accents(name.upper())  # In hoa và bỏ dấu
        parts = name.split()
        if len(parts) >= 2:
            first = parts[0]  # Họ
            rest = parts[1:]  # Tên đệm + tên
            return f"{first}<<{'<'.join(rest)}"
        return name

    # === 3. Tạo mã MRZ gồm 3 dòng ===
    def generate_mrz(No, Full_name, Date_of_birth, Sex, Nationality, Date_of_expiry, Date_month_year):
        sex_code = "M" if Sex.lower() == "nam" else "F"
        country_code = "VNM"

        dob_mrz = to_mrz_date(Date_of_birth)
        expiry_mrz = to_mrz_date(Date_of_expiry)
        issue_mrz = to_mrz_date(Date_month_year)

        line1 = f"ID{country_code}3{issue_mrz}{No}{No[-1]}<<4".ljust(30, "<")
        line2 = f"{dob_mrz}{sex_code}{expiry_mrz}{country_code}<<<<<<<<<<0".ljust(30, "<")
        line3 = normalize_name(Full_name).ljust(30, "<")[:30]

        return line1, line2, line3

    # === 4. Load font MRZ ===
    def load_mrz_font(size=35):
        try:
            return ImageFont.truetype("font-text/OCR-B_10_BT_Regular.ttf", size)
        except:
            return ImageFont.truetype("arial.ttf", size)  # Fallback nếu không có OCR font
        
    # === 5. Ghi MRZ lên ảnh ===
    def write_mrz_to_image(image_path, output_path, mrz_lines):
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        font = load_mrz_font(44)
        text_color = (0, 0, 0)

        # Ghi 3 dòng MRZ từ trái qua phải, mỗi dòng cách nhau ~40px
        x_start = 200   
        y_start = 573
        line_spacing = 45

        for i, line in enumerate(mrz_lines):
            position = (x_start, y_start + i * line_spacing)
            draw.text(position, line, font=font, fill=text_color)

        img.save(output_path)
        print(f"✅ Đã lưu ảnh có MRZ vào: {output_path}")

    # /////////////////////////////////////////////////////////////////////////

    # === Lưu ảnh kết quả ===
    output_path = "cccd_text_ms.png"
    image.save(output_path)
    print(f"✅ Đã chèn chữ vào ảnh và lưu tại: {output_path}")

    line1, line2, line3 = generate_mrz(No, Full_name, Date_of_birth, Sex, Nationality, Date_of_expiry, Date_month_year)
    print('line1:',line1)
    write_mrz_to_image(
        image_path="cccd_text_ms.png",  # Tên ảnh CCCD gốc
        output_path="cccd_text_ms.png",
        mrz_lines=[line1, line2, line3]
    )


No = "035065003965"
Full_name = "Vũ Hoàng Anh"
Date_of_birth = "12/03/1990"
Sex = "Nam"
Nationality = "Việt Nam"
Place_of_origin =  "Nam Bình 2, Hoà Xuân Tây, Thị xã Đông Hoà, Phú Yên"
Place_of_residence = "Hoà Xuân Tây, Thị xã Đông Hoà, Phú Yên"
Date_month_year = "08/09/2024"
Date_of_expiry = "04/07/2035"

import_text_ms(No,Full_name,Date_of_birth,Sex,Nationality,Place_of_origin,Place_of_residence,Date_of_expiry,Date_month_year)
