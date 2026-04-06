import tkinter as tk
from tkinter import font as tkfont
import random

# --- UI CONFIGURATION (DO NOT MODIFY COLORS/OFFSETS) ---
BG          = "#C8A97A"
PANEL_DARK  = "#1B6B8A"
PANEL_MID   = "#1E8FB5"
BLUE_CARD   = "#2D6DA8"
PINK_CARD   = "#D94F7E"
RECORD_CARD = "#E8E4D0"
TEAL_DOT    = "#1EC6C6"
GRAY_DOT    = "#5A5A6A"
WHITE       = "#FFFFFF"
RED_VS      = "#CC2222"
TEXT_DARK   = "#1A1A2E"
GREEN       = "#1FAA55"
RED_LOSE    = "#B03040"
SEL_BG      = "#0D3F55"

CHOICES = ["Rock", "Paper", "Scissors"]
EMOJI   = {"Rock": "✊", "Paper": "🖐", "Scissors": "✌️"}

# Animation rhythm
SHAKE_OFFSETS = [0,-22,0,22,0,-18,0,18,0,-13,0,13,0,-8,0,8,0,-4,0,4,0,0]
SHAKE_MS      = 50
W             = 700

class RockPaperScissors(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Rock · Paper · Scissors")
        self.resizable(False, False)
        self.configure(bg=BG)

        self._init_fonts()
        self._init_game_state()
        self._build_main_ui()
        
        # Start the flow by showing the round selection overlay
        self.show_round_selection()

    def _init_fonts(self):
        """Initialize all font styles used in the application."""
        self.f_big   = tkfont.Font(family="Segoe UI", size=48, weight="bold")
        self.f_mid   = tkfont.Font(family="Segoe UI", size=20, weight="bold")
        self.f_sm    = tkfont.Font(family="Segoe UI", size=13)
        self.f_xs    = tkfont.Font(family="Segoe UI", size=11)
        self.f_btn   = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        self.f_vs    = tkfont.Font(family="Impact",   size=36, weight="bold")
        self.f_bar   = tkfont.Font(family="Segoe UI", size=13, weight="bold")
        self.f_sel   = tkfont.Font(family="Segoe UI", size=22, weight="bold")
        self.f_info  = tkfont.Font(family="Segoe UI", size=11)

    def _init_game_state(self):
        """Set up persistent and session-based variables."""
        # Lifetime stats
        self.total_matches_won = 0
        self.all_time_best     = 0

        # Current match state
        self.max_rounds     = 3
        self.user_score     = 0
        self.cpu_score      = 0
        self.current_round  = 0
        self.session_points = 0
        
        # Animation & UI tracking
        self.game_phase     = "select"  # select, choose, animating, result, gameover
        self.pending_moves  = {"user": None, "cpu": None}
        self.shake_index    = 0

    # --- UI CONSTRUCTION ---

    def _build_main_ui(self):
        """Constructs the base layout of the game window."""
        tk.Frame(self, bg=BG, height=12).pack(fill="x")

        # Top Info Bar
        info_container = tk.Frame(self, bg=TEXT_DARK, width=W, height=30)
        info_container.pack(padx=20)
        info_container.pack_propagate(False)
        self.info_label = tk.Label(info_container, text="", font=self.f_info, bg=TEXT_DARK, fg="#AAD8EE")
        self.info_label.place(relx=0.5, rely=0.5, anchor="center")

        # Central Battle Arena
        self.battle_panel = tk.Frame(self, bg=PANEL_DARK, width=W, height=175)
        self.battle_panel.pack(padx=20)
        self.battle_panel.pack_propagate(False)

        self.canvas = tk.Canvas(self.battle_panel, bg=PANEL_DARK, width=W, height=175, highlightthickness=0)
        self.canvas.pack()

        # Visual Elements: Fists and VS text
        self.user_fist = tk.Label(self.canvas, text="✊", font=self.f_big, bg=PANEL_DARK, fg=WHITE)
        self.user_fist_id = self.canvas.create_window(115, 82, window=self.user_fist, anchor="center")

        vs_label = tk.Label(self.canvas, text="VS", font=self.f_vs, bg=PANEL_DARK, fg=RED_VS)
        self.canvas.create_window(W // 2, 80, window=vs_label, anchor="center")

        self.cpu_fist = tk.Label(self.canvas, text="✊", font=self.f_big, bg=PANEL_DARK, fg=WHITE)
        self.cpu_fist_id = self.canvas.create_window(W - 115, 82, window=self.cpu_fist, anchor="center")

        # Choice Sub-labels (e.g., "Rock", "Paper")
        self.user_choice_text = tk.Label(self.canvas, text="", font=self.f_xs, bg=PANEL_DARK, fg="#AAD8EE")
        self.canvas.create_window(115, 152, window=self.user_choice_text, anchor="center")

        self.cpu_choice_text = tk.Label(self.canvas, text="", font=self.f_xs, bg=PANEL_DARK, fg="#AAD8EE")
        self.canvas.create_window(W - 115, 152, window=self.cpu_choice_text, anchor="center")

        self.base_fist_y = 82

        # Status Notification Bar
        self.status_bar = tk.Frame(self, bg=PANEL_MID, width=W, height=38)
        self.status_bar.pack(padx=20)
        self.status_bar.pack_propagate(False)
        self.status_text = tk.StringVar(value="")
        self.status_label = tk.Label(self.status_bar, textvariable=self.status_text, font=self.f_bar, bg=PANEL_MID, fg=WHITE)
        self.status_label.place(relx=0.5, rely=0.5, anchor="center")

        # Score and Record Section
        score_row = tk.Frame(self, bg=BG)
        score_row.pack(padx=20, pady=10, fill="x")

        # Left: User Card
        user_card = tk.Frame(score_row, bg=BLUE_CARD, width=162, height=115)
        user_card.pack(side="left", padx=(0, 6))
        user_card.pack_propagate(False)
        tk.Label(user_card, text="You", font=self.f_mid, bg=BLUE_CARD, fg=WHITE).place(relx=0.5, rely=0.25, anchor="center")
        self.user_dot_container = tk.Frame(user_card, bg=BLUE_CARD)
        self.user_dot_container.place(relx=0.5, rely=0.72, anchor="center")

        # Center: Record Card
        record_card = tk.Frame(score_row, bg=RECORD_CARD, width=240, height=115)
        record_card.pack(side="left", padx=4)
        record_card.pack_propagate(False)
        tk.Label(record_card, text="Record:", font=self.f_sm, bg=RECORD_CARD, fg=TEXT_DARK, anchor="w").place(x=16, y=8)
        self.rec_won_label = tk.Label(record_card, text="Matches Won: 0", font=self.f_xs, bg=RECORD_CARD, fg=TEXT_DARK, anchor="w")
        self.rec_won_label.place(x=16, y=36)
        self.rec_score_label = tk.Label(record_card, text="Score: 0", font=self.f_xs, bg=RECORD_CARD, fg=TEXT_DARK, anchor="w")
        self.rec_score_label.place(x=16, y=60)
        self.rec_best_label = tk.Label(record_card, text="Your Best Score: 0", font=self.f_xs, bg=RECORD_CARD, fg=TEXT_DARK, anchor="w")
        self.rec_best_label.place(x=16, y=84)

        # Right: CPU Card
        cpu_card = tk.Frame(score_row, bg=PINK_CARD, width=162, height=115)
        cpu_card.pack(side="left", padx=(6, 0))
        cpu_card.pack_propagate(False)
        tk.Label(cpu_card, text="CPU", font=self.f_mid, bg=PINK_CARD, fg=WHITE).place(relx=0.5, rely=0.25, anchor="center")
        self.cpu_dot_container = tk.Frame(cpu_card, bg=PINK_CARD)
        self.cpu_dot_container.place(relx=0.5, rely=0.72, anchor="center")

        # Action Buttons
        button_row = tk.Frame(self, bg=BG)
        button_row.pack(pady=(2, 16))
        self.choice_buttons = []
        for choice in CHOICES:
            btn = tk.Button(button_row, text=f"{EMOJI[choice]}\n{choice}", font=self.f_btn, width=6, height=2,
                            bg=PANEL_DARK, fg=WHITE, activebackground=PANEL_MID, activeforeground=WHITE,
                            relief="flat", cursor="hand2", disabledforeground="#607080",
                            command=lambda c=choice: self.handle_user_choice(c))
            btn.pack(side="left", padx=12)
            btn.bind("<Enter>", lambda e, w=btn: w.config(bg=PANEL_MID) if str(w["state"]) == "normal" else None)
            btn.bind("<Leave>", lambda e, w=btn: w.config(bg=PANEL_DARK) if str(w["state"]) == "normal" else None)
            self.choice_buttons.append(btn)

        self.refresh_score_dots()

    # --- GAME FLOW CONTROL ---

    def show_round_selection(self):
        """Displays the round selection overlay."""
        self.game_phase = "select"
        self.reset_battle_ui()
        self.toggle_buttons("disabled")
        self.update_status_bar("Pick a round count to begin!", PANEL_MID)

        self.selection_overlay = tk.Frame(self.battle_panel, bg=SEL_BG)
        self.selection_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        tk.Label(self.selection_overlay, text="🎮  Choose Number of Rounds", font=self.f_mid, bg=SEL_BG, fg=WHITE).pack(pady=(22, 12))
        btn_row = tk.Frame(self.selection_overlay, bg=SEL_BG)
        btn_row.pack()

        for rounds in (3, 5, 7):
            b = tk.Button(btn_row, text=str(rounds), font=self.f_sel, width=3, bg=PANEL_MID, fg=WHITE,
                          activebackground=TEAL_DOT, activeforeground=WHITE, relief="flat", cursor="hand2",
                          command=lambda r=rounds: self.start_new_match(r))
            b.pack(side="left", padx=16)
            b.bind("<Enter>", lambda e, w=b: w.config(bg=TEAL_DOT))
            b.bind("<Leave>", lambda e, w=b: w.config(bg=PANEL_MID))

        tk.Label(self.selection_overlay, text="First to win majority of rounds wins the match",
                 font=self.f_xs, bg=SEL_BG, fg="#AAD8EE").pack(pady=(10, 0))

    def start_new_match(self, rounds):
        """Initializes a match with the selected number of rounds."""
        self.max_rounds     = rounds
        self.user_score     = 0
        self.cpu_score      = 0
        self.current_round  = 0
        self.session_points = 0

        if hasattr(self, "selection_overlay"):
            self.selection_overlay.destroy()

        self.refresh_score_dots()
        self.sync_info_text()
        self.advance_to_next_round()

    def advance_to_next_round(self):
        """Prepares the UI for the user to make a move."""
        self.status_bar.unbind("<Button-1>")
        self.status_label.unbind("<Button-1>")
        self.reset_battle_ui()
        self.update_status_bar("Choose your move!", PANEL_MID)
        self.game_phase = "choose"
        self.toggle_buttons("normal")

    def handle_user_choice(self, choice):
        """Triggered when user clicks an RPS button."""
        if self.game_phase != "choose":
            return
        self.toggle_buttons("disabled")
        self.run_battle_animation(choice, random.choice(CHOICES))

    # --- ANIMATION & LOGIC ---

    def run_battle_animation(self, user_ch, cpu_ch):
        """Starts the 'Rock... Paper... Scissors' shaking animation."""
        self.game_phase = "animating"
        self.pending_moves = {"user": user_ch, "cpu": cpu_ch}
        self.shake_index = 0

        self.user_fist.config(text="✊", fg=WHITE)
        self.cpu_fist.config(text="✊", fg=WHITE)
        self.user_choice_text.config(text="")
        self.cpu_choice_text.config(text="")
        self.update_status_bar("🤜  Rock … Paper … Scissors …  🤛", PANEL_MID)

        self._process_animation_frame()

    def _process_animation_frame(self):
        """Handles each frame of the vertical fist shake."""
        if self.shake_index >= len(SHAKE_OFFSETS):
            self.reveal_battle_result()
            return

        offset = SHAKE_OFFSETS[self.shake_index]
        self.canvas.coords(self.user_fist_id, 115, self.base_fist_y + offset)
        self.canvas.coords(self.cpu_fist_id, W - 115, self.base_fist_y + offset)
        self.shake_index += 1
        self.after(SHAKE_MS, self._process_animation_frame)

    def reveal_battle_result(self):
        """Reveals choices and updates scores after animation ends."""
        user_move = self.pending_moves["user"]
        cpu_move = self.pending_moves["cpu"]

        self.user_fist.config(text=EMOJI[user_move])
        self.cpu_fist.config(text=EMOJI[cpu_move])
        self.user_choice_text.config(text=user_move)
        self.cpu_choice_text.config(text=cpu_move)

        outcome = self.calculate_winner(user_move, cpu_move)
        points_to_win = (self.max_rounds // 2) + 1

        if outcome == "win":
            self.user_score += 1
            self.session_points += 10
            self.update_status_bar("🎉  You Win this round!  — click to continue", GREEN)
        elif outcome == "lose":
            self.cpu_score += 1
            self.session_points -= 5
            self.update_status_bar("🤖  CPU wins this round!  — click to continue", RED_LOSE)
        else:
            self.session_points += 2
            self.update_status_bar("🤝  It's a Tie!  — click to continue", PANEL_MID)

        self.current_round += 1
        self.refresh_score_dots()
        self.sync_info_text()
        self.update_record_display()

        is_match_over = self.user_score >= points_to_win or self.cpu_score >= points_to_win
        is_last_round = self.current_round >= self.max_rounds

        if is_match_over or is_last_round:
            self.game_phase = "gameover"
            msg = "🏆  You won the match!" if self.user_score > self.cpu_score else "😢  CPU won the match!"
            if self.user_score > self.cpu_score:
                self.total_matches_won += 1
                self.update_record_display()
            self.after(700, lambda: self.show_final_results(msg))
        else:
            self.game_phase = "result"
            # Click the bar to continue
            self.status_bar.bind("<Button-1>", lambda e: self.advance_to_next_round())
            self.status_label.bind("<Button-1>", lambda e: self.advance_to_next_round())

    @staticmethod
    def calculate_winner(u, c):
        """Determines result of a single throw."""
        if u == c: return "tie"
        winning_map = {"Rock": "Scissors", "Scissors": "Paper", "Paper": "Rock"}
        return "win" if winning_map[u] == c else "lose"

    # --- UI HELPERS ---

    def refresh_score_dots(self):
        """Redraws the win indicators for both players."""
        for container in (self.user_dot_container, self.cpu_dot_container):
            for child in container.winfo_children():
                child.destroy()

        required_wins = (self.max_rounds // 2) + 1

        def create_dot(parent, active):
            c = tk.Canvas(parent, width=20, height=20, bg=parent["bg"], highlightthickness=0)
            c.pack(side="left", padx=2)
            c.create_oval(2, 2, 18, 18, fill=TEAL_DOT if active else GRAY_DOT, outline="")

        for i in range(required_wins):
            create_dot(self.user_dot_container, i < self.user_score)
            create_dot(self.cpu_dot_container, i < self.cpu_score)

    def sync_info_text(self):
        """Updates the top info string."""
        needed = (self.max_rounds // 2) + 1
        text = (f"Best of {self.max_rounds}  ·  Round {self.current_round}/{self.max_rounds}  ·  "
                f"You {self.user_score} – {self.cpu_score} CPU  ·  First to {needed} wins")
        self.info_label.config(text=text)

    def update_status_bar(self, text, color):
        """Updates the feedback bar text and background color."""
        self.status_text.set(text)
        self.status_bar.config(bg=color)
        self.status_label.config(bg=color)

    def toggle_buttons(self, state):
        """Enables or disables game buttons."""
        for b in self.choice_buttons:
            b.config(state=state, bg=PANEL_DARK if state == "normal" else "#14506A")

    def update_record_display(self):
        """Refreshes the record card labels."""
        if self.session_points > self.all_time_best:
            self.all_time_best = self.session_points
        self.rec_won_label.config(text=f"Matches Won: {self.total_matches_won}")
        self.rec_score_label.config(text=f"Score: {self.session_points}")
        self.rec_best_label.config(text=f"Your Best Score: {self.all_time_best}")

    def reset_battle_ui(self):
        """Resets fists to neutral position and neutral icon."""
        self.user_fist.config(text="✊")
        self.cpu_fist.config(text="✊")
        self.user_choice_text.config(text="")
        self.cpu_choice_text.config(text="")
        self.canvas.coords(self.user_fist_id, 115, self.base_fist_y)
        self.canvas.coords(self.cpu_fist_id, W - 115, self.base_fist_y)

    def show_final_results(self, message):
        """Creates a popup window at the end of a match."""
        popup = tk.Toplevel(self)
        popup.title("Match Over")
        popup.resizable(False, False)
        popup.configure(bg=TEXT_DARK)
        popup.grab_set()

        f_title = tkfont.Font(family="Segoe UI", size=24, weight="bold")
        f_body  = tkfont.Font(family="Segoe UI", size=13)
        f_pbtn  = tkfont.Font(family="Segoe UI", size=14, weight="bold")

        tk.Label(popup, text=message, font=f_title, bg=TEXT_DARK, fg=WHITE, pady=24, padx=50).pack()

        stats = (f"Best of {self.max_rounds}  ·  First to {(self.max_rounds // 2) + 1} wins\n"
                 f"Final score  :  You {self.user_score}  –  {self.cpu_score}  CPU\n"
                 f"Match score  :  {self.session_points} pts\n"
                 f"Matches won  :  {self.total_matches_won}\n"
                 f"Best score   :  {self.all_time_best} pts")
        tk.Label(popup, text=stats, font=f_body, bg=TEXT_DARK, fg="#AAD8EE", justify="left", padx=50, pady=6).pack()

        btn_frame = tk.Frame(popup, bg=TEXT_DARK, pady=18)
        btn_frame.pack()

        tk.Button(btn_frame, text="▶  Play Again", font=f_pbtn, bg=GREEN, fg=WHITE, relief="flat",
                  padx=20, pady=8, cursor="hand2", 
                  command=lambda: [popup.destroy(), self.refresh_score_dots(), self.show_round_selection()]).pack(side="left", padx=14)

        tk.Button(btn_frame, text="✕  Quit", font=f_pbtn, bg=RED_LOSE, fg=WHITE, relief="flat",
                  padx=20, pady=8, cursor="hand2", command=self.destroy).pack(side="left", padx=14)

        # Center popup on parent
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width()  - popup.winfo_reqwidth())  // 2
        y = self.winfo_y() + (self.winfo_height() - popup.winfo_reqheight()) // 2
        popup.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    game = RockPaperScissors()
    game.mainloop()