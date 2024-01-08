import argparse, pprint
import pandas as pd
from JSONProcessing import JSONProcessing
from Search import Search
from consts import USF_LAT_LON, json_folder


def show_all_searches():
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
        print(df)


def check_below_zero(num):
    if not num > 0:
        print("This value needs to be greater than zero.")
        return False
    return True


def rent_check(min_rent, max_rent):
    if not (0 < min_rent < max_rent):
        print("The minimum rent cutoff needs to be less than the maximum rent and greater than zero.")
        return False
    return True


def lat_check(latitude):
    if not (-90.0 <= latitude <= 90.0):
        print("Latitude must be within [-90.0, 90.0]")
        return False
    return True


def lon_check(longitude):
    if not (-180.0 <= longitude <= 180.0):
        print("Longitude must be within [-180.0, 180.0]")
        return False
    return True


def search_type_validation(search_type):
    if not (search_type == "apa" or search_type == "roo"):
        print("Search type must be 'apa' or 'roo'")
        return False
    return True


def name_validation(name):
    if JSONProcessing.search_name_exists(name):
        print("This search name already exists. If you want to overwrite it, please use the --overwrite argument.")
        return False
    return True


def get_input_with_checks_str(prompt, validation_function):
    while True:
        user_input = input(prompt)
        if validation_function(user_input):
            return user_input


def get_input_with_checks_int(prompt, validation_function):
    while True:
        user_input = input(prompt)
        try:
            user_input = int(user_input)
        except ValueError as e:
            print("Please enter a valid int.")
            continue
        if validation_function(user_input):
            return user_input


def get_input_with_checks_float(prompt, validation_function):
    while True:
        user_input = input(prompt)
        try:
            user_input = float(user_input)
        except ValueError as e:
            print("Please enter a valid float.")
            continue
        if validation_function(user_input):
            return user_input


def create_new_search(overwrite=False):
    # Check for name first
    print("Enter values for your search settings as you are prompted.")
    search_dict = {}
    if not overwrite:
        search_dict['search_name'] = get_input_with_checks_str("Please enter your search name:\n", name_validation)
    else:
        search_dict['search_name'] = input("Please enter your search name:\n")
    search_dict['search_lat'] = get_input_with_checks_float("Please enter your search latitude:\n", lat_check)
    search_dict['search_lon'] = get_input_with_checks_float("Please enter your search longitude:\n", lon_check)
    search_dict['search_radius'] = get_input_with_checks_float("Please enter your desired search radius (in miles):\n",
                                                               check_below_zero)
    search_dict['max_rent'] = get_input_with_checks_int("Please enter your maximum rent (in $):\n", check_below_zero)
    search_dict['min_rent_cutoff'] = get_input_with_checks_int("Please enter your minimum rent cutoff (in $):\n",
                                                               check_below_zero)
    search_dict['bedrooms'] = get_input_with_checks_int("Please enter the number of bedrooms desired:\n",
                                                        check_below_zero)
    search_dict['search_type'] = get_input_with_checks_str("Are you searching for a whole apartment or a sublet? \n("
                                                           "\"apa\" for the whole apartment, \"roo\" to sublet):\n",
                                                           search_type_validation)
    pprint.pprint(search_dict)
    # Need to do type checks

    # Remember to check for max_rent < min_rent_cutoff
    JSONProcessing.make_search_json_file(json_filename=search_dict['search_name'], data=search_dict, overwrite=overwrite)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Runs a search on Craigslist for living spaces based on "
                                                 "specified parameters")
    # Show a high-level overview of all Searches
    parser.add_argument("--show", help="Show saved Searches and settings.", action="store_true")
    # Run a search on Craigslist
    parser.add_argument("--run", help="Run a specific Search.")
    # Let user create things one by one - error handling done by JSONProcessing
    parser.add_argument("--new", help="Create a new Search.", action="store_true")
    # Let user enter blank to not change it, or enter a value to change a value.
    parser.add_argument("--overwrite", help="Overwrite an existing Search with new parameters")
    args = parser.parse_args()

    if args.show:
        show_all_searches()
    if args.new:
        create_new_search()
    if args.overwrite:
        create_new_search(overwrite=True)

    # [Price, Distance, Bedrooms, Lat, Lon, search_name, low_threshold, type]
    # search_names = ["one_bedroom_usf", "room_sublet_usf"]
    # for search in search_names:
    #     search_vals = JSONProcessing.get_json_dict(search + ".json")
    #     pprint.pprint(search_vals)
    # print(
    #     f"\nSearch for {setting[2]} room at a max price of {setting[0]} and a search radius of {setting[1]}. Setting = {setting[7]}"
    # )
    # low_budget_threshold = 0 if len(setting) < 7 else setting[6]
    # tst = Search(
    #     max_price=setting[0],
    #     max_dist=setting[1],
    #     bedrooms=setting[2],
    #     target_lat=setting[3],
    #     target_lon=setting[4],
    #     search_savepath=setting[5],
    #     low_budget_threshold=low_budget_threshold,
    #     search_type=setting[7],
    # )
    # tst.run()
