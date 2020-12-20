from urllib2 import urlopen
precincts = """001 - Noble 1
002 - Noble 2
003 - Noble 3
004 - Noble 4
005 - Noble 5
006 - Noble 6
007 - Noble 7
008 - Noble 8
009 - Noble 9
010 - Noble 10
011 - Noble 11
012 - Chester 1
013 - Chester 2
014 - Chester 3
015 - Chester 4
016 - Chester 5
017 - Chester 6
018 - Pleasant 1
019 - Pleasant 2
020 - Lagro 1
021 - Lagro 2
022 - Lagro 3
023 - Liberty 1
024 - Liberty 2
025 - Paw Paw
026 - Waltz""".split("\n")
pages = {}
num_to_name = {}
for s in precincts:
    i = int(s[:2])
    num_to_name[i] = s
    s = s.replace(" ", "%20")
    url = "http://clerk.wabashcounty85.us/custom/00000185/elections/election2018g/Wabash_PrecSumm_"+s[:3]+".htm"
    print url
    f = urlopen(url)
    page = f.read()
    pages[i] = page
f = open("pages", "w")
f.write(repr(pages))

from re import search
def get_class_name(line):
    """
    go from laporte HTML line to the class of that line
    """
    pattern = "class=(.|_|\\t)+?( |>)"
    res = search(pattern, line)
    if res == None:
        return "None"
    return res.group()[6:-1]

def get_data_from_line(line):
    """
    go from laporte HTML line to the data of that line
    """
    pattern = ">.*<"
    if line == "</div>":
        return "close_div"
    return search(pattern, line).group()[1:-1]


def get_precinct_name(num):
    """
    Given precinct name, get precinct number
    """
    return num_to_name[num]

from csv import writer
name = "20181106__in__general__wabash__precinct.csv"
out_f = open(name, "w")
output = writer(out_f)

# KEY: County, Precinct, Machine Ballots, Absentee Ballots, Provisional Ballots, Total Ballots, Race, Candidate
key = ["county", "precinct", "election_day", "absentee", "provisional", "votes", "office", "candidate"]
output.writerow(key)

# s5_ is the first one we care about

# s5_.f1_ has the race name

# For each s0_ (candidate row):
#   f3_ has Machine votes
#   f4_ has Absentee votes
#   f5_ has Provisional votes
#   f23_ has Total votes
#   f6_ has candidate (WRITE HERE)

# s6_ has a break

# s2_ means we don't care anymore

county = "Wabash"

precinct_name = "ERROR"
candidate = "ERROR"
race = "ERROR"
total = "ERROR"
provisional = "ERROR"
absentee = "ERROR"
machine = "ERROR"
for precinct in pages.keys():
    print precinct
    page = pages[precinct]
    precinct_name = get_precinct_name(precinct)
    too_early = True
    for line in page.split("\n"):
        # Ignore the ones that're too early - they mess up our system
        if too_early:
            if "s5_" in line:
                print "no longer too early"
                too_early = False
            else:
                continue
        clazz = get_class_name(line)
        print clazz
        if clazz == "f0_":
            race = get_data_from_line(line)
        elif clazz == "f1_":
            machine = get_data_from_line(line)
        elif clazz == "f2_":
            absentee = get_data_from_line(line)
        elif clazz == "f3_":
            provisional = get_data_from_line(line)
        elif clazz == "f16_":
            total = get_data_from_line(line)
        elif clazz == "f4_":
            print "getting candidate"
            candidate = get_data_from_line(line)
            row = [county, precinct_name, machine, absentee, provisional, total, race, candidate]
            output.writerow(row)
        elif clazz == "s6_":
            candidate = "ERROR"
            race = "ERROR"
            total = "ERROR"
            provisional = "ERROR"
            absentee = "ERROR"
            machine = "ERROR"
        elif clazz == "s2_":
            continue
        else:
            continue
#            print "not useful", clazz

# KEY: County, Precinct, Machine Ballots, Absentee Ballots, Provisional Ballots, Total Ballots, Race, Candidate
