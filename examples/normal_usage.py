from progressreporting.TelegramProgressReporter import TelegramReporter
from data_processing_bureaucrat.Bureaucrat import TelegramReportingInformation # Here I hide the token of my bot. Never make it public.
from time import sleep

reporter = TelegramReporter(
	telegram_token = TelegramReportingInformation().token, # Here I store the token of my bot hidden, never make it public.
	telegram_chat_id = TelegramReportingInformation().chat_id,
)

reporter.send_message('Send whatever message you like.')
reporter.send_message('It is safe to send messages with this method because it will not raise any error if the message cannot be sent (e.g. cause the internet connection is down), so your program will not crash. It will just show a warning.')
reporter.send_message('This method has to be used to send individual messages, but you are responsible for not putting this into a `for` loop to avoid spamming your Telegram chat. Also, Telegram will temporarily block the bot if they detect you are sending too much messages, so be careful.')


MAX_K = 999
TOTAL_LOOP_TIME = 5*60 # Seconds, this is 5 minutes.
TOKEN = TelegramReportingInformation().token # Replace this line with the token of your bot.
CHAT_ID = TelegramReportingInformation().chat_id # Replace this line with the chat_id to which you want to send the information.

with reporter.report_for_loop(MAX_K,'An optional name for the loop') as reporter:
	for k in range(MAX_K):
		sleep(TOTAL_LOOP_TIME/MAX_K) # Here you would do some stuff, I will just sleep.
		reporter.update(1) # This line tells the reporter that one iteration has been completed, and automatically sends the updates once per minute to the Telegram chat.

reporter.send_message('Here you can send more messages.')
