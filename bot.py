import tkinter as tk
import pyautogui
import threading
import time
import ctypes

# --- fixing windows scale issue ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    ctypes.windll.user32.SetProcessDPIAware()

# settings
TOLERANCE = 35 

def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb

class DraggableSensor(tk.Toplevel):
    def __init__(self, master, title, x, y, border_color):
        super().__init__(master)
        self.overrideredirect(True)
        self.geometry(f"24x24+{x}+{y}")
        self.attributes("-topmost", True)
        
        # --- making window transparent ---
        self.configure(bg="white")
        self.wm_attributes("-transparentcolor", "white")

        self.bind("<Button-1>", self.start_move)
        self.bind("<B1-Motion>", self.do_move)
        
        self.canvas = tk.Canvas(self, width=24, height=24, bg="white", highlightthickness=0)
        self.canvas.pack()
        
        # --- drawing border ---
        self.canvas.create_rectangle(0, 0, 23, 23, outline=border_color, width=3)
        
        # --- drawing crosshair ---
        self.canvas.create_line(12, 0, 12, 8, fill="black", width=2)
        self.canvas.create_line(12, 16, 12, 24, fill="black", width=2)
        self.canvas.create_line(0, 12, 8, 12, fill="black", width=2)
        self.canvas.create_line(16, 12, 24, 12, fill="black", width=2)
        
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        x = self.winfo_x() + (event.x - self.x)
        y = self.winfo_y() + (event.y - self.y)
        self.geometry(f"+{x}+{y}")

    def get_center_pos(self):
        return (self.winfo_x() + 12, self.winfo_y() + 12)

