import argparse
import sys
import csv
import operator
import os
import re
import datetime
from subprocess import call

PROJECTS = ['Closure', 'Lang', 'Chart', 'Math', 'Mockito', 'Time']

PROJECT_BUGS = [
    [str(x) for x in range(1, 134)],
    [str(x) for x in range(1, 66)],
    [str(x) for x in range(1, 27)],
    [str(x) for x in range(1, 107)],
    [str(x) for x in range(1, 39)],
    [str(x) for x in range(1, 28)]
]

#FORMULA = ['barinel', 'dstar2', 'jaccard', 'muse', 'ochiai', 'opt2', 'tarantula']
FORMULA = ['tarantula']


def find_recency(input_file, output_file, project, bug, formula):
    """
    find the recency of the last update for every suspiciouss line

    Parameters
    ----------
    input_file : str (file contains sorted suspicousness lines with date)
    output_file: str (file contains sorted suspiciousness lines file with date, author and recency)
    project: str (project name)
    bug: str (bug id) 
    formula: str (fault localization technique)
    commit_id: str (commit id of the buggy vesion)

    """
   
    input_file = "/home/kanag23/Desktop/Fault_loc/Python_scripts_Apr_10/" + input_file
    sorted_susp_lines = read_susp_lines_from_file(input_file)
    
    # output file
    output_file = "/home/kanag23/Desktop/Fault_loc/Python_scripts_Apr_10/" + output_file

    dates = []

    for susp_line in sorted_susp_lines:
        date = susp_line[-1].strip()
        if date != "NOT_FOUND":
            datetime_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
            bug_date = datetime_obj.date()
        else:
            return
        dates.append(bug_date)

    if max(dates) == datetime.date.today():
        first_max_date = max(dates)
        try:
            second_max_date = sorted(set(dates))[-2]
        except IndexError:
            return
        dates = [date if date != first_max_date else second_max_date  for date in dates]

    min_date = min(dates)
    max_date = max(dates)

    no_of_days_elapsed = []

    for date in dates:
        no_of_days_elapsed.append((max_date - date).days)

    min_days = min(no_of_days_elapsed)
    max_days = max(no_of_days_elapsed)
    diff_days = max_days - min_days

    line_counter = 0

    for susp_line in sorted_susp_lines:
        if diff_days == 0:
            print("Divide by Zero: Max and Min are same")
            continue
        normalized_time = (no_of_days_elapsed[line_counter] - min_days)/diff_days
        recency = 1 - normalized_time      
        add_recency_to_file(output_file, susp_line, recency)
        line_counter += 1
        

def add_recency_to_file(output_file, susp_line, recency):
    """
    appends the author and date to the output file containing suspiciousness lines
    
    Paramaeters:
    ------------
    output_file: str 
    susp_line: str
    recency: str

    """
    susp_line = ", ".join(susp_line)
    with open(output_file, mode="a", encoding="utf-8") as myFile:
        myFile.write(f"{susp_line}, {recency}\n")


def read_susp_lines_from_file(input_file):
    """
    reads the suspiciousness lines data from the sorted suspiciousness file

    Parameters:
    ----------
    input_file: str

    return:
    ------
    sorted_susp_lines: list (2D)

    """
    susp_data = csv.reader(open(input_file), delimiter=',')
    sorted_susp_lines = [susp_line for susp_line in susp_data]
    
    return sorted_susp_lines   
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--suspiciousness-data-dir', required=True, help='Suspiciousness data directory')
    parser.add_argument('-o', '--output-dir', required=True, help='Output directory')

    args = parser.parse_args()

    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        for bug in bugs:
            for formula in FORMULA:
                input_csv = f"{project}-{bug}-{formula}-sorted-susp-with-date"
                output_csv = f"{project}-{bug}-{formula}-sorted-susp-with-recency"
                find_recency(os.path.join(args.suspiciousness_data_dir, input_csv),
                     os.path.join(args.output_dir, output_csv), project, bug, formula)
