import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import math
import os
import threading
import time

FFMPEG = os.path.join(os.getcwd(), "ffmpeg.exe")
FFPROBE = os.path.join(os.getcwd(), "ffprobe.exe")

class VideoSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("视频切割器 - 带进度条和暂停功能")

        self.video_path_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.segment_entry = tk.Entry(root)
        self.progress = tk.DoubleVar()

        self.pause_flag = False
        self.stop_flag = False

        self.create_widgets()

    def create_widgets(self):
        tk.Label(root, text="选择视频文件：").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        tk.Entry(root, textvariable=self.video_path_var, width=50).grid(row=0, column=1)
        tk.Button(root, text="浏览", command=self.choose_file).grid(row=0, column=2)

        tk.Label(root, text="输出目录：").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        tk.Entry(root, textvariable=self.output_dir_var, width=50).grid(row=1, column=1)
        tk.Button(root, text="选择", command=self.choose_output_dir).grid(row=1, column=2)

        tk.Label(root, text="分段数（可选）：").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.segment_entry.grid(row=2, column=1)

        tk.Button(root, text="开始分割", command=self.run_split_thread).grid(row=3, column=1, pady=10)
        self.pause_btn = tk.Button(root, text="暂停", command=self.toggle_pause)
        self.pause_btn.grid(row=3, column=2)

        tk.Label(root, text="处理进度：").grid(row=4, column=0, padx=10, pady=5, sticky='e')
        self.progress_bar = tk.Scale(root, variable=self.progress, from_=0, to=100, orient='horizontal', length=400)
        self.progress_bar.grid(row=4, column=1, columnspan=2)

    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[("视频文件", "*.mp4;*.avi;*.mov;*.mkv")])
        if path:
            self.video_path_var.set(path)

    def choose_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_var.set(directory)

    def toggle_pause(self):
        self.pause_flag = not self.pause_flag
        self.pause_btn.config(text="继续" if self.pause_flag else "暂停")

    def get_video_duration(self, path):
        try:
            result = subprocess.run(
                [FFPROBE, "-v", "error", "-select_streams", "v:0",
                 "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path],
                capture_output=True, text=True, check=True
            )
            return float(result.stdout.strip())
        except Exception as e:
            messagebox.showerror("错误", f"获取视频时长失败：{e}")
            return None

    def run_split_thread(self):
        thread = threading.Thread(target=self.split_video)
        thread.start()

    def split_video(self):
        path = self.video_path_var.get()
        out_dir = self.output_dir_var.get()
        seg_input = self.segment_entry.get()

        if not os.path.exists(path) or not os.path.exists(FFMPEG) or not os.path.exists(FFPROBE):
            messagebox.showerror("错误", "请确认视频文件和 ffmpeg 工具是否存在")
            return

        if not out_dir:
            messagebox.showerror("错误", "请选择输出目录")
            return

        duration = self.get_video_duration(path)
        if not duration:
            return

        try:
            seg_count = int(seg_input) if seg_input else 0
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效数字")
            return

        if seg_count == 0:
            seg_count = math.ceil(duration / 10)
            seg_len = 10
        else:
            seg_len = math.floor(duration / seg_count)

        base = os.path.splitext(os.path.basename(path))[0]

        for i in range(1, seg_count + 1):
            while self.pause_flag:
                time.sleep(0.1)

            start = (i - 1) * seg_len
            if start >= duration:
                break

            out_name = os.path.join(out_dir, f"{base}_{i:03d}.mp4")
            cmd = [FFMPEG, "-ss", str(start), "-i", path, "-t", str(seg_len),
                   "-c:v", "libx264", "-c:a", "aac", "-y", out_name]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            progress_value = i / seg_count * 100
            self.progress.set(progress_value)

        messagebox.showinfo("完成", f"共生成 {seg_count} 段视频")
        self.progress.set(100)

if __name__ == '__main__':
    root = tk.Tk()
    app = VideoSplitterApp(root)
    root.mainloop()