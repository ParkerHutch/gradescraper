import asyncio
from typing import ClassVar, List

import aiohttp
from bs4 import BeautifulSoup, SoupStrainer

from gradescraper.util import processor
from gradescraper.structures.course import Course


class GradescopeMessenger:
    """A class for handling requests to the Gradescope website.

    Attributes:
        session (aiohttp.ClientSession): the session used when making requests
        to the Gradescope website.
        logged_in (bool): whether the session has been successfully logged in
        to the Gradescope website.
        email (str, optional): The user's email address.
        password (str, optional): The user's password.
    """

    base_url: ClassVar[str] = 'https://www.gradescope.com'

    def __init__(self, email: str='', password: str=''):
        """Create a GradescopeMessenger, initializing an aiohttp ClientSession.

        Args:
            email (str, optional): The user's email address. Defaults to ''.
            password (str, optional): The user's password. Defaults to ''.
        """
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()
        self.logged_in: bool = False
        self.email = email
        self.password = password

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, exc_traceback):
        await self.session.close()

    async def get_auth_token(self) -> str:
        """Get the authentication token cookie from the Gradescope site.

        Returns:
            str: the authentication token.
        """
        response = await self.session.get(self.base_url)
        response_text = await response.text()
        parsed_init_resp = BeautifulSoup(
            response_text, 'lxml', parse_only=SoupStrainer("input")
        )
        return (
            parsed_init_resp.find('input', {'name': 'authenticity_token'})
        ).get("value")

    async def login(self) -> BeautifulSoup:
        """Attempt to login to the Gradescope website.

        The GradescopeMessenger's stored email and password attributes are used
        in addition to an authentication token to make this login attempt.

        Raises:
            Exception: error related to a failure to log in to Gradescope.

        Returns:
            BeautifulSoup: the user's Gradescope dashboard if the login was
            successful.
        """

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
        """Finds assignments for the given course and stores them in the course.

        Assignments for the given course are found via a GET request to the
        course's special Gradescope URL. After the response is parsed into valid
        Assignment objects, the list of those assignments is stored in the
        course's assignments attribute.

        Note:
            To find assignments for the given course, the user must be logged
            in. If the user is not logged in when this method is called, the 
            login method is called, and then the rest of the method executes.

        Args:
            course (Course): The course to find assignments for.
        """

        if not self.logged_in:
            await self.login()

        course_page_response = await self.session.get(
            f'{self.base_url}/courses/{course.number}'
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
        """Asynchronously retrieve assignments for the given courses.

        Since courses could contain a list of courses from irrelevant years or 
        terms, recent_only can be specified to only retrieve assignments for
        the courses occuring in the most recent term.

        Args:
            courses (List[Course]): A list of Courses to possibly retrieve 
            assignments for.
            recent_only (bool): Whether to only retrieve assignments for courses
            occuring in the most recent term.
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

    async def get_courses_and_assignments(self, recent_only: bool = True) -> List[Course]:
        """Get the user's courses and assignments.

        Args:
            recent_only (bool, optional): Whether to only retrieve assignments
            for courses occuring in the most recent term. Defaults to True.


        Returns:
            List[Course]: A list of the user's courses and their possibly
            retrieved assignments. Retrieval of assignments is contingent upon
            the value of recent_only.
        """

        soup = await self.login()

        courses = processor.extract_courses(soup)

        await self.retrieve_assignments_for_courses(courses, recent_only)

        return courses
