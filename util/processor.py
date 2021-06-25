from util.term import Term
from util.course import Course
from typing import List
from datetime import datetime
from util.assignment import Assignment

def extract_courses(
    dashboard_page_soup,
):  # TODO try to make this async, or make the individual course extraction async
    courses = []
    course_list_div_children = list(
        dashboard_page_soup.find('div', {'class': 'courseList'}).children
    )
    for i in [
        x for x in range(len(course_list_div_children) - 1) if x % 2 == 0
    ]:
        term_season, term_year_str = course_list_div_children[i].string.split(
            ' '
        )
        term = Term(term_season, int(term_year_str))
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


def extract_assignment_from_row(row_soup, course_name, assignment_year):
    submitted = not row_soup.find(
        'td', {'class': 'submissionStatus submissionStatus-warning'}
    )
    assignment_link_header = row_soup.find(
        'th', {'class': 'table--primaryLink'}
    )
    assignment_link_element = assignment_link_header.find('a')
    assignment_name = (
        assignment_link_element or assignment_link_header
    ).string

    base_url = 'https://www.gradescope.com'

    assignment_url = (
        base_url + assignment_link_element['href'].split('/submissions')[0]
        if assignment_link_element
        else ''
    )

    release_date = row_soup.find(
        'span', {'class': 'submissionTimeChart--releaseDate'}
    ).contents

    due_dates = [
        datetime.strptime(
            span.string.split('Due Date: ')[-1], '%b %d at %I:%M%p'
        ).replace(year=int(assignment_year))
        for span in row_soup.find_all(
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
    most_recent_term = sorted(courses_list, key=lambda x: x.term)[0].term
    return [
        course for course in courses_list if course.term == most_recent_term
    ]