from Search import Search
from consts import USF_LAT_LON

# TODO: Use dict instead of lists for search settings

if __name__ == "__main__":
    # [Price, Distance, Bedrooms, Lat, Lon, search_name, low_threshold, type]
    old_lat_lon = (37.7722, -122.4529)
    SW_usf = (37.7659, -122.4554)
    EAST_usf = (37.777, -122.4357)
    # search_settings = [
    #     [
    #         "3000",
    #         "0.45",
    #         "2",
    #         old_lat_lon[0],
    #         old_lat_lon[1],
    #         "short_search/",
    #         1000,
    #         "apa",
    #     ],
    # ]

    search_settings = [
        # [
        #     "3000",
        #     "0.75",
        #     "2",
        #     USF_LAT_LON[0],
        #     USF_LAT_LON[1],
        #     "two_bedroom_usf/",
        #     1500,
        #     "apa",
        # ],
        [
            "1650",
            "1.75",
            "1",
            USF_LAT_LON[0],
            USF_LAT_LON[1],
            "one_bedroom_usf/",
            100,
            "apa",
        ],
        # [
        #     "1600",
        #     "0.75",
        #     "1",
        #     SW_usf[0],
        #     SW_usf[1],
        #     "one_bedroom_SW/",
        #     100,
        #     "apa",
        # ],
        # [
        #     "1600",
        #     "1.0",
        #     "0.7",
        #     EAST_usf[0],
        #     EAST_usf[1],
        #     "one_bedroom_EAST/",
        #     100,
        #     "apa",
        # ],
        # [
        #     "4000",
        #     "1.0",
        #     "3",
        #     USF_LAT_LON[0],
        #     USF_LAT_LON[1],
        #     "three_bedroom_usf/",
        #     2500,
        #     "apa",
        # ],
        # [
        #     "1400",
        #     "1.0",
        #     "1",
        #     USF_LAT_LON[0],
        #     USF_LAT_LON[1],
        #     "room_sublet_usf/",
        #     100,
        #     "roo",
        # ],
    ]

    for setting in search_settings:
        print(
            f"\nSearch for {setting[2]} room at a max price of {setting[0]} and a search radius of {setting[1]}. Setting = {setting[7]}"
        )
        low_budget_threshold = 0 if len(setting) < 7 else setting[6]
        tst = Search(
            max_price=setting[0],
            max_dist=setting[1],
            bedrooms=setting[2],
            target_lat=setting[3],
            target_lon=setting[4],
            search_savepath=setting[5],
            low_budget_threshold=low_budget_threshold,
            search_type=setting[7],
        )
        tst.run()
    # print(tst.df.to_string())
