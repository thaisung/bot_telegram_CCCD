import os
import asyncio
import datetime
import unicodedata
from telegram import Update, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes,
    ConversationHandler, filters
)
from PIL import Image, ImageDraw, ImageFont
from PIL import Image, ImageFilter, ImageDraw
from PIL import ImageEnhance, ImageOps

import sys

from telegram import BotCommand

from telegram import Bot
from telegram.error import TelegramError

from datetime import datetime

import subprocess
import sys
import os
import html
import numpy as np


# ==== Font loader ====
def load_font_Regular(size): return ImageFont.truetype("font-text/LiberationSans-Regular.ttf", size)
def load_font_Bold(size): return ImageFont.truetype("font-text/LiberationSans-Bold.ttf", size)

def load_mrz_font(size=35):
    try:
        return ImageFont.truetype("font-text/OCR-B_10_BT_Regular.ttf", size)
    except:
        return ImageFont.truetype("arial.ttf", size)

# ==== Utility for MRZ ====
def to_mrz_date(date_str):
    dt = datetime.strptime(date_str, "%d/%m/%Y")  # dùng datetime đã import từ 'from datetime import datetime'
    return dt.strftime("%y%m%d")

def remove_accents(input_str):
    input_str = input_str.replace("Đ", "D").replace("đ", "d")
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c) and c.isascii()])

def normalize_name(name):
    name = remove_accents(name.upper())
    parts = name.split()
    if len(parts) >= 2:
        return f"{parts[0]}<<{'<'.join(parts[1:])}"
    return name

# def generate_mrz(No, Full_name, DOB, Sex, Nation, Expiry, Issue):
#     sex_code = "M" if Sex.lower() == "nam" else "F"
#     country_code = "VNM"
#     line1 = f"ID{country_code}3{to_mrz_date(Issue)}{No}{No[-1]}<<4".ljust(30, "<")
#     line2 = f"{to_mrz_date(DOB)}{sex_code}{to_mrz_date(Expiry)}{country_code}<<<<<<<<<<0".ljust(30, "<")
#     line3 = normalize_name(Full_name).ljust(30, "<")[:30]
#     return line1, line2, line3

def generate_mrz(No, Full_name, DOB, Sex, Nation, Expiry, Issue):
    import unicodedata

    def to_mrz_date(date_str):
        # Định dạng "yyyy-mm-dd" → "yymmdd"
        parts = date_str.split("/")
        yyyy, mm, dd = parts
        return f"{yyyy[-2:]}{mm}{dd}"

    def normalize_name(name):
        name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode()
        parts = name.upper().split()
        if len(parts) >= 2:
            return f"{parts[0]}<<{'<'.join(parts[1:])}"
        else:
            return f"{parts[0]}<<"

    def checksum(data):
        weights = [7, 3, 1]
        total = 0
        for i, char in enumerate(data):
            if char.isdigit():
                val = int(char)
            elif char.isalpha():
                val = ord(char.upper()) - 55
            elif char == '<':
                val = 0
            else:
                val = 0
            total += val * weights[i % 3]
        return str(total % 10)

    sex_code = "M" if Sex.lower() == "nam" else "F"
    country_code = "VNM"

    # ==== LINE 1 ====
    issue_date = to_mrz_date(Issue)
    line1_core = f"ID{country_code}3{issue_date}{No}"
    check1 = checksum(line1_core[5:])  # checksum của issue_date + No
    line1 = (line1_core + "<" * (29 - len(line1_core)) + check1)[:30]

    # ==== LINE 2 ====
    dob = to_mrz_date(DOB)
    expiry = to_mrz_date(Expiry)
    line2_core = f"{dob}{sex_code}{expiry}{country_code}"
    check2 = checksum(line2_core)
    filler2 = "<" * (29 - len(line2_core))
    line2 = (line2_core + filler2 + check2)[:30]

    # ==== LINE 3 ====
    line3 = normalize_name(Full_name).ljust(30, "<")[:30]

    return line1, line2, line3




# ==== CCCD tạo ảnh ====
def apply_sepia(img):
    """Hiệu ứng ảnh cũ nhẹ nhàng, giữ màu gốc"""

    # 1. Giảm độ bão hòa (50%)
    converter = ImageEnhance.Color(img)
    desaturated = converter.enhance(0.5)

    # 2. Áp màu ám vàng nhẹ (warm filter)
    r, g, b = desaturated.split()
    r = r.point(lambda i: min(i + 10, 255))
    g = g.point(lambda i: min(i + 5, 255))
    warm_img = Image.merge("RGB", (r, g, b))

    # 3. Thêm noise nhẹ (giả lập film grain)
    np_img = np.array(warm_img).astype(np.uint8)
    noise = np.random.normal(0, 10, np_img.shape).astype(np.int16)
    noisy = np.clip(np_img + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy)

