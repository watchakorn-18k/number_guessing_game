import flet as ft
from flet import Theme
import random
import pyautogui
import threading
import time


# DATABASE #
import sqlite3


def create_database():
    # Connect to or create the database
    conn = sqlite3.connect("storage.db")

    # Create a cursor object
    c = conn.cursor()
    # Execute a query to create a table
    c.execute(
        """CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT, score INTEGER)"""
    )

    # Insert data into the table
    c.execute("INSERT INTO players (name, score) VALUES ('WK', 10)")
    c.execute("INSERT INTO players (name, score) VALUES ('AC', 2)")
    c.execute("INSERT INTO players (name, score) VALUES ('DW', 5)")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def qurty_database():
    conn = sqlite3.connect("storage.db")

    # Create a cursor object
    c = conn.cursor()

    # Execute a query to sort by score in descending order
    c.execute("SELECT name, score FROM players ORDER BY score DESC")

    # Fetch all the results
    results = c.fetchall()

    # Close the connection
    return results


def check_database():
    import os

    if not os.path.exists("storage.db"):
        create_database()


check_database()
# END DATABASE #


class Countdown(ft.UserControl):
    """
    ตัวจับเวลา
    """

    def __init__(self, seconds):
        super().__init__()
        self.seconds = seconds
        self.timeout = False

    def did_mount(self):
        self.running = True
        self.th = threading.Thread(target=self.update_timer, args=(), daemon=True)
        self.th.start()

    def will_unmount(self):
        self.running = False
        self.th.join()

    def update_timer(self):
        while self.running:
            self.countdown.value = f"{self.seconds} วินาที"
            self.update()
            time.sleep(1)
            if self.seconds > 0:
                self.seconds -= 1
            else:
                self.timeout = True
            if (
                self.seconds == 0
                or self.seconds == 1
                or self.seconds == 2
                or self.seconds == 3
            ):
                self.countdown.color = ft.colors.RED_ACCENT
            else:
                self.countdown.color = ft.colors.WHITE

    def build(self):
        self.countdown = ft.Text()
        return self.countdown


