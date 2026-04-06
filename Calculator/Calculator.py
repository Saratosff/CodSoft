import tkinter as tk
from tkinter import font
import os
from PIL import Image, ImageTk


class AndroidCalculator:

    def __init__(self):
        # setting up the main window (nothing fancy, just works)
        self.root = tk.Tk()
        self.root.title("Calculator")
        self.root.geometry("380x680")
        self.root.resizable(False, False)
        self.root.configure(bg="#202124")

        # try loading icon (honestly sometimes I forget to keep the file in place)
        self.set_window_icon()

        # keeping track of numbers and operations
        self.prev_value = None   # renamed from stored_value (feels more natural to me)
        self.current_op = None
        self.should_reset = False   # flag to clear entry on next input

        self._build_ui()
        self._bind_keys()

        self.root.mainloop()

    def set_window_icon(self):
        """Attempt to set window icon from a PNG file."""
        icon_path = "calcupu.png"

        # quick existence check (no point crashing over an icon)
        if os.path.exists(icon_path):
            try:
                img = Image.open(icon_path)
                self.icon_img = ImageTk.PhotoImage(img)

                # delay a bit, tkinter sometimes acts weird if set immediately
                self.root.after(200, lambda: self.root.iconphoto(False, self.icon_img))
            except Exception as e:
                print("Icon load failed:", e)
        else:
            print("Icon not found, skipping...")  # not critical anyway

    def _validate_input(self, P):
        # basic validation (not super strict, just avoids obvious issues)
        if P == "" or P == "-":
            return True
        try:
            float(P)
            return True
        except ValueError:
            return False

    def _bind_keys(self):
        # keyboard shortcuts (still feels incomplete, maybe add more later)
        self.root.bind("<Return>", lambda e: self._calculate())
        self.root.bind("<KP_Enter>", lambda e: self._calculate())

        self.root.bind("<BackSpace>", lambda e: self._clear_entry())
        self.root.bind("<Escape>", lambda e: self._all_clear())

        # mapping keys to display symbols
        op_map = {"+": "+", "-": "−", "*": "×", "/": "÷"}

        for key, disp in op_map.items():
            # using default arg trick (I always forget this otherwise)
            self.root.bind(key, lambda e, d=disp: self._handle_button(d))

    def _build_ui(self):
        # fonts (Roboto might not exist everywhere but looks nice if it does)
        self.font_main = font.Font(family="Roboto", size=40)
        self.font_expr = font.Font(family="Roboto", size=14)
        self.font_num = font.Font(family="Roboto", size=20)
        self.font_op = font.Font(family="Roboto", size=18)

        vcmd = (self.root.register(self._validate_input), '%P')

        # display section
        top_frame = tk.Frame(self.root, bg="#202124", padx=20, pady=40)
        top_frame.pack(fill="x")

        self.expr_text = tk.StringVar(value="")
        tk.Label(
            top_frame,
            textvariable=self.expr_text,
            font=self.font_expr,
            bg="#202124",
            fg="#9aa0a6",
            anchor="e"
        ).pack(fill="x")

        self.entry = tk.Entry(
            top_frame,
            font=self.font_main,
            bg="#202124",
            fg="#e8eaed",
            borderwidth=0,
            highlightthickness=0,
            justify="right",
            insertbackground="#e8eaed",
            validate="key",
            validatecommand=vcmd
        )

        self.entry.insert(0, "0")
        self.entry.pack(fill="x", pady=(10, 20))
        self.entry.focus_set()

        # button area
        btn_frame = tk.Frame(self.root, bg="#202124", padx=10, pady=10)
        btn_frame.pack(expand=True, fill="both")

        # colors (hardcoded... maybe should move to config later)
        C_FUNC = "#3c4043"
        C_OP = "#ea8600"
        C_NUM = "#303134"
        FG = "#e8eaed"

        btns = [
            ("AC", C_FUNC, 0, 0), ("C", C_FUNC, 1, 0), ("%", C_FUNC, 2, 0), ("÷", C_OP, 3, 0),
            ("7", C_NUM, 0, 1), ("8", C_NUM, 1, 1), ("9", C_NUM, 2, 1), ("×", C_OP, 3, 1),
            ("4", C_NUM, 0, 2), ("5", C_NUM, 1, 2), ("6", C_NUM, 2, 2), ("−", C_OP, 3, 2),
            ("1", C_NUM, 0, 3), ("2", C_NUM, 1, 3), ("3", C_NUM, 2, 3), ("+", C_OP, 3, 3),
            ("+/-", C_NUM, 0, 4), ("0", C_NUM, 1, 4), (".", C_NUM, 2, 4), ("=", C_OP, 3, 4),
        ]

        # grid weights (so resizing works... though resizing is disabled anyway )
        for i in range(4):
            btn_frame.columnconfigure(i, weight=1)
        for i in range(5):
            btn_frame.rowconfigure(i, weight=1)

        # creating buttons using canvas (a bit overkill but looks better)
        for (text, bg, col, row) in btns:
            size = 80

            canvas = tk.Canvas(
                btn_frame,
                width=size,
                height=size,
                bg="#202124",
                highlightthickness=0,
                cursor="hand2"
            )

            canvas.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")

            canvas.create_oval(5, 5, size-5, size-5, fill=bg, outline=bg)

            canvas.create_text(
                size // 2,
                size // 2,
                text=text,
                fill=FG,
                font=self.font_num if bg == C_NUM else self.font_op
            )

            # binding click (again lambda trick...)
            canvas.tag_bind("all", "<Button-1>", lambda e, t=text: self._handle_button(t))

    def _format_number(self, val):
        # removes .0 when possible (cleaner output)
        try:
            num = float(val)
            if num == int(num):
                return int(num)
            return num
        except:
            return val  # fallback (not ideal but safe)

    def _handle_button(self, label):
        # central dispatcher (kind of messy but manageable)
        if label.isdigit() or label == ".":
            self._input(label)

        elif label == "C":
            self._clear_entry()

        elif label == "AC":
            self._all_clear()

        elif label in ["+", "−", "×", "÷"]:
            mapping = {"÷": "/", "×": "*", "−": "-", "+": "+"}
            self._set_operator(label, mapping[label])

        elif label == "=":
            self._calculate()

        elif label == "+/-":
            self._toggle_sign()

        elif label == "%":
            self._percent()

    def _input(self, char):
        current = self.entry.get()

        # overwrite if needed
        if self.should_reset or (current == "0" and char != "."):
            self.entry.delete(0, tk.END)
            self.entry.insert(0, char)
            self.should_reset = False
        else:
            self.entry.insert(tk.END, char)

    def _clear_entry(self):
        val = self.entry.get()

        # simple backspace logic
        if len(val) <= 1 or "Error" in val:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, "0")
        else:
            self.entry.delete(len(val) - 1, tk.END)

    def _all_clear(self):
        # reset everything
        self.entry.delete(0, tk.END)
        self.entry.insert(0, "0")

        self.prev_value = None
        self.current_op = None
        self.expr_text.set("")
        self.should_reset = False

    def _set_operator(self, disp_op, real_op):
        val = self.entry.get()

        if "Error" in val:
            return

        try:
            num = float(val)

            self.prev_value = num
            self.current_op = real_op

            self.expr_text.set(f"{self._format_number(num)} {disp_op}")

            self.entry.delete(0, tk.END)
            self.entry.insert(0, "0")

            self.should_reset = True

        except ValueError:
            pass  # ignore weird cases

    def _calculate(self):
        if self.current_op is None or self.prev_value is None:
            return  # nothing to do

        try:
            b = float(self.entry.get())
            a = self.prev_value

            # doing operation (could use eval, this is safer way)
            if self.current_op == "+":
                result = a + b
            elif self.current_op == "-":
                result = a - b
            elif self.current_op == "*":
                result = a * b
            elif self.current_op == "/":
                result = a / b

            self.expr_text.set(f"{self._format_number(a)} {self.current_op} {self._format_number(b)} =")

            self.entry.delete(0, tk.END)
            self.entry.insert(0, str(self._format_number(result)))

            # store result for chaining operations
            self.prev_value = result
            self.current_op = None
            self.should_reset = True

        except ZeroDivisionError:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, "Error: Div by 0")

        except Exception as e:
            # generic fallback (not super helpful but avoids crash)
            print("Calc error:", e)
            self.entry.delete(0, tk.END)
            self.entry.insert(0, "Error")

    def _toggle_sign(self):
        val = self.entry.get()

        if val == "0":
            return  # no need to negate zero

        if val.startswith("-"):
            self.entry.delete(0, 1)
        else:
            self.entry.insert(0, "-")

    def _percent(self):
        try:
            num = float(self.entry.get())
            num = num / 100  # basic percentage conversion

            self.entry.delete(0, tk.END)
            self.entry.insert(0, str(self._format_number(num)))
        except:
            pass  # ignore errors silently (maybe log later)


if __name__ == "__main__":
    # entry point
    AndroidCalculator()