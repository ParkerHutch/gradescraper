from datetime import datetime
from operator import attrgetter
from typing import List

from bs4 import BeautifulSoup, element

from gradescraper.structures.assignment import Assignment
from gradescraper.structures.course import Course
from gradescraper.structures.term import Term


def extract_course(course_entry: BeautifulSoup, term: Term) -> Course:
    """Extract a course from its HTML entry in the courses overview.

    Args:
        course_entry (BeautifulSoup): the course's HTML entry in the
        overall course dashboard.
        term (Term): the term during which the course takes place.

    Returns:
        Course: A course containing the information parsed from course_entry.
    """
    course_num = int(course_entry.get('href').replace('/courses/', ''))
    name = course_entry.find('h4', {'class': 'courseBox--name'}).string
    short_name = course_entry.find(
        'h3', {'class': 'courseBox--shortname'}
    ).string
    total_assignments = int(
        course_entry.find(
            'div', {'class': 'courseBox--assignments'}
        ).string.split(' ')[0]
    )
    return Course(term, course_num, short_name, name, total_assignments)


def extract_courses(courses_dashboard: BeautifulSoup) -> List[Course]:
    """Extract every course from the dashboard of courses.

    Args:
        courses_dashboard (BeautifulSoup): The courses dashboard, which should
        contain a div with class 'courseList' containing an entry for each of
        the user's courses.

    Returns:
        List[Course]: A list of Courses parsed from the dashboard given.
    """
    courses: List[Course] = []
    course_list_div_children: List[BeautifulSoup] = list(
        courses_dashboard.find('div', {'class': 'courseList'}).children
    )
    for i in [
        x for x in range(len(course_list_div_children) - 1) if x % 2 == 0
    ]:
        term_season, term_year = course_list_div_children[i].string.split(' ')
        term = Term(term_season, int(term_year))
        term_courses_div = course_list_div_children[i + 1]
        for tag in term_courses_div.find_all('a', class_='courseBox'):
            courses.append(extract_course(tag, term))

    return courses


def extract_assignment_from_row(
    row: BeautifulSoup, course_name: str, assignment_year: str
) -> Assignment:
    """Extract an Assignment from the row given.

    Args:
        row (BeautifulSoup): An HTML 'tr' element containing information about
        an Assignment.
        course_name (str): The name of the course that this assignment belongs
        to. Required because the assignment row typically contains due dates
        without a listed year.
        assignment_year (str): The year that the assignment was assigned.

    Returns:
        Assignment: an assignment parsed from the row HTML given.
    """
    submitted = not row.find(
        'td', {'class': 'submissionStatus submissionStatus-warning'}
    )
    assignment_link_header: element.Tag = row.find(
        'th', {'class': 'table--primaryLink'}
    )
    assignment_link_element: element.Tag = assignment_link_header.find('a')
    assignment_name: str = (
        assignment_link_element or assignment_link_header
    ).string

    base_url = 'https://www.gradescope.com'

    assignment_url: str = (
        base_url + assignment_link_element['href'].split('/submissions')[0]
        if assignment_link_element
        else ''
    )

    
    release_date = datetime.strptime(row.find(
        'span', {'class': 'submissionTimeChart--releaseDate'}
    ).string, '%b %d').replace(year=int(assignment_year)) 
    # TODO get rid of int(assignment_year), just pass the int year

    due_dates = [
        datetime.strptime(
            span.string.split('Due Date: ')[-1], '%b %d at %I:%M%p'
        ).replace(year=int(assignment_year))
        for span in row.find_all(
            'span', {'class': 'submissionTimeChart--dueDate'}
        )
    ]
    due_date = due_dates[0]
    late_due_date = due_dates[1] if len(due_dates) == 2 else None
    return Assignment(
        assignment_name,
        course_name,
        assignment_url,
        submitted,
        release_date,
        due_date,
        late_due_date,
    )


def strip_old_courses(courses_list: List[Course]) -> List[Course]:
    """Return the courses in courses_list that occurred in the most recent term.

    Args:
        courses_list (List[Course]): A list of courses from various terms.

    Returns:
        List[Course]: courses in courses_list that took place in the most recent
        term.
    """
    most_recent_term = min(courses_list, key=attrgetter('term')).term
    return [
        course for course in courses_list if course.term == most_recent_term
    ]
