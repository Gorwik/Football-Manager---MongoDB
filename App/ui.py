from .abstract_controller import PlayerControllerABC, ClubControllerABC
from .models import PlayersSimpliefied, PlayerSpecific, Club

from PyQt6.QtWidgets import (
    QApplication,
    QStackedWidget,
    QComboBox,
    QFrame,
    QToolBar,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QTableWidget,
    QFormLayout,
    QTableWidgetItem,
)
from PyQt6.QtGui import QAction


class MainWindow(QMainWindow):
    def __init__(
        self, player_controller: PlayerControllerABC, club_controller: ClubControllerABC
    ):
        super().__init__()
        self.player_controller = player_controller
        self.club_controller = club_controller
        self.clubs_dict = self.club_controller.get_clubs_dict()
        self.players_app = PlayersView(self, player_controller)
        self.display_player_app = DisplayPlayerApp(self, player_controller)
        self.create_player_app = CreatePlayerApp(self, player_controller)
        self.clubs_app = ClubsView(self, club_controller)
        self.display_club_app = DisplayClubApp(self, club_controller)
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Footbal Database")
        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.addWidget(self.players_app)
        self.stacked_widget.addWidget(self.display_player_app)
        self.stacked_widget.addWidget(self.create_player_app)
        self.stacked_widget.addWidget(self.clubs_app)
        self.stacked_widget.addWidget(self.display_club_app)
        self.setCentralWidget(self.stacked_widget)
        self.stacked_widget.setCurrentWidget(self.players_app)

        toolbar = QToolBar()
        self.addToolBar(toolbar)

        action1 = QAction("Search Players", self)
        action1.triggered.connect(self.serach_players)
        toolbar.addAction(action1)

        action2 = QAction("Search Clubs", self)
        action2.triggered.connect(self.search_clubs)
        toolbar.addAction(action2)

        action3 = QAction("Add Player", self)
        action3.triggered.connect(self.create_player)
        toolbar.addAction(action3)

    def more_data_from_players_app(self, player_id):
        self.stacked_widget.setCurrentWidget(self.display_player_app)
        self.display_player_app.player_specific = (
            self.player_controller.find_choosen_object(player_id)
        )
        self.display_player_app.display()

    def serach_players(self):
        self.stacked_widget.setCurrentWidget(self.players_app)

    def create_player(self):
        self.stacked_widget.setCurrentWidget(self.create_player_app)

    def search_clubs(self):
        self.stacked_widget.setCurrentWidget(self.clubs_app)

    def more_data_from_clubs_app(self, club_id):
        self.stacked_widget.setCurrentWidget(self.display_club_app)
        (
            self.display_club_app.club,
            self.display_club_app.leagues_names,
            self.display_club_app.players_names,
        ) = self.club_controller.find_choosen_object(club_id)
        self.display_club_app.display()

    def update_clubs(self):
        self.clubs_dict = self.club_controller.get_clubs_dict()


