import argparse
import csv
import os


FORMULA = {'barinel', 'dstar2', 'jaccard', 'muse', 'ochiai', 'opt2', 'tarantula'}


def get_lines(data, num_lines):
    """
    Get the line numbers from the dataset

    Parameters
    ----------
    data : OrderedDict
        an OrderedDict containing information about lines present in a bug
    num_lines : int
        number of lines to consider for each bug

    Returns
    -------
    list : an array of lines
    """
    lines = []
    for i in range(1, num_lines+1):
        lines.append(data['line_%s' % i])
    return lines


def multiplicative_reweighting(data, num_lines):
    """
    Simple reweight multiplies all the values of suspiciousness across all formulae

    Parameters
    ----------
    data : OrderedDict
        each row of the csv file represents an OrderedDict called data
    num_lines : int
        number of lines to consider for each bug

    Returns
    -------
    list : a reweighted suspiciousness value for each line in the bug
    """
    hybrid_suspiciousness = [1000 for _ in range(num_lines)]
    for i in range(1, num_lines+1):
        for formula in FORMULA:
            key = 'line_%s_%s' % (i, formula)
            if data[key] is None:
                return None
            hybrid_suspiciousness[i-1] *= float(data[key])
    return hybrid_suspiciousness


def reweight_dataset(dataset, num_lines, output_dir):
    """
    Reweight a dataset based on the multiplicative principle

    Parameters
    ----------
    dataset : str
        a csv file containing the dataset
    num_lines : int
        number of lines to consider for each bug
    output_dir : str
        output directory for storing the csv files
    """
    with open(dataset) as freader:
        csvreader = csv.DictReader(freader)
        for row in csvreader:
            suspiciousness = multiplicative_reweighting(row, num_lines)
            if suspiciousness is None:
                continue
            lines = get_lines(row, num_lines)
            output = os.path.join(output_dir, 'reweighted-%s-%s.csv' % (row['project'], row['bug']))
            with open(output, 'w') as fwriter:
                fwriter.write('Line,Suspiciousness\n')
                for line, susp in zip(lines, suspiciousness):
                    fwriter.write('%s,%s\n' % (line, susp))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset', required=True, help='path to the dataset csv')
    parser.add_argument('-n', '--num-lines', required=True, type=int, help='number of lines for each bug')
    parser.add_argument('-o', '--output-dir', required=True,
                        help='output directory to write reweighted suspiciousness to')

    args = parser.parse_args()

    reweight_dataset(args.dataset, args.num_lines, args.output_dir)
