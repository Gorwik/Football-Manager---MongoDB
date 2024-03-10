from .ui import *
from .player_controller import PlayerController
from .club_controller import ClubController
from .mongo_db import MongoDB
import sys


def create_app():
    mongo_db = MongoDB()
    player_controller = PlayerController(mongo_db)
    club_controller = ClubController(mongo_db)
    app = QApplication(sys.argv)
    main_app = MainWindow(player_controller, club_controller)
    main_app.show()

    app.exec()
