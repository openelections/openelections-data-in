''' 
Description: Parse out election data from Indiana pdf's
 & Year: Clay 2018 GE, Morgan 2018 GE, Randolph 2018 GE
Author: Karen Santamaria   
'''


import csv
import pdftotext
from table import Table, Row
from utils import standardize_office_name
import re
import os
from os import listdir
from os.path import isfile, join


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
    '''
    check if line contains precinct name by using the two lines after it 
    since precinct is not explicitly stated but the two lines following precinct names are
    always the same
    '''
    
    return ( ( '---VOTES---' in ''.join(one_aftr_precinct) ) or
            ('VOTES' in ''.join(one_aftr_precinct) and 'MAP' in ''.join(two_aftr_precinct) ) or
            ('VOTES' in ''.join(one_aftr_precinct) and not '=' in ''.join(one_aftr_precinct) ) 
            )

def is_county_name(line):
    '''check if line contains county name'''
    return (len(line) == 3 and line[1] == 'County,')

def list_to_string(line):
    '''change list to string'''
    return ' '.join(line)

def create_row(office, district, precinct, county, candidate_line):
    '''
    create row which contains all necessary information for csv
    parses out information from candidate likes which looks like this:
    ['16', '10', '0', '26', '7.22%', '(L)', 'Lucy', 'M', 'Brenton']
    and uses infomation that was obtained previously (office, district, precinct, county)
    '''
    machine = candidate_line[0]
    absente = candidate_line[1]
    prov = candidate_line[2]
    total_vote = candidate_line[3]
    if(is_int(total_vote)): #prevent 'election' from being vote. 
        party = get_party(candidate_line)
        candidate = get_candidate(candidate_line)
        row = Row(county, precinct, office, district, party, candidate, total_vote,election_day=machine, provisional=prov, absentee=absente)
        return row
    else:
        return None #could not create row

def get_no_letter(strng):
    '''get only the numbers from a string''' 
    return re.sub(r'[^0-9]+', '', strng)
    
def get_district(office_lst):
    '''
    extract district number if present in an unformatted list that contains office
    SAMPLE INPUT : [VOTES=, 452, State, Representative, District, 17]
    SAMPLE OUTPUT = 17
    '''
    district = ''
    for i in range(1, len(office_lst)-1):
        if('dist' in office_lst[i].lower()):
            if(is_int(get_no_letter(office_lst[i+1]))): 
                # if district number after office name
                district = get_no_letter(office_lst[i+1])
            elif(is_int(get_no_letter(office_lst[i-1]))):
                # if district number before office name
                district = get_no_letter(office_lst[i-1])      
    return district

def get_party(candidate_line):
    '''
    get party from a 'candidate line'
    SAMPLE INPUT: ['16', '10', '0', '26', '7.22%', '(D)', 'Lucy', 'M', 'Brenton'] 
    SAMPLE OUTPUT: D
    '''
    party = ''
    if not (candidate_line[5].lower() == 'write-in' 
            or candidate_line[5].lower == 'yes'
            or candidate_line[5].lower == 'no'):
        if(candidate_line[5].lower() == '(r)'):
            party = 'R'
        elif(candidate_line[5].lower() == '(d)'):
            party = 'D'
        elif(candidate_line[5].lower() == '(l)'):
            party = 'L'
    return party
    
    
def get_candidate(candidate_line):
    '''
    get name from a 'candidate line' which is a list
    SAMPLE INPUT: ['16', '10', '0', '26', '7.22%', '(L)', 'JANE', 'M', 'DOE']
    SAMPLE OUTPUT: 'Jane M Doe'
    '''
    candidate = ''
    if(candidate_line[5].lower() == 'write-in'):
        candidate = 'Write in'
    else:
        candidate = list_to_string(candidate_line[6:]) #take out voting and party
        candidate = ' '.join(word.capitalize() for word in candidate.split()) #capitalize
        
    return candidate

def get_precinct(precinct_lst):
    '''
    get precinct name formatted from a list that contains precinct information
    SAMPLE INPUT: ['PRECINCT, NAME: , CLAY, PRECINCT, 4, WARD, 2 ']
    SAMPLE OUTPUT: 'Clay P4W2'
    '''
    
    unformatted_precinct = list_to_string(precinct_lst).lower()
    unformatted_precinct = unformatted_precinct.replace('precinct name: ', '' )
    
    if(is_int(unformatted_precinct.split('-')[0]) and len(unformatted_precinct.split('-')) > 1):
        unformatted_precinct = unformatted_precinct.split('-')[1]
    
    precinct = ' '.join(word.capitalize() for word in unformatted_precinct.split())
    
    precinct = precinct.replace('ward ', 'W' )
    precinct = precinct.replace(' precinct ', 'P' )
    precinct = precinct.replace(' ,', '' )
    
    return precinct

def import_pdf(filename):
    '''
    import pdf and get a list of all lines in a pdf and within that, list of all strings
    SAMPLE INPUT: my_dir/to_pdf/county.pdf
    SAMPLE OUTPUT: [['Washington', 'Township', 'Board', 'Member'], 
                    ['VOTES=', '436'], ['150', '22', '0', '172', '39.45%', '(R)', 'RICHARD', '(RITTER)', 'COX'], 
                    ['112', '20', '0', '132', '30.28%', '(R)', 'RYAN', 'WALTER'], 
                    ].....(.etc very long)]
    '''
    
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

def get_office(unformatted_office):
    '''
    get unformatted_office as string
    SAMPLE INPUT: 'VOTES= 371 United States Senator'
    SAMPLE OUTPUT: 'U.S. Senate'
    '''

    if('=' in unformatted_office):
        unformatted_office = unformatted_office.replace('VOTES', '')
        unformatted_office = unformatted_office.replace('=', '')
        unformatted_office = unformatted_office.strip()
    if(is_int(unformatted_office.split(' ')[0])):
        unformatted_office = list_to_string(unformatted_office.split(' ')[1:])

    office = standardize_office_name(unformatted_office)
    
    return office
    
           
