import csv
import requests
from BeautifulSoup import BeautifulSoup
results = []

urls = ['https://secure2.hamiltoncounty.in.gov/Elections/2008G/President%20of%20the%20US.htm', 'https://secure2.hamiltoncounty.in.gov/Elections/2008G/Governor%20And%20Lieutenant%20Governor.htm',
    'https://secure2.hamiltoncounty.in.gov/Elections/2008G/Attorney%20General.htm', 'https://secure2.hamiltoncounty.in.gov/Elections/2008G/Superintendent%20of%20Public%20Inst.htm', 'https://secure2.hamiltoncounty.in.gov/Elections/2008G/United%20States%20Rep%20District%205.htm',
    'https://secure2.hamiltoncounty.in.gov/Elections/2008G/State%20Senator%20District%2020.htm', 'https://secure2.hamiltoncounty.in.gov/Elections/2008G/State%20Senator%20District%2028.htm',
    'https://secure2.hamiltoncounty.in.gov/Elections/2008G/State%20Senator%20District%2030.htm', 'https://secure2.hamiltoncounty.in.gov/Elections/2008G/State%20Representative%20District%2029.htm',
    'https://secure2.hamiltoncounty.in.gov/Elections/2008G/State%20Representative%20District%2032.htm', 'https://secure2.hamiltoncounty.in.gov/Elections/2008G/State%20Representative%20District%2035.htm',
    'https://secure2.hamiltoncounty.in.gov/Elections/2008G/State%20Representative%20District%2036.htm', 'https://secure2.hamiltoncounty.in.gov/Elections/2008G/State%20Representative%20District%2038.htm',
    'https://secure2.hamiltoncounty.in.gov/Elections/2008G/State%20Representative%20District%2039.htm', 'https://secure2.hamiltoncounty.in.gov/Elections/2008G/State%20Representative%20District%2086.htm',
    'https://secure2.hamiltoncounty.in.gov/Elections/2008G/State%20Representative%20District%2087.htm', 'https://secure2.hamiltoncounty.in.gov/Elections/2008G/State%20Representative%20District%2088.htm'
]

for url in urls:
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html)

    office = soup.find('div', {'class':'s5_'}).findAll('span')[1].text
    if 'District' in office:
        office, district = office.split(' District ')
        district = district.strip()
    else:
        district = None
    candidate_headers = [x.text.replace('&nbsp;','') for x in soup.find('div', {'class':'s5_'}).findAll('span')[2:-1]]
    candidate_results = soup.findAll('div', {'class':'s0_'})

    for row in candidate_results:
        precinct = row.find('span').text
        cand_pairs = zip(candidate_headers, [x.text for x in row.findAll('span')[1:]])
        for candidate, votes in cand_pairs:
            if "(" in candidate:
                print candidate
                cand, party = candidate.split('(', 1)
                party = party.replace(')', '')
                results.append(['Hamilton', precinct, office, district, party, cand.strip(), votes])
            else:
                results.append(['Hamilton', precinct, office, district, None, candidate, votes])

with open('20081104__in__general__hamilton__precinct.csv', 'wb') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(["county", "precinct", "office", "district", "party", "candidate", "votes"])
    writer.writerows(results)
