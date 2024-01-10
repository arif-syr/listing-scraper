import datetime, json, requests
from bs4 import BeautifulSoup
from consts import HEADER, USF_LAT_LON, cols
from geopy import distance


class Listing:
    def __init__(self, listing_raw):
        self.raw = listing_raw
        self.routes = ""

        # Get listing url
        self.url = self.raw.find("a").get("href")
        # Get unique id for listing
        self.pid = int(self.url.split("/")[-1].split(".")[0])

        self.title = ""
        self.price = 0
        self.location = ""
        self.posted = datetime.timedelta()
        self.lat_lon = ()
        self.crow_distance = 0.0
        self.travel_time = datetime.timedelta()

    # Gets all attributes
    def get_info(self):
        # Usually price= $1,000. So replace comma with empty char and convert it to an int.
        self.price = int(self.raw.find(class_="price").text[1:].replace(",", ""))
        self.title = self.raw.find(class_="title").text
        self.location = self.raw.find(class_="location").text.strip()
        self.get_listing_page_info()
        self.init_routes()
        self.get_travel_time()

    def get_listing_page_info(self):
        listing_page_source = requests.get(self.url, headers=HEADER)
        # Create new soup of new listing
        listing_soup = BeautifulSoup(listing_page_source.text, "html.parser")

        # Grab element with lat/lon data
        listing_lat_lon_element = listing_soup.find(id="map")

        # Grab date and time of posting
        date_posted, time_posted = listing_soup.find(class_="date timeago").text.split()

        # Convert date posted to days since
        # datetime.date object below
        days_since = datetime.datetime.strptime(date_posted, "%Y-%m-%d")

        # Converts datetime object with hours, etc. to days ago
        self.posted = datetime.datetime.now() - days_since  # timedelta object

        # Get class name which is lat and longitude
        self.lat_lon = (
            float(listing_lat_lon_element["data-latitude"]),
            float(listing_lat_lon_element["data-longitude"]),
        )
        self.crow_distance = round(
            distance.distance(self.lat_lon, USF_LAT_LON).miles, 1
        )

    def get_data(self):
        to_return = [
            self.pid,
            self.title,
            self.price,
            self.travel_time,
            self.url,
            self.location,
            self.crow_distance,
            self.posted,
        ]
        return to_return

    def print_data(self):
        print(cols)
        print(
            [
                self.pid,
                self.title,
                self.price,
                self.travel_time,
                self.url,
                self.location,
                self.crow_distance,
                self.posted,
            ]
        )

    # Gets OSRM json data
    def init_routes(self):
        r = requests.get(
            f"https://routing.openstreetmap.de/routed-foot/route/v1/foot/{self.lat_lon[1]},{self.lat_lon[0]};{USF_LAT_LON[1]},{USF_LAT_LON[0]}?overview=false"
        )
        self.routes = json.loads(r.content)

    # Returns string of travel time in HH:MM:SS. By default returns no. of days too.
    def get_travel_time(self):
        route_data_json = self.routes.get("routes")[0]  # JSON of route information
        self.travel_time = datetime.timedelta(seconds=route_data_json["duration"])