class GamePlay(ft.UserControl):
    """
    สำหรับเข้าสู่โหมดเล่นเกมทายเลข
    """

    def __init__(self):
        super().__init__()
        self.score_difficulty = 0
        self.score_combo = 0
        self.answer = random.randint(1, 10)
        self.clock_limit = random.randint(5, 15)
        self.iswinner = False
        self.score = 0
        self.clock = Countdown(self.clock_limit)
        self.title = ft.Text("เกมทายเลข", style="displaySmall", text_align="center")
        self.player_guess_number = ft.TextField(
            label="กรอกตัวเลขที่จะทาย",
            helper_text=f"ทิป: ตอบให้ถูกภายในเวลา {self.clock_limit} วินาที",
            on_change=self.check_empty_input,
            shift_enter=True,
            on_submit=self.check_answer,
        )
        self.send_answer = ft.ElevatedButton(
            content=ft.Text("ส่งคำตอบ", size=20),
            width=800,
            on_click=self.check_answer,
            disabled=True,
        )
        self.name_replay = ft.Text("เริ่มเล่นใหม่", size=20, color=ft.colors.WHITE)
        self.replay = ft.ElevatedButton(
            content=self.name_replay,
            width=800,
            bgcolor=ft.colors.BLUE,
        )
        self.name_back_to_main = ft.Text(
            "กลับไปยังหน้าแรก", size=20, color=ft.colors.WHITE
        )
        self.back_to_main = ft.ElevatedButton(
            content=self.name_back_to_main, width=800, bgcolor=ft.colors.RED
        )
        self.label_score = ft.Text("คะแนนของคุณคือ", size=20, text_align="center")
        self.hint_answer = ft.Text(
            "เดาให้ถูกหากคุณแน่จริง", size=25, text_align="center"
        )
        self.show_score = ft.Text(self.score, size=150, text_align="center")
        self.hint_answer = ft.Text(
            "เดาให้ถูกหากคุณแน่จริง", size=25, text_align="center"
        )

        def set_time_out(e):
            self.clock.timeout = True

        self.debug_set_time_out = ft.ElevatedButton(
            text="TIME_OUT", on_click=set_time_out
        )

    def did_mount(self):
        self.running = True
        self.th = threading.Thread(target=self.update_forever, args=(), daemon=True)
        self.th.start()

    def will_unmount(self):
        self.running = False

    def update_forever(self):

        while self.running:
            time.sleep(0.5)
            if self.clock.timeout and not self.iswinner:
                self.player_guess_number.disabled = True
                self.hint_answer.value = "หมดเวลาแล้ว\nคำตอบคือ {}".format(self.answer)
                self.send_answer.disabled = True
                self.show_score.value = self.score
                self.hint_answer.color = ft.colors.RED_ACCENT
                self.hint_answer.size = 25
                self.name_replay.value = "เริ่มเล่นใหม่"
                self.replay.disabled = True
                self.replay.opacity = 0.5
                self.update()

    def check_answer(self, e):
        """
        เช็คเงื่อนไขคำตอบจากผู้เล่น จากนั้นแสดงผลด้วยข้อความต่างๆ
        \n
        โดยตรวจสอบเงื่อนไขดังนี้:
        \n
        `น้อยไป` จะแสดงผลข้อความออกมาก็ต่อเมื่อผู้เล่นกรอกตัวเลขน้อยกว่า `self.answer`
        \n
        `มากไป` จะแสดงผลข้อความออกมาก็ต่อเมื่อผู้เล่นกรอกตัวเลขมากกว่า `self.answer`
        \n
        `WINNER` จะแสดงผลข้อความออกมาก็ต่อเมื่อผู้เล่นกรอกตัวเลข้ท่ากับ `self.answer`
        """
        try:
            player = int(self.player_guess_number.value)
            if player == self.answer:
                self.hint_answer.value = f"คุณตอบถูก \n เฉลยเลข {self.answer}"
                self.hint_answer.size = 26
                self.hint_answer.color = ft.colors.GREEN_ACCENT
                self.send_answer.disabled = True
                self.player_guess_number.disabled = True
                self.iswinner = True
                if self.score_combo == 2:
                    self.score += self.score_difficulty * 2
                else:
                    self.score += self.score_difficulty
                    self.score_combo += 1

                self.show_score.value = self.score
                self.name_replay.value = "เล่นต่อ"
            elif player < self.answer:
                self.hint_answer.value = f"เลข {self.player_guess_number.value} น้อยไป"
                self.hint_answer.color = ft.colors.RED_ACCENT
                self.hint_answer.size = 30
                self.player_guess_number.value = ""
                self.player_guess_number.focus()
                self.score_combo -= 2 if self.score_combo > 0 else 0
                self.update()
                time.sleep(0.5)
                self.hint_answer.value = ""
                self.update()
            elif player > self.answer:
                self.hint_answer.value = f"เลข {self.player_guess_number.value} มากไป"
                self.hint_answer.color = ft.colors.BLUE_ACCENT
                self.hint_answer.size = 30
                self.player_guess_number.value = ""
                self.player_guess_number.focus()
                self.score_combo -= 2 if self.score_combo > 0 else 0
                self.update()
                time.sleep(0.5)
                self.hint_answer.value = ""
                self.update()
            print(self.score_combo)
        except:
            self.hint_answer.value = "ต้องพิมพ์ตัวเลข"
            self.hint_answer.color = ft.colors.RED_ACCENT
        self.update()

    def check_empty_input(self, e):
        """
        ตรวจสอบในกรณีที่ผู้เล่นไม่ได้ออกข้อมูล หากไม่ออกข้อมูลปุ่ม `ส่งคำตอบ` ก็จะไม่แสดงผลออกมา
        """
        self.send_answer.disabled = (
            False if self.player_guess_number.value.isdigit() else True
        )
        self.update()

    def build(self):
        """
        ตั้งค่าวิดเจ็ตต่างๆแล้วส่งข้อมูลกลับไปเป็น ``List[Control]`` ของ flet
        """
        # ชุด Container
        self.section_time = ft.Container(
            content=ft.Row(
                [ft.Text("เหลือเวลาอีก"), self.clock],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.only(top=10, bottom=10),
        )
        self.section_input = ft.Container(
            content=ft.Column(
                [
                    self.title,
                    self.section_time,
                    ft.Container(
                        content=self.hint_answer,
                        padding=ft.padding.only(top=20, bottom=20),
                    ),
                    self.player_guess_number,
                    self.send_answer,
                    self.replay,
                    self.back_to_main,
                ],
                horizontal_alignment="center",
            ),
            padding=ft.padding.only(bottom=50),
        )
        self.section_result = ft.Container(
            content=ft.Column(
                [self.label_score, self.show_score],
                horizontal_alignment="center",
            ),
            alignment=ft.alignment.center,
        )
        self.debug = ft.Container(
            content=ft.Column(
                [ft.Text("DEBUG"), ft.Row([self.debug_set_time_out])],
                horizontal_alignment="center",
            )
        )
        self.section_time.alignment = ft.alignment.Alignment(-2.0, -10.5)
        self.section_result.padding = 10
        return ft.Column(
            [
                self.section_input,
                # self.debug,
                self.section_result,
            ]
        )


class MenuGame(ft.UserControl):
    def __init__(self) -> None:
        super().__init__()
        self.title = ft.Text("เกมทายเลข", size=50, text_align="center")
        self.banner_img = ft.Image(
            src=f"https://cdn.discordapp.com/attachments/585069498986397707/1054391841690226759/box_318-871209.png",
            width=100,
            height=100,
            fit=ft.ImageFit.CONTAIN,
        )
        self.btn_start = ft.ElevatedButton(
            content=ft.Text(
                "เล่นเกม",
                size=20,
            ),
            width=200,
            style=self.btn_style(ft.colors.GREEN, ft.colors.GREEN_900, 300),
            on_click=self.run_play,
        )
        self.btn_scoreboard = ft.ElevatedButton(
            content=ft.Text(
                "ตารางคะแนน",
                size=20,
            ),
            width=200,
            style=self.btn_style(ft.colors.YELLOW_800, ft.colors.YELLOW_900, 300),
        )
        self.btn_help = ft.ElevatedButton(
            content=ft.Text(
                "ช่วยเหลือ",
                size=20,
            ),
            width=200,
            style=self.btn_style(ft.colors.BLUE, ft.colors.BLUE_900, 300),
        )
        self.btn_exit = ft.ElevatedButton(
            content=ft.Text(
                "ออกเกม",
                size=20,
            ),
            width=200,
            style=self.btn_style(ft.colors.RED, ft.colors.RED_900, 300),
        )

        self.container_main = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Container(
                                    content=ft.Column(
                                        [self.title, self.banner_img],
                                        horizontal_alignment="center",
                                    ),
                                    padding=ft.padding.only(bottom=20),
                                ),
                                self.btn_start,
                                self.btn_scoreboard,
                                self.btn_help,
                                self.btn_exit,
                            ],
                            horizontal_alignment="center",
                        ),
                        alignment=ft.alignment.center,
                    )
                ]
            ),
            padding=ft.padding.symmetric(vertical=120),
        )

    def run_play(self, e):
        print(5)

    def btn_style(self, color1, color2, time):
        return ft.ButtonStyle(
            color={ft.MaterialState.DEFAULT.value: ft.colors.WHITE},
            bgcolor={
                ft.MaterialState.DEFAULT.value: color1,
                ft.MaterialState.HOVERED.value: color2,
            },
            animation_duration=time,
        )

    def build(self):
        pass


