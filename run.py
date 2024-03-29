import argparse, pprint
import os
import re

import pandas as pd
from JSONProcessing import JSONProcessing
from Search import Search
from consts import json_folder


def show_all_searches() -> None:
    """
    Shows all existing search settings at a high level
    """
    searches = JSONProcessing.get_existing_searches()

    if not searches:
        print(f"No searches saved locally under {json_folder}")
    else:
        print("Showing all searches below:")
        # Get all dicts
        search_list = [JSONProcessing.get_json_dict(search) for search in searches]
        # Create a dataframe, sort by no. bedrooms, and set search name as index
        df = pd.DataFrame(search_list)
        df.sort_values(by=['bedrooms'], inplace=True)
        df.set_index('search_name', inplace=True)
        # Rename with some units and then print
        df.rename(columns={"search_radius": "search_radius (mi)", "max_rent": "max_rent ($)",
                           "min_rent_cutoff": "min_rent_cutoff ($)"}, inplace=True)
        print(df.to_string())


def check_above_zero(num: int) -> bool:
    """
    Checks if a number is below zero
    Args:
        num: number to be checked

    Returns: True if above zero

    """
    if not num > 0:
        print("This value needs to be greater than zero.")
        return False
    return True


def lat_check(latitude: float) -> bool:
    """
    Validation function to check user-entered latitude value
    Args:
        latitude: Latitude value

    Returns: true if valid latitude

    """
    print("NOTE: If latitude and longitude are outside the USA or Craigslist's map ranges, you may get nonsensical "
          "results in return when running the search.")
    if not (-90.0 <= latitude <= 90.0):
        print("Latitude must be within [-90.0, 90.0]")
        return False
    return True


def lon_check(longitude: float) -> bool:
    """
    Validation function to check user-entered longitude value
    Args:
        longitude: Longitude value

    Returns: true if valid longitude

    """
    if not (-180.0 <= longitude <= 180.0):
        print("Longitude must be within [-180.0, 180.0]")
        return False
    return True


def search_type_validation(search_type: str) -> bool:
    """
    Validation function to check user-entered search type
    Args:
        search_type: type of rental search

    Returns: true if valid search type

    """
    if not (search_type == "apa" or search_type == "roo"):
        print("Search type must be 'apa' or 'roo'")
        return False
    return True


def name_validation(name: str) -> bool:
    """
    Validation function to check user-entered Search name
    Args:
        name: name of Search

    Returns: True if search is valid

    """
    validation_regex = "[A-Za-z0-9_-]*"
    if not (re.fullmatch(validation_regex, name)):
        print("Your search can only have upper or lowercase characters, digits from 0-9, hyphens and underscores")
        return False
    elif JSONProcessing.search_name_exists(name):
        print("This search name already exists. If you want to overwrite it, please use the --overwrite argument.")
        return False
    elif name == "Q":
        print("This name is reserved and cannot be used as a search name.")
        return False
    return True


def get_input_with_checks_str(prompt: str, validation_function: callable) -> str:
    """
    Method to handle validating a user-input string with a corresponding validation function.
    Args:
        prompt: User prompt for input
        validation_function: function to validate input with

    Returns: user input, if valid

    """
    while True:
        user_input = input(prompt)
        if validation_function(user_input):
            return user_input


def get_input_with_checks_int(prompt: str, validation_function: callable) -> int:
    """
    Method to handle validating a user-input integer with a corresponding validation function.
    Also converts the user input to an integer if valid.
    Args:
        prompt: User prompt for input
        validation_function: function to validate input with

    Returns: user input, if valid

    """
    while True:
        user_input = input(prompt)
        try:
            user_input = int(user_input)
        except ValueError as e:
            print("Please enter a valid int.")
            continue
        if validation_function(user_input):
            return user_input


def get_input_with_checks_float(prompt: str, validation_function: callable) -> float:
    """
    Method to handle validating a user-input float with a corresponding validation function.
    Also converts the user input to a float if valid.
    Args:
        prompt: User prompt for input
        validation_function: function to validate input with

    Returns: user input, if valid

    """
    while True:
        user_input = input(prompt)
        try:
            user_input = float(user_input)
        except ValueError as e:
            print("Please enter a valid float.")
            continue
        if validation_function(user_input):
            return user_input


def create_new_search(overwrite: bool = False) -> None:
    """
    Creates a new Search and saves it as a .json file. Also validates inputs.
    Args:
        overwrite: flag for whether a Search should be overwritten
    """
    print("Enter values for your search settings as you are prompted.")
    search_dict = {}
    # Check if user wants to overwrite a Search
    if not overwrite:
        search_dict['search_name'] = get_input_with_checks_str("Please enter your search name:\n",
                                                               name_validation)
    else:
        while True:
            search_name = input("Please enter your search name:\n")
            if JSONProcessing.search_name_exists(search_name):
                search_dict['search_name'] = search_name
                break
            else:
                print("That search does not exist. Please enter the name of an existing search.")
                print(show_all_searches())

    search_dict['search_lat'] = get_input_with_checks_float("Please enter your search latitude:\n", lat_check)
    search_dict['search_lon'] = get_input_with_checks_float("Please enter your search longitude:\n", lon_check)
    search_dict['search_radius'] = get_input_with_checks_float("Please enter your desired search radius "
                                                               "(in miles):\n", check_above_zero)
    search_dict['max_rent'] = get_input_with_checks_int("Please enter your maximum rent (in $):\n",
                                                        check_above_zero)
    search_dict['min_rent_cutoff'] = get_input_with_checks_int("Please enter your minimum rent cutoff (in $):\n",
                                                               check_above_zero)
    search_dict['bedrooms'] = get_input_with_checks_int("Please enter the number of bedrooms desired:\n",
                                                        check_above_zero)
    search_dict['search_type'] = get_input_with_checks_str("Are you searching for a whole apartment or a sublet?"
                                                           " \n(\"apa\" for the whole apartment, \"roo\" to sublet):\n",
                                                           search_type_validation)
    pprint.pprint(search_dict)
    JSONProcessing.make_search_json_file(json_filename=search_dict['search_name'], data=search_dict, overwrite=overwrite)


if __name__ == "__main__":
    if not os.path.exists(json_folder):
        os.mkdir(json_folder)
        print("Made json_folder since it does not exist.")

    parser = argparse.ArgumentParser(description="Runs a search on Craigslist for living spaces based on "
                                                 "specified parameters")
    # Show a high-level overview of all Searches
    parser.add_argument("--show",
                        help="Show saved Searches and settings.",
                        action="store_true")

    # Run a search on Craigslist
    parser.add_argument("--run",
                        help="Run a specific Search from available searches.",
                        action="store_true")

    # Let user create things one by one - error handling done by JSONProcessing
    parser.add_argument("--new",
                        help="Create a new Search.",
                        action="store_true")

    # Let user enter blank to not change it, or enter a value to change a value.
    parser.add_argument("--overwrite",
                        help="Overwrite an existing Search with new parameters",
                        action="store_true")

    args = parser.parse_args()

    if args.show:
        show_all_searches()
    if args.new:
        create_new_search()
    if args.overwrite:
        create_new_search(args.overwrite)
    if args.run:
        show_all_searches()
        while True:
            current_search_name = input("Which search do you want to run?\n")
            if current_search_name == "Q":
                break
            if JSONProcessing.search_name_exists(current_search_name):
                current_search = Search(JSONProcessing.get_json_dict(current_search_name))
                current_search.run()
            else:
                print("This search does not exist. Please try again, or type 'Q' to exit.")
                continue
    else:
        print("No args supplied. Use the -h flag to see what options exist.")
