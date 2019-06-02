import csv

source = '/Users/derekwillis/Downloads/porter_2018_general.htm'
offices = ['STRAIGHT PARTY', 'US SENATOR', 'SECT OF STATE', 'STATE AUDITOR', 'STATE TREASURER', 'US REP DST 1', 'STATE SENATOR DST 4', 'STATE REP DST 11', 'STATE REP DST 4', 'STATE REP DST 9', 'STATE REP DST 10', 'STATE REP DST 19', 'PUBLIC QUESTION #1',
'SUPER. CT JUDGE 2', 'SUPER. CT JUDGE 6', 'COUNTY PROSECUTOR', 'COUNTY CLERK', 'COUNTY AUDITOR', 'COUNTY RECORDER', 'COUNTY SHERIFF', 'COUNTY CORONER', 'COUNTY ASSESSOR', 'COMMISSIONER DST 2 CENTER', 'COUNTY COUNCIL DST 4', 'BOONE TRUSTEE', 'BOONE TWP BOARD',
'MSD BOONE SCHOOL BD MBR DST 1', 'MSD BOONE SCHOOL BD MBR DST 2', 'MSD BOONE SCHOOL BD MBR DST 3', 'JUSTICE OF THE SUPREME COURT', 'JDG OF THE COURT OF APPEALS DIST 2', 'COUNTY COUNCIL DST 3', 'CENTER TRUSTEE', 'CENTER TWP BOARD', 'COUNTY COUNCIL DST 1',
'JACKSON TRUSTEE', 'JACKSON TWP BOARD', 'DUNELAND SCHOOL BD MBR AT-LARGE', 'LIBERTY TRUSTEE', 'DUNELAND SCHOOL BD MBR LIB TWP', 'DUNELAND SCHOOL BD MBR WST/PNE TWP', 'MORGAN TRUSTEE', 'MORGAN TWP BOARD', 'EPCS BOARD MBR DST 1 - MORGAN', 'EPCS BOARD MBR DST 2 - PLEASANT',
'EPCS BD MBR DST 3 - WAS TWP', 'PINE TRUSTEE', 'PINE TWP BOARD', 'MCAS BD MBR AT-LARGE MICHIGAN CITY', 'MCAS BD MBR CIVIL CITY AT-LARGE', 'PLEASANT TRUSTEE', 'PLEASANT TWP BOARD', 'KOUTS TOWN COUNCIL DST 2', 'KOUTS TOWN COUNCIL DST 4', 'COUNTY COUNCIL DST 2',
'PORTAGE TWP ASSESSOR', 'PORTAGE TRUSTEE', 'PORTAGE TWP BOARD', 'PORTAGE TWP SCHOOL BD MBR AT-LARGE', 'PORTAGE TWP SCHOOL BD MBR DST 1', 'PORTAGE TWP SCHOOL BD MBR DST 2', 'PORTER TRUSTEE', 'PORTER TWP BOARD', 'PORTER TWP SCHOOL BD MBR AT-LARGE', 'PORTER TWP SCHOOL BD MBR DST 1',
'PORTER TWP SCHOOL BD MBR DST 3', 'UNION TRUSTEE', 'UNION TWP BOARD', 'UNION TWP SCHOOL BD MBR AT-LARGE', 'UNION TWP SCHOOL BD MBR DST 2', 'UNION TWP SCHOOL BD MBR DST 4', 'WASHINGTON TRUSTEE', 'WASHINGTON TWP BOARD', 'WESTCHESTER TRUSTEE', 'WESTCHESTER TWP BOARD', 'LIBERTY TWP BOARD',
'OGDEN DUNES CLERK', 'TOWN OF OGDEN DUNES DIST 5']

lines = open(source).readlines()
results = []

for line in lines:
    if line == '\n':
        continue
    if "<" in line:
        continue
    if "OFFICIAL  REPORT\n" in line:
        continue
    if "RUN DATE" in line:
        continue
    if "RUN TIME" in line:
        precinct = None
        continue
    if "VOTES  PERCENT" in line:
        continue
    if 'VOTE FOR ' in line:
        continue
    if 'VOTER TURNOUT - TOTAL' in line:
        continue
    if 'Total .' in line:
        continue
    if any(o in line for o in offices):
        office = line.strip()
    if "           " not in line:
        if not any(o in line for o in offices):
            precinct = line.strip()
    if ".  ." in line:
        # this is a result line
        if "REGISTERED VOTERS" in line:
            office = None
            candidate = "Registered Voters"
            party = None
            votes = line.split('.  .', 1)[1].split(' ',1)[1].replace('.','').strip()
        elif "BALLOTS CAST" in line:
            office = None
            candidate = "Ballots Cast"
            party = None
            votes = line.split('.  .', 1)[1].split(' ',1)[1].replace('.','').strip()
        elif 'WRITE-IN' in line:
            candidate = 'Write-ins'
            party = None
            votes = line.split('    ', 3)[3].split('   ')[0].strip()
        else:
            print line
            try:
                candidate, party = line.split('    ', 3)[2].split(').')[0].split(' (')
                party = party[0:3]
                candidate = candidate.strip()
                votes = line.split('    ', 3)[3].split('   ')[0].strip()
            except:
                candidate = line.split('  ')[0]
                party = None
                votes = line.split('    ', 3)[3].split('   ')[0].strip()
        results.append(['Porter', precinct, office, None, party, candidate, votes])

with open('20181106__in__general__porter__precinct.csv', 'wt') as csvfile:
    w = csv.writer(csvfile)
    headers = ['county', 'precinct', 'office', 'district', 'party', 'candidate', 'votes']
    w.writerow(headers)
    w.writerows(results)
