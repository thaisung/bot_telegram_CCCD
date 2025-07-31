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
# def load_font_Regular(size): return ImageFont.truetype("font-text/LiberationSans-Regular.ttf", size)
# def load_font_Bold(size): return ImageFont.truetype("font-text/LiberationSans-Bold.ttf", size)

def load_font_Bold(size): return ImageFont.truetype("font_text1/SVN-Arial-3-bold.ttf", size)
def load_font_Regular(size): return ImageFont.truetype("font_text1/SVN-Arial-3.ttf", size)

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

def add_noise(img, amount=0.02, distribution="gaussian"):
    """Thêm nhiễu ngẫu nhiên vào ảnh RGBA với phân phối Gaussian hoặc Uniform"""
    arr = np.array(img).astype(np.float32)

    if distribution == "uniform":
        noise = np.random.uniform(-255 * amount, 255 * amount, arr.shape)
    elif distribution == "gaussian":
        noise = np.random.normal(0, 255 * amount, arr.shape)
    else:
        raise ValueError("Chỉ hỗ trợ 'uniform' hoặc 'gaussian'.")

    noisy = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy, mode=img.mode)

def draw_effect_text(base_img, text, position, font, fill=(30, 30, 30), shadow_offset=(2, 2)):
    """Vẽ chữ có Drop Shadow + Blur + Noise giống Photoshop"""
    x, y = position
    width, height = base_img.size

    # Layer bóng đổ
    shadow = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.text((x + shadow_offset[0], y + shadow_offset[1]), text, font=font, fill=(0, 0, 0, 100))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=5))

    # Layer chữ chính
    text_layer = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_layer)
    draw.text(position, text, font=font, fill=fill)

    # Gộp bóng và chữ
    combined = Image.alpha_composite(shadow, text_layer)

    # Làm mờ + làm nét + nhiễu
    blurred = combined.filter(ImageFilter.GaussianBlur(radius=1))
    sharpened = blurred.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
    noisy = add_noise(sharpened, amount=0)

    # Gộp với ảnh gốc
    final = Image.alpha_composite(base_img, noisy)
    return final

def draw_soft_filtered_text(base_img, text, position, font, fill=(30, 30, 30), shadow_offset=(2, 2)):
    """Vẽ chữ có Drop Shadow + Blur + Noise giống Photoshop"""
    x, y = position
    width, height = base_img.size

    # Layer bóng đổ
    shadow = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.text((x + shadow_offset[0], y + shadow_offset[1]), text, font=font, fill=(0, 0, 0, 100))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=5))

    # Layer chữ chính
    text_layer = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_layer)
    draw.text(position, text, font=font, fill=fill)

    # Gộp bóng và chữ
    combined = Image.alpha_composite(shadow, text_layer)

    # Làm mờ + làm nét + nhiễu
    blurred = combined.filter(ImageFilter.GaussianBlur(radius=1))
    sharpened = blurred.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
    noisy = add_noise(sharpened, amount=0)

    # Gộp với ảnh gốc
    final = Image.alpha_composite(base_img, noisy)
    return final


def import_text_mt(No, Full_name, DOB, Sex, Nation, image_path="temp_cccd_photo.png"):
    img = Image.open(image_path).convert("RGBA")


    # Vẽ từng dòng có hiệu ứng như Photoshop
    img = draw_effect_text(img, No, (425, 455), font=load_font_Bold(45))
    img = draw_soft_filtered_text(img, Full_name.upper(), (432, 555), font=load_font_Regular(35))
    img = draw_soft_filtered_text(img, Full_name.upper(), (432, 555), font=load_font_Regular(35))
    img = draw_soft_filtered_text(img, DOB, (432, 649), font=load_font_Regular(30))
    img = draw_soft_filtered_text(img, DOB, (432, 649), font=load_font_Regular(30))
    img = draw_soft_filtered_text(img, Sex, (906, 645), font=load_font_Regular(30))
    img = draw_soft_filtered_text(img, Sex, (906, 645), font=load_font_Regular(30))
    img = draw_soft_filtered_text(img, Nation, (477, 727), font=load_font_Regular(30))
    img = draw_soft_filtered_text(img, Nation, (477, 727), font=load_font_Regular(30))

    output_path = "cccd_text_mt.png"
    img.convert("RGB").save(output_path)
    return output_path

def import_text_ms(Full_name, No, Origin, Residence, Expiry, Issue, DOB, Sex, Nation):
    img = Image.open("MMSS.png").convert("RGBA")

    # Vẽ các lớp thông tin hành chính (Origin, Residence, ...)
    img = draw_soft_filtered_text(img,Origin,(250, 210), font=load_font_Regular(28))
    img = draw_soft_filtered_text(img,Origin,(250, 210), font=load_font_Regular(28))
    img = draw_soft_filtered_text(img,Residence,(250, 299), font=load_font_Regular(28))
    img = draw_soft_filtered_text(img,Residence,(250, 299), font=load_font_Regular(28))
    img = draw_soft_filtered_text(img,Issue,(619, 377), font=load_font_Regular(28))
    img = draw_soft_filtered_text(img,Issue,(619, 377), font=load_font_Regular(28))
    img = draw_soft_filtered_text(img,Expiry,(620, 437), font=load_font_Regular(28))
    img = draw_soft_filtered_text(img,Expiry,(620, 437), font=load_font_Regular(28))

    # Vẽ 3 dòng MRZ vào lớp riêng với blur nhẹ
    mrz_lines = generate_mrz(No, Full_name, DOB, Sex, Nation, Expiry, Issue)
    for i, line in enumerate(mrz_lines):
        img = draw_soft_filtered_text(img,line,(246, 573 + i * 48), font=load_mrz_font(46))

    # Lưu ảnh đầu ra
    output_path = "cccd_text_ms.png"
    img.convert("RGB").save(output_path)
    return output_path


No='023654889255'
Full_name='Nguyễn Bình Long'
DOB='20/09/1996'
Sex='Nam' 
Nation='Việt Nam'
# import_text_mt(No, Full_name, DOB, Sex, Nation, image_path="temp_cccd_photo.png")
Origin= 'Khu Phố Hiệp Tâm 2'
Residence = 'Khu Phố Hiệp Tâm 2'
Expiry = '20/09/1996'
Issue = '20/09/1996'
import_text_ms(Full_name, No, Origin, Residence, Expiry, Issue, DOB, Sex, Nation)