# def apply_sepia(img):
#     """Hiệu ứng ảnh cũ nhẹ nhàng, giữ màu gốc"""

#     # 1. Giảm độ bão hòa (giữ màu nguyên bản hơn, thay vì 0.5 thì tăng lên)
#     converter = ImageEnhance.Color(img)
#     desaturated = converter.enhance(0.7)  # Ít xỉn màu hơn

#     # 2. Áp màu vàng nhẹ (warm filter)
#     r, g, b = desaturated.split()
#     r = r.point(lambda i: min(i + 8, 255))  # giảm từ +10 → +8
#     g = g.point(lambda i: min(i + 4, 255))  # giảm từ +5 → +4
#     warm_img = Image.merge("RGB", (r, g, b))

#     # 3. Thêm noise nhẹ hơn
#     np_img = np.array(warm_img).astype(np.uint8)
#     noise = np.random.normal(0, 3, np_img.shape).astype(np.int16)  # giảm từ 10 → 3
#     noisy = np.clip(np_img + noise, 0, 255).astype(np.uint8)

#     # 4. Làm mịn ảnh để giảm "chấm" thấy rõ
#     final_img = Image.fromarray(noisy).filter(ImageFilter.SMOOTH_MORE)

#     return final_img


def import_photo(file_path):
    # Load ảnh nền CCCD và ảnh chân dung
    cccd_img = Image.open("MMTT.png").convert("RGB")
    portrait_img = Image.open(file_path).convert("RGB").resize((245, 350))

    # Làm mờ nhẹ ảnh chân dung và áp hiệu ứng sepia
    blurred = portrait_img.filter(ImageFilter.GaussianBlur(0.8))
    sepia_portrait = apply_sepia(blurred)

    # Kích thước và vị trí
    width, height = sepia_portrait.size
    fade_margin = 15
    paste_x, paste_y = 166, 442

    # Tạo mask mờ viền từ ngoài vào trong
    mask = Image.new("L", (width, height), 255)
    for y in range(height):
        for x in range(width):
            dist_to_edge = min(x, y, width - x - 1, height - y - 1)
            if dist_to_edge < fade_margin:
                alpha = int(255 * (dist_to_edge / fade_margin))
                mask.putpixel((x, y), alpha)
    mask = mask.filter(ImageFilter.GaussianBlur(2))

    # Cắt phần nền CCCD tương ứng vị trí dán để blend vào
    bg_crop = cccd_img.crop((paste_x, paste_y, paste_x + width, paste_y + height))

    # Trộn ảnh chân dung với nền CCCD bằng mask viền mờ
    blended = Image.composite(sepia_portrait, bg_crop, mask)

    # Dán ảnh đã trộn vào ảnh CCCD
    cccd_img.paste(blended, (paste_x, paste_y))

    # Lưu kết quả
    temp_path = "temp_cccd_photo.png"
    cccd_img.save(temp_path)
    return temp_path

def import_text_mt(No, Full_name, DOB, Sex, Nation, image_path="temp_cccd_photo.png"):
    img = Image.open(image_path).convert("RGBA")

    # Hàm tạo layer chữ mờ
    def draw_blurred_text(position, text, font, blur_radius, alpha):
        layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(layer)
        draw.text(position, text, font=font, fill=(0, 0, 0, alpha))
        return layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    # Tạo từng lớp text với mức mờ khác nhau
    layer_no = draw_blurred_text((454, 530), No, load_font_Bold(42), blur_radius=0.8, alpha=220)
    layer_name = draw_blurred_text((454, 629), Full_name.upper(), load_font_Regular(30), blur_radius=0.8, alpha=300)
    layer_dob = draw_blurred_text((454, 722), DOB, load_font_Regular(25), blur_radius=0.8, alpha=300)
    layer_sex = draw_blurred_text((926, 720), Sex, load_font_Regular(25), blur_radius=0.8, alpha=300)
    layer_nation = draw_blurred_text((484, 798), Nation, load_font_Regular(25), blur_radius=0.8, alpha=300)

    # Gộp tất cả các lớp text vào ảnh gốc
    combined = Image.alpha_composite(img, layer_no)
    for layer in [layer_name, layer_dob, layer_sex, layer_nation]:
        combined = Image.alpha_composite(combined, layer)

    # Lưu kết quả
    output_path = "cccd_text_mt.png"
    combined.convert("RGB").save(output_path)
    return output_path

