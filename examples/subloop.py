from progressreporting.TelegramProgressReporter import SafeTelegramReporter4Loops
import my_telegram_bots # Here I keep the info from my bots, never make it public!
from time import sleep
import numpy

reporter = SafeTelegramReporter4Loops(
	bot_token = my_telegram_bots.robobot.token,
	chat_id = my_telegram_bots.chat_ids['Robobot TCT setup'],
	parse_mode = 'Markdown',
)

n_iterations = 9
subloop_time = 33 # seconds
with reporter.report_loop(n_iterations,'Main loop',20):
	for n1 in range(n_iterations):
		n_subiterations = numpy.random.randint(low=111,high=222)
		with reporter.report_subloop(n_subiterations,f'Subloop number {n1}',20) as subloop_reporter:
			for n2 in range(n_subiterations):
				sleep(subloop_time/n_subiterations)
				if n2 == int(n_subiterations/2):
					subloop_reporter.warn(f'n2 = {n2}! *This is important*.')
				subloop_reporter.update(1)
		reporter.update(1) # This line tells the reporter that one iteration has been completed, and automatically sends the updates once per minute to the Telegram chat.