def create_table(formatted_lines):
    '''
    create table to make csv by using list of lists made from import_pdf
    
    SAMPLE INPUT : [['Washington', 'Township', 'Board', 'Member'], 
                    ['VOTES=', '436'], ['150', '22', '0', '172', '39.45%', '(R)', 'RICHARD', '(RITTER)', 'COX'], 
                    ['112', '20', '0', '132', '30.28%', '(R)', 'RYAN', 'WALTER'], 
                    ].....(.etc very long)] 
    SAMPLE OUTPUT: Table(...) (A table with rows inside)
    '''
    table = Table()
    
    #keep track of information not within of 'candidate line' but needed for csv row
    cur_office = ''
    cur_precinct = ''
    cur_county = get_county_name(formatted_lines)
    cur_district = ''
    
    
    for i in range(0, len(formatted_lines)): 
        cur_line = formatted_lines[i]
        if(is_candidate_row(cur_line) and cur_office != None and cur_precinct):
            # make the csv row, add to table
            row = create_row(cur_office, cur_district, cur_precinct, cur_county, cur_line)
            if (row != None):
                table.add_to_table(row)
        elif(is_office_name(cur_line)):
            # check if office name and from that get district and format office name
            cur_district = get_district(formatted_lines[i+1])
            cur_office = get_office(list_to_string(formatted_lines[i+1]).strip())
        elif(i < len(formatted_lines)-2 and is_precinct_name(formatted_lines[i+1], formatted_lines[i+2]) ):
            cur_precinct = get_precinct(cur_line)
        elif(is_county_name(cur_line)):
            cur_county = cur_line[0]
    
    return table

def get_election_date(formatted_lines):
    ''' 
    get election date as '11/9/17' 
    transform to 20171109
    '''
    date = '' 
    if(len(formatted_lines) > 1 and 
        len(formatted_lines[-2]) > 5 and 
        len(formatted_lines[-2][5])> 0):
        date_lst = formatted_lines[-2][5][:-1].split('/')
        
        if (len(date_lst) == 3):
            year = date_lst[2]
            month = date_lst[0]
            day = date_lst[1]
            
            if (len(month) == 1):
                month = '0' + month
            if (len(day) == 1):
                day = '0' + day
            date = year + month + day
            
    return date
    
    

def get_out_filename(formatted_lines):
    '''get filename for csv output by using imported pdf
    SAMPLE INPUT : [['Washington', 'Township', 'Board', 'Member'], 
                ['VOTES=', '436'], ['150', '22', '0', '172', '39.45%', '(R)', 'RICHARD', '(RITTER)', 'COX'], 
                ['112', '20', '0', '132', '30.28%', '(R)', 'RYAN', 'WALTER'], 
                ].....(etc. very long)]
    SAMPLE OUTPUT: 20181106__in__general__whitley__precinct.csv
    '''
    
    date = get_election_date(formatted_lines)
    state = 'in'
    election_type = 'general'
    result_type = 'precinct'
    county = get_county_name(formatted_lines).lower()
    
    filename = "__".join([date, state, election_type, county, result_type]) + '.csv'
    
    return filename

def get_county_name(formatted_lines):
    '''get county name for filename
    SAMPLE INPUT : [..., ['Precinct', 'Summary', 'Report'], 
                    ['Whitley', 'County,', 'Indiana'], 
                    ['2018', 'General', 'Election'], ['INWHIG18'], ['11/6/2018'], 
                    ...] (etc. very long) 
    SAMPLE OUTPUT: 20181106__in__general__whitley__precinct.csv
    '''
    
    county = ''
    for cur_line in formatted_lines:
        if (is_county_name(cur_line)):
            return cur_line[0].capitalize()
    return county

def create_csv(in_filepath, out_filepath):
    '''
    SAMPLE INPUT: my_dir/2018 GE Clay Precinct Report.pdf (in_filepath)
                  my_dir/20181106__in__general__clay__precinct.csv (out_filepath)
                  
    SAMPLE OUTPUT: ---csv with desired filepath and within the csv rows shown below---
                county,precinct,office,district,party,candidate,votes,,,,
                Clay,Brazil 1,U.S. Senate,,R,Mike Braun,260,,,,,
                Clay,Brazil 1,U.S. Senate,,D,Joe Donnelly,136,,,,,

    ''' 
    
    if (in_filepath.endswith('.pdf')):
        imported_pdf = import_pdf(in_filepath)
        table = create_table(imported_pdf)
        csv_filename = get_out_filename(imported_pdf)
        if (len(table.get_rows()) > 0):
            table.convert_to_csv(out_filepath + csv_filename)
        else:
            print('Could not parse:', in_filepath)
        
def main():
    
    in_filepath = input("Enter file or folder to parse: ").strip()
    csv_out_dir = input("Enter output directory: ").strip()
    
    csv_out_dir = csv_out_dir if csv_out_dir.endswith('/') else csv_out_dir+'/'

    if not os.path.exists(csv_out_dir):
            os.mkdir(csv_out_dir)
    
    if (in_filepath.endswith('.pdf')):
        create_csv(in_filepath, csv_out_dir)
    else:
        in_filepath = in_filepath if in_filepath.endswith('/') else in_filepath+'/'
        pdf_lst = [f for f in listdir(in_filepath) if (isfile(join(in_filepath, f)) and f.endswith('.pdf'))]
        
        for pdf_filename in pdf_lst:
            create_csv(in_filepath + pdf_filename, csv_out_dir)
                
if __name__ == "__main__":
    main()

