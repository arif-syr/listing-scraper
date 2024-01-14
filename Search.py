import datetime, os, pandas as pd, requests
from consts import (
    USF_LAT_LON,
    HEADER,
    cols,
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
    """Creates a class to scrape and operate Craigslist listings.
    Constructor requires dictionary of the following parameters:
    search_name (str): Name of search
    search_lat (float): Latitude of search.
    search_lon (float): Longitude of search.
    bedrooms (int): No of bedrooms interested in.
    max_rent (int): Maximum budget.
    search_radius (str): Radius of search.
    search_savepath (str): Directory to store results in.
    min_rent_cutoff (int): Filter out listings below this price. Defaults to 0.
    search_type (str): Type of search - "apa" for whole apartments, "roo" for room(s) in existing apartments.
        Defaults to "apa".

    Args:
        data_dict: Dictionary containing all the search parameters
    """

    def __init__(self, data_dict: dict) -> None:
        if not all(key in data_dict for key in required_search_cols):
            raise KeyError("Search settings missing values.")
        self.search_name = data_dict['search_name']
        self.max_rent = data_dict['max_rent']
        self.min_rent_cutoff = data_dict['min_rent_cutoff']
        self.search_lat = data_dict['search_lat']
        self.search_lon = data_dict['search_lon']
        self.search_radius = data_dict['search_radius']
        self.bedrooms = data_dict['bedrooms']
        self.search_type = data_dict['search_type']

        self.url = (f"https://sfbay.craigslist.org/search/san-francisco-ca/{self.search_type}?lat={self.search_lat}"
                    f"&lon={self.search_lon}&max_price={self.max_rent}&search_distance={self.search_radius}"
                    f"&max_bedrooms={self.bedrooms}")
        print(f"Checking URL {self.url}")

        # pid = unique id for a listing
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

    def get_listing_info(self, listing_raw_list) -> []:
        """Iterates through listing HTML and adds relevant data to a list.
        Creates Listing() objects using the listing HTML and returns them in a list to be concatenated with df

        Args:
            listing_raw_list: List of bs4 Tag objects representing Listing HTML
        """
        new_listings = []
        for curr_listing_idx, listing_raw in enumerate(listing_raw_list):
            curr_listing_idx += 1  # For one-indexing
            curr_listing = Listing(listing_raw)
            self.current_run_pids.add(curr_listing.pid)

            # If data exists for this listing, skip it
            if curr_listing.pid in self.pids:
                print(
                    f"Listing {curr_listing_idx} - {curr_listing.pid} already exists; skipping"
                )
                continue

            # If listing cannot be processed for some reason, print and skip. Else, add it to csv
            try:
                print(f"PROCESSING listing {curr_listing_idx}")
                curr_listing.generate_listing_data()
            except Exception as e:
                print(
                    f"Could not get data for listing number {curr_listing_idx} - {curr_listing.url}"
                )
                print(f"Exception: \n{e}")
            else:
                print(
                    f"Adding {curr_listing.pid} to dataframe, \nposted {curr_listing.posted.days} days ago"
                    f"\nTitle: {curr_listing.title}\nURL: {curr_listing.url}\n"
                )
                new_listings.append(curr_listing.get_data())
        return new_listings

    def get_listings(self):
        """Scrapes data from main page and gets information for each listing.
        - gets the response from the URL and creates a soup out of it.
        - finds all the list items and grabs their HTML <li> tag
        - removes non-listing list items
        - Calls get_listing_info() on linking HTML to get info about listings

        Returns: -1 if no listings, +1 if yes listings
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

        new_listings = self.get_listing_info(listing_raw_list)
        new_listings_df = pd.DataFrame(new_listings, columns=cols)
        print(f"old df size: {len(self.df)}")
        self.df = pd.concat([self.df, new_listings_df])
        print(f"new df size: {len(self.df)}")
        return 1

    def delete_old_listings(self):
        """Deletes removed listings from craigslist search."""

        old_listings = self.pids - self.current_run_pids
        preserved_listings = self.current_run_pids.intersection(self.pids)
        if not old_listings:
            print("No removed listings to be deleted")
        else:
            print("Listings to be deleted:\n", old_listings)
            print(f"df size before removing old pids: {len(self.df)}")
            self.df = self.df[~self.df.PID.isin(old_listings)]
            print(f"new df size after removing old pids: {len(self.df)}")
            print(self.df.to_string())
            print(f"preserved listings: {preserved_listings}")

    def drop_listings(self):
        """Drops listings below a specified threshold to filter fake listings."""
        print(
            "listings to be dropped because of price:",
            self.df[(self.df["PRICE ($)"] <= self.min_rent_cutoff)].to_string(),
        )
        self.df = self.df[~(self.df["PRICE ($)"] <= self.min_rent_cutoff)]

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
            os.path.join(json_folder, self.search_name + ".csv"), mode="w+"
        )

    def save_to_html(self):
        """Saves df to HTML file."""
        self.make_df_pretty()
        html_path = os.path.join(json_folder, self.search_name + ".html")
        with open(html_path, "w+") as html_file:
            self.df = self.df.drop(columns=["PID"])
            print(html_path)

            # Write to HTML
            html_file.write(
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
        hours = posted.seconds // 60 ** 2
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
        if cont == -1:
            print("Current search settings have no results.")
            print("Please overwrite with new settings or wait for new listings.")
            return
        self.delete_old_listings()
        self.drop_listings()
        self.sort_df()
        self.write_to_csv()
        self.save_to_html()
