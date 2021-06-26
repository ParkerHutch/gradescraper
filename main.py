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
        '--store-account',
        help='store username and password in the given filename for later use',
        type=str,
        default='',
    )

    account_info_group = parser.add_mutually_exclusive_group(required=True)
    account_info_group.add_argument(
        '-f',
        '--file',
        metavar='FILE',
        help='use file for account information',
        type=str,
        default='',
    )
    account_info_group.add_argument(
        '--account',
        nargs=2,
        metavar=('USERNAME', 'PASSWORD'),
        help='use given account name for Gradescope login, overriding the value stored in the file if passed with --file. Requires password to be specified via --file or --account',
        type=str,
        default='',
    )

    return parser


async def main():
    print('\U0001F4F6 Extracting courses and assignments...')
    args = get_parser().parse_args()  # TODO make sure this works
    account_email = ''
    password = ''

    if args.file:
        with open(args.file, 'r') as account_file:
            account_json = json.load(account_file)
            account_email, password = (
                account_json['email'],
                account_json['password'],
            )
    else:
        account_email, password = args.account

    if args.store_account:
        with open(args.store_account, 'w') as account_file:
            account_dict = {"email": account_email, "password": password}
            json.dump(account_dict, account_file, ensure_ascii=False, indent=4)

    async with GradescopeMessenger(account_email, password) as messenger:
        courses = await messenger.get_courses_and_assignments()

    # TODO should actually be datetime.now() in prod
    today = datetime.datetime(2021, 4, 10)

    upcoming_assignments = [
        assignment
        for course in courses
        for assignment in course.get_assignments_in_range(
            today, today + datetime.timedelta(days=7)
        )
    ]

    print('Upcoming assignments:')
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
