import customtkinter as ctk
from tkinter import filedialog, messagebox
import os, threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class FileListExtractor(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("File List Extractor")
        self.geometry("820x640")
        self.minsize(700, 520)
        self.configure(fg_color="#0f0f0f")
        self.file_list = []
        self._build_ui()

    def _build_ui(self):
        title_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=0, height=56)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        ctk.CTkLabel(title_frame, text="File List Extractor",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#e0e0e0").pack(side="left", padx=20, pady=14)
        ctrl = ctk.CTkFrame(self, fg_color="#151515", corner_radius=0, height=110)
        ctrl.pack(fill="x")
        ctrl.pack_propagate(False)
        inner = ctk.CTkFrame(ctrl, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=12)
        row1 = ctk.CTkFrame(inner, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 8))
        self.folder_entry = ctk.CTkEntry(row1, placeholder_text="Select a folder...",
            fg_color="#222222", border_color="#333333", text_color="#c0c0c0",
            font=ctk.CTkFont(size=13), height=36, corner_radius=8)
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(row1, text="Browse", width=100, height=36,
            fg_color="#1f6feb", hover_color="#388bfd", font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=8, command=self._browse).pack(side="left")
        ctk.CTkButton(row1, text="Extract", width=100, height=36,
            fg_color="#238636", hover_color="#2ea043", font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=8, command=self._extract).pack(side="left", padx=(10, 0))
        row2 = ctk.CTkFrame(inner, fg_color="transparent")
        row2.pack(fill="x")
        self.include_ext_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(row2, text="Include extension", variable=self.include_ext_var,
            font=ctk.CTkFont(size=12), text_color="#a0a0a0", fg_color="#1f6feb",
            hover_color="#388bfd", border_color="#444444", checkmark_color="white").pack(side="left", padx=(0,20))
        self.include_subdir_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(row2, text="Include subdirectories", variable=self.include_subdir_var,
            font=ctk.CTkFont(size=12), text_color="#a0a0a0", fg_color="#1f6feb",
            hover_color="#388bfd", border_color="#444444", checkmark_color="white").pack(side="left", padx=(0,20))
        self.show_full_path_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(row2, text="Show full path", variable=self.show_full_path_var,
            font=ctk.CTkFont(size=12), text_color="#a0a0a0", fg_color="#1f6feb",
            hover_color="#388bfd", border_color="#444444", checkmark_color="white").pack(side="left")
        ctk.CTkFrame(self, fg_color="#2a2a2a", height=1, corner_radius=0).pack(fill="x")
        self.status_label = ctk.CTkLabel(self, text="No folder selected.",
            font=ctk.CTkFont(size=11), text_color="#606060", anchor="w")
        self.status_label.pack(fill="x", padx=20, pady=(6,2))
        text_frame = ctk.CTkFrame(self, fg_color="#111111", corner_radius=10)
        text_frame.pack(fill="both", expand=True, padx=16, pady=(0,8))
        self.textbox = ctk.CTkTextbox(text_frame, fg_color="#111111", text_color="#d0d0d0",
            font=ctk.CTkFont(family="Consolas", size=12), border_width=0, corner_radius=10)
        self.textbox.pack(fill="both", expand=True, padx=4, pady=4)
        btn_bar = ctk.CTkFrame(self, fg_color="#151515", corner_radius=0, height=52)
        btn_bar.pack(fill="x")
        btn_bar.pack_propagate(False)
        bi = ctk.CTkFrame(btn_bar, fg_color="transparent")
        bi.pack(side="right", padx=16, pady=10)
        ctk.CTkButton(bi, text="Copy to Clipboard", width=160, height=32, fg_color="#2d2d2d",
            hover_color="#3d3d3d", font=ctk.CTkFont(size=12), corner_radius=8,
            border_width=1, border_color="#444444", command=self._copy).pack(side="left", padx=(0,8))
        ctk.CTkButton(bi, text="Save as TXT", width=140, height=32, fg_color="#2d2d2d",
            hover_color="#3d3d3d", font=ctk.CTkFont(size=12), corner_radius=8,
            border_width=1, border_color="#444444", command=self._save).pack(side="left", padx=(0,8))
        ctk.CTkButton(bi, text="Clear", width=90, height=32, fg_color="#2d2d2d",
            hover_color="#3a1a1a", font=ctk.CTkFont(size=12), corner_radius=8,
            border_width=1, border_color="#444444", command=self._clear).pack(side="left")

    def _browse(self):
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)
            self.status_label.configure(text=f"Folder selected: {folder}", text_color="#606060")

    def _extract(self):
        folder = self.folder_entry.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Error", "Please select a valid folder first.")
            return
        threading.Thread(target=self._do_extract, args=(folder,), daemon=True).start()

    def _do_extract(self, folder):
        include_ext = self.include_ext_var.get()
        include_sub = self.include_subdir_var.get()
        full_path = self.show_full_path_var.get()
        lines = []
        total = 0
        try:
            if include_sub:
                for root, dirs, files in os.walk(folder):
                    dirs.sort()
                    rel_root = os.path.relpath(root, folder)
                    for f in sorted(files):
                        total += 1
                        name = f if include_ext else os.path.splitext(f)[0]
                        lines.append(os.path.join(root, name) if full_path else (name if rel_root == "." else os.path.join(rel_root, name)))
            else:
                for f in sorted(os.listdir(folder)):
                    if os.path.isfile(os.path.join(folder, f)):
                        total += 1
                        name = f if include_ext else os.path.splitext(f)[0]
                        lines.append(os.path.join(folder, name) if full_path else name)
            self.file_list = lines
            self.textbox.configure(state="normal")
            self.textbox.delete("1.0", "end")
            self.textbox.insert("1.0", "\n".join(lines))
            self.status_label.configure(text=f"  {total} file(s) found in '{os.path.basename(folder)}'", text_color="#3fb950")
        except Exception as e:
            self.status_label.configure(text=f"  Error: {e}", text_color="#f85149")

    def _copy(self):
        content = self.textbox.get("1.0", "end").strip()
        if not content: messagebox.showwarning("Nothing to copy", "Extract files first."); return
        self.clipboard_clear(); self.clipboard_append(content); self.update()
        self.status_label.configure(text="Copied to clipboard!", text_color="#58a6ff")

    def _save(self):
        content = self.textbox.get("1.0", "end").strip()
        if not content: messagebox.showwarning("Nothing to save", "Extract files first."); return
        path = filedialog.asksaveasfilename(defaultextension=".txt",
            filetypes=[("Text files","*.txt"),("All files","*.*")], initialfile="filelist.txt")
        if path:
            with open(path, "w", encoding="utf-8") as f: f.write(content)
            self.status_label.configure(text=f"Saved to {path}", text_color="#3fb950")

    def _clear(self):
        self.textbox.delete("1.0", "end"); self.file_list = []
        self.status_label.configure(text="Cleared.", text_color="#606060")

if __name__ == "__main__":
    app = FileListExtractor()
    app.mainloop()