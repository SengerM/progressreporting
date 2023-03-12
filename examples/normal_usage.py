from progressreporting.TelegramProgressReporter import SafeTelegramReporter4Loops
import my_telegram_bots # Here I keep the info from my bots, never make it public!
from time import sleep

TOTAL_LOOP_TIME = 60 # Seconds, this is 5 minutes.

reporter = SafeTelegramReporter4Loops(
	bot_token = my_telegram_bots.robobot.token,
	chat_id = my_telegram_bots.chat_ids['Robobot TCT setup'],
	parse_mode = 'Markdown', # This is optional. But it is cool.
)

reporter.send_message('Send whatever message you like. 😃')
reporter.send_message('✅ It is safe to send messages with this method because if it cannot be sent (e.g. cause the internet connection is down) *it will not raise any error* but instead it will _just show a warning_. So your program will never crash because of this.')
reporter.send_message('⚠️ If you use `reporter.send_message` then *you are responsible* for not putting this into a `for` loop *to avoid spamming* your Telegram chat. Also, *Telegram will temporarily block the bot* if they detect you are sending too much messages, so be careful.\n\nThe safe way to send messages while reporting a loop is with `reporter.warn`.')

n_iterations = 999
with reporter.report_loop(n_iterations,'A loop in which everything works fine',20):
	for n in range(n_iterations):
		sleep(TOTAL_LOOP_TIME/n_iterations) # Here you would do some stuff, I will just sleep.
		reporter.update(1) # This line tells the reporter that one iteration has been completed, and automatically sends the updates once per minute to the Telegram chat.

reporter.send_message("Let's now see what happens when an error occurs within a loop that is being reported.")

with reporter.report_loop(n_iterations,'A loop with an error',20):
	for n in range(n_iterations):
		sleep(TOTAL_LOOP_TIME/n_iterations) # Here you would do some stuff, I will just sleep.
		
		if n == int(n_iterations*10/100):
			raise RuntimeError(f'Oh no!! An error!!!')
		
		reporter.update(1) # This line tells the reporter that one iteration has been completed, and automatically sends the updates once per minute to the Telegram chat.
