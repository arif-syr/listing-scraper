USF_LAT_LON = (37.77935412096749, -122.45205444263789)
HEADER = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/113.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}

dtypes = {
    "PID": "int64",  # int64
    "TITLE": "str",  # str
    "PRICE ($)": "int64",  # int32
    "TRAVEL TIME": "str",  # datetime
    "LINK": "str",  # str
    "LOCATION": "str",  # str
    "CROW_DISTANCE": "float64",  # float
    "POSTED": "str",  # timedelta object
}

cols = [
    "PID",  # int64
    "TITLE",  # str
    "PRICE ($)",  # int32
    "TRAVEL TIME",  # timedelta64[ns]
    "LINK",  # str
    "LOCATION",  # str
    "CROW_DISTANCE",  # float64
    "POSTED",  # timedelta64[ns]
]

required_search_cols = {"max_rent",
                        "search_radius",
                        "bedrooms",
                        "search_lat",
                        "search_lon",
                        "search_name",
                        "min_rent_cutoff"}

json_folder = "./json-searches"
