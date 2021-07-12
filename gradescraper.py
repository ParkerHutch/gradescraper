# Gradescope API Info: https://courses.csail.mit.edu/6.857/2016/files/20.pdf

import argparse
import asyncio
import datetime
import json
import platform
from asyncio.proactor_events import _ProactorBasePipeTransport
from functools import wraps

from gradescraper.util.messenger import GradescopeMessenger


def get_parser() -> argparse.ArgumentParser:
    """Build an ArgumentParser to handle various command line arguments.

    Returns:
        argparse.ArgumentParser: an ArgumentParser to handle command line
        arguments
    """
    parser = argparse.ArgumentParser(
        description='Get upcoming assignments from the Gradescope website.'
    )
    parser.add_argument(
        '-v',
        '--verbose',
        help='show output when running the program',
        action='store_true',
    )
    parser.add_argument(
        '--remember-me',
        help='store username and password in ./data.json for later use',
        action='store_const',
        const='data.json',
        default=False
    )

    account_info_group = parser.add_mutually_exclusive_group(required=False)
    account_info_group.add_argument(
        '-f',
        '--file',
        metavar='FILE',
        help='use the given file for account information',
        type=str,
        default='data.json',
    )
    account_info_group.add_argument(
        '--account',
        nargs=2,
        metavar=('USERNAME', 'PASSWORD'),
        help='use given account name for Gradescope login, overriding the value stored in the file if passed with --file. Requires password to be specified via --file or --account',
        type=str,
        default='',
    )

    account_info_group.add_argument(
        '-d', '--days-forward',
        metavar='NUM',
        help='retrieve assignments up to NUM days from today',
        type=int,
        default=7,
    )

    return parser

async def main():
    args = get_parser().parse_args()
    account_email = ''
    password = ''

    if args.account:
        account_email, password = args.account
    else:
        with open(args.file, 'r') as account_file:
            account_json = json.load(account_file)
            account_email, password = (
                account_json['email'],
                account_json['password'],
            )
    if args.remember_me or args.file:
        with open(args.remember_me or args.file, 'w') as account_file:
            account_dict = {"email": account_email, "password": password}
            json.dump(account_dict, account_file, ensure_ascii=False, indent=4)

    print(f'\U0001F4F6 Retrieving assignents from courses...')
    async with GradescopeMessenger(account_email, password) as messenger:
        courses = await messenger.get_courses_and_assignments()

    # TODO should actually be datetime.now() in prod
    today = datetime.datetime(2021, 4, 10)
    end_date = today + datetime.timedelta(days=args.days_forward)
    upcoming_assignments = [
        assignment
        for course in courses
        for assignment in course.get_assignments_in_range(today, end_date)
    ]

    print(f'Upcoming assignments over the next {args.days_forward} days ({today:%m/%d}\U000027A1 {end_date:%m/%d}):')
    print(f'{"Course Name":<20} {"Assignment": <15}   Due Date        Submitted')
    for assignment in upcoming_assignments:
        print(assignment)


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
        _ProactorBasePipeTransport.__del__ = silence_event_loop_closed(
            _ProactorBasePipeTransport.__del__
        )
    asyncio.run(main())