class LumberJackBot:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Lumber Bot Ultimate")
        self.root.geometry("320x370")
        self.root.attributes("-topmost", True)
        self.running = False
        self.side = "right" 
        
        self.ref_color_l = (0, 0, 0)
        self.ref_color_r = (0, 0, 0)
        
        # --- speed variable ---
        # default: 0.04 seconds
        # default: 0.04 seconds
        self.delay_var = tk.DoubleVar(value=0.04)

        # --- limit variable ---
        # 0 = unlimited
        self.limit_var = tk.IntVar(value=0)

        # --- sensors ---
        self.sensor_l = DraggableSensor(self.root, "L", 850, 500, "red")
        self.sensor_r = DraggableSensor(self.root, "R", 1050, 500, "blue")

        # --- UI ---
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=10)

        # --- Left Info ---
        tk.Label(info_frame, text="Left Sensor", fg="red", font=("bold")).grid(row=0, column=0, padx=10)
        self.color_box_l = tk.Label(info_frame, text="     ", bg="#000000", relief="sunken", width=10)
        self.color_box_l.grid(row=1, column=0, pady=5)
        self.status_text_l = tk.Label(info_frame, text="WAITING", fg="gray", font=("Arial", 10, "bold"))
        self.status_text_l.grid(row=2, column=0)
        self.lbl_rgb_l = tk.Label(info_frame, text="-", font=("Arial", 8))
        self.lbl_rgb_l.grid(row=3, column=0)

        # --- Right Info ---
        tk.Label(info_frame, text="Right Sensor", fg="blue", font=("bold")).grid(row=0, column=1, padx=10)
        self.color_box_r = tk.Label(info_frame, text="     ", bg="#000000", relief="sunken", width=10)
        self.color_box_r.grid(row=1, column=1, pady=5)
        self.status_text_r = tk.Label(info_frame, text="WAITING", fg="gray", font=("Arial", 10, "bold"))
        self.status_text_r.grid(row=2, column=1)
        self.lbl_rgb_r = tk.Label(info_frame, text="-", font=("Arial", 8))
        self.lbl_rgb_r.grid(row=3, column=1)

        # --- speed control slider ---
        slider_frame = tk.LabelFrame(self.root, text="Speed Control (Delay)", padx=5, pady=5)
        slider_frame.pack(fill="x", padx=20, pady=5)
        
        self.speed_scale = tk.Scale(slider_frame, from_=0.01, to=0.20, resolution=0.01, 
                                    orient="horizontal", variable=self.delay_var, length=250)
        self.speed_scale.pack()
        
        tk.Label(slider_frame, text="Left: Faster | Right: Slower", font=("Arial", 7), fg="gray").pack()

        # --- click limit input ---
        limit_frame = tk.Frame(self.root)
        limit_frame.pack(pady=5)
        
        tk.Label(limit_frame, text="Click Limit (0=Unlimited): ").pack(side="left")
        self.limit_entry = tk.Entry(limit_frame, textvariable=self.limit_var, width=10)
        self.limit_entry.pack(side="left")

        # --- start button ---
        self.btn = tk.Button(self.root, text="START BOT", command=self.toggle, bg="green", fg="white", font=("Arial", 12, "bold"))
        self.btn.pack(expand=True, fill='x', padx=20, pady=10)
        

    def update_ui_status(self, side, is_branch, current_color):
        lbl = self.status_text_l if side == "left" else self.status_text_r
        val_lbl = self.lbl_rgb_l if side == "left" else self.lbl_rgb_r
        
        val_lbl.config(text=str(current_color))

        if current_color == (0,0,0):
             lbl.config(text="BLK ERROR", fg="purple")
             return

        if is_branch:
            lbl.config(text="BRANCH", fg="red")
        else:
            lbl.config(text="SKY", fg="green")

    def toggle(self):
        if not self.running:
            pos_l = self.sensor_l.get_center_pos()
            pos_r = self.sensor_r.get_center_pos()
            
            try:
                self.ref_color_l = pyautogui.pixel(*pos_l)
                self.ref_color_r = pyautogui.pixel(*pos_r)
                
                self.color_box_l.config(bg=rgb_to_hex(self.ref_color_l))
                self.color_box_r.config(bg=rgb_to_hex(self.ref_color_r))
                
                print(f"Calibrated Ref: L={self.ref_color_l} R={self.ref_color_r}")

                self.running = True
                self.btn.config(text="STOP", bg="red")
                # Disable limit entry while running
                self.limit_entry.config(state="disabled")
                threading.Thread(target=self.run_logic, daemon=True).start()
            except Exception as e:
                print(f"Error: {e}")
        else:
            self.stop_bot()

    def stop_bot(self):
        self.running = False
        self.btn.config(text="START BOT", bg="green")
        self.limit_entry.config(state="normal")

    def has_branch(self, pos, ref_color):
        try:
            pixel = pyautogui.pixel(*pos)
            diff = sum(abs(pixel[i] - ref_color[i]) for i in range(3))
            return (diff > TOLERANCE), pixel
        except:
            return False, (0,0,0)

    def run_logic(self):
        clicks_done = 0
        limit = self.limit_var.get()
        
        while self.running:
            pos_l = self.sensor_l.get_center_pos()
            pos_r = self.sensor_r.get_center_pos()
            
            is_branch_l, col_l = self.has_branch(pos_l, self.ref_color_l)
            is_branch_r, col_r = self.has_branch(pos_r, self.ref_color_r)

            try:
                self.update_ui_status("left", is_branch_l, col_l)
                self.update_ui_status("right", is_branch_r, col_r)
            except:
                pass

            if self.side == "left" and is_branch_l:
                self.side = "right"
            elif self.side == "right" and is_branch_r:
                self.side = "left"
            
            if not ((self.side == "left" and is_branch_l) or (self.side == "right" and is_branch_r)):
                pyautogui.press(self.side)
                clicks_done += 1
                
                if limit > 0 and clicks_done >= limit:
                    print(f"Limit of {limit} clicks reached. Stopping.")
                    # utilize root.after to safely update UI from another thread
                    self.root.after(0, self.stop_bot)
                    break
            
            # the delay value from the slider in each loop
            current_delay = self.delay_var.get()
            time.sleep(current_delay)

if __name__ == "__main__":
    LumberJackBot().root.mainloop()