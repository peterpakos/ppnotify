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
import requests
from requests.exceptions import RequestException, Timeout
import time

from ppconfig import Config

log = logging.getLogger(__name__)


class Teams:
    def __init__(self, channel):
        try:
            self._config = Config('ppnotify')
            self._webhook_url = self._config.get(channel, section='teams')
        except Exception as e:
            log.debug(e)
            raise
        else:
            log.debug('Successfully obtained Teams webhook URL from config')

    @staticmethod
    def _post_with_retry(url, payload, headers=None, max_attempts=5, base_delay=1.0, timeout=5.0):
        headers = headers or {'Content-Type': 'application/json'}
        last_exception = None

        for attempt in range(1, max_attempts + 1):
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=timeout)

                # Success
                if response.status_code < 300:
                    return response

                # Rate limited or transient server error
                if response.status_code in (429, 500, 502, 503, 504):
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

    def send(self, sender, subject, message, code=False):
        body = []

        lines = [line.replace(' ', '\u00A0') for line in message.splitlines()]

        if sender:
            body.append({
                'type': 'TextBlock',
                'text': sender,
                'weight': 'Lighter',
                'size': 'Small',
                'spacing': 'Default',
                'wrap': True
            })

        if subject:
            body.append({
                'type': 'TextBlock',
                'text': subject,
                'weight': 'Bolder',
                'size': 'Default',
                'spacing': 'Default',
                'wrap': True
            })

        for idx, line in enumerate(lines):
            body.append({
                'type': 'TextBlock',
                'text': line,
                'weight': 'Lighter',
                'size': 'Small',
                'spacing': 'None' if idx > 1 else 'Default',
                'wrap': True,
                'fontType': 'Monospace' if code else 'Default'
            })

        payload = {
            'type': 'message',
            'attachments': [
                {
                    'contentType': 'application/vnd.microsoft.card.adaptive',
                    'content': {
                        '$schema': 'http://adaptivecards.io/schemas/adaptive-card.json',
                        'type': 'AdaptiveCard',
                        'version': '1.5',
                        'body': body,
                        'msTeams': {
                            'width': 'Full'
                        }
                    }
                }
            ]
        }

        self._post_with_retry(self._webhook_url, payload)

        return True
