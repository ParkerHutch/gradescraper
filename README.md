
![Logo](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/th5xamgrr6se0x5ro4g6.png)


![badge](https://img.shields.io/lgtm/grade/python/github/ParkerHutch/gradescraper)
![loc_badge](https://img.shields.io/tokei/lines/github/ParkerHutch/gradescraper)
![repo_size_badge](https://img.shields.io/github/repo-size/ParkerHutch/gradescraper?label=size)
# Gradescraper

A command line program that scrapes a user's courses from the Gradescope website and offers them a quick overview of upcoming assignments. 


## Features

- Asynchronous requests
- Command line tool

# Usage


```bash
python main.py [-h] [-v] [--store-account STORE_ACCOUNT] (-f FILE | --account USERNAME PASSWORD)

```
# Arguments

|short|long|help|
| :--- | :--- | :--- |
|`-h`|`--help`|show this help message and exit|
|`-v`|`--verbose`|show output when running the program|
||`--store-account`|store username and password in the given filename for later use|
|`-f`|`--file`|use file for account information|
||`--account`|use given account name for Gradescope login, overriding the value stored in the file if passed with --file. Requires password to be specified via --file or --account|

## Running Tests

Tests are stored in the tests directory. To run them, run the following command from the root folder of the project:

```bash
python -m pytest tests
```

## Optimizations

Asynchronous requests were utilized to retrieve the information for multiple courses at once.

  
## Acknowledgements

 [Security Analysis of Gradescope](https://courses.csail.mit.edu/6.857/2016/files/20.pdf) was useful for understanding Gradescope's API endpoints. 


  