class PlayersView(QWidget):
    def __init__(self, parent, player_controller: PlayerControllerABC):
        super().__init__(parent)
        self.player_controller = player_controller
        self.players_simpliefied: list[PlayersSimpliefied]
        self.actual_clicked_player_row: int = None
        self.actual_page: int = 0
        self.fields_for_searching: dict()

        self.setWindowTitle("Player App")

        self._setup_ui()

    def _setup_ui(self):

        layout = QHBoxLayout()

        self.setLayout(layout)

        form_layout = QFormLayout()

        self.first_name_edit = QLineEdit()
        self.last_name_edit = QLineEdit()
        self.country_edit = QLineEdit()
        self.height_min_spin = QSpinBox()
        self.height_min_spin.setMaximum(250)
        self.height_max_spin = QSpinBox()
        self.height_max_spin.setMaximum(250)
        self.weight_min_spin = QSpinBox()
        self.weight_min_spin.setMaximum(150)
        self.weight_max_spin = QSpinBox()
        self.weight_max_spin.setMaximum(150)
        self.pref_pos_combo = QComboBox()
        self.value_min_spin = QSpinBox()
        self.value_min_spin.setMaximum(2_147_483_647)
        self.value_max_spin = QSpinBox()
        self.value_max_spin.setMaximum(2_147_483_647)
        self.wage_min_spin = QSpinBox()
        self.wage_min_spin.setMaximum(2_147_483_647)
        self.wage_max_spin = QSpinBox()
        self.wage_max_spin.setMaximum(2_147_483_647)
        self.pref_foot_combo = QComboBox()

        self.pref_pos_combo.addItems(
            [
                "",
                "RW",
                "LCM",
                "LS",
                "LCB",
                "ST",
                "GK",
                "RS",
                "CDM",
                "SUB",
                "RCB",
                "LB",
                "LDM",
                "CAM",
                "RAM",
                "LW",
                "LAM",
                "CM",
                "RM",
                "LM",
                "RES",
                "RB",
                "RDM",
                "RCM",
                "LWB",
                "LF",
                "CB",
                "RWB",
                "RF",
                "CF",
            ]
        )
        self.pref_foot_combo.addItems(["", "Left", "Right"])

        self.pref_pos_combo.setEditable(True)

        form_layout.addRow("First Name:", self.first_name_edit)
        form_layout.addRow("Last Name:", self.last_name_edit)
        form_layout.addRow("Country:", self.country_edit)
        form_layout.addRow("Height Min:", self.height_min_spin)
        form_layout.addRow("Height Max:", self.height_max_spin)
        form_layout.addRow("Weight Min:", self.weight_min_spin)
        form_layout.addRow("Weight Max:", self.weight_max_spin)
        form_layout.addRow("Preferred Position:", self.pref_pos_combo)
        form_layout.addRow("Value Min:", self.value_min_spin)
        form_layout.addRow("Value Max:", self.value_max_spin)
        form_layout.addRow("Wage Min:", self.wage_min_spin)
        form_layout.addRow("Wage Max:", self.wage_max_spin)
        form_layout.addRow("Preferred Foot:", self.pref_foot_combo)

        search_button = QPushButton("Search")
        search_button.clicked.connect(self._search)
        form_layout.addWidget(search_button)

        layout.addLayout(form_layout)

        self.players_table = QTableWidget()
        self.players_table.setColumnCount(5)
        self.players_table.setHorizontalHeaderLabels(
            ["First Name", "Last Name", "Date of Birth", "Country", "Overall"]
        )
        self.players_table.clicked.connect(self._on_cell_clicked)

        more_data_button = QPushButton("More Data")
        more_data_button.clicked.connect(self._more_data)
        previous_page_button = QPushButton("Previous")
        previous_page_button.clicked.connect(self._dec_page)
        next_page_button = QPushButton("Next")
        next_page_button.clicked.connect(self._inc_page)

        buttons_layout = QHBoxLayout()

        buttons_layout.addWidget(more_data_button)
        buttons_layout.addWidget(previous_page_button)
        buttons_layout.addWidget(next_page_button)

        table_buttons_layout = QVBoxLayout()

        table_buttons_layout.addWidget(self.players_table)
        table_buttons_layout.addLayout(buttons_layout)

        layout.addLayout(table_buttons_layout)

    def _inc_page(self):
        if self.players_table.rowCount():
            self.actual_page += 1
            self._search()

    def _dec_page(self):
        if self.actual_page:
            self.actual_page -= 1
            self._search()

    def _on_cell_clicked(self, item):
        self.actual_clicked_player_row = item.row()

    def _search(self):
        self.players_simpliefied = self._search_players()
        self._display_players()

    def _search_players(self):
        self.fields_for_searching = {
            "first_name": self.first_name_edit.text(),
            "last_name": self.last_name_edit.text(),
            "country": self.country_edit.text(),
            "height_min": self.height_min_spin.value(),
            "height_max": self.height_max_spin.value(),
            "weight_min": self.weight_min_spin.value(),
            "weight_max": self.weight_max_spin.value(),
            "pref_pos": self.pref_pos_combo.currentText(),
            "value_min": self.value_min_spin.value(),
            "value_max": self.value_max_spin.value(),
            "wage_min": self.wage_min_spin.value(),
            "wage_max": self.wage_max_spin.value(),
            "pref_foot": self.pref_foot_combo.currentText(),
            "page": self.actual_page,
        }
        return self.player_controller.find_objects_fit_to_data(
            self.fields_for_searching
        )

    def _display_players(self):
        self.players_table.clearContents()
        self.players_table.setRowCount(len(self.players_simpliefied))

        for row, player in enumerate(self.players_simpliefied):
            # ["First Name", "Last Name", "Date of Birth", "Country", "Overall"]
            self.players_table.setItem(row, 0, QTableWidgetItem(player.first_name))
            self.players_table.setItem(row, 1, QTableWidgetItem(player.last_name))
            self.players_table.setItem(
                row, 2, QTableWidgetItem(player.date_of_birth.strftime("%d-%m-%Y"))
            )
            self.players_table.setItem(row, 3, QTableWidgetItem(player.country))
            self.players_table.setItem(row, 4, QTableWidgetItem(str(player.overall)))

    def _more_data(self):
        if not self.actual_clicked_player_row == None:
            self.parent().parent().more_data_from_players_app(
                self.players_simpliefied[self.actual_clicked_player_row].id
            )


