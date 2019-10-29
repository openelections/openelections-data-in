''' 
Description: Parse out election data from Indiana pdf's
Author: Karen Santamaria   
Date Last Edited: Oct. 29, 2019
'''


import csv
import pdftotext
from table import Table, Row
import re
import os
from os import listdir
from os.path import isfile, join

office_names = [
    "President",
    "U.S. Senate",
    "U.S. House",
    "State Senate",
    "State House",
    "Governor",
    "Attorney General",
    "State Treasurer",
    "Secretary of State"]

def is_int(s):
    '''check if a value is an integer'''
    try: 
        int(s)
        return True
    except ValueError:
        return False

def is_candidate_row(line):
    '''check if line is a candidate row with candidate name and votes'''
    return (len(line) > 5 
            and len(line) < 12 
            and is_int(line[0]) 
            and line[3] != '[Election'
            and line[-1].lower() != 'yes' 
            and line[-1].lower() != 'no')
    
def is_office_name(line):
    '''check if the next line is an office name'''
    return (line[0] == 'VOTE')

def is_precinct_name(one_aftr_precinct, two_aftr_precinct):
    '''check if line contains precinct name'''
    
    return ( ( '---VOTES---' in ''.join(one_aftr_precinct) ) or
            ('VOTES' in ''.join(one_aftr_precinct) and 'MAP' in ''.join(two_aftr_precinct) ) )

def is_county_name(line):
    '''check if line contains county name'''
    return (len(line) == 3 and line[1] == 'County,')

def list_to_string(line):
    '''change list to string'''
    return ' '.join(line)

def create_row(office, district, precinct, county, candidate_line):
    '''create row object'''
    total_vote = candidate_line[3]
    party = get_party(candidate_line)
    candidate = get_candidate(candidate_line)
    row = Row(county, precinct, office, district, party, candidate, total_vote)
    return row

def get_no_letter(strng):
    return re.sub(r'[^0-9]+', '', strng)
    
def get_district(office_lst):
    '''
    extract district number if present
    VOTES= 452 State Representative District 17 -> 17
    '''
    district = ''
    for i in range(1, len(office_lst)-1):
        if('dist' in office_lst[i].lower()):
            if(is_int(get_no_letter(office_lst[i+1]))): 
                # if district number after office name
                district = get_no_letter(office_lst[i+1])
            elif(is_int(get_no_letter(office_lst[i+1]))):
                # if district number before office name
                district = get_no_letter(office_lst[i-1])      
    return district

def get_party(candidate_line):
    '''
    get party from a candidate line
    ['16', '10', '0', '26', '7.22%', '(L)', 'Lucy', 'M', 'Brenton'] -> L
    '''
    party = ''
    if not (candidate_line[5].lower() == 'write-in' 
            or candidate_line[5].lower == 'yes'
            or candidate_line[5].lower == 'no'):
        if(candidate_line[5] == '(R)'):
            party = 'R'
        elif(candidate_line[5] == '(D)'):
            party = 'D'
        elif(candidate_line[5] == "(L)"):
            party = 'L'
    return party
    
    
def get_candidate(candidate_line):
    '''get name from a candidate line
    ['16', '10', '0', '26', '7.22%', '(L)', 'JANE', 'M', 'DOE'] -> Jane M Doe
    '''
    candidate = ''
    if(candidate_line[5].lower() == 'write-in'):
        candidate = 'Write-In'
    else:
        for i in range(6, len(candidate_line)):
            candidate_line[i] = candidate_line[i].capitalize() #JANE DOE -> Jane Doe
        candidate = list_to_string(candidate_line[6:])
    return candidate

def get_precinct(precinct_line):
    '''get precinct name formatted'''
    # precinct = precinct_line[2:]
    precinct = precinct_line
    for i in range(0, len(precinct)):
        precinct[i] = precinct[i].capitalize()
    
    precinct = list_to_string(precinct)
    precinct = precinct.replace('Precinct Name: ', '' )
    
    return precinct

def import_pdf(filename):
    '''import pdf and get a list that contains all the lines in list format'''
    with open(filename, "rb") as f:
        pdf = pdftotext.PDF(f)
        
    formatted_lines = []
    for page in pdf:
        lines = page.split('\n')
        for i in range(0, len(lines)):
            lines[i] = lines[i].replace('•', '')
            line_lst = ' '.join(lines[i].split()).split(' ')
            formatted_lines.append(line_lst)
    

    return formatted_lines