def import_text_ms(Full_name, No, Origin, Residence, Expiry, Issue, DOB, Sex, Nation):
    from PIL import Image, ImageDraw, ImageFont, ImageFilter

    img = Image.open("MMSS.png").convert("RGBA")

    def draw_blurred_text(position, text, font, blur_radius=0.8, alpha=300):
        layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(layer)
        draw.text(position, text, font=font, fill=(0, 0, 0, alpha))
        return layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    # Vẽ các lớp thông tin hành chính (Origin, Residence, ...)
    layers = [
        draw_blurred_text((178, 240), Origin, load_font_Regular(26)),
        draw_blurred_text((178, 318), Residence, load_font_Regular(26)),
        draw_blurred_text((499, 387), Issue, load_font_Regular(26)),
        draw_blurred_text((494, 447), Expiry, load_font_Regular(26)),
    ]

    # Vẽ 3 dòng MRZ vào lớp riêng với blur nhẹ
    mrz_lines = generate_mrz(No, Full_name, DOB, Sex, Nation, Expiry, Issue)
    for i, line in enumerate(mrz_lines):
        mrz_layer = draw_blurred_text((200, 573 + i * 45), line, load_mrz_font(44), blur_radius=0.8, alpha=255)
        layers.append(mrz_layer)

    # Gộp lần lượt tất cả lớp vào ảnh chính
    combined = img
    for layer in layers:
        combined = Image.alpha_composite(combined, layer)

    # Lưu ảnh đầu ra
    output_path = "cccd_text_ms.png"
    combined.convert("RGB").save(output_path)
    return output_path


# def import_text_ms(Full_name, No, Origin, Residence, Expiry, Issue, DOB, Sex, Nation):
#     img = Image.open("MMSS.png").convert("RGBA")

#     def draw_blurred_text(position, text, font, blur_radius=0.8, alpha=300):
#         layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
#         draw = ImageDraw.Draw(layer)
#         draw.text(position, text, font=font, fill=(0, 0, 0, alpha))
#         return layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))

#     # Các lớp text chính (mờ nhẹ, như mặt trước)
#     layer_origin = draw_blurred_text((178, 240), Origin, load_font_Regular(26))
#     layer_residence = draw_blurred_text((178, 318), Residence, load_font_Regular(26))
#     layer_issue = draw_blurred_text((499, 387), Issue, load_font_Regular(26))
#     layer_expiry = draw_blurred_text((494, 447), Expiry, load_font_Regular(26))

#     # Gộp các lớp vào ảnh gốc
#     combined = Image.alpha_composite(img, layer_origin)
#     for layer in [layer_residence, layer_issue, layer_expiry]:
#         combined = Image.alpha_composite(combined, layer)

#     # MRZ vẫn giữ vẽ trực tiếp (nét đậm, không blur)
#     draw = ImageDraw.Draw(combined)
#     lines = generate_mrz(No, Full_name, DOB, Sex, Nation, Expiry, Issue)
#     for i, line in enumerate(lines):
#         draw.text((200, 573 + i * 45), line, font=load_mrz_font(44), fill=(0, 0, 0))

#     # Lưu kết quả
#     output_path = "cccd_text_ms.png"
#     combined.convert("RGB").save(output_path)
#     return output_path

# def import_text_ms(Full_name, No, Origin, Residence, Expiry, Issue, DOB, Sex, Nation):
#     img = Image.open("MMSS.png").convert("RGB")
#     draw = ImageDraw.Draw(img)
#     draw.text((178, 240), Origin, font=load_font_Regular(26), fill=(0, 0, 0))
#     draw.text((178, 318), Residence, font=load_font_Regular(26), fill=(0, 0, 0))
#     draw.text((499, 387), Issue, font=load_font_Regular(26), fill=(0, 0, 0))
#     draw.text((494, 447), Expiry, font=load_font_Regular(26), fill=(0, 0, 0))
#     lines = generate_mrz(No, Full_name, DOB, Sex, Nation, Expiry, Issue)
#     for i, line in enumerate(lines):
#         draw.text((200, 573 + i * 45), line, font=load_mrz_font(44), fill=(0, 0, 0))
#     img.save("cccd_text_ms.png")
#     return "cccd_text_ms.png"