class PlayerView(QWidget):
    def __init__(self, parent, player_controller: PlayerControllerABC):
        super().__init__(parent)
        self.player_controller = player_controller
        self.player_specific: PlayerSpecific
        self.PLAYER_PARAM: tuple
        self.STATS_PARAM = (
            "season",
            "club_name",
            "goals",
            "assists",
            "min_on_a_pitch",
            "yellow_cards",
            "red_cards",
            "kit_number",
        )
        self.actual_clicked_table = {"table_type": None, "row": None}
        self._setup_ui()

    def _setup_ui(self):

        self.player_table = QTableWidget()
        self.player_table.setRowCount(1)
        self.player_table.setVerticalHeaderLabels(["Player"])
        self.player_table.clicked.connect(self._on_cell_clicked)

        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(8)
        self.stats_table.setRowCount(10)
        self.stats_table.setHorizontalHeaderLabels(
            [
                "Season",
                "Club",
                "Goals",
                "Assists",
                "Min On a Pitch",
                "Yellow cards",
                "Red Cards",
                "Kit Number",
            ]
        )
        self.stats_table.clicked.connect(self._on_cell_clicked)

        self.clubs_combo_boxes = [QComboBox() for _ in range(11)]

        for combo_box in self.clubs_combo_boxes:
            combo_box.addItems([""] + list(self.parent().clubs_dict.values()))
            combo_box.setEditable(True)
            combo_box.setCurrentIndex(0)

        for row in range(10):
            self.stats_table.setCellWidget(row, 1, self.clubs_combo_boxes[row + 1])

        self.information_note = QLabel(parent=self)
        self.information_note.setWordWrap(True)

        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.player_table)
        self.vbox.addWidget(self.stats_table)
        self.vbox.addWidget(self.information_note)
        self.vbox.addLayout(self.hbox)

        self.vbox.setStretchFactor(self.player_table, 1)
        self.vbox.setStretchFactor(self.stats_table, 3)
        self.vbox.setStretchFactor(self.information_note, 2)

        self.setLayout(self.vbox)

    def _print_information(self, information):
        self.information_note.setText(information)

    def _get_player_and_seasons_from_table(self):
        player = dict()
        for column, key in enumerate(self.PLAYER_PARAM):
            if key == "club_name":
                cell_widget = self.player_table.cellWidget(0, column)
                player[key] = cell_widget.currentText() if cell_widget else None
                continue
            if not (item := self.player_table.item(0, column)):
                player[key] = None
                continue
            player[key] = item.text() if not item.text() == "" else None

        seasons = []
        for row in range(self.stats_table.rowCount()):
            season = dict()
            for column, key in enumerate(self.STATS_PARAM):
                if key == "club_name":
                    cell_widget = self.stats_table.cellWidget(row, column)
                    season[key] = cell_widget.currentText() if cell_widget else None
                    continue
                if not (item := self.stats_table.item(row, column)):
                    season[key] = None
                    continue
                season[key] = item.text() if not item.text() == "" else None
            seasons.append(season)

        return player, seasons

    def _on_cell_clicked(self, item):
        sender_table = self.sender()
        if sender_table == self.player_table:
            self.actual_clicked_table["table_type"] = "player"
        else:
            self.actual_clicked_table["table_type"] = "stats"
        self.actual_clicked_table["row"] = item.row()


