import os
import sys
import re
import customtkinter as ctk
from tkinter import messagebox, filedialog, Menu
from darkdetect import theme
from tkhtmlview import HTMLLabel
import markdown


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class MarkdownEditorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.BASE_DIR = os.path.abspath(os.path.dirname(__file__))
        self.ICON_PATH = resource_path(os.path.join("resources", "icon.ico"))
        self.title("Doctus")
        self.geometry("1200x800")
        self.minsize(1200, 800)
        self.iconbitmap(self.ICON_PATH)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme(resource_path(os.path.join("theme", "app_theme.json")))

        self.create_menu()

        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(18, 9), pady=18)

        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=(9, 18), pady=18)

        self.input_label = ctk.CTkLabel(
            self.left_frame,
            text="Markdown",
            font=ctk.CTkFont(size=15, weight="bold"))
        self.input_label.pack(pady=(10, 6))

        self.text_input = ctk.CTkTextbox(self.left_frame, font=ctk.CTkFont(family="Consolas", size=15), wrap="word")
        self.text_input.pack(fill="both", expand=True, padx=7, pady=(0, 15))
        self.text_input.bind("<KeyRelease>", self._debounced_update_preview)

        self.context_menu = self.create_context_menu()
        self.text_input.bind("<Button-3>", self.show_context_menu)
        self.text_input.bind("<Button-2>", self.show_context_menu)

        btn_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        btn_frame.pack(fill="y", anchor="w", pady=(0, 32), padx=4)

        theme_txt = "Dark theme" if ctk.get_appearance_mode() == "Light" else "Light theme"

        btn_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=4, pady=(0, 8))

        buttons = [("Save...", self.save_file),
                   ("Open...", self.open_file),
                   ("Copy Markdown", self.copy_markdown),
                   ("Change font size", self.change_font_size),
                   (f"Turn on {theme_txt}", self.toggle_theme)
                   ]

        for text, cmd in buttons:
            ctk.CTkButton(
                btn_frame,
                text=text,
                command=cmd
            ).pack(fill="x", pady=3, anchor="w")

        self.preview_label = ctk.CTkLabel(self.right_frame, text="Preview:",
                                          font=ctk.CTkFont(size=15, weight="bold"))
        self.preview_label.pack(pady=(10, 6))
        pbtn = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        pbtn.pack(fill="x", padx=5, pady=(0, 7))
        ctk.CTkButton(pbtn, text="Copy Preview as HTML", command=self.copy_html).pack(side="left", padx=(0, 10))
        ctk.CTkButton(pbtn, text="How can I copy it visually?", command=self.hint_copy).pack(side="left")

        self.preview = HTMLLabel(self.right_frame, html="", width=90, background="white")
        self.preview.pack(fill="both", expand=True, padx=10, pady=(0, 12))

        self.fontsize = 15
        self.set_sample_text()
        self.update_preview()

        self._update_job = None

    def create_context_menu(self):
        menu = Menu(self.text_input, tearoff=0)
        menu.add_command(label="Cut", command=self._cut)
        menu.add_command(label="Copy", command=self._copy)
        menu.add_command(label="Paste", command=self._paste)
        menu.add_separator()
        menu.add_command(label="Select all", command=self._select_all)
        return menu

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def create_menu(self):
        self.menu_bar = ctk.CTkFrame(self, corner_radius=0, fg_color="gray10")
        self.menu_bar.pack(fill="x", side="top")
        ctk.CTkButton(
            self.menu_bar,
            text="About the app",
            command=self.show_about,
            fg_color="gray17",
            hover_color="gray32",
            height=25,
            width=110
        ).pack(side="right", padx=12, pady=1)

    def set_sample_text(self):
        self.text_input.delete("1.0", "end")
        sample = (
            "# First level heading\n"
            "## Second level heading\n"
            "### Third level heading\n\n"
            "**bold**, *cursive*, ~~strike~~, `code`\n\n"
            "\n"
            "!!Alert!!\n"
            "&&Warning&&\n\n"
            "**@#898AC4@List:@end@**\n\n"
            "- (U_U) \n"
            "- (OwO) \n"
            "- (O_O) \n\n"
            "[Link](https://goo.su/JDpxUZ)\n"
            "\n\n"
            "> Quote\n\n"
            "```python\nprint(*[i for i in range(0, 10, 2) if i % 2 == 0])\n```\n\n"
            "![UWU](https://goo.su/BJW1X)\n"
            "\n\n"
            "# *@#BBDCE5@UWU@end@*\n\n"
            "*@#F0A8D0@Quick Markdown Example in Doctus!@end@*"
        )
        self.text_input.insert("1.0", sample)

    # ----- File Operations -----
    def save_file(self):
        fpath = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown; *.md", "*.md"), ("Text", "*.txt"), ("All", "*.*")]
        )
        if fpath:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(self.text_input.get("1.0", "end").strip())
            messagebox.showinfo("Doctus", "The file has been saved successfully!")

    def open_file(self):
        fpath = filedialog.askopenfilename(
            filetypes=[("Markdown; *.md", "*.md"), ("Text", "*.txt"), ("All", "*.*")]
        )
        if fpath:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            self.text_input.delete("1.0", "end")
            self.text_input.insert("1.0", content)
            self.update_preview()

    # ----- Preview update -----
    def update_preview(self):
        markdown_text = self.text_input.get("1.0", "end").strip()
        markdown_text = re.sub(r"~~(.*?)~~", r'<span style="text-decoration:line-through;">\1</span>', markdown_text)
        markdown_text = re.sub(
            r"!!(.*?)!!",
            r'<span style="color:#E62727; font-weight:bold; background:#fff2cf; border-radius:3px;">&#9888; \1</span>',
            markdown_text)
        markdown_text = re.sub(
            r"&&(.*?)&&",
            r'<span style="color:#FFB200; font-weight:bold; background:#fff2cf; border-radius:3px;">&#9888; \1</span>',
            markdown_text)
        markdown_text = re.sub(r"(?m)^\s*---+\s*$", r"<hr>", markdown_text)
        markdown_text = re.sub(
            r"@([a-zA-Z]+)@(.+?)@end@",
            r'<span style="color:\1;">\2</span>',
            markdown_text
        )
        markdown_text = re.sub(
            r"@(#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}))@(.+?)@end@",
            r'<span style="color:\1;">\2</span>',
            markdown_text
        )

        try:
            html_output = markdown.markdown(
                markdown_text,
                extensions=["extra", "sane_lists", "nl2br", "smarty", "fenced_code"]
            )

            def blockquote_replace(match):
                content = match.group(1)
                return (
                    '<blockquote>'
                    '<div style="color:#7A7A73; border-left:4px solid #bbb; margin:0.5em 0; '
                    'padding:0.5em 0.8em 0.5em 0.5em;"><span style="font-size:1em;">&#9632; </span>'
                    f'<i>{content}</i></div></blockquote>'
                )

            html_output = re.sub(
                r"<blockquote>(.*?)</blockquote>",
                blockquote_replace,
                html_output,
                flags=re.DOTALL
            )
        except Exception as e:
            html_output = f"<span style=\'color:red\'>Parsing error: {e}</span>"
        self.preview.set_html(html_output)

    def _debounced_update_preview(self, event=None):
        if self._update_job is not None:
            self.after_cancel(self._update_job)
        self._update_job = self.after(180, self.update_preview)  # 180ms задержка

    # ----- Copy features -----
    def copy_markdown(self):
        markdown_text = self.text_input.get("1.0", "end").strip()
        self.clipboard_clear()
        self.clipboard_append(markdown_text)
        messagebox.showinfo("Copied", "Markdown has been copied to the clipboard.")

    def copy_html(self):
        markdown_text = self.text_input.get("1.0", "end").strip()
        try:
            html_output = markdown.markdown(
                markdown_text,
                extensions=["extra", "sane_lists", "nl2br", "smarty", "fenced_code"]
            )
            self.clipboard_clear()
            self.clipboard_append(html_output)
            messagebox.showinfo("Copied", "The HTML has been copied to the clipboard.")
        except Exception as e:
            messagebox.showerror("Error", f"Couldn't convert Markdown to HTML: {e}")

    @staticmethod
    def hint_copy():
        messagebox.showinfo(
            "Copying from the preview",
            "Выделите нужный текст мышкой в предпросмотре и нажмите Ctrl+C.\n"
            "For the original markdown, use the «Copy Markdown» button."
        )

    # ----- Theme & Font -----
    def toggle_theme(self):
        current = ctk.get_appearance_mode()
        if current == "Light":
            ctk.set_appearance_mode("Dark")
            self.theme_btn.configure(text="Turn on the Light theme")
        else:
            ctk.set_appearance_mode("Light")
            self.theme_btn.configure(text="Turn on the Dark Theme")

    def change_font_size(self):
        sizes = [15, 17, 20]
        idx = sizes.index(self.fontsize) if self.fontsize in sizes else 1
        self.fontsize = sizes[(idx + 1) % len(sizes)]
        self.text_input.configure(font=ctk.CTkFont(family="Consolas", size=self.fontsize))
        messagebox.showinfo("Font Size", f"The font is now{self.fontsize} pt")

    # ----- About -----
    @staticmethod
    def show_about():
        messagebox.showinfo(
            "About the program",
            "Doctus\n"
            "• preview HTML\n"
            "• copy Markdown or HTML\n"
            "• auto-save and open files\n"
            "• change theme, change font\n\n"
            "2025, Python + CustomTkinter + tkhtmlview"
        )

    def _cut(self):
        try:
            sel = self.text_input.get("sel.first", "sel.last")
            self.clipboard_clear()
            self.clipboard_append(sel)
            self.text_input.delete("sel.first", "sel.last")
        except Exception:
            pass

    def _copy(self):
        try:
            sel = self.text_input.get("sel.first", "sel.last")
            self.clipboard_clear()
            self.clipboard_append(sel)
        except Exception:
            pass

    def _paste(self):
        try:
            text = self.clipboard_get()
            self.text_input.insert("insert", text)
        except Exception:
            pass

    def _select_all(self):
        self.text_input.tag_add("sel", "1.0", "end")
        self.text_input.focus()


app = MarkdownEditorApp()
app.mainloop()
