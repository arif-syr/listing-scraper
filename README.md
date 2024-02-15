# listing-scraper
A script I made to help increase the number of Craigslist listings you can view
at once by a huge amount. This is done by condensing all the listings for a 
particular search into an .html file that shows you most of the info you need,
 such as the rent, no. of bedrooms, distance from your desired neighborhood,
commute time, and so on, in an easily readable table. If you see a listing
that matches your basic requirements, you can just click the link to see
its pictures.

This helped me find an apartment in sf, as instead of spending 1-2 minutes
per listing, I could now spend 1-2 minutes looking at dozens of listings. 
It got cumbersome looking at a listing 
just to find out it's too far away for my commute, too far away from my 
desired neighborhood, or both, or was posted ages ago and is probably
inactive, or something else.

Mostly, it was just to solve a problem I had with code, to have a bit of fun,
to learn, and be creative.

This program also has some additional capability, like being able
to specify a commute location and see how long it takes to get there by foot,
car or bike. 

You can sort listings by commute times, date posted, rent, etc.

You can specify a minimum rent to avoid a lot of spam.

### Running it with docker-compose:
All you have to do is have Docker installed, and run ```docker-compose up```.  Instructions to build it manually 
from the Dockerfile are below

### Running it with Docker (optional):
To run this with Docker, follow these steps to get the docker container running, then follow the steps in the next 
section. 

Use these steps to build and run the repo from a Dockerfile:
1. cd into the repo: ```cd path/to/folder/listing-scraper```
2. Build the image:
   1. ```docker build -t listing-scraper .```
   2. You can change the tag to whatever you want
3. Run the container:
   1. ```docker run -v ./:/usr/src/app -t -d listing-scraper```
   2. The ```-v``` flag binds the current directory to the working directory of the container. This is done so the 
output files of the script are stored on your machine
4. Enter the container's command line:
   1. ```docker exec -it <container id> /bin/bash```
   2. All containers can be listed using ```docker ps -a```. Just copy the one matching the tag.
5. Follow steps in the next section to run the script

### Running it (compiling from source code):
If you are not following the Docker route, you need Python 3, and the libraries in requirements.txt.

You can run the program by typing ```python3 run.py <options>```. 
Accepted options are shown under ```python3 run.py --help``` 

If it's your first search, follow these steps:
1. Add your commute latitude and longitude to ```consts.py```
2. Specify your commute mode (car/foot/bike) in ```consts.py```
3. Run the following command to create a new search:```python3 run.py --new```
4. Enter required params (target latitude, target longitude, search radius, etc.)
5. Once the search is created, run ```python3 run.py --run```
6. Enter your **search name** in the following prompt
7. An html file with the results will be saved to json-searches/

To change how the html file is sorted, change the columns it's sorted by on line 184 of Search.py

### Overview:

Modify consts.py to specify your commute latitude/longitude and commute type (foot/bike/bus)

List available options using -h or --help

List existing searches by using --show as the option

Run an existing search by using the option --run 

Create a new search by using the --new argument

Overwrite an existing Search's parameters by using the --overwrite flag, and then choosing 
a Search to overwrite