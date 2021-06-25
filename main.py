# Gradescope API Info: https://courses.csail.mit.edu/6.857/2016/files/20.pdf

from util import extractor
import asyncio
import aiohttp
import json

import platform
from functools import wraps
from asyncio.proactor_events import _ProactorBasePipeTransport

import datetime

import argparse
from util.messenger import GradescopeMesssenger
from util import processor
"""
        TODO
            - Loading circle
            - Timeout
            - async_get_auth_token takes most of the program time, see if there's a way to speed it up
            - Add something to documentation about how cchardet supposedly speeds up encoding
            - Make a requirements.txt
            - More error handling
"""


def get_parser() -> argparse.ArgumentParser:
    """Build an ArgumentParser to handle various command line arguments.

    Returns:
        argparse.ArgumentParser: an ArgumentParser to handle command line 
        arguments
    """
    parser = argparse.ArgumentParser(
        description='Get upcoming assignments from the Gradescope website.')
    parser.add_argument('-v', '--verbose', 
                        help='show output when running the program', 
                        action='store_true')
    parser.add_argument('-f', '--file', 
                        help='use file for account information', 
                        type=str,
                        default='')
    parser.add_argument('--store', 
                        help='store username and password in ./data.json for later use', 
                        action='store_true')
    
    return parser

base_url = 'https://www.gradescope.com' # TODO remove
account_info_filename = 'data.json'


async def retrieve_courses_and_recent_assignments():
    # TODO: move this method into extractor?
    with open('data.json', 'r') as account_file:
        json_account_info = json.load(account_file)
        messenger = GradescopeMesssenger()
        soup = await messenger.async_login(json_account_info['email'], json_account_info['password']) # TODO later this should just be incorporated into each method inside messenger

        courses = processor.extract_courses(soup)

        await messenger.retrieve_assignments_for_courses(courses, recent_only=True)
        await messenger.session.close()
        return courses
        # rewrite here


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

    args = get_parser().parse_args()

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


