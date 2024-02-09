import json
import os

from consts import json_folder


class JSONProcessing:
    @staticmethod
    def json_filename_to_path(json_filename: str) -> str:
        """
        Converts a path to a Search to the path relative to root. Appends .json to filename if it does not exist,
        and joins the json folder and search/json filename to give a full path relative to root.
        Args:
            json_filename: name of the Search or .json of the Search

        Returns: string of full path to .json file relative to root

        """
        if not json_filename.endswith(".json"):
            json_filename += ".json"
        if not json_filename.startswith(json_folder):
            json_filename = os.path.join(json_folder, json_filename)
        return json_filename

    @staticmethod
    def search_name_exists(search_name: str) -> bool:
        """
        Checks if search name exists
        Args:
            search_name: Name of search

        Returns: Bool

        """
        search_name = JSONProcessing.json_filename_to_path(search_name)
        return os.path.exists(search_name)

    @staticmethod
    def create_search_dict(max_rent: int, search_radius: float, bedrooms: int, search_lat: float, search_lon: float,
                           search_name: str, min_rent_cutoff: int, search_type: str) -> dict:
        """
        Creates a dictionary out of parameters and returns it
        Args:
            max_rent: budget for rent 
            search_radius: search radius around lat/lon to look in
            bedrooms: no. of bedrooms you're looking for
            search_lat: latitude of search center
            search_lon: longitude of search center
            search_name: name of the current search
            min_rent_cutoff: Min price to look for - filters out spam
            search_type: "roo" or "apa" if you're looking for a whole apartment or just a room

        Returns:

        """

        if max_rent < 0 or min_rent_cutoff < 0 or max_rent < min_rent_cutoff:
            raise ValueError("'max rent' and 'rent cutoff' must be positive, and max_rent must be > rent cutoff.")
        if search_radius <= 0.0 or not -90.0 <= search_lat <= 90.0 or not -180.0 <= search_lon <= 180.0:
            raise ValueError("search radius must be positive, "
                             "search_lat ∈ [-90.0, 90.0] and search_lon ∈ [-180.0, 180.0]")
        if bedrooms <= 0:
            raise ValueError("Enter a positive number of bedrooms.")
        if not (search_type == "apa" or search_type == "roo"):
            raise ValueError("Search type must be 'apa' or 'roo'")
        if JSONProcessing.search_name_exists(search_name):
            print("Creating a dictionary for an existing search.")

        search_dict = {}
        search_dict['max_rent'] = max_rent
        search_dict['search_radius'] = search_radius
        search_dict['bedrooms'] = bedrooms
        search_dict['search_lat'] = search_lat
        search_dict['search_lon'] = search_lon
        search_dict['search_name'] = search_name
        search_dict['min_rent_cutoff'] = min_rent_cutoff
        search_dict['search_type'] = search_type
        return search_dict

    @staticmethod
    def make_search_json_file(json_filename: str, data: dict, overwrite=False) -> bool:
        """
        Converts an array of search settings into a JSON file
        Args:
            json_filename: filename to store settings in
            data: Search setting data
            overwrite: Overwrite file if it exists

        Returns: Boolean, True if succeeded

        """
        save_path = JSONProcessing.json_filename_to_path(json_filename)
        if JSONProcessing.search_name_exists(save_path) and not overwrite:
            raise FileExistsError("Search already exists, and overwrite flag is false. "
                                  "Rename the search or overwrite the file please.")

        with open(save_path, "w") as output_file:
            json.dump(fp=output_file, obj=data, indent=4)
            return True

    @staticmethod
    def get_json_dict(json_filename: str) -> dict:
        """
        Converts a json into a dict
        Args:
            json_filename: filename of search to parse

        Returns: search data in dict format

        """
        json_path = JSONProcessing.json_filename_to_path(json_filename)
        if not JSONProcessing.search_name_exists(json_path):
            raise FileNotFoundError("Search .json does not exist")
        with open(json_path, "r") as input_file:
            search_data = json.load(input_file)
        return search_data

    @staticmethod
    def get_existing_searches() -> list:
        """
        Gets all existing Search setting files.
        Returns: list of files.

        """
        files = os.listdir(json_folder)
        files = [file for file in files if file.endswith(".json")]
        return files