class LevelGame(ft.UserControl):
    def __init__(self) -> None:
        super().__init__()
        self.title = ft.Text("เกมทายเลข", size=50, text_align="center")
        self.banner_img = ft.Image(
            src=f"https://cdn.discordapp.com/attachments/585069498986397707/1054391841690226759/box_318-871209.png",
            width=100,
            height=100,
            fit=ft.ImageFit.CONTAIN,
        )
        self.dropdown_difficulty_select = ft.Dropdown(
            width=200,
            options=[
                ft.dropdown.Option(text="ง่าย", key=1),
                ft.dropdown.Option(text="ปานกลาง", key=2),
                ft.dropdown.Option(text="ยาก", key=3),
            ],
            autofocus=True,
            value=1,
        )
        self.btn_submit = ft.ElevatedButton(
            content=ft.Text(
                "เริ่มเล่นเกม",
                size=20,
            ),
            width=200,
            on_click=lambda e: print(self.dropdown_difficulty_select.value),
            style=self.btn_style(ft.colors.BLUE, ft.colors.BLUE_900, 300),
        )
        self.btn_back = ft.ElevatedButton(
            content=ft.Text(
                "กลับไปหน้าแรก",
                size=20,
            ),
            width=200,
            style=self.btn_style(ft.colors.RED, ft.colors.RED_900, 300),
        )

        self.container_main = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Container(
                                    content=ft.Column(
                                        [self.title, self.banner_img],
                                        horizontal_alignment="center",
                                    ),
                                    padding=ft.padding.only(bottom=20),
                                ),
                                ft.Text("ระดับความยาก"),
                                self.dropdown_difficulty_select,
                                self.btn_submit,
                                self.btn_back,
                            ],
                            horizontal_alignment="center",
                        ),
                        alignment=ft.alignment.center,
                    )
                ]
            ),
            padding=ft.padding.symmetric(vertical=120),
        )

    def btn_style(self, color1, color2, time):
        return ft.ButtonStyle(
            color={ft.MaterialState.DEFAULT.value: ft.colors.WHITE},
            bgcolor={
                ft.MaterialState.DEFAULT.value: color1,
                ft.MaterialState.HOVERED.value: color2,
            },
            animation_duration=time,
        )

    def build(self):
        pass


