from typing import List
import aiohttp
from util.course import Course
from bs4 import BeautifulSoup, SoupStrainer
from util.assignment import Assignment
from datetime import datetime
from util.term import Term
import asyncio

base_url = 'https://www.gradescope.com'


def get_auth_token(session: aiohttp.ClientSession):
    parsed_init_resp = BeautifulSoup(
        session.get(base_url).text, 'lxml', parse_only=SoupStrainer("input")
    )
    return (
        parsed_init_resp.find('input', {'name': 'authenticity_token'})
    ).get("value")


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


def get_login_soup(session: aiohttp.ClientSession, account_info_json):

    if not all(
        x in account_info_json for x in ['email', 'password']
    ):  # TODO try turning this into just two boolean conditions rather than a search
        raise Exception('Insufficient account information provided.')

    post_params = {
        "session[email]": account_info_json['email'],
        "session[password]": account_info_json['password'],
        "authenticity_token": get_auth_token(session),
    }

    # Login and get the response, or access the base url if the user is already logged in.
    response = session.post(
        f'{base_url}/login', params=post_params
    ) or session.get(base_url)

    soup = BeautifulSoup(response.content, 'lxml')
    if soup.find('title').string == 'Log In | Gradescope':
        raise Exception(
            'Failed to log in. Please check username and password.'
        )

    return soup


def extract_assignment_from_row(row_soup, assignment_year):
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
        assignment_url,
        submitted,
        release_date,
        due_date,
        late_due_date,
    )


def get_course_assignments(
    session: aiohttp.ClientSession, course_num: int, course_year: int
):
    course_page_response = session.get(f'{base_url}/courses/{course_num}')

    assignments_soup = BeautifulSoup(
        course_page_response.content, 'lxml', parse_only=SoupStrainer('tr')
    ).find_all('tr')[1:]

    return [
        extract_assignment_from_row(row, course_year)
        for row in assignments_soup
    ]


async def async_get_auth_token(url, session: aiohttp.ClientSession):
    response = await session.get(url)
    response_text = await response.text()
    parsed_init_resp = BeautifulSoup(
        response_text, 'lxml', parse_only=SoupStrainer("input")
    )
    return (
        parsed_init_resp.find('input', {'name': 'authenticity_token'})
    ).get("value")


async def async_get_login_soup(
    session: aiohttp.ClientSession, account_info_json
):

    if not all(x in account_info_json for x in ['email', 'password']):
        raise Exception('Insufficient account information provided.')

    post_params = {
        "session[email]": account_info_json['email'],
        "session[password]": account_info_json['password'],
        "authenticity_token": await async_get_auth_token(base_url, session),
    }

    # Login and get the response, or access the base url if the user is already logged in.
    response = await session.post(
        f'{base_url}/login', params=post_params
    ) or await session.get(base_url)

    soup = BeautifulSoup(await response.text(), 'lxml')
    if soup.find('title').string == 'Log In | Gradescope':
        raise Exception(
            'Failed to log in. Please check username and password.'
        )

    return soup


async def async_retrieve_course_assignments(
    session: aiohttp.ClientSession, course: Course
):
    course_page_response = await session.get(
        f'{base_url}/courses/{course.course_num}'
    )

    assignments_soup = BeautifulSoup(
        await course_page_response.text(),
        'lxml',
        parse_only=SoupStrainer('tr'),
    ).find_all('tr')[1:]
    course.assignments = [
        extract_assignment_from_row(row, course.term.year)
        for row in assignments_soup
    ]


# Returns a list of the courses from the most recent year and season
def strip_old_courses(courses_list: List[Course]) -> List[Course]:
    most_recent_term = sorted(courses_list, key=lambda x: x.term)[0].term
    return [
        course for course in courses_list if course.term == most_recent_term
    ]


async def retrieve_assignments_for_courses(
    session: aiohttp.ClientSession, courses: List[Course], recent_only
) -> None:
    """
        TODO refactor this to be align better with OOP principles, ex:
        for course in courses:
            course.assignments = async_get_assignments(course.course_num)
    """
    if recent_only:
        await asyncio.gather(
            *[
                async_retrieve_course_assignments(session, course)
                for course in strip_old_courses(courses)
            ]
        )
    else:
        await asyncio.gather(
            *[
                async_retrieve_course_assignments(session, course)
                for course in courses
            ]
        )

