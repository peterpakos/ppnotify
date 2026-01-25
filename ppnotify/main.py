# -*- coding: utf-8 -*-
"""Tool to send notifications

Copyright (c) 2019-2026 Peter Pakos. All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import argparse
import os
import platform
import sys

from pplogger import get_logger
from . import __version__

__app_name__ = 'ppnotify'

parser = argparse.ArgumentParser(description='Tool to send notifications', add_help=False)
parser.add_argument('--version', action='version', version=f'{__app_name__} {__version__}')
parser.add_argument('--help', action='help', help='show this help message and exit')
parser.add_argument('--debug', action='store_true', dest='debug', help='debugging mode')
parser.add_argument('--verbose', action='store_true', dest='verbose', help='verbose debugging mode')
parser.add_argument('-m', '--method', dest='method', choices=['slack', 'teams'], default='teams',
                    help='notification method (default: %(default)s)')
parser.add_argument('-f', '--from', dest='sender', help='sender')
parser.add_argument('-t', '--to', dest='recipients', nargs='+', required=True, help='recipient', default=[])
parser.add_argument('-s', '--subject', dest='subject', default='', help='subject')
parser.add_argument('-H', '--code', dest='code', action='store_true', help='send code block')
args = parser.parse_args()

log = get_logger(name='ppnotify', debug=args.debug, verbose=args.verbose)


def main():
    log.debug(args)

    sender = args.sender if args.sender else os.getenv('USER') + '@' + platform.node()
    log.debug(f'Sender: {sender}')

    message = ''
    lines = 0

    for line in sys.stdin:
        message += line
        if line != '' and line != '\n':
            lines += 1

    if not lines:
        message = ''

    if not lines and not args.subject:
        log.warn('Nothing to send')
        sys.exit(0)

    try:
        if args.method == 'slack':
            from .slack import Slack
            slack = Slack()
            slack.send(
                sender=sender,
                recipients=args.recipients,
                subject=args.subject,
                message=message,
                code=args.code
            )
        elif args.method == 'teams':
            from .teams import Teams
            teams = Teams(args.recipients[0])
            teams.send(
                sender=sender,
                subject=args.subject,
                message=message,
                code=args.code
            )
        else:
            log.critical(f'Unknown method: {args.method}')
            sys.exit(0)
    except Exception as e:
        log.critical(e)
        sys.exit(0)