class DisplayPlayerApp(PlayerView):
    def __init__(self, parent, player_controller: PlayerControllerABC):
        super().__init__(parent, player_controller)
        self.PLAYER_PARAM = (
            "first_name",
            "last_name",
            "date_of_birth",
            "age",
            "country",
            "club_name",
            "height",
            "weight",
            "pref_pos",
            "pref_foot",
            "value",
            "wage",
            "overall",
        )

    def _setup_ui(self):
        super()._setup_ui()

        self.player_table.setColumnCount(13)
        self.player_table.setHorizontalHeaderLabels(
            [
                "First Name",
                "Last Name",
                "Date of Birth",
                "Age",
                "Country",
                "Club",
                "Height",
                "Weight",
                "Pref Pos",
                "Pref Foot",
                "Value",
                "Wage",
                "Overall",
            ]
        )
        self.player_table.setCellWidget(0, 5, self.clubs_combo_boxes[0])

        update_button = QPushButton("Update")
        update_button.clicked.connect(self._update_player)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self._delete_player)

        go_to_club_button = QPushButton("Go to club")
        go_to_club_button.clicked.connect(self._go_to_club)

        go_back_to_search = QPushButton("Go back to search")
        go_back_to_search.clicked.connect(self.parent().serach_players)

        self.hbox.addWidget(go_to_club_button)
        self.hbox.addWidget(go_back_to_search)
        self.hbox.addWidget(update_button)
        self.hbox.addWidget(delete_button)

    def _display_player(
        self,
    ):
        player = self.player_specific.dict(exclude_none=True, exclude_unset=True)
        self.player_table.setItem(0, 0, QTableWidgetItem(player["first_name"]))
        self.player_table.setItem(0, 1, QTableWidgetItem(player["last_name"]))
        self.player_table.setItem(
            0, 2, QTableWidgetItem(player["date_of_birth"].strftime("%d-%m-%Y"))
        )
        self.player_table.setItem(0, 3, QTableWidgetItem(str(player.get("age", ""))))
        self.player_table.setItem(0, 4, QTableWidgetItem(player["country"]))
        self.clubs_combo_boxes[0].setCurrentText(player.get("club_name", ""))
        self.player_table.setItem(0, 6, QTableWidgetItem(str(player.get("height", ""))))
        self.player_table.setItem(0, 7, QTableWidgetItem(str(player.get("weight", ""))))
        self.player_table.setItem(
            0,
            8,
            QTableWidgetItem(
                self.player_specific.pref_pos.name
                if self.player_specific.pref_pos
                else ""
            ),
        )
        self.player_table.setItem(
            0,
            9,
            QTableWidgetItem(
                self.player_specific.pref_foot.name
                if self.player_specific.pref_foot
                else ""
            ),
        )
        self.player_table.setItem(0, 10, QTableWidgetItem(str(player.get("value", ""))))
        self.player_table.setItem(0, 11, QTableWidgetItem(str(player.get("wage", ""))))
        self.player_table.setItem(
            0, 12, QTableWidgetItem(str(player.get("overall", "")))
        )

    def _display_stats(self):
        if stats := self.player_specific.stats:
            for row, season in enumerate(stats):
                self.stats_table.setItem(
                    row, 0, QTableWidgetItem(str(season.get("season", "")))
                )
                self.clubs_combo_boxes[row + 1].setCurrentText(
                    season.get("club_name", "")
                )
                self.stats_table.setItem(
                    row, 2, QTableWidgetItem(str(season.get("goals", "")))
                )
                self.stats_table.setItem(
                    row, 3, QTableWidgetItem(str(season.get("assists", "")))
                )
                self.stats_table.setItem(
                    row, 4, QTableWidgetItem(str(season.get("min_on_a_pitch", "")))
                )
                self.stats_table.setItem(
                    row, 5, QTableWidgetItem(str(season.get("yellow_cards", "")))
                )
                self.stats_table.setItem(
                    row, 6, QTableWidgetItem(str(season.get("red_cards", "")))
                )
                self.stats_table.setItem(
                    row, 7, QTableWidgetItem(str(season.get("kit_number", "")))
                )
        else:
            row = -1

        for row in range(row + 1, 10):
            for column in range(8):
                if column == 1:
                    self.clubs_combo_boxes[row + 1].setCurrentIndex(0)
                    continue
                self.stats_table.setItem(row, column, QTableWidgetItem())

    def display(self):
        self._display_player()
        self._display_stats()

    def _update_player(self):
        player, seasons = self._get_player_and_seasons_from_table()
        try:
            self.player_controller.update_object(player, seasons, self.player_specific)
            self._print_information("Palyer has been updated successfully")
        except Exception as e:
            self._print_information(str(e))
        finally:
            self.player_specific = self.player_controller.find_choosen_object(
                self.player_specific.id
            )
            self.display()

    def _delete_player(self):
        self.player_controller.delete_object(
            self.player_specific.id,
            " ".join((self.player_specific.first_name, self.player_specific.last_name)),
        )
        self._print_information("Player has been deleted")

    def _go_to_club(self):
        if not (table_type := self.actual_clicked_table["table_type"]) or not (
            row := self.actual_clicked_table["row"]
        ):
            return
        if table_type == "player":
            club_name = self.clubs_combo_boxes[0].currentText()
        else:
            club_name = self.clubs_combo_boxes[row + 1].currentText()
        if not club_name:
            return
        club_id = [
            i
            for i in self.parent().parent().clubs_dict
            if self.parent().parent().clubs_dict[i] == club_name
        ][0]
        self.parent().parent().more_data_from_clubs_app(club_id)


