from progressreporting.TelegramProgressReporter import SafeTelegramReporter4Loops
import my_telegram_bots # Here I keep the info from my bots, never make it public!
from time import sleep
import numpy as np

MAX_K = 999
TOTAL_LOOP_TIME = 33 # Seconds

reporter = SafeTelegramReporter4Loops(bot_token=my_telegram_bots.robobot.token, chat_id=my_telegram_bots.chat_ids['Robobot TCT setup'])

with reporter.report_loop(total_loop_iterations=MAX_K, loop_name='Testing warnings'):
	for k in range(MAX_K):
		sleep(TOTAL_LOOP_TIME/MAX_K) # Here you would do some stuff, I will just sleep..
		if k in {111,112}:
			reporter.warn('This warning should be notified two times, in two different messages.')
		if 222 < k < 333:
			reporter.warn("A very repetitive warning! Don't worry, you will not be spammed. They will be all collected in a small number of messages.")
		if k == 444:
			reporter.warn("Now I will report many different warnings at the same time.")
			reporter.warn("All these warnings will be collected in one message.")
			reporter.warn("Well, it may be in two messages. Because the first warning will be sent immediately, and the next warnings will be collected and sent later on. This, however, will depend on the time elapsed since the previous warning report and the <minimum_warn_time_seconds> passed when creating the TelegramProgressReporter.")
			reporter.warn("This is the last warning, I promise.")
		if np.random.rand() < 2/MAX_K: # Randomly let's assume that the temperature of your device gets too high.
			reporter.warn("The temperature is too high!")
		reporter.update(1) # This line tells the reporter that one loop has been completed, and automatically sends the updates once per minute to the Telegram chat.
