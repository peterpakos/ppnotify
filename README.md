# ppnotify
Tool to send notifications

PyPI package: [ppnotify](https://pypi.org/project/ppnotify/)

Feel free to open a [GitHub issue](https://github.com/peterpakos/ppnotify/issues) if you spot a problem or have an
improvement idea. I will be happy to look into it for you.

## Installation
The package is available in PyPI and can be installed using pip:
```
$ pip install --user ppnotify
$ ppnotify --help
```

Once installed, a command line tool `ppnotify` will be available in your system's PATH.

## Configuration
By default, the tool reads its configuration from `~/.config/ppnotify` file (the
location can be overridden by setting environment variable `XDG_CONFIG_HOME`).

The config file should look like this:
```
[default]
slack_key=xxx
email_domain=example.com
```

## Usage - Help
```
$ ppnotify --help
usage: ppnotify [--version] [--help] [--debug] [--verbose] [-f SENDER] -t RECIPIENTS [RECIPIENTS ...] [-s SUBJECT] [-H]

Tool to send Slack messages

options:
  --version             show program's version number and exit
  --help                show this help message and exit
  --debug               debugging mode
  --verbose             verbose debugging mode
  -f SENDER, --from SENDER
                        sender
  -t RECIPIENTS [RECIPIENTS ...], --to RECIPIENTS [RECIPIENTS ...]
                        recipient
  -s SUBJECT, --subject SUBJECT
                        subject
  -H, --code            send code block
```

## Usage - CLI
```
$ echo 'The king is dead, long live the king!' \
  | ppnotify -Hf 'Jon Snow' \
  -t 'arya.stark@winterfell.com' \
  -s 'Re: secret message'
```

## Usage - Python module
```
from ppnotify import Slack

slack = Slack()

status = slack.send(
    sender='Jon Snow',
    recipients=['arya.stark@winterfell.com'],
    subject='Re: secret message',
    message='The king is dead, long live the king!',
    code=True
)
```
