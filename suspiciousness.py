from __future__ import division
from __future__ import print_function
from glob import glob

import collections
import re
import argparse
import csv
import os
import sys


def eprint(*args, **kwargs):
    """
    Print to stderr
    """
    print(*args, file=sys.stderr, **kwargs)


def tarantula(passed, failed, totalpassed, totalfailed):
    """
    Calculates the Tarantula suspiciousness score for the line
    Adapted directly from: https://bitbucket.org/rjust/fault-localization-data/
    in file analysis/pipeline-scripts/crush-matrix

    Parameters
    ----------
    passed : int
        number of test cases passed with the line
    failed : int
        number of test cases failed with the line
    totalpassed : int
        total number of test cases passed
    totalfailed : int
        total number of test cases failed

    Returns
    -------
    float
        the Tarantula suspiciousness value
    """
    if totalpassed == 0 or totalfailed == 0 or (passed+failed == 0):
        return 0
    return (failed/totalfailed)/(failed/totalfailed + passed/totalpassed)


def tarantula_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
    """
    Calculates the Tarantula suspiciousness score for the line
    Adapted directly from: https://bitbucket.org/rjust/fault-localization-data/
    in file analysis/pipeline-scripts/crush-matrix

    Parameters
    ----------
    passed : int
        number of test cases passed with the line
    failed : int
        number of test cases failed with the line
    totalpassed : int
        total number of test cases passed
    totalfailed : int
        total number of test cases failed
    was_covered : bool

    Returns
    -------
    float
        the Tarantula hybrid suspiciousness value
    """
    if totalpassed == 0 or totalfailed == 0 or (passed+failed == 0):
        return 0
    return (passed/totalpassed + (1 if was_covered else 0)/(passed/totalpassed + failed/totalfailed))


def ochiai(passed, failed, totalpassed, totalfailed):
    """
    Calculates the Ochiai suspiciousness score for the line
    Adapted directly from: https://bitbucket.org/rjust/fault-localization-data/
    in file analysis/pipeline-scripts/crush-matrix

    Parameters
    ----------
    passed : int
        number of test cases passed with the line
    failed : int
        number of test cases failed with the line
    totalpassed : int
        total number of test cases passed
    totalfailed : int
        total number of test cases failed
    
    Returns
    -------
    float
        the Ochiai hybrid suspiciousness value
    """
    if totalfailed == 0 or (passed+failed == 0):
        return 0
    return failed/(totalfailed*(failed+passed))**0.5


def ochiai_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
    """
    Calculates the Ochiai suspiciousness score for the line
    Adapted directly from: https://bitbucket.org/rjust/fault-localization-data/
    in file analysis/pipeline-scripts/crush-matrix

    Parameters
    ----------
    passed : int
        number of test cases passed with the line
    failed : int
        number of test cases failed with the line
    totalpassed : int
        total number of test cases passed
    totalfailed : int
        total number of test cases failed
    was_covered : bool
    
    Returns
    -------
    float
        the Ochiai hybrid suspiciousness value
    """
    if totalfailed == 0 or (passed+failed == 0):
        return 0
    return (failed + (1 if was_covered else 0))/(totalfailed*(failed+passed))**0.5


def opt2(passed, failed, totalpassed, totalfailed):
    """
    Calculates the Opt2 suspiciousness score for the line
    Adapted directly from: https://bitbucket.org/rjust/fault-localization-data/
    in file analysis/pipeline-scripts/crush-matrix

    Parameters
    ----------
    passed : int
        number of test cases passed with the line
    failed : int
        number of test cases failed with the line
    totalpassed : int
        total number of test cases passed
    totalfailed : int
        total number of test cases failed
    
    Returns
    -------
    float
        the Opt2 hybrid suspiciousness value
    """
    return failed - passed/(totalpassed+1)


def opt2_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
    """
    Calculates the Opt2 suspiciousness score for the line

    Adapted directly from: https://bitbucket.org/rjust/fault-localization-data/
    in file analysis/pipeline-scripts/crush-matrix

    Parameters
    ----------
    passed : int
        number of test cases passed with the line
    failed : int
        number of test cases failed with the line
    totalpassed : int
        total number of test cases passed
    totalfailed : int
        total number of test cases failed
    was_covered : bool
    
    Returns
    -------
    float
        the Opt2 hybrid suspiciousness value
    """
    return failed - (passed-(1 if was_covered else 0))/(totalpassed+1)


def barinel(passed, failed, totalpassed, totalfailed):
    """
    Calculates the barinel suspiciousness score for the line

    Adapted directly from: https://bitbucket.org/rjust/fault-localization-data/
    in file analysis/pipeline-scripts/crush-matrix

    Parameters
    ----------
    passed : int
        number of test cases passed with the line
    failed : int
        number of test cases failed with the line
    totalpassed : int
        total number of test cases passed
    totalfailed : int
        total number of test cases failed
    
    Returns
    -------
    float
        the barinel hybrid suspiciousness value
    """
    if failed == 0:
        return 0
    h = passed/(passed+failed)
    return 1-h


