
import customtkinter as ctk
import sqlite3
from datetime import datetime


# ============================================================
# APPLICATION SETTINGS
# ============================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ============================================================
# COLORS
# ============================================================

BG_COLOR = "#080C14"
PANEL_COLOR = "#101722"
CARD_COLOR = "#151E2D"
BOARD_COLOR = "#0C1320"

TEXT_COLOR = "#F8FAFC"
MUTED_COLOR = "#64748B"

X_COLOR = "#60A5FA"
X_BG = "#172554"

O_COLOR = "#F472B6"
O_BG = "#3B1229"

WIN_COLOR = "#22C55E"
WIN_BG = "#14532D"

BORDER_COLOR = "#263449"


# ============================================================
# DATABASE
# ============================================================

class Database:

    def __init__(self):

        self.connection = sqlite3.connect(
            "tic_tac_toe.db"
        )

        self.cursor = self.connection.cursor()

        self.create_tables()


    def create_tables(self):

        # Player statistics

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                draws INTEGER DEFAULT 0
            )
        """)

        # Individual match records

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_x TEXT NOT NULL,
                player_o TEXT NOT NULL,
                winner TEXT,
                result TEXT NOT NULL,
                played_at TEXT NOT NULL
            )
        """)

        self.connection.commit()


    def add_player(self, name):

        self.cursor.execute(
            """
            INSERT OR IGNORE INTO players (name)
            VALUES (?)
            """,
            (name,)
        )

        self.connection.commit()


    def get_player_stats(self, name):

        self.cursor.execute(
            """
            SELECT wins, losses, draws
            FROM players
            WHERE name = ?
            """,
            (name,)
        )

        return self.cursor.fetchone()


    def update_win(self, winner, loser):

        self.cursor.execute(
            """
            UPDATE players
            SET wins = wins + 1
            WHERE name = ?
            """,
            (winner,)
        )

        self.cursor.execute(
            """
            UPDATE players
            SET losses = losses + 1
            WHERE name = ?
            """,
            (loser,)
        )

        self.connection.commit()


    def update_draw(self, player_x, player_o):

        self.cursor.execute(
            """
            UPDATE players
            SET draws = draws + 1
            WHERE name IN (?, ?)
            """,
            (player_x, player_o)
        )

        self.connection.commit()


    def save_match(
        self,
        player_x,
        player_o,
        winner,
        result
    ):

        self.cursor.execute(
            """
            INSERT INTO matches
            (
                player_x,
                player_o,
                winner,
                result,
                played_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                player_x,
                player_o,
                winner,
                result,
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )
        )

        self.connection.commit()


    def get_recent_matches(self, limit=20):

        self.cursor.execute(
            """
            SELECT
                player_x,
                player_o,
                winner,
                result,
                played_at
            FROM matches
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        )

        return self.cursor.fetchall()


    def close(self):

        self.connection.close()


# ============================================================
# TIC TAC TOE APPLICATION
# ============================================================

