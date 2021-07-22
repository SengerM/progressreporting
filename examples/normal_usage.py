from progressreporting.TelegramProgressReporter import TelegramProgressReporter
from data_processing_bureaucrat.Bureaucrat import TelegramReportingInformation # Here I hide the token of my bot. Never make it public.
from time import sleep

MAX_K = 999
TOTAL_LOOP_TIME = 5*60 # Seconds, this is 5 minutes.
TOKEN = TelegramReportingInformation().token # Replace this line with the token of your bot.
CHAT_ID = TelegramReportingInformation().chat_id # Replace this line with the chat_id to which you want to send the information.

with TelegramProgressReporter(MAX_K, TOKEN,	CHAT_ID, f'Testing the TelegramProgressReporter in a normal condition') as reporter:
	for k in range(MAX_K):
		sleep(TOTAL_LOOP_TIME/MAX_K) # Here you would do some stuff, I will just sleep.
		reporter.update(1) # This line tells the reporter that one loop has been completed, and automatically sends the updates once per minute to the Telegram chat.
