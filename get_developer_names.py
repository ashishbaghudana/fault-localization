import subprocess

from pygit2 import Repository
from pygit2 import GIT_SORT_TOPOLOGICAL

PROJECTS = ['Closure', 'Lang', 'Chart', 'Math', 'Mockito', 'Time']
PROJECT_BUGS = [
    [str(x) for x in range(1, 134)],
    [str(x) for x in range(1, 66)],
    [str(x) for x in range(1, 27)],
    [str(x) for x in range(1, 107)],
    [str(x) for x in range(1, 39)],
    [str(x) for x in range(1, 28)]
]

developer_details = []

for project, bugs in zip(PROJECTS, PROJECT_BUGS):
    for bug in bugs:
        defects4j_checkout_command = ['defects4j', 'checkout', '-p', project, '-v', '%sf' % bug, '-w',
                                      '/Users/ashish/code/cs5704/temp/%s_%s' % (project, bug)]
        subprocess.call(defects4j_checkout_command)

        repo_dir = '/Users/ashish/code/cs5704/temp/%s_%s/.git' % (project, bug)
        repo = Repository(repo_dir)

        author_name = None
        for commit in repo.walk(repo.head.target, GIT_SORT_TOPOLOGICAL):
            if commit.author.name != 'defects4j':
                author_name = commit.author.name
                break

        if author_name is not None:
            developer_details.append('%s,%s,%s\n' % (project, bug, author_name))


with open('developers.csv', 'w') as fwriter:
    for row in developer_details:
        fwriter.write(row)
