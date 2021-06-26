# Gradescope API Info: https://courses.csail.mit.edu/6.857/2016/files/20.pdf

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
            - YAML for user info
"""

def parse_account(args):
    print(args)#with open(args.file)

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
    parser.add_argument('--store-account', 
                        help='store username and password in the given filename for later use', 
                        type=str,
                        default='')
    account_info_group = parser.add_mutually_exclusive_group(required=True)
    account_info_group.add_argument('-f', '--file', metavar='FILE',
                        help='use file for account information', 
                        type=str,
                        default='')
    account_info_group.add_argument('--account', nargs=2, metavar=('USERNAME', 'PASSWORD'),
                        help='use given account name for Gradescope login, overriding the value stored in the file if passed with --file. Requires password to be specified via --file or --account',
                        type=str,
                        default='')
    
    
    return parser

base_url = 'https://www.gradescope.com' # TODO remove
account_info_filename = 'data.json' # TODO remove

"""
async def retrieve_courses_and_recent_assignments():
    # TODO: move this method into extractor?
    with open('data.json', 'r') as account_file:
        json_account_info = json.load(account_file)
        messenger = GradescopeMesssenger(json_account_info['email'], json_account_info['password'])
        soup = await messenger.async_login() # TODO later this should just be incorporated into each method inside messenger

        courses = processor.extract_courses(soup)

        await messenger.retrieve_assignments_for_courses(courses, recent_only=True)
        await messenger.session.close() # TODO add this to a finally?
        return courses
"""

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

async def main():
    print('\U0001F4F6 Extracting courses and assignments...')
    args = get_parser().parse_args() # TODO make sure this works
    account_email = ''
    password = ''

    if args.file:
        with open(args.file, 'r') as account_file:
            account_json = json.load(account_file)
            account_email, password = account_json['email'], account_json['password']
    else:
        account_email, password = args.account

    if args.store_account:
        with open(args.store_account, 'w') as account_file:
            account_dict = {"email": account_email, "password": password}
            json.dump(account_dict, account_file, ensure_ascii=False, indent=4)

    async with GradescopeMesssenger(account_email, password) as messenger:
        courses = await messenger.get_courses_and_assignments()
    
    today = datetime.datetime(2021, 4, 10)# TODO should actually be datetime.now() in prod

    upcoming_assignments = [assignment for course in courses for assignment in course.get_assignments_in_range(today, today + datetime.timedelta(days = 7))]
    
    print('Upcoming assignments:')
    for assignment in upcoming_assignments:
        print(assignment)
    
if __name__ == '__main__':

    # Silence the RuntimeError if the OS is Windows
    if platform.system() == 'Windows':
        _ProactorBasePipeTransport.__del__ = silence_event_loop_closed(
            _ProactorBasePipeTransport.__del__
        )
    asyncio.run(main())



