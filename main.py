# Gradescope API Info: https://courses.csail.mit.edu/6.857/2016/files/20.pdf

from util import extractor
import asyncio
import aiohttp
import time
import json

import platform
from functools import wraps
from asyncio.proactor_events import _ProactorBasePipeTransport

base_url = 'https://www.gradescope.com'
account_info_filename = 'data.json'

async def main():
    """
        TODO
            - Assignment years are all set to 1900, fix this
            - async_get_auth_token takes most of the program time, see if there's a way to speed it up
            - Add something to documentation about how cchardet supposedly speeds up encoding
    """
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        with open('data.json', 'r') as account_file:
            soup = await extractor.async_get_login_soup(session, json.load(account_file))

            courses = extractor.extract_courses(soup)
            
            recent_courses = extractor.strip_old_courses(courses)

            """
            TODO refactor this to be align better with OOP principles, ex:
            for course in courses:
                course.assignments = async_get_assignments(course.course_num)
            """
            await asyncio.gather(*[extractor.async_retrieve_course_assignments(session, course) for course in recent_courses])

        
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
    
    # Silence the RuntimeError if the OS is Windows
    if platform.system() == 'Windows':
        _ProactorBasePipeTransport.__del__ = silence_event_loop_closed(_ProactorBasePipeTransport.__del__)
    

    time_start = time.time()
    asyncio.run(main())
    time_end = time.time()
    print(f'Execution time: {time_end - time_start}')

