import json
import tkinter as tk
import traceback
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk
import ezcord
import pandas as pd
import pyperclip
import sv_ttk


def load_translations():
    with open("utils/data/lang/language.json", 'r', encoding="utf-8") as f:
        return json.load(f)


class ManagerApp:
    def __init__(self):
        self.translations = load_translations()
        self.load_config()
        self.setup_window()
        self.setup_styles()
        self.create_frames()
        self.create_widgets()
        self.create_treeview()
        self.setup_bindings()
        self.df = None
        self.original_df = None

    def load_config(self):
        config_path = Path("config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "theme": "dark",
                "accent_color": "#007bff",
                "font_family": "Roboto",
                "language": "en"
            }
            with open(config_path, 'w') as f:
                json.dump(self.config, f)
        self.language = self.config.get("language", "en")

    def save_config(self):
        self.config["language"] = self.language
        with open("config.json", 'w') as f:
            json.dump(self.config, f)

    def setup_window(self):
        self.window = ctk.CTk()
        self.window.title(self.translations[self.language]["title"])
        self.window.geometry("1400x800")
        self.window.configure(fg_color="#1a1a1a")

        icon_path = Path("utils/data/assets/logo.ico")
        if icon_path.exists():
            self.window.iconbitmap(icon_path)

    def setup_styles(self):
        sv_ttk.set_theme("dark")

        self.style = ttk.Style()
        self.style.configure(
            "Custom.Treeview",
            background="#2d2d2d",
            foreground="white",
            fieldbackground="#2d2d2d",
            rowheight=30,
            borderwidth=0
        )
        self.style.configure(
            "Custom.Treeview.Heading",
            background="#3d3d3d",
            foreground="white",
            relief="flat"
        )
        self.style.map(
            "Custom.Treeview",
            background=[("selected", "#007bff")],
            foreground=[("selected", "white")]
        )

    def create_frames(self):
        self.main_container = ctk.CTkFrame(
            self.window,
            fg_color="#1e1e1e",
            corner_radius=15
        )
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        self.header_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="#252525",
            corner_radius=10,
            height=60
        )
        self.header_frame.pack(fill="x", padx=10, pady=(10, 5))

        self.sidebar_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="#252525",
            corner_radius=10,
            width=300
        )
        self.sidebar_frame.pack(side="left", fill="y", padx=(10, 5), pady=5)

        self.content_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="#252525",
            corner_radius=10
        )
        self.content_frame.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=5)

    def create_widgets(self):
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=self.translations[self.language]["title"],
            font=("Roboto", 24, "bold"),
            text_color="#ffffff"
        )
        self.title_label.pack(side="left", padx=20, pady=10)
        self.create_sidebar_widgets()

    def create_sidebar_widgets(self):
        self.file_section = self.create_section(self.sidebar_frame, self.translations[self.language]["file_management"])

        self.load_button = self.create_button(
            self.file_section,
            self.translations[self.language]["load_file"],
            self.load_file
        )

        self.export_button = self.create_button(
            self.file_section,
            self.translations[self.language]["export_data"],
            self.export_data
        )

        self.sort_section = self.create_section(self.sidebar_frame, self.translations[self.language]["sort"])

        self.sort_column = ctk.StringVar(value=self.translations[self.language]["member_count"])
        self.sort_dropdown = ctk.CTkOptionMenu(
            self.sort_section,
            values=[self.translations[self.language]["guild_name"], self.translations[self.language]["member_count"], self.translations[self.language]["guild_id"], self.translations[self.language]["owner"]],
            variable=self.sort_column,
            fg_color="#3d3d3d",
            button_color="#007bff",
            button_hover_color="#0056b3"
        )
        self.sort_dropdown.pack(fill="x", padx=10, pady=5)

        self.sort_order = ctk.StringVar(value=self.translations[self.language]["descending"])
        self.sort_order_dropdown = ctk.CTkOptionMenu(
            self.sort_section,
            values=[self.translations[self.language]["ascending"], self.translations[self.language]["descending"]],
            variable=self.sort_order,
            fg_color="#3d3d3d",
            button_color="#007bff",
            button_hover_color="#0056b3"
        )
        self.sort_order_dropdown.pack(fill="x", padx=10, pady=5)

        self.sort_button = self.create_button(
            self.sort_section,
            self.translations[self.language]["sort_button"],
            self.sort_data
        )

        self.search_section = self.create_section(self.sidebar_frame, self.translations[self.language]["search"])

        self.search_column = ctk.StringVar(value=self.translations[self.language]["guild_name"])
        self.search_dropdown = ctk.CTkOptionMenu(
            self.search_section,
            values=[self.translations[self.language]["guild_name"], self.translations[self.language]["member_count"], self.translations[self.language]["guild_id"], self.translations[self.language]["owner"]],
            variable=self.search_column,
            fg_color="#3d3d3d",
            button_color="#007bff",
            button_hover_color="#0056b3"
        )
        self.search_dropdown.pack(fill="x", padx=10, pady=5)

        self.search_entry = ctk.CTkEntry(
            self.search_section,
            placeholder_text=self.translations[self.language]["search_placeholder"],
            fg_color="#3d3d3d",
            border_color="#007bff",
            text_color="white"
        )
        self.search_entry.pack(fill="x", padx=10, pady=5)

        self.search_button = self.create_button(
            self.search_section,
            self.translations[self.language]["search_button"],
            self.search_data
        )

    def create_section(self, parent, title):
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill="x", padx=10, pady=5)

        label = ctk.CTkLabel(
            section,
            text=title,
            font=("Roboto", 14, "bold"),
            text_color="#888888"
        )
        label.pack(anchor="w", padx=10, pady=5)

        return section

    def create_button(self, parent, text, command):
        button = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            fg_color="#007bff",
            hover_color="#0056b3",
            height=35,
            corner_radius=8
        )
        button.pack(fill="x", padx=10, pady=5)
        return button

    def create_treeview(self):
        self.tree_container = ctk.CTkFrame(
            self.content_frame,
            fg_color="#2d2d2d",
            corner_radius=10
        )
        self.tree_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(
            self.tree_container,
            style="Custom.Treeview",
            show="headings"
        )
        self.tree.pack(fill="both", expand=True, padx=2, pady=2)

        self.yscrollbar = ttk.Scrollbar(
            self.tree,
            orient="vertical",
            command=self.tree.yview
        )
        self.yscrollbar.pack(side="right", fill="y")

        self.xscrollbar = ttk.Scrollbar(
            self.tree,
            orient="horizontal",
            command=self.tree.xview
        )
        self.xscrollbar.pack(side="bottom", fill="x")

        self.tree.configure(
            yscrollcommand=self.yscrollbar.set,
            xscrollcommand=self.xscrollbar.set
        )

    def setup_bindings(self):
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.window.bind("<Control-f>", lambda e: self.search_entry.focus())
        self.search_entry.bind("<Return>", lambda e: self.search_data())

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            try:
                self.df = self.load_and_parse_file(file_path)
                self.original_df = self.df.copy()
                self.display_data_in_table(self.df)
            except Exception as e:
                messagebox.showerror(self.translations[self.language]["error"], f"{self.translations[self.language]["error_load"]} {e}")
                traceback.print_exc()

    def load_and_parse_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        guilds = []
        failed_guilds = []
        for line in lines:
            parts = line.split(" - ")
            if len(parts) == 4:
                guild = {
                    self.translations[self.language]["guild_name"]: parts[0].strip(),
                    self.translations[self.language]["member_count"]: int(parts[1].replace(',', '').strip()),
                    self.translations[self.language]["guild_id"]: parts[2].strip(),
                    self.translations[self.language]["owner"]: parts[3].strip()
                }
                guilds.append(guild)
            else:
                failed_guilds.append(line)

        if failed_guilds:
            print(f"Failed to parse {len(failed_guilds)} lines out of {len(lines)} lines. Failed lines: \n{failed_guilds}")
        #
        # If a guild is in Failed List, Check if the Format is Correct
        #
        # GUILD-NAME - MEMBER-COUNT - GUILD-ID - OWNER
        #
        # If the GUILD-NAME or OWNER has a '-' in it, it will be put in the failed list
        #
        return pd.DataFrame(guilds)

    def display_data_in_table(self, dataframe):
        if self.tree is None:
            messagebox.showerror(self.translations[self.language]["error"], self.translations[self.language]["error_table"])
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.tree["columns"] = list(dataframe.columns)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(col, anchor="w", width=150)

        for index, row in dataframe.iterrows():
            self.tree.insert("", "end", values=list(row))

    def show_context_menu(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            menu = tk.Menu(self.tree, tearoff=0)
            menu.configure(bg="#2d2d2d", fg="white")
            menu.add_command(
                label=self.translations[self.language]["copy_guild_id"],
                command=lambda: self.copy_to_clipboard(self.translations[self.language]["guild_id"], selected_item)
            )
            menu.add_command(
                label=self.translations[self.language]["copy_owner"],
                command=lambda: self.copy_to_clipboard(self.translations[self.language]["owner"], selected_item)
            )
            menu.add_separator()
            menu.add_command(
                label=self.translations[self.language]["copy_all"],
                command=lambda: self.copy_all_to_clipboard(selected_item)
            )
            menu.post(event.x_root, event.y_root)

    def copy_to_clipboard(self, column, selected_item):
        values = self.tree.item(selected_item)["values"]
        index = self.tree["columns"].index(column)
        pyperclip.copy(values[index])

    def copy_all_to_clipboard(self, selected_item):
        values = self.tree.item(selected_item)["values"]
        all_data = "\t".join(map(str, values))
        pyperclip.copy(all_data)

    def sort_data(self):
        if self.df is not None:
            column = self.sort_column.get()
            ascending = self.sort_order.get() == self.translations[self.language]["ascending"]
            self.df = self.df.sort_values(by=column, ascending=ascending)
            self.display_data_in_table(self.df)

    def search_data(self):
        if self.original_df is not None:
            self.df = self.original_df.copy()
            column = self.search_column.get()
            search_term = self.search_entry.get().strip()
            if search_term:
                self.df = self.df[self.df[column].str.contains(search_term, case=False)]
            self.display_data_in_table(self.df)

    def export_data(self):
        if self.df is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx")
            if file_path:
                self.df.to_excel(file_path, index=False)
                messagebox.showinfo(self.translations[self.language]["success"], self.translations[self.language]["success_export"])
        else:
            messagebox.showerror(self.translations[self.language]["error"], self.translations[self.language]["error_export"])

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = ManagerApp()
    app.run()