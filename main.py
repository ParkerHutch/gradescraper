# Gradescope API Info: https://courses.csail.mit.edu/6.857/2016/files/20.pdf

from util import extractor
import asyncio
import aiohttp
import time
import json

import platform
from functools import wraps
from asyncio.proactor_events import _ProactorBasePipeTransport

#from datetime import datetime
import datetime
base_url = 'https://www.gradescope.com'
account_info_filename = 'data.json'


async def retrieve_courses_and_recent_assignments():
    # TODO: move this method into extractor?
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        with open('data.json', 'r') as account_file:
            soup = await extractor.async_get_login_soup(
                session, json.load(account_file)
            )

            courses = extractor.extract_courses(soup)

            await extractor.retrieve_assignments_for_courses(
                session, courses, recent_only=True
            )

            return courses


"""
The below 'dirty' fix silences a weird RunTime Error raised when the ProactorBasePipeTransport
class is used to close the event loop on Windows.
Source: https://github.com/aio-libs/aiohttp/issues/4324#issuecomment-733884349
"""


def silence_event_loop_closed(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RuntimeError as e:
            if str(e) != 'Event loop is closed':
                raise

    return wrapper


if __name__ == '__main__':

    """
        TODO
            - Loading circle
            - Timeout
            - async_get_auth_token takes most of the program time, see if there's a way to speed it up
            - Add something to documentation about how cchardet supposedly speeds up encoding
            - Make a requirements.txt
            - More error handling
    """

    # Silence the RuntimeError if the OS is Windows
    if platform.system() == 'Windows':
        _ProactorBasePipeTransport.__del__ = silence_event_loop_closed(
            _ProactorBasePipeTransport.__del__
        )

    print('\U0001F4F6 Extracting courses and assignments...')
    courses = asyncio.run(retrieve_courses_and_recent_assignments())

    today = datetime.datetime(2021, 4, 10)# TODO should actually be datetime.now()

    upcoming_assignments = [assignment for course in courses for assignment in course.get_assignments_in_range(today, today + datetime.timedelta(days = 7))]
    
    print('Upcoming assignments:')
    for assignment in upcoming_assignments:
        print(assignment)


