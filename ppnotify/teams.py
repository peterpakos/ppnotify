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
import requests

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

    def send(self, sender, subject, message, code=False):
        body = []

        message = message.replace('\n', '\n\n')

        if sender:
            body.append({
                "type": "TextBlock",
                "text": sender,
                "weight": "Lighter",
                "size": "Small",
                "wrap": True
            })

        if subject:
            body.append({
                "type": "TextBlock",
                "text": subject,
                "weight": "Bolder",
                # "size": "Large",
                "wrap": True
            })

        body.append({
            "type": "TextBlock",
            "text": message,
            "wrap": True,
            "FontType": "monospace" if code else "default"
        })

        payload = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.5",
                        "body": body,
                        "msteams": {
                            "width": "Full"
                        }
                    }
                }
            ]
        }

        requests.post(self._webhook_url, headers={'Content-Type': 'application/json'}, json=payload)

        return
