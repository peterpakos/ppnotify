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
slack_key = xxx
email_domain = example.com

[teams]
channel1 = https://url1.example.com
channel2 = https://url2.example.com
```

## Usage - Help
```
$ ppnotify --help
usage: ppnotify [--version] [--help] [--debug] [--verbose] [-m {slack,teams}] [-f SENDER] -t RECIPIENTS [RECIPIENTS ...] [-s SUBJECT] [-H]

Tool to send notifications

options:
  --version             show program's version number and exit
  --help                show this help message and exit
  --debug               debugging mode
  --verbose             verbose debugging mode
  -m, --method {slack,teams}
                        notification method (default: teams)
  -f, --from SENDER     sender
  -t, --to RECIPIENTS [RECIPIENTS ...]
                        recipient
  -s, --subject SUBJECT
                        subject
  -H, --code            send code block
```

## Usage - CLI
```
$ echo 'The king is dead, long live the king!' \
  | ppnotify -Hf 'Jon Snow' \
  -t 'game-of-thrones-channel' \
  -s 'Re: secret message'
```

## Usage - Python module
```
from ppnotify import Slack

slack = Slack()

status = slack.send(
    sender='Jon Snow',
    recipients=['game-of-thrones-channel'],
    subject='Re: secret message',
    message='The king is dead, long live the king!',
    code=True
)
```
