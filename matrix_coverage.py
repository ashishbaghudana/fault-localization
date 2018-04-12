import tarfile
import os
import argparse


PROJECTS = ['Closure', 'Lang', 'Chart', 'Math', 'Mockito', 'Time']
PROJECT_BUGS = [
    [str(x) for x in range(1, 134)],
    [str(x) for x in range(1, 66)],
    [str(x) for x in range(1, 27)],
    [str(x) for x in range(1, 107)],
    [str(x) for x in range(1, 39)],
    [str(x) for x in range(1, 28)]
]
TAR_FILE = 'gzoltar-files.tar.gz'


def extract_files(data_dir, output_dir):
    """
    Extract tar gz files from data directory to get coverage and spectra files

    Parameters
    ----------
    data_dir : str
        the main data directory which holds all projects
    
    output_dir : str
        the output directory to write coverage and spectra files to
        this directory must exist
    
    Returns
    -------
    None
    """
    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        for bug in bugs:
            tar = os.path.join(data_dir, project, bug, TAR_FILE)
            coverage, spectra = extract_tar_file(tar)
            if coverage is None or spectra is None:
                print('Could not get coverage/spectra for %s' % tar)
            else:
                coverage_file = os.path.join(output_dir, '%s-%s-%s' % (project, bug, 'coverage'))
                spectra_file = os.path.join(output_dir, '%s-%s-%s' % (project, bug, 'spectra'))
                write_file(coverage_file, coverage)
                write_file(spectra_file, spectra)


def extract_tar_file(tar):
    """
    Extract a tar file and return the matrix and spectra content

    Parameters
    ----------
    tar : str
        the path to the tarfile
    
    Returns
    tuple(str, str)
        the contents of the coverage matrix and spectra
    """
    coverage, spectra = None, None
    tar = tarfile.open(tar)
    for member in tar.getmembers():
        if 'matrix' in member.get_info()['name']:
            f = tar.extractfile(member)
            if f is not None:
                coverage = f.read()
        if 'spectra' in member.get_info()['name']:
            f = tar.extractfile(member)
            if f is not None:
                spectra = f.read()
    return coverage, spectra


def write_file(filename, content):
    """
    Write content to the given filename

    Parameters
    ----------
    filename : str
    content : str
    """
    with open(filename, 'wb') as fwriter:
        fwriter.write(content)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', required=True, help='data directory that holds data')
    parser.add_argument('--output-dir', required=True, help='file to write coverage and spectra matrices to')

    args = parser.parse_args()
    
    extract_files(args.data_dir, args.output_dir)
