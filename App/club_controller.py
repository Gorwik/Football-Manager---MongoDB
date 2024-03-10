from .mongo_db import MongoDB
from .abstract_controller import ClubControllerABC
from .models import Club


class ClubController(ClubControllerABC):
    OBJECTS_PER_PAGE = 10

    def __init__(self, mongo_db: MongoDB):
        self._mongo_db = mongo_db

    def find_objects_fit_to_data(self, data_fields):
        """find clubs that fit to data given from view widget"""
        if not data_fields:
            print("Cannot get data from view widget")
            return None
        projection = {
            "id": "$_id",
            "name": True,
            "country": True,
        }
        query, page = self._parse_data_fields_send_query(data_fields)
        clubs = (
            self._mongo_db.clubs.find(query, projection)
            .skip(page * self.OBJECTS_PER_PAGE)
            .limit(self.OBJECTS_PER_PAGE)
        )

        return [Club(**club) for club in clubs]

    def _parse_data_fields_send_query(self, data_fields):
        """Func takes data from view widget's fields and
        parse them into query request"""
        query = dict()

        if name := data_fields["name"]:
            query["name"] = name
        if country := data_fields["country"]:
            query["country"] = country

        page = data_fields.get("page", 0)

        return query, page

    def find_choosen_object(self, club_id):
        """make query for choosen player"""
        aggregation = [
            {"$match": {"_id": club_id}},
            # left join by club _id
            {
                "$lookup": {
                    "from": "players",
                    "localField": "seasons.players.head",
                    "foreignField": "_id",
                    "as": "head",
                },
            },
            {
                "$lookup": {
                    "from": "players",
                    "localField": "seasons.players.substitute",
                    "foreignField": "_id",
                    "as": "substitute",
                },
            },
            {
                "$lookup": {
                    "from": "leagues",
                    "localField": "seasons.league",
                    "foreignField": "_id",
                    "as": "league_name",
                },
            },
            {
                "$project": {
                    "id": "$_id",
                    "name": True,
                    "country": True,
                    "seasons": True,
                    "head._id": True,
                    "head.first_name": True,
                    "head.last_name": True,
                    "substitute._id": True,
                    "substitute.first_name": True,
                    "substitute.last_name": True,
                    "league_name._id": True,
                    "league_name.name": True,
                }
            },
        ]
        data = self._mongo_db.clubs.aggregate(aggregation)
        club, leagues_names_by_ids, players_names_by_ids = (
            self._parse_reponse_into_club(data)
        )
        return club, leagues_names_by_ids, players_names_by_ids

    def _parse_reponse_into_club(self, data):
        data = list(data)[0]
        club = Club(
            id=data["_id"],
            country=data["country"],
            name=data["name"],
        )

        leagues_names_by_ids = dict()
        for league in data.get("league_name"):
            leagues_names_by_ids[league["_id"]] = league["name"]

        players_names_by_ids = dict()
        for head in data.get("head"):
            players_names_by_ids[head["_id"]] = (
                head["first_name"] + " " + head["last_name"]
            )

        for substitute in data.get("substitute"):
            players_names_by_ids[substitute["_id"]] = (
                substitute["first_name"] + " " + substitute["last_name"]
            )

        club.seasons = data.get("seasons")

        return club, leagues_names_by_ids, players_names_by_ids

    def get_clubs_dict(self):
        clubs_dict = dict()
        clubs_list = self._mongo_db.clubs.find({}, {"_id": True, "name": True})
        for club in clubs_list:
            clubs_dict[club["_id"]] = club["name"]
        return clubs_dict
