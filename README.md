
![Logo](img/logo.png)


![quality_badge](https://img.shields.io/lgtm/grade/python/github/ParkerHutch/gradescraper)
![workflow_badge](https://github.com/ParkerHutch/gradescraper/actions/workflows/python_test.yml/badge.svg?branch=master)
![loc_badge](https://img.shields.io/tokei/lines/github/ParkerHutch/gradescraper)
![repo_size_badge](https://img.shields.io/github/repo-size/ParkerHutch/gradescraper?label=size)
# Gradescraper

A command line program that scrapes a user's courses from the Gradescope website and offers them a quick overview of upcoming assignments. 

## Demo
```bash
$ python gradescraper.py
📶 Retrieving assignents from courses...
Upcoming assignments over the next 7 days (04/10➡04/17):
Course Name          Assignment        Due Date        Submitted
Linear Algebra       📓WS 10A          📅04/10 11:59PM ✅
Linear Algebra       📓HW 3B           📅04/14 11:59PM ✅
World History        📓HW 5            📅04/12 11:59PM ❌
Calculus II          📓WS 4.5          📅04/16 11:59PM ✅
Advanced Econ        📓Quiz 4          📅04/12 11:59PM ❌
Biology              📓Lab 5           📅04/13 11:00PM ✅
```

## Features

- Asynchronous requests
- Command line tool

## Usage


```bash
python gradescraper.py [-h] [-v] [--store-account STORE_ACCOUNT] (-f FILE | --account USERNAME PASSWORD)

```
## Arguments

|short|long&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|help|
| :--- | :--- | :--- |
|`-h`|`--help`|show this help message and exit|
|`-v`|`--verbose`|show output when running the program|
||`--store-account`|store username and password in the given filename for later use|
|`-f`|`--file`|use file for account information|
||`--account`|use given account name for Gradescope login, overriding the value stored in the file if passed with --file. Requires password to be specified via --file or --account|

## Running Tests

Tests are stored in the [tests](tests) directory. To run them, run the following command from the root folder of the project:

```bash
python -m pytest tests
```

### Optimizations

Asynchronous requests were utilized to retrieve the information for multiple courses at once.

  
## Acknowledgements

 [Security Analysis of Gradescope](https://courses.csail.mit.edu/6.857/2016/files/20.pdf) was useful for understanding Gradescope's API endpoints. 


  