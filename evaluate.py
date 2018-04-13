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
BUGGY_LINES_SUFFIX = 'buggy.lines'


def get_reweighted_lines(input_file, top_n):
    lines = set()
    index = 0
    with open(input_file) as freader:
        csvreader = csv.DictReader(freader)
        for row in csvreader:
            lines.add(row['Line'])
            index += 1
            if index >= top_n:
                break
    return lines


def get_buggy_lines(input_file):
    buggy_lines = set()
    with open(input_file) as freader:
        for line in freader:
            buggy_lines.add('#'.join(line.split('#')[0:2]))
    return buggy_lines


def calculate_accuracy(input_dir, bug_dir, top_n):
    accuracies = []
    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        for bug in bugs:
            try:
                input_file = os.path.join(input_dir, 'reweighted-%s-%s.csv' % (project, bug))
                reweighted_lines = get_reweighted_lines(input_file, top_n)
                bug_file = os.path.join(bug_dir, '%s-%s.%s' % (project, bug, BUGGY_LINES_SUFFIX))
                buggy_lines = get_buggy_lines(bug_file)
                accuracy = len(reweighted_lines.intersection(buggy_lines)) / len(buggy_lines)
                accuracies.append(accuracy)
            except:
                continue
    return sum(accuracies) / len(accuracies)


def calculate_accuracy_formula(input_dir, bug_dir, formula, top_n):
    accuracies = []
    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        for bug in bugs:
            try:
                input_file = os.path.join(input_dir, '%s-%s-%s-sorted-susp' % (project, bug, formula))
                reweighted_lines = get_reweighted_lines(input_file, top_n)
                bug_file = os.path.join(bug_dir, '%s-%s.%s' % (project, bug, BUGGY_LINES_SUFFIX))
                buggy_lines = get_buggy_lines(bug_file)
                accuracy = len(reweighted_lines.intersection(buggy_lines)) / len(buggy_lines)
                accuracies.append(accuracy)
            except:
                continue
    return sum(accuracies) / len(accuracies)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--input-dir', required=True, help='Path to input directory')
    parser.add_argument('-b', '--bug-dir', required=True, help='Path to directory containing bugs')
    parser.add_argument('-n', '--top-n', required=True, type=int, help='Top-n accuracy')
    parser.add_argument('-f', '--formula', required=False, help='Supply a formula to check against')

    args = parser.parse_args()

    if args.formula is None:
        accuracy = calculate_accuracy(args.input_dir, args.bug_dir, args.top_n)
        print(accuracy)
    else:
        accuracy = calculate_accuracy_formula(args.input_dir, args.bug_dir, args.formula, args.top_n)
        print(accuracy)
