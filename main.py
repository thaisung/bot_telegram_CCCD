import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import datetime
import unicodedata


# def import_photo(url):
#     # Ảnh CCCD gốc
#     cccd_path = "mt.png"
#     cccd_img = Image.open(cccd_path).convert("RGB")

#     # Ảnh chân dung từ file trên máy
#     portrait_img = Image.open(url).convert("RGB")

#     # Resize ảnh chân dung cho vừa khung (kích thước 184x250)
#     portrait_resized = portrait_img.resize((184, 250))

#     # Vị trí khung trống trên CCCD (x, y)
#     position = (128, 265)  # Bạn có thể điều chỉnh tọa độ này

#     # Dán ảnh vào CCCD
#     cccd_img.paste(portrait_resized, position)

#     # Lưu kết quả
#     cccd_img.save("mt.png")
#     print("✅ Đã chèn ảnh từ file vào CCCD → 'mt.png'")

def import_photo(url):
    # Ảnh CCCD gốc
    cccd_path = "MMTT.png"
    cccd_img = Image.open(cccd_path).convert("RGB")

    # Ảnh chân dung từ file trên máy
    portrait_img = Image.open(url).convert("RGB")

    # Resize ảnh chân dung cho vừa khung (kích thước 184x250)
    portrait_resized = portrait_img.resize((245, 350))

    # Vị trí khung trống trên CCCD (x, y)
    position = (166, 442)  # Bạn có thể điều chỉnh tọa độ này

    # Dán ảnh vào CCCD
    cccd_img.paste(portrait_resized, position)

    # Lưu kết quả
    cccd_img.save("mt.png")
    print("✅ Đã chèn ảnh từ file vào CCCD → 'mt.png'")



def load_font_Regular(size):
    font_path = "font-text/LiberationSans-Regular.ttf"  # Đường dẫn tới font
    font = ImageFont.truetype(font_path, size)
    return font

def load_font_Bold(size):
    font_path = "font-text/LiberationSans-Bold.ttf"  # Đường dẫn tới font
    font = ImageFont.truetype(font_path, size)
    return font

# def import_text_mt(No,Full_name,Date_of_birth,Sex,Nationality,Place_of_origin,Place_of_residence,Date_of_expiry):
#     # === Load ảnh gốc và tạo đối tượng vẽ ===
#     image_path = "mt.png"  # ảnh CCCD gốc
#     image = Image.open(image_path).convert("RGB")
#     draw = ImageDraw.Draw(image)

#     # === 1. Thông tin và vị trí cần chèn số CCCD ===
#     text = No
#     position = (415, 290)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
#     text_color = (0, 0, 0)  # Màu đen
#     draw.text(position, text, font=load_font_Bold(35), fill=text_color)

#     # === .2 Thông tin và vị trí cần chèn Họ và tên ===
#     text = Full_name
#     text = text.upper()
#     position = (335, 358)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
#     text_color = (0, 0, 0)  # Màu đen
#     draw.text(position, text, font=load_font_Regular(26), fill=text_color)

#     # === 3. Thông tin và vị trí cần chèn Ngay sinh ===
#     text = Date_of_birth
#     position = (545, 382)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
#     text_color = (0, 0, 0)  # Màu đen
#     draw.text(position, text, font=load_font_Regular(24), fill=text_color)

#     # === 4. Thông tin và vị trí cần chèn Giới tính ===
#     text = Sex
#     position = (468, 414)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
#     text_color = (0, 0, 0)  # Màu đen
#     draw.text(position, text, font=load_font_Regular(24), fill=text_color)

#     # === 5. Thông tin và vị trí cần chèn Quốc tịch ===
#     text = Nationality
#     position = (724, 412)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
#     text_color = (0, 0, 0)  # Màu đen
#     draw.text(position, text, font=load_font_Regular(24), fill=text_color)

#     # === 6. Thông tin và vị trí cần chèn Quê quán ===
#     text = Place_of_origin
#     position = (337, 473)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
#     text_color = (0, 0, 0)  # Màu đen
#     draw.text(position, text, font=load_font_Regular(24), fill=text_color)

#     # === 7. Thông tin và vị trí cần chèn Nơi thường chú ===
#     text = Place_of_residence
#     position = (335, 533)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
#     text_color = (0, 0, 0)  # Màu đen
#     draw.text(position, text, font=load_font_Regular(24), fill=text_color)

#     # === 7. Thông tin và vị trí cần chèn Có giá trị dến ===
#     text = Date_of_expiry
#     position = (230, 520)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
#     text_color = (0, 0, 0)  # Màu đen
#     draw.text(position, text, font=load_font_Regular(19), fill=text_color)


#     # ===  Lưu ảnh kết quả ===
#     output_path = "cccd_text_mt.png"
#     image.save(output_path)
#     print(f"✅ Đã chèn chữ vào ảnh và lưu tại: {output_path}")

