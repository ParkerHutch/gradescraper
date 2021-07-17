import argparse
import asyncio
import datetime
import platform
from asyncio.proactor_events import _ProactorBasePipeTransport
from functools import wraps

import keyring

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
        help='store username and password for later use',
        action='store_const',
        const='data.json',
        default=False,
    )
    parser.add_argument(
        '--forget-me',
        help='delete stored username and password and exit',
        action='store_true',
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

    parser.add_argument(
        '-d',
        '--days-forward',
        metavar='NUM',
        help='retrieve assignments up to NUM days from today',
        type=int,
        default=7,
    )

    return parser


async def main():
    args = get_parser().parse_args()

    service_id = 'Gradescraper'

    if args.forget_me:
        account_email = keyring.get_password(service_id, 'STORED_EMAIL')
        if not account_email:
            print('No stored account info was found')
        else:
            keyring.delete_password(service_id, account_email)
            keyring.delete_password(service_id, 'STORED_EMAIL')
            print(f'Removed account information for {account_email}')

        return None

    if args.account:
        account_email, password = args.account
        if args.remember_me:
            keyring.set_password(service_id, account_email, password)
            keyring.set_password(service_id, 'STORED_EMAIL', account_email)
    else:
        account_email = keyring.get_password(service_id, 'STORED_EMAIL')
        password = keyring.get_password(service_id, account_email)
        if not (account_email and password):
            print(
                'No stored account info was found. Please run with --account and --remember-me to save account information.'
            )
            return None

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

    print(
        f'Upcoming assignments over the next {args.days_forward} days ({today:%m/%d}\U000027A1 {end_date:%m/%d}):'
    )
    print(
        f'{"Course Name":<20} {"Assignment": <15}   Due Date        Submitted'
    )
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