class CreatePlayerApp(PlayerView):

    def __init__(self, parent, player_controller: PlayerControllerABC):
        super().__init__(parent, player_controller)
        self.PLAYER_PARAM = (
            "first_name",
            "last_name",
            "date_of_birth",
            "country",
            "club_name",
            "height",
            "weight",
            "pref_pos",
            "pref_foot",
            "value",
            "wage",
            "overall",
        )
        self._print_information("Add new player")

    def _setup_ui(self):
        super()._setup_ui()

        self.player_table.setColumnCount(12)
        self.player_table.setHorizontalHeaderLabels(
            [
                "First Name",
                "Last Name",
                "Date of Birth",
                "Country",
                "Club",
                "Height",
                "Weight",
                "Pref Pos",
                "Pref Foot",
                "Value",
                "Wage",
                "Overall",
            ]
        )

        self.player_table.setCellWidget(0, 4, self.clubs_combo_boxes[0])

        add_player = QPushButton("Add Player")
        add_player.clicked.connect(self._add_player)
        self.hbox.addWidget(add_player)

    def _add_player(self):

        player, seasons = self._get_player_and_seasons_from_table()
        information = self.player_controller.add_object(player, seasons)
        self._print_information(information)


class ClubsView(QWidget):
    def __init__(self, parent, club_controller: ClubControllerABC):
        super().__init__(parent)
        self.club_controller = club_controller
        self.clubs: list[Club]
        self.actual_clicked_club_row: int = None
        self.actual_page: int = 0
        self.fields_for_searching: dict()

        self.setWindowTitle("Clubs App")

        self._setup_ui()

    def _setup_ui(self):

        layout = QHBoxLayout()

        self.setLayout(layout)

        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.country_edit = QLineEdit()

        form_layout.addRow("Name:", self.name_edit)
        form_layout.addRow("Country:", self.country_edit)

        search_button = QPushButton("Search")
        search_button.clicked.connect(self._search)
        form_layout.addWidget(search_button)

        layout.addLayout(form_layout)

        self.clubs_table = QTableWidget()
        self.clubs_table.setColumnCount(2)
        self.clubs_table.setHorizontalHeaderLabels(
            [
                "Name",
                "Country",
            ]
        )
        self.clubs_table.clicked.connect(self._on_cell_clicked)

        more_data_button = QPushButton("More Data")
        more_data_button.clicked.connect(self._more_data)
        previous_page_button = QPushButton("Previous")
        previous_page_button.clicked.connect(self._dec_page)
        next_page_button = QPushButton("Next")
        next_page_button.clicked.connect(self._inc_page)

        buttons_layout = QHBoxLayout()

        buttons_layout.addWidget(more_data_button)
        buttons_layout.addWidget(previous_page_button)
        buttons_layout.addWidget(next_page_button)

        table_buttons_layout = QVBoxLayout()

        table_buttons_layout.addWidget(self.clubs_table)
        table_buttons_layout.addLayout(buttons_layout)

        layout.addLayout(table_buttons_layout)

    def _inc_page(self):
        if self.clubs_table.rowCount():
            self.actual_page += 1
            self._search()

    def _dec_page(self):
        if self.actual_page:
            self.actual_page -= 1
            self._search()

    def _on_cell_clicked(self, item):
        self.actual_clicked_club_row = item.row()

    def _search(self):
        self.clubs = self._search_clubs()
        self._display_clubs()

    def _search_clubs(self):
        self.fields_for_searching = {
            "name": self.name_edit.text(),
            "country": self.country_edit.text(),
            "page": self.actual_page,
        }
        return self.club_controller.find_objects_fit_to_data(self.fields_for_searching)

    def _display_clubs(self):
        self.clubs_table.clearContents()
        self.clubs_table.setRowCount(len(self.clubs))

        for row, club in enumerate(self.clubs):
            ["First Name", "Last Name", "Date of Birth", "Country", "Overall"]
            self.clubs_table.setItem(row, 0, QTableWidgetItem(club.name))
            self.clubs_table.setItem(row, 1, QTableWidgetItem(club.country))

    def _more_data(self):
        if not self.actual_clicked_club_row == None:
            self.parent().parent().more_data_from_clubs_app(
                self.clubs[self.actual_clicked_club_row].id
            )


