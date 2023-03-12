# progressreporting

Easy and live status updates to a Telegram chat using a bot.

## Installation

```
pip install git+https://github.com/SengerM/progressreporting
```

## Usage

See the [examples directory](examples).

Quick example:

```python
from progressreporting.TelegramProgressReporter import SafeTelegramReporter4Loops
from time import sleep

reporter = SafeTelegramReporter4Loops(
	bot_token = "your_bot's_token",
	chat_id = 'id_of_a_chat_where_your_bot_can_send_messages_to',
)

reporter.send_message('Send whatever message you like. 😃')

n_iterations = 999
with reporter.report_loop(n_iterations,'Give your loop a name',20):
	for n in range(n_iterations):
		sleep(60/n_iterations) # Here you would do some stuff, I will just sleep.
		reporter.update(1) # This line tells the reporter that one iteration has been completed, and automatically sends the updates once per minute to the Telegram chat.
```

## Some screenshots

![Example screenshot](/docs/PyHEP_2021_workshop_presentation/media/3.svg)

## Creating a bot

To create a Telegram bot you can follow any of the tutorials that are around. 

To get the **chat ID** just talk to your bot, say "Hi", and then go to `https://api.telegram.org/bot<YourBOTToken>/getUpdates`. More info [here](https://stackoverflow.com/a/32572159/8849755).
