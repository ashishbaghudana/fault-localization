import argparse
import sys
import csv
import operator
import os


PROJECTS = ['Closure', 'Lang', 'Chart', 'Math', 'Mockito', 'Time']
PROJECT_BUGS = [
    [str(x) for x in range(1, 134)],
    [str(x) for x in range(1, 66)],
    [str(x) for x in range(1, 27)],
    [str(x) for x in range(1, 107)],
    [str(x) for x in range(1, 39)],
    [str(x) for x in range(1, 28)]
]
FORMULA = ['barinel', 'dstar2', 'jaccard', 'muse', 'ochiai', 'opt2', 'tarantula']


def sort(input_csv, output_csv, column=1):
    """
    Sort a csv based on a column

    Parameters
    ----------
    input_csv : str
        input csv file
    output_csv : str
        output csv file
    column : int
        the column number to sort the input csv file on
    """
    data = csv.reader(open(input_csv),delimiter=',')
    sortedlist = sorted(data, key=operator.itemgetter(column))
    sortedlist.reverse()
    
    with open(output_csv, 'w') as f:
        fileWriter = csv.writer(f, delimiter=',')
        for row in sortedlist:
            fileWriter.writerow(row)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--suspiciousness-data-dir', required=True, help='Suspiciousness data directory')
    parser.add_argument('-o', '--output-dir', required=True, help='Output directory')
    
    args = parser.parse_args()

    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        for bug in bugs:
            for formula in FORMULA:
                input_csv = '%s-%s-%s-line-suspiciousness' % (project, bug, formula)
                output_csv = '%s-%s-%s-sorted-susp' % (project, bug, formula)
                sort(os.path.join(args.suspiciousness_data_dir, input_csv), 
                     os.path.join(args.output_dir, output_csv))