def import_text_mt(No,Full_name,Date_of_birth,Sex,Nationality):
    # === Load ảnh gốc và tạo đối tượng vẽ ===
    image_path = "MMTT.png"  # ảnh CCCD gốc
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    # === 1. Thông tin và vị trí cần chèn số CCCD ===
    text = No
    position = (454, 530)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
    text_color = (0, 0, 0)  # Màu đen
    draw.text(position, text, font=load_font_Bold(42), fill=text_color)

    # === .2 Thông tin và vị trí cần chèn Họ và tên ===
    text = Full_name
    text = text.upper()
    position = (454, 629)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
    text_color = (0, 0, 0)  # Màu đen
    draw.text(position, text, font=load_font_Regular(30), fill=text_color)

    # === 3. Thông tin và vị trí cần chèn Ngay sinh ===
    text = Date_of_birth
    position = (454, 722)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
    text_color = (0, 0, 0)  # Màu đen
    draw.text(position, text, font=load_font_Regular(25), fill=text_color)

    # === 4. Thông tin và vị trí cần chèn Giới tính ===
    text = Sex
    position = (926, 720)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
    text_color = (0, 0, 0)  # Màu đen
    draw.text(position, text, font=load_font_Regular(25), fill=text_color)

    # === 5. Thông tin và vị trí cần chèn Quốc tịch ===
    text = Nationality
    position = (484, 798)  # Tọa độ x, y bạn có thể thay đổi theo ý muốn
    text_color = (0, 0, 0)  # Màu đen
    draw.text(position, text, font=load_font_Regular(25), fill=text_color)

    # ===  Lưu ảnh kết quả ===
    output_path = "cccd_text_mt.png"
    image.save(output_path)
    print(f"✅ Đã chèn chữ vào ảnh và lưu tại: {output_path}")



def import_text_ms(Personal_identification, Date_month_year):
    # === Load ảnh gốc và tạo đối tượng vẽ ===
    image_path = "mss.png"  # ảnh CCCD gốc
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    # === 1. Chèn Đặc điểm nhận dạng (tự động xuống dòng nếu > 7 từ) ===
    words = Personal_identification.split()
    lines = []

    # Chia thành các dòng mỗi dòng tối đa 7 từ
    for i in range(0, len(words), 7):
        line = " ".join(words[i:i + 7])
        lines.append(line)

    # Vẽ từng dòng tại tọa độ (100, y), tăng y theo dòng
    y = 103
    line_height = draw.textbbox((0, 0), "A", font=load_font_Regular(18))[3] + 4

    for line in lines:
        draw.text((100, y), line, font=load_font_Regular(18), fill=(0, 0, 0))
        y += line_height

    # === 2. Chèn Ngày tháng năm ===
    draw.text((380, 140), Date_month_year, font=load_font_Regular(18), fill=(0, 0, 0))

    # === Lưu ảnh kết quả ===
    output_path = "cccd_text_ms.png"
    image.save(output_path)
    print(f"✅ Đã chèn chữ vào ảnh và lưu tại: {output_path}")

# ==== Nhập từ terminal với giá trị mặc định ====
def input_or_default(prompt, default):
    value = input(f"{prompt} [{default}]: ")
    return value.strip() or default

# url = "https://i.pinimg.com/236x/9e/5a/5d/9e5a5d47ea9f1d160d328919525e0bf7.jpg"
url = input_or_default("Đường dẫn ảnh", "avatar/iu.jpg")
import_photo(url)

# No = "035065003965"
# Full_name = "Vũ Hoàng Anh"
# Date_of_birth = "12/03/1990"
# Sex = "Nam"
# Nationality = "Việt Nam"
# Place_of_origin = "Thanh Xuân, Hà Nội"
# Place_of_residence = "Thanh Xuân, Hà Nội"
# Date_of_expiry = "20/09/2036"

No = input_or_default("Số CCCD", "035065003965")
Full_name = input_or_default("Họ tên", "Vũ Hoàng Anh")
Date_of_birth = input_or_default("Ngày sinh (dd/mm/yyyy)", "12/03/1990")
Sex = input_or_default("Giới tính (Nam/Nữ)", "Nam")
Nationality = input_or_default("Quốc tịch", "Việt Nam")
Place_of_origin = input_or_default("Nguyên quán", "Thanh Xuân, Hà Nội")
Place_of_residence = input_or_default("Nơi cư trú", "Thanh Xuân, Hà Nội")
Date_of_expiry = input_or_default("Ngày hết hạn (dd/mm/yyyy)", "20/09/2036")


import_text_mt(No,Full_name,Date_of_birth,Sex,Nationality,Place_of_origin,Place_of_residence,Date_of_expiry)

# Personal_identification = "Sẹo chấm C:2,5 cm trên trước đuôi lông mày phải"
# Date_month_year = "12/08/2025"
Personal_identification = input_or_default("Đặc điểm nhận dạng", "Sẹo chấm C:2,5 cm trên trước đuôi lông mày phải")
Date_month_year = input_or_default("Ngày cấp (dd/mm/yyyy)", "12/08/2025")
import_text_ms(Personal_identification,Date_month_year)



# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

from PIL import Image, ImageDraw, ImageFont
import datetime
import unicodedata

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
    font = load_mrz_font(36)
    text_color = (0, 0, 0)

    # Ghi 3 dòng MRZ từ trái qua phải, mỗi dòng cách nhau ~40px
    x_start = 113
    y_start = 390
    line_spacing = 40

    for i, line in enumerate(mrz_lines):
        position = (x_start, y_start + i * line_spacing)
        draw.text(position, line, font=font, fill=text_color)

    img.save(output_path)
    print(f"✅ Đã lưu ảnh có MRZ vào: {output_path}")


# === 7. Gọi hàm ===
line1, line2, line3 = generate_mrz(No, Full_name, Date_of_birth, Sex, Nationality, Date_of_expiry, Date_month_year)
write_mrz_to_image(
    image_path="cccd_text_ms.png",  # Tên ảnh CCCD gốc
    output_path="cccd_text_ms.png",
    mrz_lines=[line1, line2, line3]
)
