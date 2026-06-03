"""
Claude Code 状态灯 - 最终修复版（闲置绝不乱变红）
🟢 完成/就绪  🔵 思考  🟠 执行  🟣 等待确认(呼吸)  🔴 错误
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
MIN_HOLD_SEC = 0.6

COLOR_MAP = {
    "done": "#2E9441",     # 🟢 完成
    "thinking": "#3399FF", # 🔵 思考
    "working": "#FF8C00",  # 🟠 执行
    "confirm": "#C83CFF",  # 🟣 等待确认
    "error": "#E53935"     # 🔴 错误
}

current_status = "done"
status_callback = None

# ========== HTTP 服务 ==========
class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): return

    def do_POST(self):
        global current_status
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length).decode())
            new_st = None

            if "event" in data:
                event = data["event"]
                if event == "UserPromptSubmit":
                    new_st = "thinking"
                elif event == "PreToolUse":
                    new_st = "working"
                elif event in ("AwaitingUserConfirmation", "PermissionRequest"):
                    new_st = "confirm"
                elif event == "Stop":
                    new_st = "done"
                
                # ======================================
                # 🔥 核心修复：屏蔽闲置 Notification 变红
                # ======================================
                elif event == "Notification":
                    # 忽略闲置通知，不切换到错误
                    pass

            elif "status" in data:
                new_st = data["status"]

            if new_st in COLOR_MAP:
                current_status = new_st
                if status_callback:
                    status_callback()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
        except:
            self.send_response(400)
            self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": current_status}).encode())

def start_server():
    HTTPServer(("127.0.0.1", PORT), RequestHandler).serve_forever()

# ========== 悬浮窗口 ==========
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

        self.cv = tk.Canvas(width=WIN_SIZE, height=WIN_SIZE, bg=self.tr_color, highlightthickness=0)
        self.cv.pack()
        x = self.winfo_screenwidth() - WIN_SIZE - 40
        y = 40
        self.geometry(f"{WIN_SIZE}x{WIN_SIZE}+{x}+{y}")

        self._x = self._y = 0
        self.cv.bind("<Button-1>", self.on_click)
        self.cv.bind("<B1-Motion>", self.on_drag)

        self.menu = Menu(self, tearoff=0)
        self.menu.add_command(label="🟢 完成/就绪", command=lambda: self.set("done"))
        self.menu.add_command(label="🔵 AI 思考", command=lambda: self.set("thinking"))
        self.menu.add_command(label="🟠 工具执行", command=lambda: self.set("working"))
        self.menu.add_command(label="🟣 等待确认", command=lambda: self.set("confirm"))
        self.menu.add_command(label="🔴 错误", command=lambda: self.set("error"))
        self.menu.add_separator()
        self.menu.add_command(label="退出程序", command=self.quit)
        self.cv.bind("<Button-3>", self.show_menu)

        c = WIN_SIZE//2
        r = WIN_SIZE//2 -5
        self.circle = self.cv.create_oval(c-r,c-r,c+r,c+r, fill=COLOR_MAP["done"], outline="white", width=1)

        self.breath_step = 0
        self.breath_up = True
        global status_callback
        status_callback = self.update_color
        self.breath_loop()

    def update_color(self):
        if current_status != "confirm":
            self.cv.itemconfig(self.circle, fill=COLOR_MAP[current_status])

    def set(self, st):
        global current_status
        current_status = st
        self.update_color()

    def show_menu(self, e):
        self.menu.tk_popup(e.x_root, e.y_root)

    def on_click(self,e):
        self._x,self._y = e.x,e.y
    def on_drag(self,e):
        dx = e.x - self._x
        dy = e.y - self._y
        self.geometry(f"+{self.winfo_x()+dx}+{self.winfo_y()+dy}")

    def breath_loop(self):
        if current_status == "confirm":
            if self.breath_up:
                self.breath_step +=6
                if self.breath_step>=70:self.breath_up=False
            else:
                self.breath_step -=6
                if self.breath_step<=0:self.breath_up=True
            r = max(0,200-self.breath_step)
            g = max(0,60-self.breath_step)
            b = max(0,255-self.breath_step)
            self.cv.itemconfig(self.circle, fill=f"#{r:02X}{g:02X}{b:02X}")
        else:
            self.breath_step = 0
            self.cv.itemconfig(self.circle, fill=COLOR_MAP[current_status])
        self.after(45,self.breath_loop)

if __name__ == "__main__":
    print(f"✅ 状态灯启动 | 端口:{PORT}")
    threading.Thread(target=start_server, daemon=True).start()
    app = FloatLight()
    app.mainloop()
