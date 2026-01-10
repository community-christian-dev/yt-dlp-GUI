import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import shutil
import re
import os


class YTDLPGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Downloader")
        self.root.geometry("700x550")

        self.queue_data = []
        self.is_downloading = False

        # -- Input Frame -- #
        input_frame = tk.LabelFrame(root, text="Add New Video", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # URL
        tk.Label(input_frame, text="Video URL:").grid(row=0, column=0, sticky="w")
        self.url_entry = tk.Entry(input_frame, width=50)
        self.url_entry.grid(row=0, column=1, padx=5, pady=2)

        # Referer
        tk.Label(input_frame, text="Referer (Optional):").grid(row=1, column=0, sticky="w")
        self.referer_entry = tk.Entry(input_frame, width=50)
        self.referer_entry.grid(row=1, column=1, padx=5, pady=2)

        # Filename
        tk.Label(input_frame, text="Filename (No Ext.):").grid(row=2, column=0, sticky="w")
        self.filename_entry = tk.Entry(input_frame, width=50)
        self.filename_entry.grid(row=2, column=1, padx=5, pady=2)

        # Folder
        tk.Label(input_frame, text="Save Folder:").grid(row=3, column=0, sticky="w")
        folder_container = tk.Frame(input_frame)
        folder_container.grid(row=3, column=1, sticky="w", padx=5)

        default_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.folder_var = tk.StringVar(value=default_path)
        self.folder_entry = tk.Entry(folder_container, textvariable=self.folder_var, width = 38)
        self.folder_entry.pack(side=tk.LEFT)
        tk.Button(folder_container, text="Browse", command=self.browse_folder).pack(side=tk.LEFT, padx=2)

        # Add Button
        self.add_btn = tk.Button(input_frame, text="Add to Queue", command=self.add_to_queue, bg="#2196F3", fg="white")
        self.add_btn.grid(row=4, column=1, sticky="e", pady=10)

        # -- Queue Frame -- #
        queue_frame = tk.LabelFrame(root, text="Download Queue", padx=10, pady=10)
        queue_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Treeview (Table)
        columns = ("filename", "url", "status")
        self.tree = ttk.Treeview(queue_frame, columns=columns, show="headings", height=8)
        self.tree.heading("filename", text="Filename")
        self.tree.heading("url", text="URL")
        self.tree.heading("status", text="Status")

        self.tree.column("filename", width=150)
        self.tree.column("url", width=250)
        self.tree.column("status", width=100)

        self.tree.pack(side=tk.LEFT, fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(queue_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        # -- Control Frame -- #
        control_frame = tk.Frame(root, padx=10, pady=10)
        control_frame.pack(fill="x")

        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", pady=5)

        # Status Label
        self.status_label = tk.Label(control_frame, text="Ready to start", fg="gray")
        self.status_label.pack()

        # Start Button
        self.start_btn = tk.Button(control_frame, text="Start Download", command=self.start_batch_thread, bg="#4CAF50", fg="white", font=("Arial", 11, "bold"))
        self.start_btn.pack(pady=5)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def add_to_queue(self):
        url = self.url_entry.get().strip()
        referer = self.referer_entry.get().strip()
        filename = self.filename_entry.get().strip()
        folder = self.folder_var.get().strip()

        if not url:
            messagebox.showerror("Error", "URL is required")
            return

        # Default filename if empty
        display_name = filename if filename else "Auto-detected"

        # Add to internal data list
        task = {
            "url": url,
            "referer": referer,
            "filename": filename,
            "folder": folder,
            "status": "Pending",
            "id": len(self.queue_data)
        }
        self.queue_data.append(task)

        # Add to UI Treeview
        self.tree.insert("", "end", iid=task["id"], values=(display_name, url, "Pending"))

        # Clear inputs
        self.url_entry.delete(0, tk.END)
        self.filename_entry.delete(0, tk.END)
        # We keep referer/folder as users often download multiple videos to same place

    def start_batch_thread(self):
        if not self.queue_data:
            messagebox.showinfo("Info", "Queue is empty!")
            return

        if self.is_downloading:
            return

        if not shutil.which("yt-dlp"):
            messagebox.showerror("Error", "yt-dlp not found!")
            return

        self.is_downloading = True
        self.start_btn.config(state=tk.DISABLED)

        thread = threading.Thread(target=self.process_queue)
        thread.daemon = True
        thread.start()

    def process_queue(self):
        for index, task in enumerate(self.queue_data):
            if task["status"] == "Done":
                continue

            self.root.after(0, lambda i=index: self.update_status(i, "Downloading..."))

            yt_dlp_path = r"C:\ytdl\yt-dlp.exe"

            cmd = [yt_dlp_path, "--newline"]

            # --- 1. SETUP PATHS ---
            if task["referer"]:
                cmd.extend(["--referer", task["referer"]])

            if task["folder"]:
                clean_path = os.path.normpath(task["folder"])
                try:
                    os.makedirs(clean_path, exist_ok=True)
                except OSError as e:
                    self.root.after(0, lambda: messagebox.showerror("Folder Error", f"Cannot create folder:\n{e}"))
                    self.root.after(0, lambda i=index: self.update_status(i, "Failed"))
                    continue
                cmd.extend(["-P", clean_path])

            if task["filename"]:
                cmd.extend(["-o", f"{task['filename']}.%(ext)s"])
            else:
                cmd.extend(["-o", "%(title)s.%(ext)s"])

            cmd.append(task["url"])

            # --- 2. RUN AND CATCH ERROR ---
            try:
                # We Capture Stderr (Errors) separately now
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,  # <--- Capture errors here
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )

                # Read output while running
                while True:
                    # Check for normal output
                    output_line = process.stdout.readline()
                    if output_line:
                        self.root.after(0, lambda l=output_line: self.parse_progress(l))

                    # Check if finished
                    if not output_line and process.poll() is not None:
                        break

                # Get the rest of the output (including error messages)
                remaining_stdout, remaining_stderr = process.communicate()

                if process.returncode == 0:
                    self.root.after(0, lambda i=index: self.update_status(i, "Done"))
                    task["status"] = "Done"
                else:
                    # SHOW THE ERROR TO THE USER
                    error_message = remaining_stderr if remaining_stderr else "Unknown Error"
                    print(f"DEBUG ERROR: {error_message}")  # Print to PyCharm console
                    self.root.after(0, lambda msg=error_message: messagebox.showerror("Download Failed",
                                                                                      f"yt-dlp error:\n{msg}"))
                    self.root.after(0, lambda i=index: self.update_status(i, "Error"))

            except Exception as e:
                print(f"CRASH: {e}")
                self.root.after(0, lambda msg=str(e): messagebox.showerror("Script Crash", f"Python Error:\n{msg}"))
                self.root.after(0, lambda i=index: self.update_status(i, "Failed"))

        self.is_downloading = False
        self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.status_label.config(text="All tasks finished."))
        self.root.after(0, lambda: self.progress_var.set(0))

    def update_status(self, index, status):
        current_values = self.tree.item(index, "values")
        if current_values:
            self.tree.item(index, values=(current_values[0], current_values[1], status))

        self.status_label.config(text=f"Task {index+1}/{len(self.queue_data)}: {status}")

    def parse_progress(self, line):
        line = line.strip()

        if "[download]" in line and "%" in line:
            try:
                # Extract percentage
                pct_match = re.search(r"(\d+\.\d+)%", line)
                if pct_match:
                    percent = float(pct_match.group(1))
                    self.progress_var.set(percent)

                    # Extract ETA
                    eta_match = re.search(r"ETA\s+([\d:]+)", line)
                    eta_text = ""

                    if eta_match:
                        raw_time = eta_match.group(1)
                        parts = list(map(int, raw_time.split(':')))

                        if len(parts) == 2:
                            mins, secs = parts
                            if mins == 0:
                                eta_text = "Less than a minute..."
                            else:
                                eta_text = f"{mins} Minute{'s' if mins != 1 else ''} left..."
                        elif len(parts) == 3:
                            hours, mins, secs = parts
                            eta_text = f"{hours} Hour{'s' if hours != 1 else ''} {mins} Minute{'s' if mins != 1 else ''} left..."

                    display_text = f"Downloading: {percent}%"
                    if eta_text:
                        display_text += f" - {eta_text}"

                    self.status_label.config(text=display_text)
            except:
                pass


if __name__ == '__main__':
    root = tk.Tk()
    app = YTDLPGUI(root)
    root.mainloop()
