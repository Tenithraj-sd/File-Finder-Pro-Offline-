import json
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import subprocess
import sys

class FileManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Explorer")
        self.root.geometry("1000x700")
        self.root.minsize(800, 500)
        self.root.configure(bg="#f0f0f0")
        self.default_json_path = "file_structure.json"
        self.icon_size = (72, 72)
        self.view_mode = "Icon"  # Default view mode
        self.df = pd.DataFrame()
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.icon_view_paths = []
        self.setup_styles()
        self.create_header()
        self.create_search_bar()
        self.create_view_buttons()
        self.create_control_frames()
        self.create_main_content_frame()
        self.create_status_bar()
        self.load_icons()
        self.load_directory_tree()

        # Mousewheel bindings
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)
        self.canvas.bind("<Button-5>", self.on_mousewheel)
        self.canvas.bind("<Shift-MouseWheel>", self.on_shift_mousewheel)

    def setup_styles(self):
        # Styling for widgets
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Segoe UI', 10))
        self.style.configure('TButton', padding=5, font=('Segoe UI', 10))
        self.style.configure('TEntry', padding=5)
        self.style.configure('Accent.TButton', background='#2196F3', foreground='white')
        self.style.map('Accent.TButton', 
            background=[('active', '#1976D2'), ('pressed', '#0D47A1')],
            foreground=[('active', 'white'), ('pressed', 'white')]
        )
        self.style.configure('Toggle.TButton', padding=8)
        self.style.map('Toggle.TButton',
            background=[('selected', '#2196F3'), ('!selected', '#e0e0e0')],
            foreground=[('selected', 'white'), ('!selected', 'black')]
        )

    def create_header(self):
        header = ttk.Frame(self.root)
        header.pack(fill='x', pady=(10, 0))
        title = ttk.Label(header, text="File Finder Pro", font=('Segoe UI', 18, 'bold'))
        title.pack(side=tk.LEFT, padx=20)
        separator = ttk.Separator(header, orient='horizontal')
        separator.pack(side=tk.BOTTOM, fill='x', pady=5)

    def create_search_bar(self):
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill='x', padx=20, pady=10)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=('Segoe UI', 12))
        search_entry.pack(side=tk.LEFT, fill='x', expand=True, ipady=5)
        search_btn = ttk.Button(search_frame, text="Search", style='Accent.TButton', 
                               command=self.perform_search)
        search_btn.pack(side=tk.RIGHT, padx=(10, 0))

    def create_view_buttons(self):
        self.view_buttons_frame = ttk.Frame(self.root)
        self.view_buttons_frame.pack(fill='x', padx=20, pady=(0, 10))
        view_label = ttk.Label(self.view_buttons_frame, text="View:")
        view_label.pack(side=tk.LEFT, padx=(0, 10))
        self.view_var = tk.StringVar(value="Icon")
        icon_btn = ttk.Radiobutton(self.view_buttons_frame, text="Icon", variable=self.view_var, 
                                  value="Icon", command=self.toggle_view, style='Toggle.TButton')
        icon_btn.pack(side=tk.LEFT, padx=5)
        list_btn = ttk.Radiobutton(self.view_buttons_frame, text="List", variable=self.view_var, 
                                  value="List", command=self.toggle_view, style='Toggle.TButton')
        list_btn.pack(side=tk.LEFT, padx=5)

    def create_control_frames(self):
        # Icon view controls
        self.icon_controls_frame = ttk.Frame(self.root)
        self.icon_row_var = tk.IntVar()
        self.icon_col_var = tk.IntVar()
        ttk.Label(self.icon_controls_frame, text="Row:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(self.icon_controls_frame, textvariable=self.icon_row_var, width=5).pack(side=tk.LEFT)
        ttk.Label(self.icon_controls_frame, text="Column:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(self.icon_controls_frame, textvariable=self.icon_col_var, width=5).pack(side=tk.LEFT)
        ttk.Button(self.icon_controls_frame, text="Open", command=self.open_icon_by_row_col).pack(side=tk.LEFT, padx=5)

        # List view controls
        self.list_controls_frame = ttk.Frame(self.root)
        self.list_index_var = tk.IntVar()
        ttk.Label(self.list_controls_frame, text="Index:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(self.list_controls_frame, textvariable=self.list_index_var, width=5).pack(side=tk.LEFT)
        ttk.Button(self.list_controls_frame, text="Open", command=self.open_by_index).pack(side=tk.LEFT, padx=5)

    def create_main_content_frame(self):
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill='both', expand=True, padx=20)
        self.canvas = tk.Canvas(content_frame, highlightthickness=0, bg='#f0f0f0')
        self.scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.canvas.yview)
        self.h_scrollbar = ttk.Scrollbar(content_frame, orient="horizontal", command=self.canvas.xview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"),
                xscrollcommand=self.h_scrollbar.set,
                yscrollcommand=self.scrollbar.set
            )
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.h_scrollbar.pack(side="bottom", fill="x")

    def create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                                   relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_icons(self):
        try:
            self.folder_icon = ImageTk.PhotoImage(
                Image.open("folder.png").resize(self.icon_size, Image.LANCZOS))
            self.file_icon = ImageTk.PhotoImage(
                Image.open("file.png").resize(self.icon_size, Image.LANCZOS))
            self.video_icon = ImageTk.PhotoImage(
                Image.open("reel.png").resize(self.icon_size, Image.LANCZOS))
            self.audio_icon = ImageTk.PhotoImage(
                Image.open("audio.png").resize(self.icon_size, Image.LANCZOS))
            self.doc_icon = ImageTk.PhotoImage(
                Image.open("doc.png").resize(self.icon_size, Image.LANCZOS))
        except FileNotFoundError:
            messagebox.showwarning("Missing Icons", 
                "Please ensure all icons (folder.png, file.png, reel.png, audio.png, doc.png) exist")
            self.root.destroy()

    def load_directory_tree(self):
        try:
            with open(self.default_json_path, 'r') as f:
                self.directory_tree = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            self.directory_tree = {}

    def perform_search(self):
        self.status_var.set("Searching...")
        self.root.update_idletasks()
        search_term = self.search_var.get().lower()
        try:
            self.search_results = self.find_in_tree(self.directory_tree, search_term)
            self.df = pd.DataFrame([{
                'name': item.get('name', 'Unknown'),
                'path': item.get('path', ''),
                'type': item.get('type', 'file'),
                'extension': item.get('extension', '')
            } for item in self.search_results])
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")
            self.df = pd.DataFrame()
        
        # Update display based on current view mode
        self.update_display()

        # Show/hide control frames based on view mode
        self.toggle_control_frames()

        self.status_var.set(f"Found {len(self.df)} item(s)")

    def find_in_tree(self, node, search_term):
        matches = []
        try:
            if (search_term in node.get('name', '').lower() or
                search_term in node.get('path', '').lower() or
                search_term in node.get('extension', '').lower()):
                matches.append(node)
            if node.get('type') == 'directory':
                for child in node.get('children', []):
                    matches.extend(self.find_in_tree(child, search_term))
        except Exception as e:
            messagebox.showerror("Error", f"Search error: {str(e)}")
        return matches

    def toggle_view(self):
        new_mode = self.view_var.get()
        if new_mode != self.view_mode:
            self.view_mode = new_mode
            self.update_display()
            self.toggle_control_frames()

    def toggle_control_frames(self):
        """Show/hide control frames based on the current view mode."""
        if self.view_mode == "Icon":
            self.icon_controls_frame.pack(fill='x', padx=20, pady=5, after=self.view_buttons_frame)
            self.list_controls_frame.pack_forget()
        elif self.view_mode == "List":
            self.list_controls_frame.pack(fill='x', padx=20, pady=5, after=self.view_buttons_frame)
            self.icon_controls_frame.pack_forget()
        else:
            self.icon_controls_frame.pack_forget()
            self.list_controls_frame.pack_forget()

    def update_display(self):
        buffer_frame = ttk.Frame(self.scrollable_frame)
        buffer_frame.grid(row=0, column=0, sticky='nsew')
        if self.df.empty:
            self.show_empty_state(buffer_frame)
        elif self.view_mode == "Icon":
            self.create_icon_view(buffer_frame)
        else:
            self.create_list_view(buffer_frame)
        for widget in self.scrollable_frame.winfo_children():
            if widget != buffer_frame:
                widget.destroy()
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def create_icon_view(self, parent):
        columns = 7  # Fixed 7-column layout
        video_ext = {'mkv', 'mp4', 'avi', 'mov'}
        audio_ext = {'mp3', 'wav', 'aac', 'flac'}
        doc_ext = {'doc', 'docx', 'pdf', 'txt', 'xls', 'xlsx'}
        self.icon_view_paths.clear()  # Reset paths for new search results
        for idx, (_, row) in enumerate(self.df.iterrows()):
            self.icon_view_paths.append(row['path'])
            frame = ttk.Frame(parent, style='Card.TFrame')
            frame.grid(row=idx//columns, column=idx%columns, padx=15, pady=15, sticky='nsew')
            icon_frame = ttk.Frame(frame)
            icon_frame.pack(pady=(10, 0))
            if row['type'] == 'directory':
                icon = self.folder_icon
            else:
                ext = row['extension'].lower()
                icon = self.video_icon if ext in video_ext else \
                       self.audio_icon if ext in audio_ext else \
                       self.doc_icon if ext in doc_ext else self.file_icon
            label = ttk.Label(icon_frame, image=icon, background='#f0f0f0')
            label.pack()
            label.bind("<Double-1>", lambda e, path=row['path']: self.open_file(path))
            name = ttk.Label(frame, text=row['name'], wraplength=120, 
                            font=('Segoe UI', 11, 'bold'), background='#f0f0f0')
            name.pack(pady=(10, 0))
            name.bind("<Double-1>", lambda e, path=row['path']: self.open_file(path))
            frame.bind("<Enter>", lambda e, f=frame: f.configure(style='CardHover.TFrame'))
            frame.bind("<Leave>", lambda e, f=frame: f.configure(style='Card.TFrame'))

    def create_list_view(self, parent):
        columns = ("#", "Name", "Path", "Type", "Extension")
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        tree.heading("#", text="#", anchor=tk.W)
        tree.heading("Name", text="Name", anchor=tk.W)
        tree.heading("Path", text="Path", anchor=tk.W)
        tree.heading("Type", text="Type", anchor=tk.W)
        tree.heading("Extension", text="Extension", anchor=tk.W)
        tree.column("#", width=50, anchor=tk.CENTER)
        tree.column("Name", width=200, anchor=tk.W)
        tree.column("Path", width=400, anchor=tk.W)
        tree.column("Type", width=100, anchor=tk.W)
        tree.column("Extension", width=100, anchor=tk.W)
        for idx, (_, row) in enumerate(self.df.iterrows(), start=1):
            tree.insert("", "end", values=(
                idx,
                row['name'],
                row['path'],
                row['type'],
                row['extension']
            ))
        tree.tag_configure('odd', background='#f8f8f8')
        tree.tag_configure('even', background='#ffffff')
        for i, item in enumerate(tree.get_children()):
            tree.item(item, tags=('even' if i % 2 else 'odd'))
        tree.pack(fill='both', expand=True, pady=10, padx=10)
        tree.bind("<Double-1>", self.on_tree_double_click)

    def show_empty_state(self, parent):
        empty_label = ttk.Label(parent, text="No items found", 
                               font=('Segoe UI', 14), foreground='#666')
        empty_label.pack(expand=True)

    def on_tree_double_click(self, event):
        tree = event.widget
        selection = tree.selection()
        if selection:
            item = tree.item(selection[0])
            path = item['values'][2]
            self.open_file(path)

    def open_file(self, path):
        try:
            if os.path.exists(path):
                if sys.platform == "linux":
                    subprocess.run(['xdg-open', path], check=True)
                else:
                    os.startfile(path)
                self.status_var.set(f"Opened: {path}")
            else:
                self.status_var.set("File not found")
                messagebox.showerror("Error", f"File not found:\n{path}")
        except subprocess.CalledProcessError as e:
            self.status_var.set("Failed to open file")
            messagebox.showerror("Error", f"Error opening file:\n{str(e)}")
        except Exception as e:
            self.status_var.set("Failed to open file")
            messagebox.showerror("Error", f"Unexpected error:\n{str(e)}")

    def open_by_index(self):
        index = self.list_index_var.get()
        if 1 <= index <= len(self.df):
            path = self.df.iloc[index-1]['path']
            self.open_file(path)
        else:
            messagebox.showerror("Invalid Index", f"Index must be between 1 and {len(self.df)}")

    def open_icon_by_row_col(self):
        row = self.icon_row_var.get()
        col = self.icon_col_var.get()
        columns = 7  # Match fixed column count
        if row < 1 or col < 1:
            messagebox.showerror("Invalid Input", "Row and column must be at least 1")
            return
        index = (row - 1) * columns + (col - 1)
        if 0 <= index < len(self.icon_view_paths):
            path = self.icon_view_paths[index]
            self.open_file(path)
        else:
            messagebox.showerror("Invalid Input", "Row or column out of range")

    def on_mousewheel(self, event):
        if event.state & 0x0001:  # Shift pressed
            self.canvas.xview_scroll(-1*(event.delta//120), "units")
        else:
            self.canvas.yview_scroll(-1*(event.delta//120), "units")

    def on_shift_mousewheel(self, event):
        self.canvas.xview_scroll(-1*(event.delta//120), "units")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileManagerApp(root)
    root.mainloop()