def barinel_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
    """
    Calculates the Barinel suspiciousness score for the line

    Adapted directly from: https://bitbucket.org/rjust/fault-localization-data/
    in file analysis/pipeline-scripts/crush-matrix

    Parameters
    ----------
    passed : int
        number of test cases passed with the line
    failed : int
        number of test cases failed with the line
    totalpassed : int
        total number of test cases passed
    totalfailed : int
        total number of test cases failed
    was_covered : bool
    
    Returns
    -------
    float
        the Barinel hybrid suspiciousness value
    """
    if failed == 0:
        return 0
    h = (passed - (1 if was_covered else 0))/(passed+failed)
    return 1-h

def dstar2(passed, failed, totalpassed, totalfailed):
    """
    Calculates the dstar2 suspiciousness score for the line

    Adapted directly from: https://bitbucket.org/rjust/fault-localization-data/
    in file analysis/pipeline-scripts/crush-matrix

    Parameters
    ----------
    passed : int
        number of test cases passed with the line
    failed : int
        number of test cases failed with the line
    totalpassed : int
        total number of test cases passed
    totalfailed : int
        total number of test cases failed
    
    Returns
    -------
    float
        the dstar2 hybrid suspiciousness value
    """
    if passed + totalfailed - failed == 0:
        assert passed==0 and failed==totalfailed
        return totalfailed**2 + 1 # slightly higher than otherwise possible
    return failed**2 / (passed + totalfailed - failed)


def dstar2_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
    """
    Calculates the dstar2 hybrid suspiciousness score for the line

    Adapted directly from: https://bitbucket.org/rjust/fault-localization-data/
    in file analysis/pipeline-scripts/crush-matrix

    Parameters
    ----------
    passed : int
        number of test cases passed with the line
    failed : int
        number of test cases failed with the line
    totalpassed : int
        total number of test cases passed
    totalfailed : int
        total number of test cases failed
    was_covered : bool
    
    Returns
    -------
    float
        the dstar2 hybrid suspiciousness value
    """
    if passed + totalfailed - failed == 0:
        assert passed==0 and failed==totalfailed
        return totalfailed**2 + 2 # slightly higher than otherwise possible
    return (failed**2 + (1 if was_covered else 0)) / (passed + totalfailed - failed)


def muse(passed, failed, totalpassed, totalfailed):
    """
    Calculates the dstar2 suspiciousness score for the line

    Adapted directly from: https://bitbucket.org/rjust/fault-localization-data/
    in file analysis/pipeline-scripts/crush-matrix

    Parameters
    ----------
    passed : int
        number of test cases passed with the line
    failed : int
        number of test cases failed with the line
    totalpassed : int
        total number of test cases passed
    totalfailed : int
        total number of test cases failed
    Returns
    -------
    float
        the dstar2 hybrid suspiciousness value
    """
    if totalpassed == 0:
        return 0
    return failed - totalfailed/totalpassed * passed


def muse_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
    """
    Calculates the dstar2 suspiciousness score for the line

    Adapted directly from: https://bitbucket.org/rjust/fault-localization-data/
    in file analysis/pipeline-scripts/crush-matrix

    Parameters
    ----------
    passed : int
        number of test cases passed with the line
    failed : int
        number of test cases failed with the line
    totalpassed : int
        total number of test cases passed
    totalfailed : int
        total number of test cases failed
    was_covered : bool
    
    Returns
    -------
    float
        the dstar2 hybrid suspiciousness value
    """
    if totalpassed == 0:
        return 0
    return failed - (totalfailed-(1 if was_covered else 0))/totalpassed * passed


def jaccard(passed, failed, totalpassed, totalfailed):
    """
    Calculates the dstar2 suspiciousness score for the line

    Adapted directly from: https://bitbucket.org/rjust/fault-localization-data/
    in file analysis/pipeline-scripts/crush-matrix

    Parameters
    ----------
    passed : int
        number of test cases passed with the line
    failed : int
        number of test cases failed with the line
    totalpassed : int
        total number of test cases passed
    totalfailed : int
        total number of test cases failed
    
    Returns
    -------
    float
        the dstar2 hybrid suspiciousness value
    """
    if totalfailed + passed == 0:
        return failed
    return failed / (totalfailed + passed)