# ==== File utils ====
def read_file_lines(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return set(line.strip() for line in f if line.strip().isdigit())
    return set()

def add_user(user_id):
    with open("user_ids.txt", "a") as f:
        f.write(f"{user_id}\n")

def remove_user(user_id):
    users = read_file_lines("user_ids.txt")
    users.discard(user_id)
    with open("user_ids.txt", "w") as f:
        for u in users:
            f.write(f"{u}\n")

# ==== Auth ====
def is_admin(user_id):
    return str(user_id) in read_file_lines("admin_ids.txt")

def is_authorized(user_id):
    return str(user_id) in read_file_lines("user_ids.txt") or is_admin(user_id)

# ==== States ====
WAITING_PHOTO, WAITING_INFO_FRONT, WAITING_INFO_BACK = range(3)

# ==== Handlers ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # === Kiểm tra hạn sử dụng ===
    limit_date = datetime.strptime("27/07/2025", "%d/%m/%Y")
    today = datetime.today()
    if today > limit_date:
        await update.message.reply_text("❌ Bot đã hết hạn sử dụng, Cần hoàn tất thanh toán cho người tạo ra mã nguồn.")
        return ConversationHandler.END

    uid = update.effective_user.id
    if not is_authorized(uid):
        await update.message.reply_text("❌ Bạn không có quyền sử dụng bot này.")
        return ConversationHandler.END
    await update.message.reply_text("📸 Gửi ảnh chân dung :")
    return WAITING_PHOTO

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    telegram_file = await context.bot.get_file(photo.file_id)

    # Lấy đuôi file gốc từ Telegram
    file_ext = telegram_file.file_path.split('.')[-1].lower()
    if file_ext not in ["jpg", "jpeg", "png", "webp"]:
        await update.message.reply_text("❌ Chỉ chấp nhận ảnh JPG, PNG hoặc WebP.")
        return ConversationHandler.END

    # Lưu file gốc
    temp_download_path = f"user_{update.effective_user.id}_original.{file_ext}"
    await telegram_file.download_to_drive(temp_download_path)

    # 👉 Tuỳ chọn: Chuyển sang JPG luôn để xử lý về sau dễ hơn
    img = Image.open(temp_download_path).convert("RGB")
    final_path = f"user_{update.effective_user.id}_photo.jpg"
    img.save(final_path, "JPEG")
    os.remove(temp_download_path)  # Xoá file gốc nếu không cần

    # Lưu vào user_data để dùng tiếp
    context.user_data["photo_path"] = final_path

    await update.message.reply_text(
        "✍️ Nhập thông tin mặt trước:\n"
        "`SốCCCD | Họ tên | Ngày sinh | Giới tính | Quốc tịch`\n\n"
        "📌 Ví dụ:\n"
        "`012345678901 | Nguyễn Văn Vinh | 01/01/1990 | Nam | Việt Nam`",
        parse_mode="Markdown"
    )
    return WAITING_INFO_FRONT

async def handle_info_front(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = [x.strip() for x in update.message.text.split("|")]
    
    if len(parts) != 5:
        await update.message.reply_text(
            "❌ Sai định dạng. Vui lòng nhập theo mẫu:\n"
            "`SốCCCD | Họ tên | Ngày sinh | Giới tính | Quốc tịch`\n\n"
            "📌 Ví dụ:\n"
            "`012345678901 | Nguyễn Văn Vinh | 01/01/1990 | Nam | Việt Nam`",
            parse_mode="Markdown"
        )
        return WAITING_INFO_FRONT

    so_cccd, ho_ten, ngay_sinh, gioi_tinh, quoc_tich = parts

    # Kiểm tra định dạng ngày sinh
    try:
        datetime.strptime(ngay_sinh, "%d/%m/%Y")
    except ValueError:
        await update.message.reply_text(
            "❌ Ngày sinh không hợp lệ. Hãy dùng định dạng `dd/mm/yyyy`. Ví dụ: `01/01/1990`"
        )
        return WAITING_INFO_FRONT

    context.user_data["front_info"] = parts
    await update.message.reply_text(
        "📄 Nhập thông tin mặt sau:\n"
        "`Nơi sinh | Nơi cư trú | Ngày cấp | Có giá trị đến`\n\n"
        "📌 Ví dụ:\n"
        "`Xã ABC Tỉnh Ninh Bình | Xã ABC Tỉnh Ninh Bình | 28/07/2020 | 28/07/2030`",
        parse_mode="Markdown"
    )

    return WAITING_INFO_BACK

async def handle_info_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = [x.strip() for x in update.message.text.split("|")]
    if len(parts) != 4:
        await update.message.reply_text(
            "❌ Sai định dạng. Vui lòng nhập theo mẫu:\n"
            "`Nơi sinh | Nơi cư trú | Ngày cấp | Có giá trị đến`\n\n"
            "📌 Ví dụ:\n"
            "`Xã ABC Tỉnh Ninh Bình | Xã ABC Tỉnh Ninh Bình | 28/07/2020 | 28/07/2030`",
            parse_mode="Markdown"
        )
        return WAITING_INFO_BACK

    Origin, Residence, Issue, Expiry = parts

    # Kiểm tra định dạng ngày cấp và có giá trị đến
    for label, date_str in [("Ngày cấp", Issue), ("Có giá trị đến", Expiry)]:
        try:
            datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            await update.message.reply_text(
                f"❌ {label} không hợp lệ. Vui lòng dùng định dạng `dd/mm/yyyy`. Ví dụ: `28/07/2025`"
            )
            return WAITING_INFO_BACK

    await update.message.reply_text("🖼️ Đang xử lý ảnh CCCD...")
    await asyncio.sleep(1)

    No, Full_name, DOB, Sex, Nation = context.user_data["front_info"]
    photo_path = context.user_data["photo_path"]
    
    mt_img = import_text_mt(No, Full_name, DOB, Sex, Nation, import_photo(photo_path))
    ms_img = import_text_ms(Full_name, No, Origin, Residence, Expiry, Issue, DOB, Sex, Nation)

    await update.message.reply_media_group([
        InputMediaPhoto(open(mt_img, "rb"), caption="✅ Mặt trước CCCD"),
        InputMediaPhoto(open(ms_img, "rb"), caption="✅ Mặt sau CCCD")
    ])

    for f in [photo_path, mt_img, ms_img, "temp_cccd_photo.png"]:
        if os.path.exists(f):
            os.remove(f)

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Đã huỷ thao tác tạo CCCD.")
    return ConversationHandler.END

# ==== Admin commands ====
async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Bạn không có quyền.")
        return
    if not context.args:
        await update.message.reply_text("⚠️ Dùng: /adduser <user_id>")
        return
    uid = context.args[0]
    add_user(uid)
    await update.message.reply_text(f"✅ Đã thêm user {uid}.")

async def removeuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Bạn không có quyền.")
        return
    if not context.args:
        await update.message.reply_text("⚠️ Dùng: /removeuser <user_id>")
        return
    uid = context.args[0]
    remove_user(uid)
    await update.message.reply_text(f"✅ Đã xoá user {uid}.")

async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Bạn không có quyền.")
        return
    if not context.args:
        await update.message.reply_text("⚠️ Dùng: /addadmin <user_id>")
        return
    uid = context.args[0]
    with open("admin_ids.txt", "a") as f:
        f.write(f"{uid}\n")
    await update.message.reply_text(f"✅ Đã thêm admin {uid}.")

async def removeadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Bạn không có quyền.")
        return
    if not context.args:
        await update.message.reply_text("⚠️ Dùng: /removeadmin <user_id>")
        return
    uid = context.args[0]
    admins = read_file_lines("admin_ids.txt")
    admins.discard(uid)
    with open("admin_ids.txt", "w") as f:
        for a in admins:
            f.write(f"{a}\n")
    await update.message.reply_text(f"✅ Đã xoá admin {uid}.")

async def listadmins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Bạn không có quyền.")
        return
    admins = read_file_lines("admin_ids.txt")
    text = "👑 Danh sách admin:\n" + "\n".join(admins) if admins else "❌ Chưa có admin nào."
    await update.message.reply_text(text)

async def listusers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Bạn không có quyền.")
        return
    users = read_file_lines("user_ids.txt")
    text = "👤 Danh sách người dùng:\n" + "\n".join(users) if users else "❌ Chưa có user nào."
    await update.message.reply_text(text)

async def settoken(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Bạn không có quyền.")

    if not context.args:
        return await update.message.reply_text("🔹 Sử dụng: /settoken <token_mới>")

    token = context.args[0]

    # Thử dùng token để kiểm tra bot
    try:
        test_bot = Bot(token)
        me = await test_bot.get_me()  # Nếu lỗi, dòng này sẽ raise exception
        bot_info = f"{me.first_name} (@{me.username})"
    except TelegramError as e:
        return await update.message.reply_text(f"❌ Token không hợp lệ: {e.message}")

    # Nếu hợp lệ, lưu lại
    with open("token.txt", "w") as f:
        f.write(token)

    await update.message.reply_text(f"✅ Token hợp lệ. Đã lưu cho bot: {bot_info}")


async def checktoken(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Bạn không có quyền.")

    try:
        with open("token.txt") as f:
            token = f.read().strip()

        test_bot = Bot(token)
        me = await test_bot.get_me()
        bot_info = f"{me.first_name} (@{me.username})"

        escaped_token = html.escape(token)
        escaped_info = html.escape(bot_info)

        await update.message.reply_text(
            f"✅ Token hiện tại hợp lệ:\n"
            f"<b>Token:</b> <code>{escaped_token}</code>\n"
            f"<b>Bot:</b> {escaped_info}",
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Token hiện tại KHÔNG hợp lệ.\n"
            f"<b>Lỗi:</b> <code>{html.escape(str(e))}</code>",
            parse_mode="HTML"
        )


# async def reloadtoken(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if not is_admin(update.effective_user.id):
#         return await update.message.reply_text("❌ Bạn không có quyền.")
    
#     await update.message.reply_text("♻️ Đang khởi động lại bot với token mới...")

#     # Khởi động lại bot bằng cách mở subprocess mới và thoát cái hiện tại
#     subprocess.Popen([sys.executable, os.path.abspath(__file__)], shell=True)
#     os._exit(0)  # Thoát tiến trình hiện tại


async def reloadtoken(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Bạn không có quyền.")

    try:
        with open("token.txt") as f:
            token = f.read().strip()

        # Thử khởi tạo Bot với token mới
        test_bot = Bot(token)
        me = await test_bot.get_me()
        bot_info = f"{me.first_name} (@{me.username})"

    except TelegramError as e:
        return await update.message.reply_text(
            f"❌ Token KHÔNG hợp lệ, bot sẽ không khởi động lại.\n"
            f"<b>Lỗi:</b> <code>{html.escape(str(e))}</code>",
            parse_mode="HTML"
        )

    # Nếu token hợp lệ => tiếp tục khởi động lại
    await update.message.reply_text(
        f"♻️ Token hợp lệ ({bot_info}) — Đang khởi động lại bot...",
        parse_mode="HTML"
    )

    subprocess.Popen([sys.executable, os.path.abspath(__file__)], shell=True)
    os._exit(0)

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    name = update.effective_user.full_name
    await update.message.reply_text(f"🆔 ID của bạn là: `{uid}`\n👤 Tên: {name}", parse_mode="Markdown")


# Thiết lập danh sách lệnh và chú thích
async def set_bot_commands(app):
    await app.bot.set_my_commands([
        BotCommand("start", "Bắt đầu tạo ảnh CCCD"),
        BotCommand("cancel", "Huỷ thao tác tạo ảnh CCCD"),
        BotCommand("myid", "Lấy ID Telegram của bạn"),
        BotCommand("adduser", "Thêm người dùng được phép"),
        BotCommand("removeuser", "Xoá người dùng"),
        BotCommand("addadmin", "Thêm quản trị viên"),
        BotCommand("removeadmin", "Xoá quản trị viên"),
        BotCommand("listadmins", "Xem danh sách quản trị viên"),
        BotCommand("listusers", "Xem danh sách người dùng"),
        BotCommand("settoken", "Nhập token mới"),
        BotCommand("checktoken", "Kiểm tra token hiện tại"),  
        BotCommand("reloadtoken", "Khởi động lại bot với token mới"),
    ])


async def main():
    with open("token.txt") as f:
        TOKEN = f.read().strip()

    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_PHOTO: [MessageHandler(filters.PHOTO, handle_photo)],
            WAITING_INFO_FRONT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_info_front)],
            WAITING_INFO_BACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_info_back)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("adduser", adduser))
    app.add_handler(CommandHandler("removeuser", removeuser))
    app.add_handler(CommandHandler("addadmin", addadmin))
    app.add_handler(CommandHandler("removeadmin", removeadmin))
    app.add_handler(CommandHandler("listadmins", listadmins))
    app.add_handler(CommandHandler("listusers", listusers))
    app.add_handler(CommandHandler("settoken", settoken))
    app.add_handler(CommandHandler("checktoken", checktoken))
    app.add_handler(CommandHandler("reloadtoken", reloadtoken))
    app.add_handler(CommandHandler("myid", myid))

    await set_bot_commands(app)

    print("🤖 Bot đang chạy...")
    await app.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())