class HelpGame(ft.UserControl):
    """
    สำหรับเข้าสู่โหมดเล่นเกมทายเลข
    """

    def __init__(self):
        super().__init__()
        import os
        import sys

        def resource_path(relative_path):
            """Get absolute path to resource, works for dev and for PyInstaller"""
            try:
                # PyInstaller creates a temp folder and stores path in _MEIPASS
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)

        self.path_markdown = resource_path("src/how_to_play.md")
        with open(self.path_markdown, "r", encoding="utf-8") as f:
            self.filemarkdown = f.read()
        self.markdown_help = ft.Markdown(
            self.filemarkdown,
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
        )
        self.banner_img = ft.Image(
            src=f"https://cdn.discordapp.com/attachments/585069498986397707/1054391841690226759/box_318-871209.png",
            width=50,
            height=50,
            fit=ft.ImageFit.CONTAIN,
        )
        self.btn_back = ft.ElevatedButton(
            content=ft.Text(
                "กลับไปหน้าแรก",
                size=20,
            ),
            width=200,
            style=self.btn_style(ft.colors.RED, ft.colors.RED_900, 300),
        )

        self.container_main = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [self.banner_img, self.markdown_help, self.btn_back],
                            horizontal_alignment="center",
                        ),
                        alignment=ft.alignment.center,
                    )
                ]
            )
        )

    def btn_style(self, color1, color2, time):
        return ft.ButtonStyle(
            color={ft.MaterialState.DEFAULT.value: ft.colors.WHITE},
            bgcolor={
                ft.MaterialState.DEFAULT.value: color1,
                ft.MaterialState.HOVERED.value: color2,
            },
            animation_duration=time,
        )