def jaccard_hybrid_numerator(passed, failed, totalpassed, totalfailed, was_covered):
    """
    Calculates the dstar2 suspiciousness score for the line

    Adapted directly from: https://bitbucket.org/rjust/fault-localization-data/
    in file analysis/pipeline-scripts/crush-matrix

    Parameters
    ----------
    passed : int
        number of test cases passed with the line
    failed : int
        number of test cases failed with the line
    totalpassed : int
        total number of test cases passed
    totalfailed : int
        total number of test cases failed
    was_covered : bool
    
    Returns
    -------
    float
        the dstar2 hybrid suspiciousness value
    """
    if totalfailed + passed == 0:
        return (failed + (1 if was_covered else 0))
    return (failed + (1 if was_covered else 0)) / (totalfailed + passed)


# Formula to function
FORMULAS = {
    'tarantula': tarantula,
    'ochiai': ochiai,
    'opt2': opt2,
    'barinel': barinel,
    'dstar2': dstar2,
    'muse': muse,
    'jaccard': jaccard
}

# Hybrid formula to function
HYBRID_NUMERATOR_FORMULAS = {
    'tarantula': tarantula_hybrid_numerator,
    'ochiai': ochiai_hybrid_numerator,
    'opt2': opt2_hybrid_numerator,
    'barinel': barinel_hybrid_numerator,
    'dstar2': dstar2_hybrid_numerator,
    'muse': muse_hybrid_numerator,
    'jaccard': jaccard_hybrid_numerator
}


def crush_row(formula, hybrid_scheme, passed, failed, totalpassed, totalfailed, 
              passed_covered=None, failed_covered=None, totalpassed_covered=0, 
              totalfailed_covered=0):
    """
    Calculates the suspiciousness of a statement or mutant based on the forumula
    given

    Adapted directly from: https://bitbucket.org/rjust/fault-localization-data/
    in file analysis/pipeline-scripts/crush-matrix

    Parameters
    ----------
    formula : str 
        the name of the formula to plug passed/failed/totalpassed/totalfailed into.
    hybrid_scheme : str 
        one of ("numerator", "constant", or "mirror")
        useful for MBFL only, specifies how the formula should be modified to 
        incorporate the number of passing/failing tests that *cover* the mutant 
        (rather than kill it).
    """
    if hybrid_scheme is None:
        return FORMULAS[formula](passed, failed, totalpassed, totalfailed)
    elif hybrid_scheme == 'numerator':
        return HYBRID_NUMERATOR_FORMULAS[formula](passed, failed, totalpassed, totalfailed, failed_covered > 0)
    elif hybrid_scheme == 'constant':
        return FORMULAS[formula](passed, failed, totalpassed, totalfailed) + (1 if failed_covered > 0 else 0)
    elif hybrid_scheme == 'mirror':
        return (FORMULAS[formula](passed, failed, totalpassed, totalfailed) +
                FORMULAS[formula](passed_covered, failed_covered, totalpassed_covered, totalfailed_covered))/2.
    elif hybrid_scheme == 'coverage-only':
        return FORMULAS[formula](passed_covered, failed_covered, totalpassed_covered, totalfailed_covered)
    raise ValueError('unrecognized hybrid scheme name: {!r}'.format(hybrid_scheme))


# PassFailTally is a container class for number of test cases passed, failed, and total counts
PassFailTally = collections.namedtuple('PassFailTally', ('n_elements', 'passed', 'failed', 'totalpassed', 'totalfailed'))


def suspiciousnesses_from_tallies(formula, hybrid_scheme, tally, hybrid_coverage_tally):
    """
    Returns a dict mapping element-number to suspiciousness.

    Parameters
    ----------
    formula : str
        the formula to use to calculate suspiciousness
    hybrid_scheme : str
        numerator, constant, or mirror
    tally : PassFailTally
        an object of the PassFailTally class
    hybrid_coverage_tally : PassFailTally
        an object of the PassFailTally class

    Returns
    -------
    dict
        a dictionary of element-number to suspiciousness value
    """
    if hybrid_coverage_tally is None:
        passed_covered = failed_covered = collections.defaultdict(lambda: None)
        totalpassed_covered = totalfailed_covered = 0
    else:
        passed_covered = hybrid_coverage_tally.passed
        failed_covered = hybrid_coverage_tally.failed
        totalpassed_covered = hybrid_coverage_tally.totalpassed
        totalfailed_covered = hybrid_coverage_tally.totalfailed
    return {
        element: crush_row(
            formula=formula, hybrid_scheme=hybrid_scheme,
            passed=tally.passed[element], failed=tally.failed[element],
            totalpassed=tally.totalpassed, totalfailed=tally.totalfailed,
            passed_covered=passed_covered[element], failed_covered=failed_covered[element],
            totalpassed_covered=totalpassed_covered, totalfailed_covered=totalfailed_covered)
            for element in range(tally.n_elements)
        }


# TestSummary is a container class for test summary information
TestSummary = collections.namedtuple('TestSummary', ('triggering', 'covered_elements'))


