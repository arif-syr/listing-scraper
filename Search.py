import datetime, os, pandas as pd, requests
from consts import (
    USF_LAT_LON,
    HEADER,
    cols,
    csv_filename,
    html_filename,
    dtypes,
    required_search_cols,
    json_folder
)
from constspriv import parent_filepath
from bs4 import BeautifulSoup
from Listing import Listing


# Article on pd.cut https://towardsdatascience.com/how-to-bin-numerical-data-with-pandas-fe5146c9dc55
# https://towardsdatascience.com/all-pandas-cut-you-should-know-for-transforming-numerical-data-into-categorical-data-1370cf7f4c4f


# Create Search object
# Go through csv to load existing listings and save pid's to set
# Go through sublisting url's and get info
#   If pid exists, then skip getting info for that specific sublisting
#   Save all pid's from run to a set curr_listings
# Now we have listing data loaded from csv, and new listing data loaded from the internet
# Remove listing data for pid's not in curr_listings from df
#   Write current listing data with old data removed to csv

class Search:
    # def __init__(
    #     self,
    #     target_lat: float,
    #     target_lon: float,
    #     bedrooms: int,
    #     max_price: str,
    #     max_dist: str,
    #     search_savepath: str,
    #     low_budget_threshold: int = 0,
    #     search_type: str = "apa",
    # ) -> None:
    #     self.target_lat = target_lat
    #     self.target_lon = target_lon
    #     self.bedrooms = bedrooms
    #     self.max_price = max_price
    #     self.max_dist = max_dist
    #     self.search_savepath = search_savepath
    #     if not self.bedrooms:
    #         self.url = f"https://sfbay.craigslist.org/search/san-francisco-ca/{search_type}?lat={target_lat}&lon={target_lon}&max_price={max_price}&search_distance={max_dist}"
    #     else:
    #         self.url = f"https://sfbay.craigslist.org/search/san-francisco-ca/{search_type}?lat={target_lat}&lon={target_lon}&max_bedrooms={bedrooms}&max_price={max_price}&min_bedrooms={bedrooms}&search_distance={max_dist}"
    #     print(f"Checking URL {self.url}")
    #     # self.listings = {}  # Maybe dict with pids as keys?
    #
    #     # Dir where csv's and html files are stored
    #     self.low_budget_threshold = low_budget_threshold
    #     self.search_savepath = search_savepath
    #     self.pids = set()  # existing pid's
    #     self.current_run_pids = set()  # current pid's
    """Creates a class to scrape and operate Craigslist listings.
    search_lat (float): Latitude of search.
    search_lon (float): Longitude of search.
    bedrooms (str): No of bedrooms interested in.
    max_rent (str): Maximum budget.
    search_radius (str): Radius of search.
    search_savepath (str): Directory to store results in.
    low_budget_threshold (int): Filter out listings below this price. Defaults to 0.
    search_type (str): Type of search - "apa" for available apartments, "roo" for rooms in existing leases.
        Defaults to "apa".

    Args:
        data_dict: Dictionary containing all the search parameters
    """

    def __init__(self, data_dict: dict) -> None:
        if not all(key in data_dict for key in required_search_cols):
            raise KeyError("Search settings missing values.")
        self.search_name = data_dict['search_name']
        self.max_rent = data_dict['max_rent']
        self.search_radius = data_dict['search_radius']
        self.bedrooms = data_dict['bedrooms']
        self.search_lat = data_dict['search_lat']
        self.search_lon = data_dict['search_lon']
        self.min_rent_cutoff = data_dict['min_rent_cutoff']
        self.search_type = data_dict['search_type']

        # Dir where csv's and html files are stored

        self.url = (f"https://sfbay.craigslist.org/search/san-francisco-ca/{self.search_type}?lat={self.search_lat}"
                    f"&lon={self.search_lon}&max_price={self.max_rent}&search_distance={self.search_radius}"
                    f"&max_bedrooms={self.bedrooms}")
        print(f"Checking URL {self.url}")
        # self.listings = {}  # Maybe dict with pids as keys?
        self.pids = set()  # existing pid's
        self.current_run_pids = set()  # current pid's
        self.df = pd.DataFrame(columns=cols)

    def load_pid_data(self):
        """Checks if search savepath and csv available, and loads/creates files as appropriate."""

        csv_path = os.path.join(json_folder, self.search_name + ".csv")
        if not os.path.exists(csv_path):
            print("This search has no .csv of existing listings")
            # os.mkdir(os.path.join(parent_filepath, self.search_savepath))
        else:
            self.df = pd.read_csv(csv_path, index_col=0)

            # Convert travel time and posted columns to timedelta objects
            self.df["TRAVEL TIME"] = pd.to_timedelta(self.df["TRAVEL TIME"])
            self.df["POSTED"] = pd.to_timedelta(self.df["POSTED"])

            print("Loaded df from csv")
            # Save pids to a set
            self.pids = set(self.df["PID"])

    def get_listing_info(self, listing_raw, curr_listing_idx):
        """Iterates through Results in ResultSet and adds relevant data to a dataframe

        Args:
            curr_listing_idx:
            listing_raw (ResultSet): Raw BeautifulSoup HTML data to parse through
        """
        curr_listing = Listing(listing_raw)

        # If data exists for this listing, skip it
        if curr_listing.pid in self.pids:
            self.current_run_pids.add(curr_listing.pid)
            print(
                f"Listing {curr_listing_idx} - {curr_listing.pid} already exists; skipping"
            )
            return

        # If listing cannot be processed for some reason, print and skip. Else, add it to csv
        try:
            print(f"PROCESSING listing {curr_listing_idx}")
            curr_listing.get_info()
        except:
            print(
                f"Could not get data for listing number {curr_listing_idx} - {curr_listing.url}"
            )
        else:
            print(
                f"Adding {curr_listing.pid} to dataframe, \nposted {curr_listing.posted.days} days ago\nTitle: {curr_listing.title}\nURL: {curr_listing.url}\nx"
            )
            self.df.loc[len(self.df)] = curr_listing.get_data()

    def get_listings(self):
        """Scrapes data from main page and gets information for each listing.

        Finds listing from main page, then goes through each listing and grabs info
        using the get_listing_info() function and Listing() class.
        """
        source = requests.get(self.url, headers=HEADER)
        soup = BeautifulSoup(source.text, "html.parser")
        # Should find most listings, unless result set is huge
        listing_raw_list = soup.find_all("li")

        if len(listing_raw_list) > 0:
            print(f"{len(listing_raw_list)} listings found\n")
        else:
            print("NO LISTINGS FOUND")
            return -1

        if listing_raw_list[0].div.text == "see also":
            print("Removed 'see also' div")
            del listing_raw_list[0]

        for i, listing_raw in enumerate(listing_raw_list):
            self.get_listing_info(listing_raw, i + 1)

    def delete_old_listings(self):
        """Deletes removed listings from craigslist search."""

        old_listings = self.pids - self.current_run_pids
        if not old_listings:
            print("No removed listings to be deleted")
        else:
            print("Listings to be deleted:\n", old_listings)
            print(
                "\nListings to be removed:",
                self.df[self.df.PID.isin(old_listings)].to_string(),
                "\n",
            )
            self.df = self.df[~self.df.PID.isin(old_listings)]

    def drop_listings(self):
        """Drops listings below a specified threshold to filter fake listings."""
        print(
            "listings to be dropped because of price:",
            self.df[(self.df["PRICE ($)"] <= self.low_budget_threshold)].to_string(),
        )
        self.df = self.df[~(self.df["PRICE ($)"] <= self.low_budget_threshold)]

    # Sort according to buckets

    def sort_df(self):
        """Sorts data according to parameters."""
        minute = 60
        # bins = [0,20], (20,30], (30,45], (45, 60]
        bins = [
            datetime.timedelta(0, 0 * minute),
            datetime.timedelta(0, 20 * minute),
            datetime.timedelta(0, 30 * minute),
            datetime.timedelta(0, 45 * minute),
            datetime.timedelta(0, 60 * minute),
        ]
        # Journey length labels
        labels = ["Short", "Medium", "Long", "Very Long"]

        # Create new column called "Cat" to store the category of journey length
        self.df["Cat"] = pd.cut(self.df["TRAVEL TIME"], bins=bins, labels=labels)
        # Sort by journey length, then price
        self.df = self.df.sort_values(by=["Cat", "POSTED"], ascending=True)

    def write_to_csv(self):
        """Saves dataframe results to a csv."""
        # Save all columns except the Cat column to csv
        self.df.loc[:, self.df.columns != "Cat"].to_csv(
            os.path.join(parent_filepath, self.search_savepath, csv_filename), mode="w+"
        )

    def save_to_html(self):
        """Saves df to HTML file."""

        self.make_df_pretty()
        file_object = open(
            os.path.join(parent_filepath, self.search_savepath, html_filename), "w+"
        )
        self.df = self.df.drop(columns=["PID"])

        # Write to HTML
        file_object.write(
            self.df.to_html(escape=False)
            .replace("<td>", "<td align='center'>")
            .replace("<th>", "<th align='center'>")
        )  # escape=False is needed to render HTML links

    def make_clickable(self, url):
        """Converst url to an HTML hyperlink.

        Args:
            url (string): Raw url.

        Returns:
            str: HTML hyperlink element
        """
        return '<a href="{}" rel="noopener noreferrer" target="_blank">{}</a>'.format(
            url, "URL"
        )

    def make_HMS(self, travel_time):
        """Converts timedelta object into HH:MM:SS format.

        Args:
            travel_time (datetime.timedelta): timedelta object representing travel time to USF.

        Returns:
            str: readable string of travel time.
        """
        travel_time = str(travel_time).split()[-1].split(".")[0]
        return travel_time

    def format_posted(self, posted):
        """Converts timedelta object to a string based on how long ago a posting was listed.

        Args:
            posted (datetime.timedelta): object representing time ago a listing was posted.

        Returns:
            str: readable format of above.
        """
        days = posted.days
        hours = (posted.seconds) // 60 ** 2
        return f"{days} days, {hours} hours ago"

    def make_df_pretty(self):
        """Formats df data to make it more readable and when saving to an HTML file."""

        # Transform travel time format
        self.df["TRAVEL TIME"] = self.df.apply(
            lambda x: self.make_HMS(travel_time=x["TRAVEL TIME"]), axis=1
        )
        # Code to convert URL column to hyperlink, for HTML email purposes
        self.df["LINK"] = self.df.apply(
            lambda x: self.make_clickable(url=x["LINK"]), axis=1
        )
        self.df["POSTED"] = self.df.apply(
            lambda x: self.format_posted(posted=x["POSTED"]), axis=1
        )

    def run(self):
        """Runs all the helper functions in class."""

        self.load_pid_data()
        cont = self.get_listings()
        # if cont == -1:
        #     return
        # self.delete_old_listings()
        # if self.low_budget_threshold:
        #     self.drop_listings()
        # self.sort_df()
        # self.write_to_csv()
        # self.save_to_html()
