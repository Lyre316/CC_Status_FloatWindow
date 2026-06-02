"""
Claude Code 四色状态灯 - 终极修复版
🟢 完成   🟣 思考中   🟠 工作中   🔴 错误
"""
import tkinter as tk
from tkinter import Menu
import threading
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# ========== 核心配置 ==========
PORT = 8765
WIN_SIZE = 68
ALPHA = 1.0
DEBOUNCE_SEC = 0.4
MIN_HOLD_SEC = 0.6

COLOR_MAP = {
    "done": "#2E8B57",     # 🟢 完成
    "thinking": "#9370DB", # 🟣 思考中
    "working": "#FF8C00",  # 🟠 工作中
    "error": "#DC143C"     # 🔴 错误
}

current_status = "done"
status_callback = None
last_set_time = 0
hold_until = 0
pending_status = None

# ========== HTTP 服务（已修复） ==========
class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): return

    def do_POST(self):
        global current_status, last_set_time, hold_until, pending_status
        try:
            now = time.time()
            length = int(self.headers.get("Content-Length", 0))
            raw_data = self.rfile.read(length).decode()
            data = json.loads(raw_data)

            # ======================================
            # 🔥 修复：支持两种格式
            # 1. CC 事件：{"event":"xxx"}
            # 2. 手动 curl：{"status":"xxx"}
            # ======================================
            new_st = None

            # 格式1：来自 Claude 的事件
            if "event" in data:
                event = data["event"]
                if event == "UserPromptSubmit":
                    new_st = "thinking"
                elif event == "PreToolUse":
                    new_st = "working"
                elif event == "Stop":
                    new_st = "done"
                elif event == "Notification":
                    new_st = "error"

            # 格式2：手动 / 脚本设置状态
            elif "status" in data:
                new_st = data["status"]

            # 执行状态更新
            if new_st in COLOR_MAP:
                current_status = new_st
                last_set_time = now
                hold_until = now + MIN_HOLD_SEC
                if status_callback:
                    status_callback()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

        except Exception as e:
            print("错误:", e)
            self.send_response(400)
            self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": current_status}).encode())

def start_server():
    server = HTTPServer(("127.0.0.1", PORT), RequestHandler)
    server.serve_forever()

# ========== 悬浮灯窗口 ==========
class FloatLight(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("StatusLight")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", ALPHA)

        self.tr_color = "#123456"
        self.config(bg=self.tr_color)
        self.attributes("-transparentcolor", self.tr_color)

        self.cv = tk.Canvas(
            self, width=WIN_SIZE, height=WIN_SIZE,
            bg=self.tr_color, highlightthickness=0
        )
        self.cv.pack()

        # 屏幕右上角
        x = self.winfo_screenwidth() - WIN_SIZE - 40
        y = 40
        self.geometry(f"{WIN_SIZE}x{WIN_SIZE}+{x}+{y}")

        # 拖动
        self._x = self._y = 0
        self.cv.bind("<Button-1>", self.on_click)
        self.cv.bind("<B1-Motion>", self.on_drag)

        # 右键菜单
        self.menu = Menu(self, tearoff=0)
        self.menu.add_command(label="🟢 完成", command=lambda: self.set("done"))
        self.menu.add_command(label="🟣 思考中", command=lambda: self.set("thinking"))
        self.menu.add_command(label="🟠 工作中", command=lambda: self.set("working"))
        self.menu.add_command(label="🔴 错误", command=lambda: self.set("error"))
        self.menu.add_separator()
        self.menu.add_command(label="退出", command=self.quit)
        self.cv.bind("<Button-3>", self.show_menu)

        # 画圆
        c = WIN_SIZE // 2
        r = WIN_SIZE // 2 - 5
        self.circle = self.cv.create_oval(
            c-r, c-r, c+r, c+r,
            fill=COLOR_MAP[current_status], outline="white", width=1
        )

        global status_callback
        status_callback = self.update_color

    def update_color(self):
        self.cv.itemconfig(self.circle, fill=COLOR_MAP[current_status])

    def set(self, st):
        global current_status
        current_status = st
        self.update_color()

    def on_click(self, e):
        self._x = e.x
        self._y = e.y

    def on_drag(self, e):
        dx = e.x - self._x
        dy = e.y - self._y
        self.geometry(f"+{self.winfo_x()+dx}+{self.winfo_y()+dy}")

    def show_menu(self, e):
        self.menu.tk_popup(e.x_root, e.y_root)

# ========== 启动 ==========
if __name__ == "__main__":
    print("✅ 状态灯已启动 - 端口:" + str(PORT))
    threading.Thread(target=start_server, daemon=True).start()
    app = FloatLight()
    app.mainloop()