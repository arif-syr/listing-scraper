import argparse, pprint

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
        print("Showing all searches below:\n")
        for search in searches:
            curr_search = JSONProcessing.get_json_dict(search)
            print(curr_search['search_name'])
            pprint.pprint(curr_search)
            print('\n###############')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Runs a search on Craigslist for living spaces based on "
                                                 "specified parameters")
    # Show a high-level overview of all Searches
    parser.add_argument("--show", help="Show saved Searches and settings.")
    # Run a search on Craigslist
    parser.add_argument("--run", help="Run a specific Search.")
    # Let user create things one by one - error handling done by JSONProcessing
    parser.add_argument("--new", help="Create a new Search.")
    # Let user enter blank to not change it, or enter a value to change a value.
    parser.add_argument("--overwrite", help="Overwrite an existing Search with new parameters")
    args = parser.parse_args()

    if args.show:
        show_all_searches()

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