class Score_add(ft.UserControl):
    """
    สำหรับเข้าสู่หน้าเพิ่มชื่อคะแนน
    """

    def __init__(self):
        super().__init__()
        import os
        import sys

        self.banner_img = ft.Image(
            src=f"https://cdn.discordapp.com/attachments/585069498986397707/1054391841690226759/box_318-871209.png",
            width=50,
            height=50,
            fit=ft.ImageFit.CONTAIN,
        )
        self.label_show_1 = ft.Text(
            "คะแนนของคุณคือ",
            size=25,
        )
        self.score_show_1 = ft.Text("0", size=78)
        self.content = ft.Column(
            [self.label_show_1, self.score_show_1],
            horizontal_alignment="center",
        )
        self.input_name_player = ft.TextField(
            label="กรอกชื่อผู้เล่น",
            width=200,
            max_length=10,
            max_lines=1,
            multiline=False,
            prefix_icon=ft.icons.PERSON_ADD,
        )
        self.btn_submit = ft.ElevatedButton(
            content=ft.Text(
                "ส่งชื่อลงบอร์ด",
                size=20,
            ),
            width=200,
            style=self.btn_style(ft.colors.BLUE, ft.colors.BLUE_900, 300),
        )
        self.btn_back = ft.ElevatedButton(
            content=ft.Text(
                "กลับไปหน้าแรก",
                size=20,
            ),
            width=200,
            style=self.btn_style(ft.colors.RED, ft.colors.RED_900, 300),
        )

        self.text_show = ft.Text(text_align="center")

        self.container_main = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                self.banner_img,
                                self.content,
                                self.input_name_player,
                                self.text_show,
                                self.btn_submit,
                                self.btn_back,
                            ],
                            horizontal_alignment="center",
                        ),
                        alignment=ft.alignment.center,
                    )
                ]
            )
        )

    def btn_style(self, color1, color2, time):
        return ft.ButtonStyle(
            color={ft.MaterialState.DEFAULT.value: ft.colors.WHITE},
            bgcolor={
                ft.MaterialState.DEFAULT.value: color1,
                ft.MaterialState.HOVERED.value: color2,
            },
            animation_duration=time,
        )


