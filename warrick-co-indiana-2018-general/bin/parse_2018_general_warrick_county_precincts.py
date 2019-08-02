from bs4 import BeautifulSoup
from datetime import datetime
import csv
import os

# Python 3.7
# Warrick Co, Indiana election results are already downloaded with scrape_2018_general_warrick_county_precincts.py
# This tabulates the results
# ["county", "date", "precinct", "registered_voters", "office", "candidate", "party", "machine_votes", "absentee_votes", "provisional_votes"]
#
#### Change these three if it's anything but fall 2018
path_stem = "htm-files/2018-fall/"
all_files = os.listdir("htm-files/2018-fall/")
out_filename = "../20181106__in__general__warrick_precinct.csv"
####

# Can do fall 2016
# path_stem = "htm-files/2016-fall/"
# all_files = os.listdir("htm-files/2016-fall/")
# out_filename = "../20161108__in__general__warrick_precinct.csv"


results = []
counter = 0

for a_file in all_files:
    pathname = path_stem + a_file
    text = open(pathname)
    soup = BeautifulSoup(text, "html.parser")

    title_span = soup.find("span", attrs={"class": "f0_"})
    if title_span.get_text().strip() == "Election Summary Report":
        pass
    else:
        print(pathname)
        counter = counter + 1

        county = "Warrick" # always

        # If date is wanted
        # date_span = soup.find("span", attrs={"class": "f35_"}) # only one span of this class
        # date_str = (date_span.get_text().strip())
        # format_str = "%m/%d/%Y"
        # datetime_obj = datetime.strptime(date_str, format_str)
        # date = datetime_obj.date()

        precinct_span = soup.find("span", attrs={"class": "f29_"}) # only one span of this class
        precinct_text = (precinct_span.get_text().strip())
        precinct = precinct_text.rsplit("-",1)[1]

        registered_voters_span = soup.find("span", attrs={"class": "f50_"}) # only one span of this class
        registered_voters = int(registered_voters_span.get_text())

        for item in soup.find_all("div"):
            if item['class'][0] == "s5_":  # if it's a div with office name
                office_span = item.find("span", attrs={"class": "f1_"})
                office_text = office_span.get_text().strip()

                if "District" in office_text:
                    office = office_text.split("District")[0].strip()
                    for r in (("United States Rep", "U.S. House"),
                              ("State Senator", "State Senate"),
                              ("State Rep", "State House")):
                        office = office.replace(*r)

                    district = office_text.split("District")[1].strip()

                else:
                    office = office_text.replace("United States Senator", "U.S. Senate")
                    district = ""

            if item['class'][0] == "s0_": # if it's a div with a choice and results
                name_span = item.find("span", attrs={"class": "f6_"})
                candidate_text = name_span.get_text().strip()

                # Name formats
                # Deborah (Debbie) Smith (R)
                # Debbie Smith (R)
                # Deborah (Debbie) Smith
                # Debbie Smith
                # Debbie Smith (NP)

                if candidate_text[-1:] == ")":
                    candidate = candidate_text.rsplit("(", 1)[0].title().strip()
                    party = candidate_text.rsplit("(", 1)[1].strip()
                    for r in (("REP", "R"),
                              ("DEM", "D"),
                              (")", "")):
                        party = party.replace(*r)
                else:
                    party = ""
                    candidate = candidate_text.title()

                machine_span = item.find("span", attrs={"class": "f3_"})
                machine_votes = int(machine_span.get_text())

                absentee_span = item.find("span", attrs={"class": "f4_"})
                absentee_votes = int(absentee_span.get_text())

                provisional_span = item.find("span", attrs={"class": "f5_"})
                provisional_votes = int(provisional_span.get_text())

                new_row = [candidate, office, district, party, county, precinct, registered_voters,  machine_votes, absentee_votes, provisional_votes]
                results.append(new_row)

        csvfile = open(out_filename,'w')
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["candidate", "office", "district", "party", "county", "precinct", "registered_voters", "machine_votes", "absentee_votes", "provisional_votes"])
        csvwriter.writerows(results)
print (str(counter) + " precinct pages tabulated")
