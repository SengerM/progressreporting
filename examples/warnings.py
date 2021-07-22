from progressreporting.TelegramProgressReporter import TelegramProgressReporter
from data_processing_bureaucrat.Bureaucrat import TelegramReportingInformation # Here I hide the token of my bot. Never make it public.
from time import sleep
import numpy as np

MAX_K = 999
TOTAL_LOOP_TIME = 20*60 # Seconds, this is 20 minutes.
TOKEN = TelegramReportingInformation().token # Replace this line with the token of your bot.
CHAT_ID = TelegramReportingInformation().chat_id # Replace this line with the chat_id to which you want to send the information.

with TelegramProgressReporter(MAX_K, TOKEN,	CHAT_ID, f'Testing warnings') as reporter:
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