class Scoreboard_scene(ft.UserControl):
    """
    สำหรับเข้าสู่หน้าเพิ่มชื่อคะแนน
    """

    def __init__(self):
        super().__init__()
        import os
        import sys

        self.data_query = qurty_database()
        self.banner_img = ft.Image(
            src=f"https://cdn.discordapp.com/attachments/585069498986397707/1054391841690226759/box_318-871209.png",
            width=50,
            height=50,
            fit=ft.ImageFit.CONTAIN,
        )
        self.rank_text = ft.Text("#1", size=18, color=ft.colors.BLACK87)
        self.name_text = ft.Text("#######", size=18, color=ft.colors.BLACK87)
        self.score_text = ft.Text("50", size=18, color=ft.colors.BLACK87)
        self.rank_1_name = ft.Text(
            self.data_query[0][0], size=18, color=ft.colors.YELLOW_800
        )
        self.rank_1_score = ft.Text(
            self.data_query[0][1], size=18, color=ft.colors.YELLOW_800
        )
        self.rank_1_rank = ft.Text("#1", size=18, color=ft.colors.YELLOW_800)
        self.player_rank_first = ft.Container(
            content=ft.Row(
                [self.rank_1_rank, self.rank_1_name, self.rank_1_score],
                alignment="spaceBetween",
            ),
            bgcolor=ft.colors.WHITE,
            padding=20,
            border_radius=22,
        )

        self.list_player_rank = ft.Container(
            content=ft.Column(self.resutl_data_list_player_rank()),
            bgcolor=ft.colors.WHITE,
            padding=20,
            border_radius=22,
        )
        self.label_show_2 = ft.Text(
            "กระดานแสดงคะแนนผู้นำ",
            size=25,
        )
        self.content = ft.Column(
            [self.label_show_2, self.player_rank_first, self.list_player_rank],
            horizontal_alignment="center",
        )
        self.btn_back = ft.ElevatedButton(
            content=ft.Text(
                "กลับไปหน้าแรก",
                size=20,
            ),
            width=200,
            style=self.btn_style(ft.colors.RED, ft.colors.RED_900, 300),
        )

        self.container_main = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                self.banner_img,
                                self.content,
                                self.btn_back,
                            ],
                            horizontal_alignment="center",
                        ),
                        alignment=ft.alignment.center,
                    )
                ]
            )
        )

    def resutl_data_list_player_rank(self):
        lists = []
        self.data_query
        for index, row in enumerate(self.data_query[1:10]):
            if row[1] != max(qurty_database()):
                self.rank_text = ft.Text(
                    index + 2,
                    size=18,
                    color=ft.colors.BLACK87,
                )
                self.name_text = ft.Text(row[0], size=18, color=ft.colors.BLACK87)
                self.score_text = ft.Text(row[1], size=18, color=ft.colors.BLACK87)

            lists.append(
                ft.Row(
                    [
                        self.rank_text,
                        self.name_text,
                        self.score_text,
                    ],
                    alignment="spaceBetween",
                )
            )
            print(f"Name: , Score: {row[1]}")

        return lists

    def btn_style(self, color1, color2, time):
        return ft.ButtonStyle(
            color={ft.MaterialState.DEFAULT.value: ft.colors.WHITE},
            bgcolor={
                ft.MaterialState.DEFAULT.value: color1,
                ft.MaterialState.HOVERED.value: color2,
            },
            animation_duration=time,
        )


