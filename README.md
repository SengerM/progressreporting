# progressreporting

Report the progress of long time lasting loops (e.g. ```for``` and ```while```) to your cell phone/computer using a Telegram bot.

Tested on Ubuntu, Windows and Raspberri Pi!

## Installation

```
pip3 install git+https://github.com/SengerM/progressreporting
```

## Usage example

The following example shows the best way to use the ```TelegramProgressReporter``` to report the progress of a loop. The ```with``` statement ensures that the inizialization and finalization is done properly (you'll be properly notified in the begining and the ending of the loop, despite there is an error or not). 

```Python
from progressreporting.TelegramProgressReporter import TelegramProgressReporter
import time

MAX_K = 99999

with TelegramProgressReporter(MAX_K, 'token of your bot', 'ID of the chat to send the messages', 'This is a long loop') as reporter:
	for k in range(MAX_K):
		print(k)
		time.sleep(0.01)
		reporter.update(1)
```

The program will automatically send messages to your Telegram chat, below some examples:

- Loop in progress. It sends a single message that is updated each time ```reporter.update(count)``` is called.

![In progress...](pics/in_progress.png)

- Loop completed. It sends a new message to notify it was completed.

![Successful](pics/finished_success.png)

- Loop finished but without reaching 100 % (e.g. because of an error in your code or some problem). It sends a new message to notify and in the original message it reports that it did not reach 100 %.s

![Failed](pics/finished_but_failed.png)

### Notifying warnings

Sometimes some condition happens that is not enough to stop your program but you deserve to know about it. So it is not an error but a warning. The `TelegramProgressReporter` supports sending warnings, just proceed as follows:
```Python
from progressreporting.TelegramProgressReporter import TelegramProgressReporter
import time

MAX_K = 99999

with TelegramProgressReporter(MAX_K, 'token of your bot', 'ID of the chat to send the messages', 'This is a long loop') as reporter:
	for k in range(MAX_K):
		print(k)
		time.sleep(0.01)
		if k == 1111:
			reporter.warn('k is 1111! This is not too dangerous, but please pay attention.')
		reporter.update(1)
```
The `warn` method will send a new message notifying the warning. Don't worry if the `warn` method is called thousands of times per second. If this happens, there is an internal mechanism to register all these warnings and send them all packed together to the chat in a single compact message, to avoid spamming. The time after which warnings are collected and sent is specified by `minimum_warn_time_seconds` when creating the `TelegramProgressReporter` object, and by default is 5 minutes.

### Further examples

See the [examples directory](examples) for further examples.

## Error handling

The ```TelegramProgressReporter``` raises no errors at all. Consider, for example, that you started yesterday a loop that will last until tomorrow, and today you lost the internet connection for 10 minutes and the updates cannot be sent to your Telegram bot. You don't want the program to crash because of this stupidity. You don't have to worry because the only thing that ```TelegramProgressReporter``` will do is to display a warning, but the program will continue to run. When the connection is restored so it will the reporting.

## Creating a bot

To create a Telegram bot you can follow any of the tutorials that are around. To get the **chat ID** just talk to your bot, say "Hi", and then go to ```https://api.telegram.org/bot<YourBOTToken>/getUpdates```.
