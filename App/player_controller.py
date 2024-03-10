from .mongo_db import MongoDB
from .abstract_controller import PlayerControllerABC
from pymongo import UpdateOne
from .models import PlayersSimpliefied, PlayerSpecific, Positions, Foot
from bson import ObjectId
from datetime import datetime as dt


class PlayerController(PlayerControllerABC):
    OBJECTS_PER_PAGE = 10
    INT_TYPE_FIELDS = (
        "height",
        "weight",
        "value",
        "wage",
        "overall",
    )

    def __init__(self, mongo_db: MongoDB):
        self._mongo_db = mongo_db

    def find_objects_fit_to_data(self, data_fields):
        """find players that fit to data given from view widget"""
        if not data_fields:
            print("Cannot get data from view widget")
            return None
        projection = {
            "id": "$_id",
            "first_name": True,
            "last_name": True,
            "date_of_birth": True,
            "country": True,
            "overall": True,
        }
        query, category_sort, sort_by, page = self._parse_data_fields_send_query(
            data_fields
        )
        players = (
            self._mongo_db.players.find(query, projection)
            .sort(category_sort, sort_by)
            .skip(page * self.OBJECTS_PER_PAGE)
            .limit(self.OBJECTS_PER_PAGE)
        )

        return [PlayersSimpliefied(**player) for player in players]

    def find_choosen_object(self, player_id) -> PlayerSpecific:
        """make query for choosen player"""
        aggregation = [
            {"$match": {"_id": player_id}},
            {
                "$set": {
                    "age": {
                        "$dateDiff": {
                            "startDate": "$date_of_birth",
                            "endDate": "$$NOW",
                            "unit": "year",
                        }
                    },
                }
            },
            # left join by club _id
            {
                "$lookup": {
                    "from": "club_teams",
                    "localField": "stats.club_team",
                    "foreignField": "_id",
                    "as": "club_name_for_stats",
                },
            },
            {
                "$lookup": {
                    "from": "club_teams",
                    "localField": "club",
                    "foreignField": "_id",
                    "as": "club_name",
                },
            },
            # form club_teams left only club_name
            {
                "$project": {
                    "_id": 1,
                    "first_name": 1,
                    "last_name": 1,
                    "date_of_birth": 1,
                    "country": 1,
                    "height": 1,
                    "weight": 1,
                    "pref_pos": 1,
                    "value": 1,
                    "wage": 1,
                    "pref_foot": 1,
                    "overall": 1,
                    "age": 1,
                    "stats": 1,
                    "club": 1,
                    "club_name_for_stats._id": 1,
                    "club_name_for_stats.name": 1,
                    "club_name.name": 1,
                }
            },
        ]
        data = self._mongo_db.players.aggregate(aggregation)
        player_specific = self._parse_query_into_player_specific(data)
        return player_specific

    def delete_object(self, player_id, names):
        """Delete player from database by id and
        change id of deleted player from clubs' seasons to player name"""
        self._mongo_db.players.delete_one({"_id": player_id})
        self._mongo_db.clubs.update_many(
            {},
            {"$set": {"seasons.$[].players.head.$[elem]": names}},
            array_filters=[{"elem": {"$eq": player_id}}],
        )

        try:
            self._mongo_db.clubs.update_many(
                {},
                {"$set": {"seasons.$[].players.substitute.$[elem]": names}},
                array_filters=[{"elem": {"$eq": player_id}}],
            )
        except:
            pass

    def add_object(self, player, seasons: list[dict]):
        """Add new player to database but only if has valid fields"""
        try:
            query = self._add_validation(player, seasons)
            response = self._mongo_db.players.insert_one(query)
        except Exception as e:
            return str(e)

        try:
            new_player_id = response.inserted_id
            self._add_new_player_to_clubs(new_player_id, query)
            return "Player has been added successfully."
        except Exception as e:
            return (
                "Player has been added successfully, but seasons parameters was put incorrectly.\nPlease write them once again.\n"
                + str(e)
            )

    def update_object(
        self,
        player_table: dict,
        seasons_table: list[dict],
        player_specific: PlayerSpecific,
    ):
        (
            player_and_updating_seasons_query,
            new_seasons_query,
            seasons_to_delete_query,
            array_filters,
        ) = self._update_validation(player_table, seasons_table, player_specific)

        queries_for_players_collection = list()
        queries_for_clubs_collection = list()
        filter = {"_id": player_specific.id}
        if player_and_updating_seasons_query:
            queries_for_players_collection.append(
                UpdateOne(
                    filter,
                    player_and_updating_seasons_query,
                    array_filters=array_filters,
                )
            )
            queries_for_clubs_collection += self._update_player_in_clubs_by_season(
                player_and_updating_seasons_query, player_specific
            )

        if new_seasons_query:
            queries_for_players_collection.append(UpdateOne(filter, new_seasons_query))
            queries_for_clubs_collection += self._add_player_in_clubs_by_season(
                new_seasons_query, player_specific
            )

        if seasons_to_delete_query:
            queries_for_players_collection.append(
                UpdateOne(filter, seasons_to_delete_query)
            )
            queries_for_clubs_collection += self._delete_player_in_clubs_by_season(
                seasons_to_delete_query, player_specific
            )
        if queries_for_players_collection:
            self._mongo_db.players.bulk_write(queries_for_players_collection)
        if queries_for_clubs_collection:
            self._mongo_db.clubs.bulk_write(queries_for_clubs_collection)
        return

    def _add_validation(self, player: dict, seasons: list[dict]):
        query = dict()

        for key, value in player.items():
            if not value:
                continue
            if key == "date_of_birth":
                try:
                    query[key] = dt.strptime(value, "%d-%m-%Y")
                    continue
                except ValueError:
                    raise Exception(
                        "The field 'Date of Birth' requires an integer type value and must respects a valid date conditions.\n Scheme looks like: day-month-year."
                    )
            if key == "club_name":
                club_id = self._get_club_id_by_name(value)
                query["club"] = club_id
                continue
            if key in self.INT_TYPE_FIELDS:
                try:
                    value = int(value)
                except ValueError:
                    raise Exception(
                        f"Field {key.replace('_', ' ').title()} requires an integer value"
                    )
            query[key] = value

        query["stats"] = list()
        unique_seasons_chech_list = list()
        for season in seasons:
            temp_season = dict()
            for key, value in season.items():
                if (key == "season" or key == "club_name") and not value:
                    break
                if not value:
                    continue
                if key == "club_name":
                    club_id = self._get_club_id_by_name(value)
                    temp_season["club_team"] = club_id
                else:
                    temp_season[key] = int(value)
            else:
                query["stats"].append(temp_season)
                unique_seasons_chech_list.append(season["season"])

        if not len(unique_seasons_chech_list) == len(set(unique_seasons_chech_list)):
            raise Exception("Values for season fields are not unique")

        if not query["stats"]:
            query.pop("stats")

        return query

    def _get_club_id_by_name(self, name):
        if response := self._mongo_db.clubs.find_one(
            {"name": name}, projection={"_id": 1}
        ):
            return response["_id"]
        raise Exception(
            "Club of this name cannot be found. Check validity of given club name"
        )

    def _add_new_player_to_clubs(self, new_player_id, query):
        not_valid_seasons = list()
        if not (seasons := query.get("stats")):
            return
        for season in seasons:
            club_id = season["club_team"]
            season = season["season"]
            """Można dodać bulkorder w celu optymalizacji"""
            result = self._mongo_db.clubs.update_one(
                {"_id": club_id},
                {
                    "$addToSet": {
                        "seasons.$[season].players.head": ObjectId(new_player_id)
                    }
                },
                array_filters=[{"season.season": int(season)}],
                upsert=True,
            )
            if not result.modified_count:
                not_valid_seasons.append(str(season))
        if not_valid_seasons:
            raise Exception(
                f"It is not possible add player to seasons: {', '.join(not_valid_seasons)}.\nPlease create theese seasons in club panel first."
            )

    def _update_validation(
        self,
        player_table: dict,
        seasons_table: list[dict],
        player_specific: PlayerSpecific,
    ):
        (
            player,
            new_seasons_list,
            seasons_to_update,
            seasons_to_delete,
        ) = self._check_validity_with_prev_player_params(
            player_table, seasons_table, player_specific
        )
        player_and_updating_seasons_query = {"$set": dict(), "$unset": dict()}
        player_query = self._check_validity_of_player_fields(player) if player else {}
        new_seasons_query = (
            self._create_query_for_new_seasons(new_seasons_list)
            if new_seasons_list
            else {}
        )
        if seasons_to_update:
            (
                seasons_to_update_query,
                array_filters,
            ) = self._create_query_for_seasons_to_update(seasons_to_update)
        else:
            seasons_to_update_query = {}
            array_filters = []

        if seasons_to_delete:
            seasons_to_delete_query = self._create_query_for_seasons_to_delete(
                seasons_to_delete
            )
        else:
            seasons_to_delete_query = {}

        player_and_updating_seasons_query["$set"] = player_query.get(
            "$set", {}
        ) | seasons_to_update_query.get("$set", {})
        if not player_and_updating_seasons_query["$set"]:
            player_and_updating_seasons_query.pop("$set")

        player_and_updating_seasons_query["$unset"] = player_query.get(
            "$unset", {}
        ) | seasons_to_update_query.get("$unset", {})
        if not player_and_updating_seasons_query["$unset"]:
            player_and_updating_seasons_query.pop("$unset")

        return (
            player_and_updating_seasons_query,
            new_seasons_query,
            seasons_to_delete_query,
            array_filters,
        )

    def _check_validity_with_prev_player_params(
        self,
        player_table: dict,
        seasons_table: list[dict],
        player_specific: PlayerSpecific,
    ):
        player = dict()
        new_seasons_list: list[dict] = []
        seasons_to_update: list[dict] = []
        seasons_to_delete: list
        existing_seasons: set = set()

        for key, value in list(player_table.items())[:-1]:
            if key == "date_of_birth":
                if not player_specific.date_of_birth.strftime("%d-%m-%Y") == value:
                    player[key] = value
                continue
            if key == "pref_pos":
                if not (pos := player_specific.pref_pos):
                    if value:
                        player[key] = value.upper()
                    continue
                if not pos.name == value.upper():
                    player[key] = value.upper()
                continue
            if key == "pref_foot":
                if not (foot := player_specific.pref_foot):
                    if value:
                        player[key] = value.capitalize()
                    continue
                if not foot.name == value.upper():
                    player[key] = value.capitalize()
                continue
            if (
                player_specific_datum := list(
                    player_specific.dict(include={key}).values()
                )[0]
            ) == value:
                continue
            if str(player_specific_datum) == value:
                continue
            if key == "age":
                raise Exception(
                    "Changing the age is not allowed. Please change the Date of Birth"
                )

            player[key] = value

        for season in seasons_table:
            if not season["season"] and not season["club_name"]:
                continue
            if (
                not season["season"]
                and season["club_name"]
                or season["season"]
                and not season["club_name"]
            ):
                raise Exception(
                    "Both Season and Club fields are requierd. Please fill them up."
                )
            if not player_specific.stats:
                new_seasons_list.append(season)
                continue

            player_season = [
                player_season
                for player_season in player_specific.stats
                if str(player_season["season"]) == season["season"]
            ]

            if not player_season:
                new_seasons_list.append(season)
                continue

            existing_seasons.add(season["season"])

            temp_season = dict()
            for key, value in season.items():
                if (player_specific_datum := player_season[0].get(key)) == value:
                    continue
                if not str(player_specific_datum) == value:
                    temp_season[key] = value

            if temp_season:
                seasons_to_update.append({"season": season["season"]} | temp_season)

        if not player_specific.stats:
            seasons_to_delete = set()
        else:
            player_seasons = set(
                [
                    str(player_season["season"])
                    for player_season in player_specific.stats
                ]
            )
            seasons_to_delete = list(player_seasons - existing_seasons)

        return player, new_seasons_list, seasons_to_update, seasons_to_delete

    def _check_validity_of_player_fields(self, player: dict):
        query = dict()
        if not all(list(player.values())):
            query["$unset"] = dict()

        if any(list(player.values())):
            query["$set"] = dict()

        for key, value in player.items():
            if not value:
                query["$unset"][key] = 1
                continue
            if key == "date_of_birth":
                try:
                    query["$set"][key] = dt.strptime(value, "%d-%m-%Y")
                    continue
                except ValueError:
                    raise Exception(
                        "The field 'Date of Birth' requires an integer type value and must respects a valid date conditions.\n Scheme looks like: day-month-year."
                    )
            if key == "club_name":
                club_id = self._get_club_id_by_name(value)
                query["$set"]["club"] = club_id
                continue
            if key in self.INT_TYPE_FIELDS:
                try:
                    value = int(value)
                except ValueError:
                    raise Exception(
                        f"Field {key.replace('_', ' ').title()} requires an integer value"
                    )

            query["$set"][key] = value

        return query

    def _check_validity_of_seasons_fields(self, seasons, update_mode: bool = False):
        query = list()
        unique_seasons_chech_list = list()
        for season in seasons:
            temp_season = dict()
            for key, value in season.items():
                if not value:
                    if update_mode:
                        temp_season[key] = value
                    continue
                if key == "club_name":
                    club_id = self._get_club_id_by_name(value)
                    temp_season["club_team"] = club_id
                else:
                    temp_season[key] = int(value)
            else:
                query.append(temp_season)
                unique_seasons_chech_list.append(season["season"])

        if not len(unique_seasons_chech_list) == len(set(unique_seasons_chech_list)):
            raise Exception("Values for season fields are not unique")

        return query

    def _create_query_for_new_seasons(self, new_seasons_list):
        query = self._check_validity_of_seasons_fields(new_seasons_list)
        return {"$addToSet": {"stats": {"$each": query}}}

    def _create_query_for_seasons_to_update(self, seasons_to_update):
        queries = self._check_validity_of_seasons_fields(
            seasons_to_update, update_mode=True
        )
        used_seasons = set()
        set_dict = {"$set": dict()}
        unset_dict = {"$unset": dict()}
        for query in queries:
            season = query.pop("season")
            used_seasons.add(season)
            for key, value in query.items():
                if value:
                    if key == "club_team":
                        set_dict["$set"][f"stats.$[s{season}].{key}"] = value
                    else:
                        set_dict["$set"][f"stats.$[s{season}].{key}"] = int(value)
                else:
                    unset_dict["$unset"][f"stats.$[s{season}].{key}"] = 1

        array_filters = [{f"s{season}.season": int(season)} for season in used_seasons]

        return set_dict | unset_dict, array_filters

    def _create_query_for_seasons_to_delete(self, seasons_to_delete):
        delete_seasons_dict = {"$pull": {"stats": {"season": {"$in": list()}}}}
        for season in seasons_to_delete:
            delete_seasons_dict["$pull"]["stats"]["season"]["$in"].append(int(season))

        return delete_seasons_dict

    def _parse_data_fields_send_query(self, data_fields):
        """Func takes data from view widget's fields and
        parse them into query request"""
        query = dict()
        sort_by = -1
        category_sort = "overall"
        page = 0
        for key, value in data_fields.items():
            if not value:
                continue
            elif "min" in key:
                filed_name = key.split("_")[0]
                query[filed_name] = {"$gte": int(value)}
            elif "max" in key:
                filed_name = key.split("_")[0]
                if not query.get(filed_name):
                    query[filed_name] = {"$lte": int(value)}
                else:
                    query[filed_name]["$lte"] = int(value)
            elif key == "sort_by":
                sort_by = int(value)
            elif key == "category_sort":
                category_sort = value
            elif key == "page":
                page = int(value)
            else:
                query[key] = {"$in": value.split(",")}

        return query, category_sort, sort_by, page

    def _parse_query_into_player_specific(self, data):
        data = list(data)[0]
        player_specific = PlayerSpecific(
            id=data["_id"],
            first_name=data["first_name"],
            last_name=data.get("last_name"),
            date_of_birth=data["date_of_birth"],
            country=data["country"],
            overall=data.get("overall"),
            height=data.get("height"),
            weight=data.get("weight"),
            value=data.get("value"),
            wage=data.get("wage"),
            age=data.get("age"),
            club_id=data.get("club"),
            club_name=(
                data.get("club_name")[0].get("name") if data.get("club_name") else ""
            ),
        )

        if not (foot := data.get("pref_foot")):
            pass
        elif foot == "Left":
            player_specific.pref_foot = Foot.LEFT
        elif foot == "Right":
            player_specific.pref_foot = Foot.RIGHT

        if not (pos := data.get("pref_pos")):
            pass
        else:
            player_specific.pref_pos = Positions[pos]

        if not (stats := data.get("stats")):
            pass
        else:
            clubs_names_by_ids = dict()
            for club in data.get("club_name_for_stats"):
                clubs_names_by_ids[club["_id"]] = club["name"]

            for season in stats:
                season["club_id"] = season.pop("club_team")
                season["club_name"] = clubs_names_by_ids[season["club_id"]]

            player_specific.stats = stats

        return player_specific

    def _add_player_in_clubs_by_season(
        self, new_seasons_query, player_specific: PlayerSpecific
    ):
        queries: list[UpdateOne] = []
        for season_stat in new_seasons_query["$addToSet"]["stats"]["$each"]:
            queries.append(
                UpdateOne(
                    {"_id": season_stat["club_team"]},
                    {
                        "$addToSet": {
                            "seasons.$[season].players.head": player_specific.id
                        }
                    },
                    array_filters=[{"season.season": season_stat["season"]}],
                )
            )

        return queries

    def _delete_player_in_clubs_by_season(
        self, seasons_to_delete_query, player_specific: PlayerSpecific
    ):
        queries: list[UpdateOne] = []
        for season in seasons_to_delete_query["$pull"]["stats"]["season"]["$in"]:
            club_id = [
                player_season["club_id"]
                for player_season in player_specific.stats
                if player_season["season"] == season
            ][0]
            queries.append(
                UpdateOne(
                    {"_id": club_id},
                    {"$pull": {"seasons.$[season].players.head": player_specific.id}},
                    array_filters=[{"season.season": season}],
                )
            )
        return queries

    def _update_player_in_clubs_by_season(
        self, player_and_updating_seasons_query, player_specific: PlayerSpecific
    ):
        changed_clubs = list()
        for club_team in list(player_and_updating_seasons_query["$set"].keys()):
            if club_team.endswith("club_team"):
                changed_clubs.append(club_team)
        if not changed_clubs:
            return []

        queries: list[UpdateOne] = []
        for key in changed_clubs:
            new_club_id = player_and_updating_seasons_query["$set"][key]
            season = int(key[9:13])
            old_club_id = [
                player_season["club_id"]
                for player_season in player_specific.stats
                if player_season["season"] == season
            ][0]

            queries.append(
                UpdateOne(
                    {"_id": old_club_id},
                    {"$pull": {"seasons.$[season].players.head": player_specific.id}},
                    array_filters=[{"season.season": season}],
                )
            )
            queries.append(
                UpdateOne(
                    {"_id": new_club_id},
                    {
                        "$addToSet": {
                            "seasons.$[season].players.head": player_specific.id
                        }
                    },
                    array_filters=[{"season.season": season}],
                )
            )

        return queries