def parse_test_summary(line, n_elements):
    words = line.strip().split(' ')
    coverages, sign = words[:-1], words[-1]
    if len(coverages) != n_elements:
        raise ValueError("expected {expected} elements in each row, got {actual} in {line!r}".format(expected=n_elements, actual=len(coverages), line=line))
    return TestSummary(
        triggering=(sign == '-'),
        covered_elements=set(i for i in range(len(words)) if words[i]=='1'))


def tally_matrix(matrix_file, total_defn, n_elements):
    """
    Returns a PassFailTally describing how many passing/failing tests there are, 
    and how many of each cover each code element.

    Parameters
    ----------

    total_defn : str 
        may be "tests" (in which case the tally's ``totalpassed`` will be the 
        number of passing tests) or "elements" (in which case it'll be the 
        number of times a passing test covers a code element) 
        (and same for ``totalfailed``).
    n_elements : str 
        is the number of code elements that each row of the matrix 
        should indicate coverage for.
    
    Returns
    -------
    namedtuple

    """
    summaries = (parse_test_summary(line, n_elements) for line in matrix_file)

    passed = {i: 0 for i in range(n_elements)}
    failed = {i: 0 for i in range(n_elements)}
    totalpassed = 0
    totalfailed = 0
    for summary in summaries:
        if summary.triggering:
            totalfailed += (1 if total_defn == 'tests' else len(summary.covered_elements))
            for element_number in summary.covered_elements:
                failed[element_number] += 1
        else:
            totalpassed += (1 if total_defn == 'tests' else len(summary.covered_elements))
            for element_number in summary.covered_elements:
                passed[element_number] += 1

    return PassFailTally(n_elements, passed, failed, totalpassed, totalfailed)


def parse_bug_from_file_name(coverage_file):
    """
    Parse bug from file name by looking

    Parameters
    ----------
    coverage_file : str
        the path to the coverage file
    
    Returns
    -------
    str
        returns the project and bug eg Closure-11
    """
    return '-'.join(coverage_file.split('/')[-1].split('-')[:-1])


def generate_suspiciousness(formula, coverage_file, spectra_file, output_dir):
    """
    Generates the suspiciousness value for each bug in the dataset.

    The method reads the coverage file and the spectra file, and uses 
    the method given in the fault-localization-data to generate a value
    between 0 and 1.

    Parameters
    ----------
    formula : str
        which formula to use for computing suspiciousness
    coverage_file : str
        path to the coverage file
    spectra_file : str
        path to the spectra file
    output_dir : str

    
    Returns
    -------
    dict
        suspiciousness value for all lines
    """
    with open(spectra_file) as name_file:
        element_names = {i: name.strip() for i, name in enumerate(name_file)}

    n_elements = len(element_names)

    with open(coverage_file) as matrix_file:
        tally = tally_matrix(matrix_file, 'tests', n_elements=n_elements)

    suspiciousnesses = suspiciousnesses_from_tallies(
        formula=formula, hybrid_scheme=None,
        tally=tally, hybrid_coverage_tally=None)

    bug = parse_bug_from_file_name(coverage_file)

    with open(os.path.join(output_dir, '%s-%s-suspiciousness' % (bug, formula)), 'w') as output_file:
        writer = csv.DictWriter(output_file, ['Statement','Suspiciousness'])
        writer.writeheader()
        for element in range(n_elements):
            writer.writerow({
                'Statement': element_names[element],
                'Suspiciousness': suspiciousnesses[element]})
    
    return suspiciousnesses


if __name__ == '__main__':
    # Slight hack to allow for 'all' as a choice
    formula_choices = set(FORMULAS.keys())
    formula_choices.add('all')

    parser = argparse.ArgumentParser()
    parser.add_argument('--formula', required=True, choices=formula_choices, help='formula to use for suspiciousness calculation')
    parser.add_argument('--data-dir', required=True, help='data directory that holds coverage and spectra files')
    parser.add_argument('--output-dir', required=True, help='file to write suspiciousness vector to')

    args = parser.parse_args()

    coverage_files = sorted(glob(os.path.join(args.data_dir, '*coverage')))
    spectra_files = sorted(glob(os.path.join(args.data_dir, '*spectra')))

    if len(coverage_files) != len(spectra_files):
        eprint('Number of coverage files is not equal to the number of spectra files')
        sys.exit(-1)
    
    if args.formula == 'all':
        for formula in FORMULAS.keys():
            for coverage_file, spectra_file in zip(coverage_files, spectra_files):
                generate_suspiciousness(formula, coverage_file, spectra_file, args.output_dir)
    else:
        for coverage_file, spectra_file in zip(coverage_files, spectra_files):
            generate_suspiciousness(args.formula, coverage_file, spectra_file, args.output_dir)