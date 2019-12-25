# Weekly Planner
[![Build Status](https://travis-ci.org/JasonYao/weekly-planner.svg?branch=source)](https://travis-ci.org/JasonYao/weekly-planner)

By [Jason Yao](https://github.com/JasonYao/weekly-planner)

> Made as a 2019 winter gift for my SO, so she can now obsessively plan everything on her own terms

This repo contains everything required to build and
distribute via github pages the generated artifacts.

[LaTeX](https://www.latex-project.org) is used due to its readability,
ease-of-change, and aesthetic final output.

The python portion to generate the latex template is built and
tested with `python 3.8.0`.

## Link to Weekly Planner
To see the pdf version of this weekly planner for 2020, please click the image below:
[![Even this thumbnail is automatically generated](https://www.jasonyao.com/weekly-planner/2020.png)
](https://www.jasonyao.com/weekly-planner/2020.pdf)

### Double Planner
My SO actually prefers using this version, so I made an easy print-friendly version
that changes it from a single week per page to two weeks per page. To see it for 2020,
click the image below:
[![Even this thumbnail is automatically generated](https://www.jasonyao.com/weekly-planner/double/2020.png)
](https://www.jasonyao.com/weekly-planner/double/2020.pdf)

## Install (macOS)
```sh
# Installs pdf generation dependencies
brew cask install mactex

# [OPTIONAL] Installs a good pdf viewer and IDE
brew cask install texmaker
```

## Usage
To generate the pdf from the command-line:
```sh
bin/build
# OR
python run.py 2020 && xelatex weekly-planner-2020.tex && xelatex biweekly-print-version-2020.tex
```

## License
This repo is licensed under the terms of the GNU GPLv3 license,
a copy of which may be found [here](LICENSE)