class TicTacToeApp(ctk.CTk):

    def __init__(self):

        super().__init__()

        # ----------------------------------------------------
        # WINDOW
        # ----------------------------------------------------

        self.title("Tic-Tac-Toe")

        self.geometry("1100x720")

        self.minsize(
            950,
            650
        )

        self.configure(
            fg_color=BG_COLOR
        )


        # ----------------------------------------------------
        # DATABASE
        # ----------------------------------------------------

        self.database = Database()


        # ----------------------------------------------------
        # GAME STATE
        # ----------------------------------------------------

        self.board = [""] * 9

        self.current_symbol = "X"

        self.game_over = False

        self.player_x = "Player X"

        self.player_o = "Player O"

        self.buttons = []


        # ----------------------------------------------------
        # CREATE UI
        # ----------------------------------------------------

        self.create_ui()

        self.protocol(
            "WM_DELETE_WINDOW",
            self.close_application
        )


    # ========================================================
    # CREATE USER INTERFACE
    # ========================================================

    def create_ui(self):

        # Main container

        self.main = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.main.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=25
        )


        # ====================================================
        # HEADER
        # ====================================================

        header = ctk.CTkFrame(
            self.main,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            pady=(0, 20)
        )


        ctk.CTkLabel(
            header,
            text="TIC-TAC-TOE",
            font=ctk.CTkFont(
                family="Arial",
                size=34,
                weight="bold"
            ),
            text_color=TEXT_COLOR
        ).pack(
            side="left"
        )


        ctk.CTkLabel(
            header,
            text="CLASSIC • TWO PLAYER • LOCAL",
            font=ctk.CTkFont(
                family="Arial",
                size=12,
                weight="bold"
            ),
            text_color=MUTED_COLOR
        ).pack(
            side="left",
            padx=18,
            pady=(10, 0)
        )


        # ====================================================
        # MAIN CONTENT
        # ====================================================

        content = ctk.CTkFrame(
            self.main,
            fg_color="transparent"
        )

        content.pack(
            fill="both",
            expand=True
        )


        # ====================================================
        # LEFT SIDEBAR
        # ====================================================

        sidebar = ctk.CTkFrame(
            content,
            width=285,
            corner_radius=20,
            fg_color=PANEL_COLOR
        )

        sidebar.pack(
            side="left",
            fill="y",
            padx=(0, 20)
        )

        sidebar.pack_propagate(False)


        # ----------------------------------------------------
        # PLAYER SETUP
        # ----------------------------------------------------

        ctk.CTkLabel(
            sidebar,
            text="PLAYER SETUP",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color=MUTED_COLOR
        ).pack(
            anchor="w",
            padx=25,
            pady=(25, 12)
        )


        # Player X

        self.player_x_entry = ctk.CTkEntry(
            sidebar,
            height=45,
            corner_radius=10,
            placeholder_text="Player X"
        )

        self.player_x_entry.pack(
            fill="x",
            padx=25,
            pady=6
        )

        self.player_x_entry.insert(
            0,
            "Player X"
        )


        # Player O

        self.player_o_entry = ctk.CTkEntry(
            sidebar,
            height=45,
            corner_radius=10,
            placeholder_text="Player O"
        )

        self.player_o_entry.pack(
            fill="x",
            padx=25,
            pady=6
        )

        self.player_o_entry.insert(
            0,
            "Player O"
        )


        # Start game

        ctk.CTkButton(
            sidebar,
            text="START NEW GAME",
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            command=self.start_game
        ).pack(
            fill="x",
            padx=25,
            pady=(12, 25)
        )


        # ====================================================
        # SCOREBOARD
        # ====================================================

        ctk.CTkLabel(
            sidebar,
            text="SCOREBOARD",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color=MUTED_COLOR
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 10)
        )


        score_card = ctk.CTkFrame(
            sidebar,
            fg_color=BOARD_COLOR,
            corner_radius=15
        )

        score_card.pack(
            fill="x",
            padx=20
        )


        # X score

        x_score_container = ctk.CTkFrame(
            score_card,
            fg_color="transparent"
        )

        x_score_container.pack(
            side="left",
            expand=True,
            pady=15
        )


        ctk.CTkLabel(
            x_score_container,
            text="X",
            font=ctk.CTkFont(
                size=15,
                weight="bold"
            ),
            text_color=X_COLOR
        ).pack()


        self.score_x_label = ctk.CTkLabel(
            x_score_container,
            text="0",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            )
        )

        self.score_x_label.pack()


        # O score

        o_score_container = ctk.CTkFrame(
            score_card,
            fg_color="transparent"
        )

        o_score_container.pack(
            side="right",
            expand=True,
            pady=15
        )


        ctk.CTkLabel(
            o_score_container,
            text="O",
            font=ctk.CTkFont(
                size=15,
                weight="bold"
            ),
            text_color=O_COLOR
        ).pack()


        self.score_o_label = ctk.CTkLabel(
            o_score_container,
            text="0",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            )
        )

        self.score_o_label.pack()


        # ====================================================
        # SIDEBAR ACTIONS
        # ====================================================

        ctk.CTkButton(
            sidebar,
            text="MATCH HISTORY",
            height=42,
            corner_radius=10,
            fg_color=CARD_COLOR,
            hover_color="#253248",
            command=self.show_history
        ).pack(
            fill="x",
            padx=25,
            pady=(25, 7)
        )


        ctk.CTkButton(
            sidebar,
            text="RESET BOARD",
            height=42,
            corner_radius=10,
            fg_color=CARD_COLOR,
            hover_color="#253248",
            command=self.reset_board
        ).pack(
            fill="x",
            padx=25,
            pady=7
        )


        # ====================================================
        # GAME PANEL
        # ====================================================

        game_panel = ctk.CTkFrame(
            content,
            corner_radius=20,
            fg_color=PANEL_COLOR
        )

        game_panel.pack(
            side="left",
            fill="both",
            expand=True
        )


        # ----------------------------------------------------
        # TURN
        # ----------------------------------------------------

        self.turn_label = ctk.CTkLabel(
            game_panel,
            text="Player X's Turn",
            font=ctk.CTkFont(
                size=23,
                weight="bold"
            ),
            text_color=X_COLOR
        )

        self.turn_label.pack(
            pady=(25, 4)
        )


        self.status_label = ctk.CTkLabel(
            game_panel,
            text="Choose a cell to make your move",
            font=ctk.CTkFont(
                size=13
            ),
            text_color=MUTED_COLOR
        )

        self.status_label.pack(
            pady=(0, 20)
        )


        # ====================================================
        # BOARD
        # ====================================================

        self.board_frame = ctk.CTkFrame(
            game_panel,
            fg_color=BOARD_COLOR,
            corner_radius=22
        )

        self.board_frame.pack(
            padx=40,
            pady=5
        )


        for index in range(9):

            button = ctk.CTkButton(
                self.board_frame,

                text="",

                width=130,

                height=105,

                corner_radius=15,

                fg_color=CARD_COLOR,

                hover_color="#1E293B",

                border_width=1,

                border_color=BORDER_COLOR,

                font=ctk.CTkFont(
                    family="Arial",
                    size=42,
                    weight="bold"
                ),

                command=lambda i=index:
                    self.make_move(i)
            )

            button.grid(
                row=index // 3,
                column=index % 3,
                padx=7,
                pady=7
            )

            self.buttons.append(button)


        # ====================================================
        # RESULT
        # ====================================================

        self.result_label = ctk.CTkLabel(
            game_panel,
            text="",
            font=ctk.CTkFont(
                size=19,
                weight="bold"
            )
        )

        self.result_label.pack(
            pady=20
        )


    # ========================================================
    # START GAME
    # ========================================================

    def start_game(self):

        x_name = self.player_x_entry.get().strip()

        o_name = self.player_o_entry.get().strip()


        if not x_name:

            x_name = "Player X"


        if not o_name:

            o_name = "Player O"


        self.player_x = x_name

        self.player_o = o_name


        self.database.add_player(
            self.player_x
        )

        self.database.add_player(
            self.player_o
        )


        self.reset_board()

        self.update_scores()


    # ========================================================
    # RESET BOARD
    # ========================================================

    def reset_board(self):

        self.board = [""] * 9

        self.current_symbol = "X"

        self.game_over = False


        self.turn_label.configure(
            text=f"{self.player_x}'s Turn",
            text_color=X_COLOR
        )


        self.status_label.configure(
            text="Choose a cell to make your move"
        )


        self.result_label.configure(
            text=""
        )


        for button in self.buttons:

            button.configure(
                text="",
                state="normal",
                fg_color=CARD_COLOR,
                hover_color="#1E293B",
                text_color=TEXT_COLOR,
                border_color=BORDER_COLOR,
                border_width=1
            )


    # ========================================================
    # MAKE MOVE
    # ========================================================

    def make_move(self, index):

        if self.game_over:

            return


        if self.board[index] != "":

            return


        self.board[index] = self.current_symbol


        button = self.buttons[index]


        if self.current_symbol == "X":

            button.configure(
                text="X",
                text_color=X_COLOR,
                fg_color=X_BG,
                hover_color="#1E3A8A"
            )

        else:

            button.configure(
                text="O",
                text_color=O_COLOR,
                fg_color=O_BG,
                hover_color="#4A1635"
            )


        button.configure(
            state="disabled"
        )


        result = self.check_winner()


        if result:

            self.end_game(result)

            return


        self.switch_turn()


    # ========================================================
    # SWITCH PLAYER
    # ========================================================

    def switch_turn(self):

        if self.current_symbol == "X":

            self.current_symbol = "O"

            self.turn_label.configure(
                text=f"{self.player_o}'s Turn",
                text_color=O_COLOR
            )

        else:

            self.current_symbol = "X"

            self.turn_label.configure(
                text=f"{self.player_x}'s Turn",
                text_color=X_COLOR
            )


    # ========================================================
    # CHECK WINNER
    # ========================================================

    def check_winner(self):

        winning_patterns = [

            (0, 1, 2),

            (3, 4, 5),

            (6, 7, 8),

            (0, 3, 6),

            (1, 4, 7),

            (2, 5, 8),

            (0, 4, 8),

            (2, 4, 6)

        ]


        for a, b, c in winning_patterns:

            if (
                self.board[a] != ""
                and
                self.board[a]
                == self.board[b]
                == self.board[c]
            ):

                self.highlight_winner(
                    [a, b, c]
                )

                return self.board[a]


        if "" not in self.board:

            return "DRAW"


        return None


    # ========================================================
    # HIGHLIGHT WINNER
    # ========================================================

    def highlight_winner(self, cells):

        for index in cells:

            self.buttons[index].configure(
                fg_color=WIN_BG,
                hover_color=WIN_BG,
                border_color=WIN_COLOR,
                border_width=2
            )


    # ========================================================
    # END GAME
    # ========================================================

    def end_game(self, result):

        self.game_over = True


        for button in self.buttons:

            button.configure(
                state="disabled"
            )


        # ----------------------------------------------------
        # DRAW
        # ----------------------------------------------------

        if result == "DRAW":

            self.turn_label.configure(
                text="GAME OVER",
                text_color="#FBBF24"
            )


            self.status_label.configure(
                text="Nobody wins this round."
            )


            self.result_label.configure(
                text="DRAW GAME",
                text_color="#FBBF24"
            )


            self.database.update_draw(
                self.player_x,
                self.player_o
            )


            self.database.save_match(
                self.player_x,
                self.player_o,
                None,
                "DRAW"
            )


        # ----------------------------------------------------
        # WIN
        # ----------------------------------------------------

        else:

            if result == "X":

                winner = self.player_x

                loser = self.player_o

            else:

                winner = self.player_o

                loser = self.player_x


            self.turn_label.configure(
                text="GAME OVER",
                text_color=WIN_COLOR
            )


            self.status_label.configure(
                text="Congratulations!"
            )


            self.result_label.configure(
                text=f"🏆 {winner} WINS!",
                text_color=WIN_COLOR
            )


            self.database.update_win(
                winner,
                loser
            )


            self.database.save_match(
                self.player_x,
                self.player_o,
                winner,
                "WIN"
            )


        self.update_scores()


    # ========================================================
    # UPDATE SCORES
    # ========================================================

    def update_scores(self):

        x_stats = self.database.get_player_stats(
            self.player_x
        )

        o_stats = self.database.get_player_stats(
            self.player_o
        )


        if x_stats:

            self.score_x_label.configure(
                text=str(x_stats[0])
            )


        if o_stats:

            self.score_o_label.configure(
                text=str(o_stats[0])
            )


    # ========================================================
    # MATCH HISTORY
    # ========================================================

    def show_history(self):

        history_window = ctk.CTkToplevel(
            self
        )

        history_window.title(
            "Match History"
        )

        history_window.geometry(
            "760x560"
        )

        history_window.configure(
            fg_color=BG_COLOR
        )


        # Header

        ctk.CTkLabel(
            history_window,
            text="MATCH HISTORY",
            font=ctk.CTkFont(
                size=26,
                weight="bold"
            )
        ).pack(
            pady=(25, 5)
        )


        ctk.CTkLabel(
            history_window,
            text="Your recent games",
            font=ctk.CTkFont(
                size=13
            ),
            text_color=MUTED_COLOR
        ).pack(
            pady=(0, 20)
        )


        matches = self.database.get_recent_matches()


        # No games

        if not matches:

            ctk.CTkLabel(
                history_window,
                text="No matches have been played yet.",
                text_color=MUTED_COLOR
            ).pack(
                pady=40
            )

            return


        # Scroll area

        scroll_frame = ctk.CTkScrollableFrame(
            history_window,
            fg_color=PANEL_COLOR,
            corner_radius=15
        )

        scroll_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 25)
        )


        # Match cards

        for (
            player_x,
            player_o,
            winner,
            result,
            played_at
        ) in matches:


            card = ctk.CTkFrame(
                scroll_frame,
                fg_color=CARD_COLOR,
                corner_radius=12
            )

            card.pack(
                fill="x",
                pady=6
            )


            if result == "DRAW":

                result_text = "DRAW"

                result_color = "#FBBF24"

            else:

                result_text = f"{winner} WON"

                result_color = WIN_COLOR


            # Players

            ctk.CTkLabel(
                card,
                text=f"{player_x}  X   vs   O  {player_o}",
                font=ctk.CTkFont(
                    size=14,
                    weight="bold"
                ),
                text_color=TEXT_COLOR
            ).pack(
                anchor="w",
                padx=18,
                pady=(12, 3)
            )


            # Result

            ctk.CTkLabel(
                card,
                text=result_text,
                font=ctk.CTkFont(
                    size=13,
                    weight="bold"
                ),
                text_color=result_color
            ).pack(
                anchor="w",
                padx=18
            )


            # Date

            ctk.CTkLabel(
                card,
                text=played_at,
                font=ctk.CTkFont(
                    size=11
                ),
                text_color=MUTED_COLOR
            ).pack(
                anchor="w",
                padx=18,
                pady=(3, 12)
            )


    # ========================================================
    # CLOSE
    # ========================================================

    def close_application(self):

        self.database.close()

        self.destroy()


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    app = TicTacToeApp()

    app.mainloop()

