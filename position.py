import tkinter as tk
from PIL import Image, ImageTk

# Đường dẫn ảnh CCCD
image_path = "MMSS.PNG"

# Tạo cửa sổ Tkinter
root = tk.Tk()
root.title("Xác định tọa độ chuột trên ảnh")

# Load ảnh bằng Pillow
img = Image.open(image_path)
tk_img = ImageTk.PhotoImage(img)

# Tạo Canvas hiển thị ảnh
canvas = tk.Canvas(root, width=img.width, height=img.height)
canvas.pack()
canvas_img = canvas.create_image(0, 0, anchor="nw", image=tk_img)

# Hàm xử lý khi di chuột
def mouse_move(event):
    x, y = event.x, event.y
    root.title(f"Tọa độ chuột: ({x}, {y})")

# Gắn sự kiện di chuột vào canvas
canvas.bind("<Motion>", mouse_move)

root.mainloop()

