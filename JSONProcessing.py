import json
import os


class JSONProcessing:
    @staticmethod
    def search_name_exists(search_name: str):
        """
        Checks if search name exists
        Args:
            search_name: Name of search

        Returns: Bool

        """
        return os.path.exists(search_name)

    @staticmethod
    def create_search_dict(max_rent: int, search_radius: float, bedrooms: int, search_lat: float, search_lon: float,
                           search_name: str, min_rent_cutoff: int, search_type: str):
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
        if search_radius <= 0.0 or not -90.0 <= search_lon <= 90.0 or not -180.0 <= search_lat <= 180.0:
            raise ValueError("search radius must be positive, "
                             "search_lon ∈ [-90.0, 90.0] and search_lat ∈ [-180.0, 180.0]")
        if bedrooms <= 0:
            raise ValueError("Enter a positive number of bedrooms.")
        if not (search_type == "apa" or search_type == "roo"):
            raise ValueError("Search type must be 'apa' or 'roo'")
        if JSONProcessing.search_name_exists(search_name):
            print("Creating a dictionary for an existing search.")

        search_dict = dict()
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
    def make_search_json_file(json_filename, data, overwrite=False):
        """
        Converts an array of search settings into a JSON file
        Args:
            json_filename: filename to store settings in
            data: Search setting data
            overwrite: Overwrite file if it exists

        Returns: Boolean, True if succeeded

        """

        return

    @staticmethod
    def get_json_dict(self, json_filename):
        """
        Converts a json into a dict
        Args:
            json_filename: filename of json file to parse

        Returns: search data in dict format

        """
        search_data = {}
        return search_data


if __name__ == '__main__':
    search = JSONProcessing.create_search_dict(max_rent=500, search_radius=0.5, bedrooms=1, search_lat=12.1212,
                                               search_lon=11.1212, search_name="test", min_rent_cutoff=100,
                                               search_type="apa")
    print(search)
    # JSONProcessing.make_search_json_file("./tst.json", search, overwrite=True)
