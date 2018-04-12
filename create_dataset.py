import argparse
import csv
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
FORMULA = {'barinel', 'dstar2', 'jaccard', 'muse', 'ochiai', 'opt2', 'tarantula'}


class Dataset(object):
    def __init__(self, formula, num_lines):
        self.base_formula = formula
        self.rows = {}
        self.num_lines = num_lines
        for project in PROJECTS:
            self.rows[project] = {}

    def to_csv(self, output_csv):
        """
        Write dataset to output csv file

        Parameters
        ----------
        output_csv : str
            Output file to write the dataset to
        """
        output = []
        columns = 'project,bug,'
        columns += ','.join(['line_%s' % (i+1) for i in range(self.num_lines)])
        for formula in FORMULA:
            for i in range(self.num_lines):
                columns += ',line_%s_%s' % (i+1, formula)
        output.append(columns)
        for project in PROJECTS:
            for bug in self.rows[project]:
                output.append(self.rows[project][bug].to_csv())
        with open(output_csv, 'w') as fwriter:
            fwriter.write('\n'.join(output))

    def __len__(self):
        return self.num_lines


class Row(object):
    """
    The row class holds information about a specific row. Mainly, it holds information about the project, bug_id,
    lines affected, suspiciousness scores for each line given by that formula
    """
    def __init__(self, project, bug_id):
        self.project = project
        self.bug_id = bug_id
        self.lines = []
        self.data = {}

        for formula in FORMULA:
            self.data[formula] = []

    def to_csv(self):
        lines_output = ','.join(self.lines)
        suspiciousness = []
        for formula in FORMULA:
            susp = ','.join([str(x) for x in self.data[formula]])
            suspiciousness.append(susp)
        return '%s,%s,%s,' % (self.project, self.bug_id, lines_output) + ','.join(suspiciousness)


def add_rows_for_formula(dataset, data_dir, formula):
    """
    Add rows for a particular formula to the dataset

    Parameters
    ----------
    dataset : Dataset
        an object of the type dataset with dataset.lines already populated
    data_dir : str
        the data directory for the suspiciousness files
    formula : str
        formula to add for

    Returns
    -------
    None
    """
    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        for bug in bugs:
            data = {}
            input_file = os.path.join(data_dir, '%s-%s-%s-sorted-susp' % (project, bug, formula))
            with open(input_file) as freader:
                csvreader = csv.DictReader(freader)
                for line in csvreader:
                    data[line['Line']] = float(line['Suspiciousness'])
            for line in dataset.rows[project][bug].lines:
                if line in data:
                    dataset.rows[project][bug].data[formula].append(data[line])
                else:
                    dataset.rows[project][bug].data[formula].append(0.0)


def create_dataset(data_dir, formula, num_lines):
    """
    Create a dataset object and add rows from the sorted suspiciousness value file to it

    Parameters
    ----------
    data_dir : str
        the data directory for the suspiciousness files
    formula : str
        formula to use as the base
    num_lines : str
        number of lines to read from the csv

    Returns
    -------
    Dataset
        a dataset object
    """
    dataset = Dataset(formula, num_lines)
    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        for bug in bugs:
            row = Row(project=project, bug_id=bug)
            input_file = os.path.join(data_dir, '%s-%s-%s-sorted-susp' % (project, bug, formula))
            with open(input_file) as freader:
                csvreader = csv.DictReader(freader)
                for line in csvreader:
                    row.lines.append(line['Line'])
                    row.data[formula].append(float(line['Suspiciousness']))
                    if len(row.lines) == num_lines:
                        break
            dataset.rows[project][bug] = row
    return dataset


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--formula', required=True, choices=FORMULA,
                        help='Base formula to use while creating the dataset')
    parser.add_argument('-d', '--data-dir', required=True, help='Data directory with all sorted suspiciousness values')
    parser.add_argument('-n', '--num-lines', required=True, type=int, help='Number of lines to consider')
    parser.add_argument('-o', '--output-dir', required=True, help='Output directory to write dataset to')

    args = parser.parse_args()

    dataset = create_dataset(args.data_dir, args.formula, args.num_lines)
    for formula in FORMULA:
        if formula != args.formula:
            add_rows_for_formula(dataset, args.data_dir, formula)
    dataset.to_csv(os.path.join(args.output_dir, 'dataset-%s-%s.csv' % (args.formula, args.num_lines)))
