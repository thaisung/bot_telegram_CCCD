from PIL import Image, ImageDraw, ImageFont
import datetime
import unicodedata

# === 1. Chuyển ngày sang MRZ format ===
def to_mrz_date(date_str):
    dt = datetime.datetime.strptime(date_str, "%d/%m/%Y")
    return dt.strftime("%y%m%d")

# === 2. Chuẩn hóa tên: LAST<<MIDDLE<FIRST ===
def remove_accents(input_str):
    """Bỏ dấu tiếng Việt"""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

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

# === 6. Thông tin đầu vào ===
No = "035065003965"
Full_name = "Vũ Kiên Quyết"
Date_of_birth = "12/03/1990"
Sex = "Nam"
Nationality = "Việt Nam"
Date_of_expiry = "20/09/2036"
Date_month_year = "12/08/2025"

# === 7. Gọi hàm ===
line1, line2, line3 = generate_mrz(No, Full_name, Date_of_birth, Sex, Nationality, Date_of_expiry, Date_month_year)
write_mrz_to_image(
    image_path="mss.png",  # Tên ảnh CCCD gốc
    output_path="cccd_with_mrz.png",
    mrz_lines=[line1, line2, line3]
)