def main(page: ft.Page):
    viewport_width, viewport_height = pyautogui.size()
    window_width, window_height = (500, 925)
    page.window_width = window_width
    page.window_height = window_height

    def setup_center_pos_window() -> None:
        new_viewport_width, new_viewport_height = (
            viewport_width / 2,
            viewport_height / 2,
        )
        new_window_width, new_window_height = (
            window_width / 2,
            window_height / 2,
        )
        page.window_left = new_viewport_width - new_window_width
        page.window_top = new_viewport_height - new_window_height

    def go_to_levelScene(e):
        """
        change scene to level scene
        """
        page.add(level_scene_all)
        page.remove(menu_game_all)

    def go_to_help_Scene(e):
        """
        change scene to help scene
        """
        page.add(help_scene_all)
        page.remove(menu_game_all)

    def go_to_scoreboard_Scene(e):
        """
        change scene to scoreboard scene
        """
        page.remove(menu_game_all)
        page.add(scoreboard_scene_all)
        scoreboard_scene.resutl_data_list_player_rank()
        page.update()

    def go_to_score_add_Scene(e):
        """
        change scene to add score scene
        """

        def change_value_text():
            # change score show to current score
            score_add_scene.score_show_1.value = game_play.score

        change_value_text()
        page.remove(game_play)
        if game_play.score != 0:
            page.add(score_add_all)
        else:
            page.add(menu_game_all)
        page.update()

    def go_to_keep_data_to_database_then_go_2_scoreboard(e):
        game_play.score += 5 * 1
        if score_add_scene.input_name_player.value != "":
            try:
                if (
                    game_play.score != 0
                    and score_add_scene.input_name_player.value != ""
                ):
                    # Connect to or create the database
                    conn = sqlite3.connect("storage.db")

                    # Create a cursor object
                    c = conn.cursor()
                    c.execute(
                        "INSERT INTO players (name, score) VALUES (?, ?)",
                        (score_add_scene.input_name_player.value, game_play.score),
                    )
                    # Commit the changes and close the connection
                    conn.commit()
                    conn.close()
                    score_add_scene.text_show.value = "บันทึกข้อมูลเรียบร้อย"
                    score_add_scene.text_show.color = ft.colors.GREEN

                    def go_to_scoreboard(e):
                        page.remove(score_add_all)
                        page.add(scoreboard_scene_all)
                        scoreboard_scene.resutl_data_list_player_rank()
                        page.update()

                    go_to_scoreboard(e)
            except UnicodeEncodeError:
                pass
        else:
            score_add_scene.text_show.value = "กรุณากรอกชื่อ"
            score_add_scene.text_show.color = ft.colors.RED
        page.update()

    def back_to_menu_main_from_levelScene(e):
        """
        change to menu scene
        """
        page.add(menu_game_all)
        page.remove(level_scene_all)

    def back_to_menu_main_from_help_Scene(e):
        """
        change to menu scene
        """
        page.add(menu_game_all)
        page.remove(help_scene_all)

    def back_to_menu_main_from_scoreboard_Scene(e):
        """
        change to menu scene
        """
        page.add(menu_game_all)
        page.remove(scoreboard_scene_all)

        page.update()

    def back_to_menu_main_from_score_add_Scene(e):
        """
        change to menu scene
        """
        page.add(menu_game_all)
        page.remove(score_add_all)
        page.update()

    def back_to_menu_main_from_gameplay_Scene(e):
        """
        change to menu scene
        """
        page.remove(game_play)
        page.add(menu_game_all)

    def go_to_play_scene(e):
        """
        change scene to game
        """
        game_play.replay.opacity = 1
        game_play.replay.disabled = False
        game_play.score = 0
        game_play.show_score.value = 0
        modes = [
            "",
            {
                "name": "ง่าย",
                "time": 30,
                "rd_range": 10,
                "score": 1,
                "color": ft.colors.GREEN,
            },
            {
                "name": "ปานกลาง",
                "time": 20,
                "rd_range": 100,
                "score": 5,
                "color": ft.colors.ORANGE,
            },
            {
                "name": "ยาก",
                "time": 10,
                "rd_range": 100,
                "score": 10,
                "color": ft.colors.RED,
            },
        ]
        level_difficulty = level_scene.dropdown_difficulty_select.value
        data_difficulty = modes[int(level_difficulty)]

        def setup_difficulty_level():
            game_play.answer = random.randint(1, data_difficulty["rd_range"])
            print("anwser : ", game_play.answer)
            game_play.score_difficulty = data_difficulty["score"]
            game_play.clock_limit = data_difficulty["time"]
            game_play.title.value = "เกมทายเลข ({})".format(
                modes[int(level_difficulty)]["name"]
            )
            game_play.player_guess_number.helper_text = (
                "ทิป: ตอบให้ถูกภายในเวลา {} วินาที".format(data_difficulty["time"])
            )
            game_play.title.size = 25 if data_difficulty["name"] == "ปานกลาง" else 30
            game_play.title.color = data_difficulty["color"]
            game_play.clock = Countdown(game_play.clock_limit)

        def replaying_game(e):
            def check_score():
                if not game_play.iswinner:
                    game_play.answer = random.randint(1, data_difficulty["rd_range"])
                    print("anwser : ", game_play.answer)
                    game_play.score -= (
                        game_play.score_difficulty / 2 if game_play.score != 0 else 0
                    )

                    game_play.show_score.value = game_play.score

            check_score()

            if game_play.iswinner:
                game_play.answer = random.randint(1, data_difficulty["rd_range"])

                print("anwser : ", game_play.answer)
            game_play.player_guess_number.helper_text = (
                f"ทิป: ตอบให้ถูกภายในเวลา {game_play.clock_limit} วินาที"
            )
            game_play.name_replay.value = "เริ่มเล่นใหม่"
            game_play.clock.timeout = False
            game_play.player_guess_number.disabled = False
            game_play.player_guess_number.value = ""
            game_play.player_guess_number.focus()
            game_play.iswinner = False
            game_play.send_answer.disabled = False
            game_play.hint_answer.size = 25
            game_play.hint_answer.value = "เริ่มใหม่แล้ว"
            game_play.hint_answer.color = ft.colors.BLUE_ACCENT
            game_play.update()
            time.sleep(1.5)
            game_play.hint_answer.color = ft.colors.WHITE
            game_play.hint_answer.size = 25
            game_play.update()

        setup_difficulty_level()
        game_play.replay.on_click = replaying_game
        page.add(game_play)
        page.remove(level_scene_all)
        game_play.clock.seconds = game_play.clock_limit
        game_play.player_guess_number.focus()
        replaying_game(e)

    def exit_game(e):
        """
        Close App
        """
        page.window_destroy()

    # setup_center_pos_window()
    page.window_to_front()
    page.fonts = {
        "Kanit": "https://raw.githubusercontent.com/google/fonts/master/ofl/kanit/Kanit-Bold.ttf",
    }
    page.theme = Theme(font_family="Kanit")
    page.dark_theme = Theme(font_family="Kanit")
    page.padding = 100

    # Setup variable
    game_play = GamePlay()
    menu_game = MenuGame()
    level_scene = LevelGame()
    help_scene = HelpGame()
    score_add_scene = Score_add()
    scoreboard_scene = Scoreboard_scene()
    menu_game_all = menu_game.container_main
    level_scene_all = level_scene.container_main
    help_scene_all = help_scene.container_main
    score_add_all = score_add_scene.container_main
    scoreboard_scene_all = scoreboard_scene.container_main

    def run_game_normal():
        """
        Run game normal
        """

        def setup_menu_main_scene():
            """
            Setup ของหน้าเมนูหลัก
            """
            menu_game.btn_start.on_click = go_to_levelScene
            menu_game.btn_help.on_click = go_to_help_Scene
            menu_game.btn_scoreboard.on_click = go_to_scoreboard_Scene
            menu_game.btn_exit.on_click = exit_game

        def setup_menu_level_scene():
            """
            Setup ของหน้าเลือกระดับความยาก
            """
            level_scene.btn_back.on_click = back_to_menu_main_from_levelScene
            level_scene.btn_submit.on_click = go_to_play_scene

        def setup_menu_help_scene():
            """
            Setup ของหน้าช่วยเหลือ
            """
            help_scene.btn_back.on_click = back_to_menu_main_from_help_Scene
            help_scene.markdown_help.on_tap_link = lambda e: page.launch_url(e.data)

        def setup_menu_scoreboard_scene():
            """
            Setup ของหน้า scoreboard
            """
            scoreboard_scene.btn_back.on_click = back_to_menu_main_from_scoreboard_Scene

        def setup_menu_add_score_scene():
            """
            Setup ของหน้า scoreboard
            """
            score_add_scene.btn_submit.on_click = (
                go_to_keep_data_to_database_then_go_2_scoreboard
            )
            score_add_scene.btn_back.on_click = back_to_menu_main_from_score_add_Scene

        def setup_play_scene():
            """
            Setup ของหน้าเล่นเกมหลัก
            """
            game_play.back_to_main.on_click = go_to_score_add_Scene

        # /////// START SETUP ////////
        setup_menu_main_scene()
        setup_menu_level_scene()
        setup_menu_help_scene()
        setup_menu_scoreboard_scene()
        setup_menu_add_score_scene()
        setup_play_scene()
        page.update()
        # ///////////////////////////

        # test
        # page.add(score_add_all)
        # page.add(scoreboard_scene_all)

        # initial start one above all

        page.add(menu_game_all)

    run_game_normal()
    page.update()


ft.app(target=main)
