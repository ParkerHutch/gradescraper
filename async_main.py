from util import extractor
import asyncio
import aiohttp
import time
import json
from bs4 import BeautifulSoup, SoupStrainer
import platform

base_url = 'https://www.gradescope.com'


async def get(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as response:
                resp = await response.read()
                print("Successfully got url {} with response of length {}.".format(url, len(resp)))
    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))


async def main(urls, amount):
    ret = await asyncio.gather(*[get(url) for url in urls])
    print("Finalized all. ret is a list of len {} outputs.".format(len(ret)))


async def async_retrieve_course_assignments(session, course):
    course_page_response = await session.get(f'{base_url}/courses/{course.course_num}')
    
    assignments_soup = BeautifulSoup(await course_page_response.text(), 'lxml', parse_only=SoupStrainer('tr')).find_all('tr')[1:]
    
    course.assignments = [extractor.extract_assignment_from_row(row) for row in assignments_soup] # TODO maybe async here


async def custom_main():
    # Log in on the session
    base_url = 'https://www.gradescope.com'

    loop = asyncio.new_event_loop()
    async with aiohttp.ClientSession() as session:
        with open('data.json', 'r') as account_file:
            account_json = json.load(account_file)
            
            soup = await extractor.async_get_login_soup(session, account_json)
            courses = extractor.extract_courses(soup)
            
            await asyncio.gather(*[async_retrieve_course_assignments(session, course) for course in courses])
        
    loop.close()
            
        
from functools import wraps

from asyncio.proactor_events import _ProactorBasePipeTransport

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
    print(f'all done: {time.time() - time_start}')

