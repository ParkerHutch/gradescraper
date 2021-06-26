from datetime import datetime
from operator import attrgetter
from typing import List

from bs4 import BeautifulSoup, element

from util.assignment import Assignment
from util.course import Course
from util.term import Term


def extract_courses(dashboard_page_soup: BeautifulSoup):
    courses: List[Course] = []
    course_list_div_children: List[BeautifulSoup] = list(
        dashboard_page_soup.find('div', {'class': 'courseList'}).children
    )
    for i in [
        x for x in range(len(course_list_div_children) - 1) if x % 2 == 0
    ]:
        term_season, term_year = course_list_div_children[i].string.split(' ')
        term = Term(term_season, int(term_year))
        term_courses_div = course_list_div_children[i + 1]
        for tag in term_courses_div.find_all('a', class_='courseBox'):
            course_num = tag.get('href').replace('/courses/', '')
            name = tag.find('h4', {'class': 'courseBox--name'}).string
            short_name = tag.find(
                'h3', {'class': 'courseBox--shortname'}
            ).string
            total_assignments = int(
                tag.find(
                    'div', {'class': 'courseBox--assignments'}
                ).string.split(' ')[0]
            )
            courses.append(
                Course(term, course_num, short_name, name, total_assignments)
            )

    return courses


def extract_assignment_from_row(
    row: BeautifulSoup, course_name: str, assignment_year: str
):
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

    release_date: str = row.find(
        'span', {'class': 'submissionTimeChart--releaseDate'}
    ).string

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


# Returns a list of the courses from the most recent year and season
def strip_old_courses(courses_list: List[Course]) -> List[Course]:
    most_recent_term = min(courses_list, key=attrgetter('term')).term
    return [
        course for course in courses_list if course.term == most_recent_term
    ]
