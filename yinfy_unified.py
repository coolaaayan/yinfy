import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import socket
import threading
import psutil
import os
import subprocess
import platform
import time

class YinfyUnified:
    def __init__(self, root):
        self.root = root
        self.root.title("Yinfy Unified v1.3")
        self.root.geometry("1000x750")
        self.root.configure(bg="#050505")
        
        self.is_leader = False
        self.node_socket = None
        self.iso_path = ""

        self.setup_ui()

    def setup_ui(self):
        # --- Top Status Bar ---
        self.top_bar = tk.Frame(self.root, bg="#111", height=45)
        self.top_bar.pack(fill="x")
        
        self.ping_canvas = tk.Canvas(self.top_bar, width=20, height=20, bg="#111", highlightthickness=0)
        self.ping_canvas.pack(side="left", padx=15)
        self.ping_light = self.ping_canvas.create_oval(5, 5, 15, 15, fill="gray")
        
        self.ping_label = tk.Label(self.top_bar, text="LAN LINK: NOT DETECTED", fg="#888", bg="#111", font=("Consolas", 10))
        self.ping_label.pack(side="left")

        # --- Brand Header ---
        tk.Label(self.root, text="YINFY DUAL-LINK", font=("Impact", 36), fg="#00ffcc", bg="#050505").pack(pady=20)

        # --- Role Selection ---
        mode_frame = tk.Frame(self.root, bg="#050505")
        mode_frame.pack(pady=10)
        tk.Button(mode_frame, text="LEADER (HOST VM)", command=self.set_leader, bg="#0055ff", fg="white", width=25, font=("Arial", 11, "bold")).pack(side="left", padx=15)
        tk.Button(mode_frame, text="FOLLOWER (RESOURCE NODE)", command=self.set_follower, bg="#333", fg="white", width=25, font=("Arial", 11, "bold")).pack(side="left", padx=15)

        # --- Connection Dashboard ---
        self.conn_frame = tk.LabelFrame(self.root, text=" LAN Hardware Bridge ", fg="#00ffcc", bg="#050505", padx=20, pady=20)
        self.conn_frame.pack(fill="x", padx=60, pady=20)
        
        tk.Label(self.conn_frame, text="Enter Follower IP:", fg="white", bg="#050505").pack(side="left")
        self.ip_entry = tk.Entry(self.conn_frame, bg="#1a1a1a", fg="#00ffcc", font=("Consolas", 12), insertbackground="white")
        self.ip_entry.pack(side="left", padx=15, fill="x", expand=True)
        tk.Button(self.conn_frame, text="LINK PCS", command=self.connect_node, bg="#222", fg="white").pack(side="left")

        # --- Resource Visualization ---
        self.dash = tk.Frame(self.root, bg="#050505")
        self.dash.pack(fill="both", expand=True, padx=60)
        self.l_cpu = self.create_bar("LOCAL CPU RESOURCE (PC 1)")
        self.r_cpu = self.create_bar("YINFY CPU V1 (PC 2)")

        # --- VM Actions ---
        ctrl_frame = tk.Frame(self.root, bg="#050505")
        ctrl_frame.pack(pady=30)
        self.btn_iso = tk.Button(ctrl_frame, text="IMPORT ISO", command=self.get_iso, state="disabled", width=15)
        self.btn_iso.pack(side="left", padx=10)
        tk.Button(ctrl_frame, text="BOOT FULLSCREEN VM", command=self.enter_fullscreen, bg="#00ffcc", fg="black", font=("Arial", 12, "bold"), padx=20).pack(side="left", padx=10)

    def create_bar(self, txt):
        tk.Label(self.dash, text=txt, fg="#666", bg="#050505", font=("Arial", 9)).pack(anchor="w", pady=(10,0))
        bar = ttk.Progressbar(self.dash, length=800, mode='determinate')
        bar.pack(pady=5, fill="x")
        return bar

    def set_leader(self):
        self.is_leader = True
        self.btn_iso.config(state="normal")
        self.update_stats()

    def set_follower(self):
        self.is_leader = False
        threading.Thread(target=self.run_follower_server, daemon=True).start()
        self.update_stats()

    def connect_node(self):
        ip = self.ip_entry.get()
        if ip:
            threading.Thread(target=self.ping_loop, args=(ip,), daemon=True).start()

    def ping_loop(self, ip):
        while True:
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            try:
                start = time.time()
                subprocess.run(['ping', param, '1', ip], stdout=subprocess.DEVNULL, check=True)
                ms = (time.time() - start) * 1000
                color = "#00ff00" if ms < 5 else "yellow" if ms < 25 else "red"
                self.ping_canvas.itemconfig(self.ping_light, fill=color)
                self.ping_label.config(text=f"LAN LINK: {ms:.1f}ms - OPTIMAL", fg=color) if ms < 10 else self.ping_label.config(text=f"LAN LINK: {ms:.1f}ms - LAGGING", fg=color)
            except:
                self.ping_canvas.itemconfig(self.ping_light, fill="red")
                self.ping_label.config(text="LAN LINK: OFFLINE", fg="red")
            time.sleep(2)

    def get_iso(self):
        self.iso_path = filedialog.askopenfilename(filetypes=[("ISO Files", "*.iso")])

    def enter_fullscreen(self):
        # This triggers the Virt-Viewer in fullscreen mode
        subprocess.Popen("virt-viewer -f --connect qemu:///system", shell=True)

    def update_stats(self):
        self.l_cpu['value'] = psutil.cpu_percent()
        # Simulated remote pull - in a final build, this would fetch from the socket
        self.root.after(1000, self.update_stats)

    def run_follower_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('0.0.0.0', 9999))
        s.listen(5)
        while True:
            conn, addr = s.accept()
            conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('default')
    style.configure("TProgressbar", thickness=25, troughcolor='#111', background='#00ffcc')
    app = YinfyUnified(root)
    root.mainloop()