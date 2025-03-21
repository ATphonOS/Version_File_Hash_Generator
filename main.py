import os
import sys
import hashlib
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Style constants
BACKGROUND_COLOR = "#1E1E1E"
FOREGROUND_COLOR = "#E0E0E0"
ACCENT_COLOR = "#0288D1"
ACCENT_COLOR_ACTIVE = "#03A9F4"
CARD_COLOR = "#2C2C2C"
PADDING = 10
FONT_DEFAULT = ("Helvetica", 10)
FONT_BOLD = ("Helvetica", 10, "bold")
BUTTON_FONT = ("Helvetica", 9)
BUTTON_PADDING = 3

class AppUtils:
    @staticmethod
    def set_window_icon(window):
        try:
            base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
            icon_path = os.path.join(base_path, "logo_app.png")
            icon = tk.PhotoImage(file=icon_path)
            window.iconphoto(True, icon)
            return icon
        except Exception as e:
            print(f"Error loading icon: {e}")
            return None

class HashGeneratorApp(AppUtils):
    def __init__(self, root):
        self.root = root
        self.root.title("ATphonOS Version File Hash Generator")
        self.root.geometry("600x480")
        self.root.resizable(False, False)
        self.root.configure(bg=BACKGROUND_COLOR)

        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TFrame', background=BACKGROUND_COLOR)
        style.configure('TLabel', background=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR, font=FONT_DEFAULT)
        style.configure('TLabelframe', background=CARD_COLOR, foreground=FOREGROUND_COLOR)
        style.configure('TLabelframe.Label', background=CARD_COLOR, foreground=FOREGROUND_COLOR, font=FONT_BOLD)
        
        style.configure('TButton', 
                       background=ACCENT_COLOR,
                       foreground=FOREGROUND_COLOR,
                       font=BUTTON_FONT,
                       padding=BUTTON_PADDING)
        style.map('TButton',
                 background=[('active', ACCENT_COLOR_ACTIVE)],
                 foreground=[('active', FOREGROUND_COLOR)])
        
        style.configure('TEntry',
                       fieldbackground=CARD_COLOR,
                       foreground=FOREGROUND_COLOR,
                       insertcolor=FOREGROUND_COLOR)

        self.icon = self.set_window_icon(self.root)

        main_frame = ttk.Frame(self.root, padding=PADDING)
        main_frame.pack(expand=True, fill="both")

        ttk.Label(main_frame, text="Directory Path:").grid(row=0, column=0, sticky="w", pady=5)
        self.dir_entry = ttk.Entry(main_frame, width=50)
        self.dir_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_directory).grid(row=0, column=2, padx=5)

        ttk.Label(main_frame, text="Version name:").grid(row=1, column=0, sticky="w", pady=5)
        self.version_entry = ttk.Entry(main_frame, width=50)
        self.version_entry.grid(row=1, column=1, padx=5, pady=5)
        self.version_entry.insert(0, "")

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        self.generate_button = ttk.Button(button_frame, text="Generate Hash File", command=self.generate_hash_file)
        self.generate_button.pack(side=tk.LEFT, padx=5)
        
        self.open_button = ttk.Button(button_frame, text="Open Generated File", command=self.open_generated_file)
        self.open_button.pack(side=tk.LEFT, padx=5)

        # Log area with auto-hiding scrollbar
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding=5)
        log_frame.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=5)
        
        self.log_text = tk.Text(log_frame, 
                              height=15, 
                              width=70, 
                              state='disabled', 
                              wrap=tk.WORD,
                              bg=CARD_COLOR,
                              fg=FOREGROUND_COLOR,
                              insertbackground=FOREGROUND_COLOR,
                              font=FONT_DEFAULT,
                              borderwidth=0)
        self.log_text.pack(side=tk.LEFT, fill="both", expand=True)
        
        self.scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=self._scrollbar_visibility)
        # Don't pack scrollbar yet - we'll manage its visibility manually

        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)

    def _scrollbar_visibility(self, *args):
        """Manage scrollbar visibility based on content"""
        if self.log_text.yview() == (0.0, 1.0):  # Content fits entirely
            self.scrollbar.pack_forget()  # Hide scrollbar
        else:
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # Show scrollbar

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
            self.log(f"Selected directory: {directory}")

    def calculate_file_hash(self, filepath: str) -> str:
        try:
            with open(filepath, 'rb') as f:
                sha1 = hashlib.sha1()
                for chunk in iter(lambda: f.read(4096), b''):
                    sha1.update(chunk)
                hash_value = sha1.hexdigest()[:16]
                self.log(f"Calculated hash for {os.path.basename(filepath)}: {hash_value}")
                return hash_value
        except Exception as e:
            error_msg = f"Error calculating hash for {filepath}: {e}"
            self.log(error_msg)
            return "Error"

    def generate_hash_file(self):
        directory = self.dir_entry.get().strip()
        if not directory:
            messagebox.showerror("Error", "Please enter or select a directory path.")
            return
        
        if not os.path.isdir(directory):
            messagebox.showerror("Error", "The specified path is not a valid directory.")
            self.log(f"Error: '{directory}' is not a valid directory")
            return

        version_text = self.version_entry.get().strip()
        if not version_text:
            messagebox.showerror("Error", "Please enter text for the last line.")
            return

        self.generate_button.config(state='disabled')
        self.open_button.config(state='disabled')
        self.log("\n--- Starting hash generation ---")
        output_file = "file_hashes.txt"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as out_f:
                files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
                total_files = len(files)
                self.log(f"Found {total_files} files to process")
                
                for i, filename in enumerate(files, 1):
                    file_path = os.path.join(directory, filename)
                    file_hash = self.calculate_file_hash(file_path)
                    out_f.write(f"{filename}  {file_hash}\n")
                    self.log(f"Progress: {i}/{total_files} files processed")
                    self.root.update_idletasks()
                
                out_f.write(f"{version_text}\n")
                self.log(f"Added last line: {version_text}")

            success_msg = f"Hash file '{output_file}' created successfully with {total_files} entries."
            self.log(success_msg)
            messagebox.showinfo("Success", success_msg)
        except Exception as e:
            error_msg = f"Error creating hash file: {e}"
            self.log(error_msg)
            messagebox.showerror("Error", error_msg)
        finally:
            self.generate_button.config(state='normal')
            self.open_button.config(state='normal')

    def open_generated_file(self):
        output_file = "file_hashes.txt"
        try:
            if os.path.exists(output_file):
                os.startfile(output_file)
                self.log(f"Opened {output_file}")
            else:
                messagebox.showerror("Error", f"File '{output_file}' not found. Generate Hash File.")
                self.log(f"Error: '{output_file}' not found")
        except Exception as e:
            error_msg = f"Error opening file: {e}"
            self.log(error_msg)
            messagebox.showerror("Error", error_msg)

    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self._scrollbar_visibility()  

if __name__ == "__main__":
    root = tk.Tk()
    app = HashGeneratorApp(root)
    root.mainloop()
