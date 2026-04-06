import customtkinter as ctk
from tkinter import messagebox
import secrets
import string
import os
from PIL import Image, ImageTk

# Setting appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class PasswordTool(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SecurePass v2.0")
        self.geometry("460x600")
        self.resizable(False, False)

        # Handle the Icon
        self.set_window_icon()

        self.grid_columnconfigure(0, weight=1)

        # UI Elements
        self.header = ctk.CTkLabel(
            self,
            text="Secure Generator",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.header.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.password_box = ctk.CTkEntry(
            self,
            placeholder_text="Click Generate...",
            height=50,
            font=("Courier", 16),
            justify="center"
        )
        self.password_box.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.options_frame.grid_columnconfigure(0, weight=1)

        self.size_text = ctk.CTkLabel(
            self.options_frame,
            text="Length: 16",
            font=ctk.CTkFont(weight="bold")
        )
        self.size_text.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="w")

        self.size_slider = ctk.CTkSlider(
            self.options_frame,
            from_=8,
            to=64,
            number_of_steps=56,
            command=self.refresh_length_text
        )
        self.size_slider.set(16)
        self.size_slider.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.lower_toggle = ctk.CTkSwitch(self.options_frame, text="Lowercase (abc)")
        self.lower_toggle.select()
        self.lower_toggle.grid(row=2, column=0, padx=20, pady=10, sticky="w")

        self.upper_toggle = ctk.CTkSwitch(self.options_frame, text="Uppercase (ABC)")
        self.upper_toggle.select()
        self.upper_toggle.grid(row=3, column=0, padx=20, pady=10, sticky="w")

        self.number_toggle = ctk.CTkSwitch(self.options_frame, text="Numbers (123)")
        self.number_toggle.select()
        self.number_toggle.grid(row=4, column=0, padx=20, pady=10, sticky="w")

        self.symbol_toggle = ctk.CTkSwitch(self.options_frame, text="Symbols (!@#)")
        self.symbol_toggle.select()
        self.symbol_toggle.grid(row=5, column=0, padx=20, pady=10, sticky="w")

        self.make_btn = ctk.CTkButton(
            self,
            text="Generate Password",
            command=self.make_password,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.make_btn.grid(row=3, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.copy_btn = ctk.CTkButton(
            self,
            text="Copy to Clipboard",
            command=self.copy_password,
            fg_color="transparent",
            border_width=2
        )
        self.copy_btn.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

    def set_window_icon(self):
        icon_path = "padlock.png"
        if os.path.exists(icon_path):
            img = Image.open(icon_path)
            self.icon_img = ImageTk.PhotoImage(img)
            # Use after to ensure the window is ready to receive the icon
            self.after(200, lambda: self.iconphoto(False, self.icon_img))
        else:
            print(f"Error: {icon_path} not found in the directory.")

    def refresh_length_text(self, current_val):
        self.size_text.configure(text=f"Length: {int(current_val)}")

    def make_password(self):
        chars = ""
        if self.lower_toggle.get(): chars += string.ascii_lowercase
        if self.upper_toggle.get(): chars += string.ascii_uppercase
        if self.number_toggle.get(): chars += string.digits
        if self.symbol_toggle.get(): chars += string.punctuation

        if not chars:
            messagebox.showwarning("Warning", "Pick at least one option first.")
            return

        pwd_len = int(self.size_slider.get())
        generated = "".join(secrets.choice(chars) for _ in range(pwd_len))

        self.password_box.delete(0, "end")
        self.password_box.insert(0, generated)

    def copy_password(self):
        current_pwd = self.password_box.get()
        if current_pwd:
            self.clipboard_clear()
            self.clipboard_append(current_pwd)
            messagebox.showinfo("Copied", "Password copied successfully!")
        else:
            messagebox.showwarning("Empty", "Nothing to copy yet.")

if __name__ == "__main__":
    window = PasswordTool()
    window.mainloop()