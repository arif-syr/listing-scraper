import datetime, json, requests

import bs4
from bs4 import BeautifulSoup
from consts import HEADER, COMMUTE_LAT_LON, COMMUTE_TYPE, OSRM_URL
from geopy import distance


class Listing:
    def __init__(self, listing_raw: bs4.Tag, commute_type: str = "foot"):
        """
        Constructor for a Listing. Partially parses a bs4.Tag element to populate the instance with relevant info about
        the listing.
        Only partially parses so the listing can be checked against existing pid's and its HTML does not have to
        be requested.
        Args:
            listing_raw: bs4.Tag element of a Craigslist listing
        """
        self.raw = listing_raw
        self.routes = json.dumps({})

        # Get listing url
        self.url = self.raw.find("a").get("href")
        # Get unique id for listing. Stored as <url>/<pid>.html
        self.pid = int(self.url.split("/")[-1].split(".")[0])

        self.title = ""
        self.price = 0
        self.location = ""
        self.posted = datetime.timedelta()
        self.lat_lon = ()
        self.crow_distance = 0.0
        self.travel_time = datetime.timedelta()

    def generate_listing_data(self) -> None:
        """
        Parses the HTML and grabs all the relevant info. The only thing generated is the travel time to a desired
        commute location.
        Returns: Nothing

        """
        # Usually price= $1,000. So replace comma with empty char and convert it to an int.
        self.price = int(self.raw.find(class_="price").text[1:].replace(",", "").strip())
        self.title = self.raw.find(class_="title").text.strip()
        self.location = self.raw.find(class_="location").text.strip()
        self.get_listing_page_info()
        self.init_routes()
        self.get_travel_time()

    def get_listing_page_info(self) -> None:
        """
        Sends a GET request to obtain the Listing HTML. Then gets all the info from the Listing page that could not
        be obtained from the Search page.
        """
        listing_page_source = requests.get(self.url, headers=HEADER)
        # Create new soup of new listing
        listing_soup = BeautifulSoup(listing_page_source.text, "html.parser")

        # Grab element with lat/lon data
        listing_lat_lon_element = listing_soup.find(id="map")
        self.lat_lon = (
            float(listing_lat_lon_element["data-latitude"]),
            float(listing_lat_lon_element["data-longitude"]),
        )

        # Crow distance is the distance to the commute location as the crow flies.
        self.crow_distance = round(
            distance.distance(self.lat_lon, COMMUTE_LAT_LON).miles, 1
        )

        # Grab date and time of posting
        date_posted, time_posted = listing_soup.find(class_="date timeago").text.split()

        # Convert date posted to days since now that it has been up.
        days_since = datetime.datetime.strptime(date_posted, "%Y-%m-%d")

        # Converts datetime object with hours, etc. to days ago
        self.posted = datetime.datetime.now() - days_since  # timedelta object

    def get_data(self) -> []:
        """
        Getter for Listing data
        Returns: an array of the listing data

        """
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

    def init_routes(self) -> None:
        """
        Queries OSRM for commute time by chosen commute type. Saves it in the current instance
        """
        formatted_url = OSRM_URL.format(commute_type=COMMUTE_TYPE, start_lon=self.lat_lon[1], start_lat=self.lat_lon[0],
                                        commute_lon=COMMUTE_LAT_LON[1], commute_lat=COMMUTE_LAT_LON[0])
        r = requests.get(formatted_url)
        self.routes = json.loads(r.content)

    def get_travel_time(self) -> None:
        """
        Stores travel time to commute location as an instance variable
        """
        route_data_json = self.routes.get("routes")[0]  # JSON of route information
        self.travel_time = datetime.timedelta(seconds=route_data_json["duration"])