class DisplayClubApp(QWidget):
    def __init__(self, parent, club_controller: ClubControllerABC):
        super().__init__(parent)
        self.club_controller = club_controller
        self.club: Club
        self.leagues_names: dict
        self.players_names: dict
        self.stats_page: int = 0
        self.actual_clicked_names: str = None

        self.setup()

    def setup(self):
        self.club_table = QTableWidget()
        self.club_table.setColumnCount(2)
        self.club_table.setRowCount(1)
        self.club_table.setVerticalHeaderLabels(["Club"])
        self.club_table.setHorizontalHeaderLabels(
            [
                "Name",
                "Country",
            ]
        )

        self.go_to_player = QPushButton("Go to Player")
        self.go_to_player.clicked.connect(self._go_to_player)

        self.go_back_to_search = QPushButton("Go Back to Search")
        self.go_back_to_search.clicked.connect(self.parent().search_clubs)

        self.previous_seasons = QPushButton("Previous seasons")
        self.previous_seasons.clicked.connect(self._dec_page)

        self.next_seasons = QPushButton("Next seasons")
        self.next_seasons.clicked.connect(self._inc_page)

        self.information_note = QLabel(parent=self)
        self.information_note.setWordWrap(True)

        self.main_layout = QVBoxLayout()
        self.stats_layout = QVBoxLayout()
        self.buttons_layout = QHBoxLayout()
        self.main_layout.addWidget(self.club_table)
        self.main_layout.addLayout(self.stats_layout)
        self.main_layout.addWidget(self.information_note)
        self.main_layout.addLayout(self.buttons_layout)

        self.buttons_layout.addWidget(self.go_to_player)
        self.buttons_layout.addWidget(self.go_back_to_search)
        self.buttons_layout.addWidget(self.previous_seasons)
        self.buttons_layout.addWidget(self.next_seasons)

        self.main_layout.setStretchFactor(self.club_table, 1)
        self.main_layout.setStretchFactor(self.stats_layout, 4)
        self.main_layout.setStretchFactor(self.information_note, 1)

        self.setLayout(self.main_layout)

    def display(self):
        self._display_club()
        self._display_stats_club()

    def _display_club(self):
        self.club_table.clearContents()
        self.stats_page = 0
        self.club_table.setItem(0, 0, QTableWidgetItem(self.club.name))
        self.club_table.setItem(0, 1, QTableWidgetItem(self.club.country))

    def _display_stats_club(self):
        self._clear_layout(self.stats_layout)
        for season in self.club.seasons[self.stats_page : self.stats_page + 3]:

            season_layout = QVBoxLayout()
            season_table = QTableWidget()
            self._set_season_table(season_table, season)
            season_layout.addWidget(season_table)

            if players := season.get("players").get("head"):
                head_table = QTableWidget()
                head_table.clicked.connect(self._on_cell_clicked)

                season_layout.addWidget(head_table)
                self._set_players_table(head_table, players, "Head")

            if players := season.get("players").get("substitute"):
                substitute_table = QTableWidget()
                substitute_table.clicked.connect(self._on_cell_clicked)

                season_layout.addWidget(substitute_table)
                self._set_players_table(substitute_table, players, "Substitute")

            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)

            self.stats_layout.addLayout(season_layout)
            self.stats_layout.addWidget(line)

    def _set_season_table(self, season_table, season):
        LABELS = ["Season", "League", "Points", "Won Titles", "Coach"]
        season_table.setRowCount(1)
        season_table.setColumnCount(len(LABELS))
        season_table.setHorizontalHeaderLabels(LABELS)
        season_table.setItem(0, 0, QTableWidgetItem(str(season.get("season"))))
        season_table.setItem(
            0, 1, QTableWidgetItem(self.leagues_names.get(season.get("league")))
        )
        season_table.setItem(0, 2, QTableWidgetItem(str(season.get("points"))))
        season_table.setItem(0, 3, QTableWidgetItem(str(season.get("won_titles"))))
        season_table.setItem(0, 4, QTableWidgetItem(season.get("coach")))

    def _set_players_table(self, table: QTableWidget, players: dict, label: str):
        table.setRowCount(1)
        table.setVerticalHeaderLabels([label])
        table.setColumnCount(len(players))
        for column, player in enumerate(players):
            table.setItem(
                0, column, QTableWidgetItem(self.players_names.get(player, player))
            )

    def _go_to_player(self):
        if not self.actual_clicked_names:
            return
        if not (
            player_id := [
                i
                for i in self.players_names
                if self.players_names[i] == self.actual_clicked_names
            ]
        ):
            self._print_information("Player no longer exists in the database.")
            return
        self.parent().parent().more_data_from_players_app(player_id[0])

    def _print_information(self, information):
        self.information_note.setText(information)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.layout():
                sub_layout = item.layout()
                while sub_layout.count():
                    sub_item = sub_layout.takeAt(0)
                    widget_item = sub_item.widget()
                    if widget_item:
                        widget_item.setParent(None)
                    else:
                        layout_item = sub_item.layout()
                        if layout_item:
                            while layout_item.count():
                                inner_item = layout_item.takeAt(0)
                                inner_widget_item = inner_item.widget()
                                if inner_widget_item:
                                    inner_widget_item.setParent(None)
                        sub_item.setParent(None)
            else:
                widget_item = item.widget()
                if widget_item:
                    widget_item.setParent(None)

    def _inc_page(self):
        if len(self.club.seasons) / 3 > self.stats_page + 1:
            self.stats_page += 1
            self._display_stats_club()

    def _dec_page(self):
        if self.stats_page > 0:
            self.stats_page -= 1
            self._display_stats_club()

    def _on_cell_clicked(self, index):
        sender_table = self.sender()
        if index.isValid():
            text = sender_table.item(index.row(), index.column()).text()
            self.actual_clicked_names = text
