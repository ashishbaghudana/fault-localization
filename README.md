# Fault Localization from Defects4J

Fault localization is a technique to help identify buggy lines from source code based on failing test cases. We develop a hybrid technique based on different kinds of formulas that generate statement suspiciousness. This project is part of the CS5704: Software Engineering (Spring 2018).

These are:

* Tarantula
* Ochiai
* Opt2
* Barinel
* Dstar2
* Muse
* Jaccard

## Dataset

We use the Defects4J dataset available [here](https://github.com/rjust/defects4j). The dataset has 395 real bugs from 6 Java projects - Lang, Closure, Chart, Mockito, Time, and Math.

Specifically, we use only Lang and Math for our research results.

## Setup

Download the data by running the following command.

```bash
wget --recursive --no-parent --accept gzoltar-files.tar.gz http://fault-localization.cs.washington.edu/data
```

Subsequently extract the matrix and coverage to a directory using the `matrix_coverage.py` file.

```text
usage: matrix_coverage.py [-h] --data-dir DATA_DIR --output-dir OUTPUT_DIR

optional arguments:
  -h, --help            show this help message and exit
  --data-dir DATA_DIR   data directory that holds data
  --output-dir OUTPUT_DIR
                        file to write coverage and spectra matrices to
```

For example, run `matrix_coverage.py` as:

```bash
mkdir $HOME/fault-localization.cs.washington.edu/coverage
python matrix_coverage.py --data-dir $HOME/fault-localization.cs.washington.edu/data --output-dir $HOME/fault-localization.cs.washington.edu/coverage
```

The suspiciousness values can be generated using `suspiciousness.py` file.

```text
usage: suspiciousness.py [-h] --formula
                         {muse,all,ochiai,tarantula,dstar2,jaccard,barinel,opt2}
                         --data-dir DATA_DIR --output-dir OUTPUT_DIR

optional arguments:
  -h, --help            show this help message and exit
  --formula {muse,all,ochiai,tarantula,dstar2,jaccard,barinel,opt2}
                        formula to use for suspiciousness calculation
  --data-dir DATA_DIR   data directory that holds coverage and spectra files
  --output-dir OUTPUT_DIR
                        file to write suspiciousness vector to
```

Run `suspiciousness.py` as follows:

```bash
mkdir $HOME/fault-localization.cs.washington.edu/suspiciousness
python suspiciousness.py --data-dir $HOME/fault-localization.cs.washington.edu/coverage --output-dir $HOME/fault-localization.cs.washington.edu/suspiciousness --formula all
```

Subsequently, the statement suspiciousness values need to be converted to line suspiciousness values. This can be done using the `s2l_suspiciousness.py`. The usage is as follows:

```text
usage: s2l_suspiciousness.py [-h] -d SUSPICIOUSNESS_DATA_DIR -s
                             SOURCE_CODE_LINES -o OUTPUT_DIR
                             [-f {jaccard,tarantula,muse,dstar2,ochiai,barinel,opt2}]

optional arguments:
  -h, --help            show this help message and exit
  -d SUSPICIOUSNESS_DATA_DIR, --suspiciousness-data-dir SUSPICIOUSNESS_DATA_DIR
                        Suspiciousness data directory
  -s SOURCE_CODE_LINES, --source-code-lines SOURCE_CODE_LINES
                        Source code lines directory
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Output directory
  -f {jaccard,tarantula,muse,dstar2,ochiai,barinel,opt2}, --formula {jaccard,tarantula,muse,dstar2,ochiai,barinel,opt2}
                        Formula to convert for
```

Finally, sort the resulting csv files using the `sort_csv.py` file.

```text
usage: sort_csv.py [-h] -d SUSPICIOUSNESS_DATA_DIR -o OUTPUT_DIR

optional arguments:
  -h, --help            show this help message and exit
  -d SUSPICIOUSNESS_DATA_DIR, --suspiciousness-data-dir SUSPICIOUSNESS_DATA_DIR
                        Suspiciousness data directory
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Output directory
```
