from util import extractor
import asyncio
import aiohttp
import time
import json

import platform
from functools import wraps
from asyncio.proactor_events import _ProactorBasePipeTransport

base_url = 'https://www.gradescope.com'

async def custom_main():
    """
    TODO
    - see if async for would be useful anywhere
    """
    async with aiohttp.ClientSession() as session:
        with open('data.json', 'r') as account_file:
            soup = await extractor.async_get_login_soup(session, json.load(account_file))
            courses = extractor.extract_courses(soup) # TODO can I make this a generator, so that once a course is identified its async assignments function is immediately called
            
            """
            TODO remove unecessary async methods (the ones I made for CPU-bound functions)
            TODO I can refactor this to be align better with OOP principles
            for course in courses:
                course.assignments = async_get_assignments(course.course_num)
            """
            # TODO also test what happens when I don't use await below, I don't think it's necessary
            await asyncio.gather(*[extractor.async_retrieve_course_assignments(session, course) for course in courses])
        
        
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
    # Note: using async methods cut runtime by about 50%!
    time_start = time.time()
    # Silence the RuntimeError if the OS is Windows
    if platform.system() == 'Windows':
        _ProactorBasePipeTransport.__del__ = silence_event_loop_closed(_ProactorBasePipeTransport.__del__)
    
    asyncio.run(custom_main())
    time_end = time.time()
    print(f'Asynchronous execution: {time_end - time_start}')

