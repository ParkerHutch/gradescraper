import asyncio
from typing import ClassVar, List

import aiohttp
from bs4 import BeautifulSoup, SoupStrainer

from gradescraper.util import processor
from gradescraper.structures.course import Course


class GradescopeMessenger:
    base_url: ClassVar[str] = 'https://www.gradescope.com'

    def __init__(self, email: str='', password: str='') -> None:
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()
        self.logged_in: bool = False
        self.email = email
        self.password = password

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, exc_traceback):
        await self.session.close()

    async def get_auth_token(self) -> str:
        response = await self.session.get(self.base_url)
        response_text = await response.text()
        parsed_init_resp = BeautifulSoup(
            response_text, 'lxml', parse_only=SoupStrainer("input")
        )
        return (
            parsed_init_resp.find('input', {'name': 'authenticity_token'})
        ).get("value")

    async def login(self) -> BeautifulSoup:
        post_params = {
            "session[email]": self.email,
            "session[password]": self.password,
            "authenticity_token": await self.get_auth_token(),
        }

        # Login and get the response, or access the base url if the user is already logged in.
        response = await self.session.post(
            f'{self.base_url}/login', params=post_params
        ) or await self.session.get(self.base_url)

        soup = BeautifulSoup(await response.text(), 'lxml')
        if soup.find('title').string == 'Log In | Gradescope':
            self.logged_in = False
            raise Exception(
                'Failed to log in. Please check username and password.'
            )
        else:
            self.logged_in = True

        return soup

    async def retrieve_assignments_for_course(self, course: Course):
        if not self.logged_in:
            await self.login()

        course_page_response = await self.session.get(
            f'{self.base_url}/courses/{course.course_num}'
        )

        assignments_soup = BeautifulSoup(
            await course_page_response.text(),
            'lxml',
            parse_only=SoupStrainer('tr'),
        ).find_all('tr')[1:]
        course.assignments = [
            processor.extract_assignment_from_row(
                row, course.name, course.term.year
            )
            for row in assignments_soup
        ]

    async def retrieve_assignments_for_courses(
        self, courses: List[Course], recent_only: bool
    ):
        """
        TODO refactor this to be align better with OOP principles, ex:
        for course in courses:
            course.assignments = async_get_assignments(course.course_num)
        """
        if recent_only:
            await asyncio.gather(
                *[
                    self.retrieve_assignments_for_course(course)
                    for course in processor.strip_old_courses(courses)
                ]
            )
        else:
            await asyncio.gather(
                *[
                    self.retrieve_assignments_for_course(course)
                    for course in courses
                ]
            )

    async def get_courses_and_assignments(self, recent_only: bool = True):
        soup = await self.login()

        courses = processor.extract_courses(soup)

        await self.retrieve_assignments_for_courses(courses, recent_only)

        return courses
