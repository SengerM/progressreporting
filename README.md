# progressreporting

Report the progress of long time lasting ```for``` and ```while``` loops to your cell phone using a Telegram bot.

## Installation

```
pip3 install git+https://github.com/SengerM/progressreporting
```

## Usage example

The following example shows the best way to use the ```TelegramProgressReporter``` with a loop. The ```with``` statement ensures that the inizialization and finalization is done properly. Also, if for some reason the messages cannot be sent (e.g. the internet connection is temporarily lost) a warning is displayed but the program keeps running. When the connection is restored, the updates are sent.

```Python
from progressreporting.TelegramProgressReporter import TelegramProgressReporter
import time

BOT_TOKEN = 'Token of your bot'
CHAT_ID = 'ID of the chat to which you want to send the updates'

MAX_K = 99

with TelegramProgressReporter(MAX_K, BOT_TOKEN, CHAT_ID, 'I am anxious about this loop') as reporter:
	for k in range(MAX_K):
		print(k)
		reporter.update(1)
		time.sleep(1)
```

To create a Telegram bot you can follow any of the tutorials that are around. It should take not more than 10-20 minutes.
