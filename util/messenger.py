from typing import ClassVar, List

import aiohttp
from bs4 import BeautifulSoup, SoupStrainer

from util.course import Course
import asyncio
from util import processor

class GradescopeMesssenger:
    base_url: ClassVar[str] = 'https://www.gradescope.com'

    def __init__(self) -> None:
        session: aiohttp.ClientSession = None
        self.logged_in: bool = False
        self.username = ''
        self.password = ''


    async def async_get_auth_token(self):
        response = await self.session.get(self.base_url)
        response_text = await response.text()
        parsed_init_resp = BeautifulSoup(
            response_text, 'lxml', parse_only=SoupStrainer("input")
        )
        return (
            parsed_init_resp.find('input', {'name': 'authenticity_token'})
        ).get("value")

    async def async_login(
        self, email, password # TODO take in optional args for user/passwd 
    ):
        self.session = aiohttp.ClientSession()
        post_params = {
            "session[email]": email,
            "session[password]": password,
            "authenticity_token": await self.async_get_auth_token(),
        }

        # Login and get the response, or access the base url if the user is already logged in.
        response = await self.session.post(
            f'{self.base_url}/login', params=post_params
        ) or await self.session.get(self.base_url)

        soup = BeautifulSoup(await response.text(), 'lxml')
        if soup.find('title').string == 'Log In | Gradescope':
            raise Exception(
                'Failed to log in. Please check username and password.'
            )

        return soup
    
    async def async_get_login_soup(
        self, account_info_json # TODO take in optional args for user/passwd 
    ):
        if not all(x in account_info_json for x in ['email', 'password']): # TODO just check each manually
            raise Exception('Insufficient account information provided.')

        post_params = {
            "session[email]": account_info_json['email'],
            "session[password]": account_info_json['password'],
            "authenticity_token": await self.async_get_auth_token(),
        }

        # Login and get the response, or access the base url if the user is already logged in.
        response = await self.session.post(
            f'{self.base_url}/login', params=post_params
        ) or await self.session.get(self.base_url)

        soup = BeautifulSoup(await response.text(), 'lxml')
        if soup.find('title').string == 'Log In | Gradescope':
            raise Exception(
                'Failed to log in. Please check username and password.'
            )

        return soup

    async def async_retrieve_course_assignments(
        self, course: Course
    ):
        course_page_response = await self.session.get(
            f'{self.base_url}/courses/{course.course_num}'
        )

        assignments_soup = BeautifulSoup(
            await course_page_response.text(),
            'lxml',
            parse_only=SoupStrainer('tr'),
        ).find_all('tr')[1:]
        course.assignments = [
            processor.extract_assignment_from_row(row, course.name, course.term.year)
            for row in assignments_soup
        ]
    
    async def retrieve_assignments_for_courses(
        self, courses: List[Course], recent_only: bool
    ) -> None:
        """
            TODO refactor this to be align better with OOP principles, ex:
            for course in courses:
                course.assignments = async_get_assignments(course.course_num)
        """
        if recent_only:
            await asyncio.gather(
                *[
                    self.async_retrieve_course_assignments(course)
                    for course in processor.strip_old_courses(courses)
                ]
            )
        else:
            await asyncio.gather(
                *[
                    self.async_retrieve_course_assignments(course)
                    for course in courses
                ]
            )
