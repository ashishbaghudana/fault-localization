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
SOURCE_CODE_SUFFIX = '.source-code.lines'
FORMULA = {'barinel', 'dstar2', 'jaccard', 'muse', 'ochiai', 'opt2', 'tarantula'}


def classname_to_filename(classname):
    """
    Convert classname to filename

    Parameters
    ----------
    classname : str
        the value from of the classname from suspiciouss spectra file
    
    Returns
    -------
    str
        filename
    """
    if '$' in classname:
        classname = classname[:classname.find('$')]
    return classname.replace('.', '/') + '.java'


def stmt_to_line(stmt):
    """
    Convert statement to line

    Parameters
    ----------
    statement : str
        the statement number along with the classname
    
    Returns
    -------
    str
        line number in file
    """
    classname, lineno = stmt.rsplit('#', 1)
    return '{}#{}'.format(classname_to_filename(classname), lineno)


def convert_statement_to_line(source_code_lines_file, statement_suspiciousness, output_file):
    source_code = dict()
    with open(source_code_lines_file) as f:
        for line in f:
            line = line.strip()
            entry = line.split(':')
            key = entry[0]
            if key in source_code:
                source_code[key].append(entry[1])
            else:
                source_code[key] = []
                source_code[key].append(entry[1])

    with open(statement_suspiciousness) as fin:
        reader = csv.DictReader(fin)
        with open(output_file, 'w') as f:
            writer = csv.DictWriter(f, ['Line','Suspiciousness'])
            writer.writeheader()
            for row in reader:
                line = stmt_to_line(row['Statement'])
                susps = row['Suspiciousness']

                writer.writerow({
                    'Line': line,
                    'Suspiciousness': susps})

                # check whether there are any sub-lines
                if line in source_code:
                    for additional_line in source_code[line]:
                        writer.writerow({'Line': additional_line, 'Suspiciousness': susps})
        f.close()
    fin.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--suspiciousness-data-dir', required=True, help='Suspiciousness data directory')
    parser.add_argument('-s', '--source-code-lines', required=True, help='Source code lines directory')
    parser.add_argument('-o', '--output-dir', required=True, help='Output directory')
    parser.add_argument('-f', '--formula', choices=FORMULA, required=False, help='Formula to convert for')

    args = parser.parse_args()

    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        # Lang-3b.source-code.lines
        for bug in bugs:
            source_code_lines_file = os.path.join(args.source_code_lines, 
                    '%s-%sb%s' % (project, bug, SOURCE_CODE_SUFFIX))
            if args.formula == None:
                for key in FORMULA:
                    statement_suspiciousness_file = os.path.join(args.suspiciousness_data_dir, 
                        '%s-%s-%s-suspiciousness' % (project, bug, key))
                    output_file = os.path.join(args.output_dir, '%s-%s-%s-line-suspiciousness' % (project, bug, key))
                    convert_statement_to_line(source_code_lines_file, statement_suspiciousness_file, output_file)
            else:
                statement_suspiciousness_file = os.path.join(args.suspiciousness_data_dir, 
                        '%s-%s-%s-suspiciousness' % (project, bug, args.formula))
                output_file = os.path.join(args.output_dir, '%s-%s-%s-line-suspiciousness' % (project, bug, args.formula))
                convert_statement_to_line(source_code_lines_file, statement_suspiciousness_file, output_file)
