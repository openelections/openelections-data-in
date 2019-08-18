import requests
from bs4 import BeautifulSoup
import time
import os

# Python 3.7
# Download Warrick, Co Indiana precinct result html pages from Fall 2018 election
# Put them in a directory
# This will include the all-electionSummary.htm for the sake of completeness, but we'll cut it out in step 2
# https://warrickcounty.gov/Election/2018 Fall/

url = "https://warrickcounty.gov/Election/2018%20Fall/"
# Set a name for the directory
dir_for_download = "2018-fall"


# can also do fall 2016
# url = "https://warrickcounty.gov/Election/2016%20Fall/"
# # Set a name for the directory
# dir_for_download = "2016-fall"


pathname = "htm-files/" + dir_for_download + "/"
os.mkdir(pathname)

response = requests.get(url)
response.raise_for_status()
soup = BeautifulSoup(response.text, 'html.parser')

counter = 0

tds = soup.find_all("td")
for td in tds:
    if td.find("a"):
        a_tag = td.find("a")
        if a_tag.get_text() == "Parent Directory":
            pass
        elif ".db" in str(a_tag):
            pass
        elif ".pdf" in str(a_tag):
            pass
        else:
            time.sleep(2)
            precinct_url = url + a_tag['href']
            print(precinct_url)
            filename = "htm-files/" + dir_for_download + "/" + a_tag.get_text().strip()
            response = requests.get(precinct_url)
            document = open(filename, 'w')
            document.write(response.text)
            document.close()
            counter = counter + 1

print(str(counter) + " files downloaded")

