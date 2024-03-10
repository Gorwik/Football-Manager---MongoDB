from abc import ABC, abstractmethod

class Controller(ABC):
    @abstractmethod
    def find_objects_fit_to_data(self):
        pass

    @abstractmethod
    def find_choosen_object(self):
        pass


class PlayerControllerABC(Controller):
    @abstractmethod
    def delete_object(self):
        pass

    @abstractmethod
    def add_object(self):
        pass

    @abstractmethod
    def update_object(self):
        pass

class ClubControllerABC(Controller):
    @abstractmethod
    def get_clubs_dict(self):
        pass