def get_office(line):
    '''
    get string line and output office
    VOTES= 371 United States Senator -> U.S. Senate
    US Representative District 2 -> State Representative
    '''
    
    office = list_to_string(line)
    office = office.replace('VOTES', '')
    office = office.replace('=', '')
    office = office.strip()
    office = office.lower()
 
    if( ('us' in office or 'united states' in office or 'u.s.' in office) 
        and ('representative' in office or 'rep' in office) ):
        office = 'U.S. House'
    elif( ('state' in office) 
         and ('representative' in office or 'rep' in office) ):
        office = 'State House'
    elif( ('us' in office or 'united states' in office or 'u.s.' in office) 
        and ('sen' in office) ):
        office = 'U.S. Senate'
    elif('state' in office and not 'd state' in office and 'sen' in office):
        office = 'State Senate'
    elif('secretary' in office and 'state' in office):
        office = 'Secretary of State'
    elif('treasure' in office and 'state' in office):
        office = 'State Treasurer'
    elif('attorney' in office and 'general' in office):
        office = 'Attorney General'
    elif('governor' in office):
        office = 'Governor'
    return office

def is_line_for_csv(line, office, precinct, county):
    return(
        is_candidate_row(line) and
        office in office_names and 
        precinct and
        county
    )
           
def create_table(formatted_lines):
    '''create table to make csv'''

    cur_office = ''
    cur_precinct = ''
    cur_county = get_county_name(formatted_lines).capitalize()
    cur_district = ''
    table = Table()
    for i in range(0, len(formatted_lines)): 
        
        cur_line = formatted_lines[i]
        
        if(is_line_for_csv(cur_line, cur_office, cur_precinct, cur_county)):
            row = create_row(cur_office, cur_district, cur_precinct, cur_county, cur_line)
            table.add_to_table(row)
            
        elif(i < len(formatted_lines)-2 and
              is_office_name(formatted_lines[i-1])):
            cur_district = get_district(cur_line)
            cur_office = get_office(cur_line)
            
        elif(i<len(formatted_lines)-2 and
              is_precinct_name(formatted_lines[i+1], formatted_lines[i+2])):
            cur_precinct = get_precinct(cur_line)
            
    
    return table

def get_election_date(formatted_lines):
    '''get election date from file'''
    date = 'ENTER_DATE__'
    for i in range (0, len(formatted_lines)):
        line_str = list_to_string(formatted_lines[i])

        if('Election Date:' in line_str):
            date_unf = (line_str[
                line_str.find(':')+2:
                    line_str.find(':')+2+10]).strip()
            date_unf = date_unf.replace(']', '')
            date_lst = date_unf.split('/')
            
            if (len(date_lst) == 3):
                year = date_lst[2]
                month = date_lst[0]
                day = date_lst[1]
                if (len(month) == 1):
                    month = '0' + month
                if (len(day) == 1):
                    day = '0' + day
                date = year+month+day
                break
    return date
    
    

def get_out_filename(formatted_lines):
    '''get filename for csv output'''
    return (get_election_date(formatted_lines) + 
                '__in__general__' +  
                get_county_name(formatted_lines) +
                '__precinct.csv')

def get_county_name(formatted_lines):
    '''get county name'''
    county = 'GET_COUNTY_NAME'
    for cur_line in formatted_lines:
        if (is_county_name(cur_line)):
            county = cur_line[0].lower()
            break
    return county

def main():
    csv_out_dir = input('Enter folder location for csv output: ')
    
    pdf_in_dir = input('Enter folder location of .pdf files: ')
    
    pdf_lst = [f for f in listdir(pdf_in_dir) 
               if (isfile(join(pdf_in_dir, f)) and f.endswith('.pdf') and 'general' in f)]
    
    for pdf_filename in pdf_lst:
        pdf_file = pdf_in_dir + pdf_filename
        imported_pdf = import_pdf(pdf_file)
        table = create_table(imported_pdf)
        csv_filename = get_out_filename(imported_pdf)
        if(len(table.get_rows())):
            table.convert_to_csv(csv_out_dir + csv_filename)
                
if __name__ == "__main__":
    main()

