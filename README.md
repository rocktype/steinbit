# Steinbit

![build](https://github.com/rocktype/steinbit/actions/workflows/build.yaml/badge.svg)

## Quickstart

Installation, creation and comparison operations using the Steinbit tool
proceed as follows:

```diff
-! Warning. The following will only work once the repo !-
-! is public and the package is available on PYPI.     !-
-!                                                     !-
-! Use "Installing for development purposes" in the    !-
-! interim.                                            !-
```

```
$ pip install steinbit
$ steinbit create images/bls*.png -o sheet.csv
$ steinbit compare sheet.csv original.las
Comparison result:
Extra columns in sheet.csv: [rtid, wellbore]
----------------------------------------
          Albite
       sheet.csv original.las
depth
1590.0     428.0     425.0
```

This constructs `sheet.csv` using the QEMSCAN image data files in the `images`
and compares it against another sheet `original.las`.

### Installing for development purposes

To install the `main` branch from GitHub for development use `pip install -e`
to create a link from the repository to the python installation.

```
$ git clone https://github.com/rocktype/steinbit
$ pip install -e ./steinbit
$ steinbit create ...
```

## Introduction

QEMSCAN data is produced by scanning rock material directly in an SEM with xray
detectors. Along with XRD and optical analysis it is the standard way of
assessing mineralogy (IR and XRF are also available but less precise). QEMSCAN
is relatively time intensive and expensive (but getting better).

Electro-magnetic logs or Logging While Drilling (LWD) is available on all
modern wells, essentially for free. Values typically include Gamma Ray, Clay
Volume, Density and Neutron. We currently make QEMSCAN-derived versions of
these for client delivery.

Because if the universal availability of Logs, they're part of the standard
subsurface analysis workflows. This tool provides a method to convert QEMSCAN
to Log data to give an alternative input to these workflows and as a way to
sanity-check the QS data and ground-truth the Log data.

## Installation

The `steinbit` tool is available from `pypi` and can be installed using:

`pip install steinbit`

## Operation

The `steinbit` tool current has two modes: `create` and `compare`. The `create`
operation constructs a CSV or LAS file from a set of images, CSVs or LAS files.
It can optionally apply translations between mineral sets and convert pixel
counts to percentages.

```
usage: steinbit.py create [-h] [-o OUTPUT] [-t] [-p] files [files ...]

positional arguments:
  files                 images, csv or las files to parse

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        the output file to write to
  -t, --translate       Reduce the output list by applying the transformation
  -p, --percent         Write percentages rather than raw pixel counts
```

If any of the inputs are already from the reduced mapping the translation is
automatically applied.

The `compare` operation takes two spreadsheets and finds a list of differences
at particular depths:

```
usage: steinbit.py compare [-h] file1 file2

positional arguments:
  file1       The first file to compare
  file2       The second file to compare

optional arguments:
  -h, --help  show this help message and exit
```

If either of the files is translated or in percentage form then both files are
transformed appropriately prior to comparison.

## Configuration

The file `steinbit.cfg` defines mappings from image pixel colours to minerals,
a translation from detailed to reduced mineral lists and decoding of image metadata.

```
[Mapping]
; Mapping files describe translations from pixels to mineral names
DetailedMapping = data/bls.csv
ReducedMapping = data/rs.csv

; The translation maps detailed mineral lists to reduced lists
Translation = data/translation.csv

[Fields]
; Fields describe metadata fields found in image exif data that describe
; the sample well and depth
Wellbore = Wellbore
Well = Wellbore
D_unit = Depth
...

[Regexes]
; Regexes decode the metadata field to the metadata item to be output
; in the resulting data frame
Well = [ _]*([0-9/-]*).*
D_unit = [0-9\.]*(.*)
...
```

Mappings can use either standard HTML colour values:

| Name      | Color   |
| --------- | ------- |
| Aluminium | #B0C4DE |

or RGB tuples:

| Name      | Red | Green | Blue |
| --------- | --- | ----- | ---- |
| Aluminium | 176 |  196  |  222 |

### Constraints

The fields `d_unit`, `depth` and `well` are required to be specified so that
a LAS header can be constructed. The mappings must contain a pixel value for
`background`.

## Contributing

Please [read our code of conduct](../../../rocktype/blob/master/v2021.01.md).
