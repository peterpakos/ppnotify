# -*- coding: utf-8 -*-
"""This module implements sending MS Teams messages

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

import logging
import random
import re
import requests
from requests.exceptions import RequestException, Timeout
import time

from ppconfig import Config

log = logging.getLogger(__name__)


class Teams:
    def __init__(self, channel):
        self._team_id = None
        self._channel_id = None

        try:
            self._config = Config('ppnotify')
            channel_config = self._config.get(channel, section='teams')

            if channel_config.startswith('https://'):
                self._webhook_url = channel_config
                log.debug('Using dedicated webhook URL')
            else:
                self._webhook_url = self._config.get('webhook_url', section='teams')
                self._team_id = channel_config.split(',')[0]
                self._channel_id = channel_config.split(',')[1]
                log.debug('Using default webhook URL, team ID and channel ID')
        except Exception as e:
            log.debug(e)
            raise
        else:
            log.debug(f'Successfully initialized Teams configuration for channel: {channel}')

    @staticmethod
    def _post_with_retry(url, payload, headers=None, max_attempts=5, base_delay=1.0, timeout=5.0):
        headers = headers or {'Content-Type': 'application/json'}
        last_exception = None

        for attempt in range(1, max_attempts + 1):
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=timeout)

                # Success
                if response.status_code < 300:
                    log.debug(f'POST successful on attempt #{attempt}: {response.status_code}')
                    return response

                # Rate limited or transient server error
                if response.status_code in (429, 500, 502, 503, 504):
                    log.debug(f'POST failed on attempt #{attempt}: {response.status_code}')
                    raise RuntimeError(
                        f'Retryable HTTP {response.status_code}: {response.text}'
                    )

                # Non-retryable client error
                response.raise_for_status()

            except (Timeout, RequestException, RuntimeError) as e:
                last_exception = e

                if attempt == max_attempts:
                    raise

                # Exponential backoff with jitter
                sleep = base_delay * (2 ** (attempt - 1))
                sleep += random.uniform(0, sleep * 0.1)

                time.sleep(sleep)

        # Defensive: should never be reached
        raise RuntimeError("post_with_retry exited unexpectedly") from last_exception

    @staticmethod
    def _url_replacer(match):
        url = match.group(0)
        # Check if the URL is already in [URL](URL) format
        # Get the string being processed from match.string
        start = match.start()
        end = match.end()
        before = match.string[max(0, start-1):start]
        after = match.string[end:end+1]
        # If the URL is already inside []() pattern, skip replacement
        if before == '(' and after == ')':
            return url
        return f'[{url}]({url})'

    # Workaround for Teams Adaptive Cards: preserve indentation by
    # prepending a zero-width space and replacing spaces with figure spaces
    @staticmethod
    def _preserve_indentation(line):
        return '\u200B' + line.replace(' ', '\u00A0')

    def send(self, sender, subject, message, code=False):
        body = []

        message = re.sub(r'(?<!]\()https?://\S+', self._url_replacer, message)
        message = '   \n'.join(self._preserve_indentation(ln) for ln in message.splitlines())

        if sender:
            body.append({
                'type': 'TextBlock',
                'text': sender,
                'weight': 'Lighter',
                'size': 'Small',
                'spacing': 'None',
                'wrap': True,
                'isSubtle': True
            })

        if subject:
            body.append({
                'type': 'TextBlock',
                'text': subject,
                'weight': 'Bolder',
                'size': 'Small',
                'spacing': 'ExtraSmall',
                'wrap': True,
                'separator': True
            })

        if message:
            body.append({
                'type': 'TextBlock',
                'text': message,
                'weight': 'Lighter',
                'size': 'Small',
                'spacing': 'ExtraSmall',
                'wrap': True,
                'fontType': 'Monospace' if code else 'Default'
            })

        payload = {
            '$schema': 'http://adaptivecards.io/schemas/adaptive-card.json',
            'type': 'AdaptiveCard',
            'version': '1.5',
            'msTeams': {
                'width': 'Full'
            },
            'body': body
        }

        if self._team_id and self._channel_id:
            payload['teamId'] = self._team_id
            payload['channelId'] = self._channel_id

        self._post_with_retry(self._webhook_url, payload)

        return True
