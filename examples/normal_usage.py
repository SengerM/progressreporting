from progressreporting.TelegramProgressReporter import SafeTelegramReporter4Loops
import my_telegram_bots # Here I keep the info from my bots, never make it public!
from time import sleep

reporter = SafeTelegramReporter4Loops(
	bot_token = my_telegram_bots.robobot.token,
	chat_id = my_telegram_bots.chat_ids['Robobot TCT setup'],
	parse_mode = 'Markdown',
)

reporter.send_message('Send whatever message you like. 😃')
reporter.send_message('It is safe to send messages with this method because *it will not raise any error* if the message cannot be sent (e.g. cause the internet connection is down), so your program will not crash. It will __just show a warning__.')
reporter.send_message('If you use `reporter.send_message` then *you are responsible* for not putting this into a `for` loop *to avoid spamming* your Telegram chat. Also, *Telegram will temporarily block the bot* if they detect you are sending too much messages, so be careful. The safe method to avoid this is `reporter.warn`.')

MAX_K = 999
TOTAL_LOOP_TIME = 60 # Seconds, this is 5 minutes.

with reporter.report_loop(MAX_K,'An optional name for the loop',20):
	for k in range(MAX_K):
		sleep(TOTAL_LOOP_TIME/MAX_K) # Here you would do some stuff, I will just sleep.
		reporter.update(1) # This line tells the reporter that one iteration has been completed, and automatically sends the updates once per minute to the Telegram chat.

reporter.send_message('Here you can send more messages.')
