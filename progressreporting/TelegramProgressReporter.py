import datetime
import warnings
import requests
try:
	import humanize
except ImportError:
	raise ImportError('You need the "humanize" package, just run "pip install humanize".')

class TelegramProgressReporter:
	"""
	Usage example
	-------------
	
	from progressreporting.TelegramProgressReporter import TelegramProgressReporter
	import time

	BOT_TOKEN = 'Token of your bot'
	CHAT_ID = 'ID of the chat to which you want to send the updates'

	MAX_K = 99999

	with TelegramProgressReporter(MAX_K, BOT_TOKEN, CHAT_ID, 'This is a long loop') as reporter:
		for k in range(MAX_K):
			print(k)
			time.sleep(0.01)
			reporter.update(1)
	
	"""
	def __init__(self, total: int, telegram_token: str, telegram_chat_id: str, loop_name=None, miminum_update_time_seconds=60, minimum_warn_time_seconds=60*5):
		self._telegram_token = telegram_token
		self._telegram_chat_id = telegram_chat_id
		self._title = loop_name if loop_name is not None else ('loop started on ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
		if not isinstance(total, int):
			raise TypeError(f'<total> must be an integer number, received {total} of type {type(total)}.')
		self._total = total
		self._session = requests.Session() # https://stackoverflow.com/questions/25239650/python-requests-speed-up-using-keep-alive
		self._minimum_update_time = datetime.timedelta(seconds=float(miminum_update_time_seconds))
		self._minimum_warn_time = datetime.timedelta(seconds=float(minimum_warn_time_seconds))
	
	@property
	def expected_finish_time(self):
		return self._start_time + (datetime.datetime.now()-self._start_time)/self._count*self._total if self._count != 0 else None
	
	def __enter__(self):
		self._count = 0
		self._start_time = datetime.datetime.now()
		try:
			response = self.send_message(f'Starting "{self._title}"...\nToday/now it is {self._start_time.strftime("%Y-%m-%d %H:%M")}\nThe next update of this message should be in {humanize.naturaldelta(self._minimum_update_time)}.')
			self._message_id = response['result']['message_id']
		except Exception as e:
			warnings.warn(f'Could not establish connection with Telegram to send the progress status. Reason: {repr(e)}')
		return self
		
	def __exit__(self, exc_type, exc_value, exc_traceback):
		self._send_warnings() # If there are warnings accumulated, sent them.
		if hasattr(self, '_message_id'):
			message_string = f'{self._title}\n\n'
			if self._count != self._total:
				message_string += f'FINISHED WITHOUT REACHING 100 %\n\n'
			message_string += f'Finished on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}\n'
			message_string += f'Total elapsed time: {humanize.naturaldelta(datetime.datetime.now()-self._start_time)}\n'
			if self._count != self._total:
				message_string += f'Percentage reached: {int(self._count/self._total*100)} %\n'
				if self.expected_finish_time is not None:
					message_string += f'Expected missing time: {humanize.naturaldelta(datetime.datetime.now()-self.expected_finish_time)}\n'
			try:
				self.edit_message(
					message_text = message_string,
					message_id = self._message_id,
				)
				self.send_message(
					message_text = 'Finished!',
					reply_to_message_id = self._message_id,
				)
			except Exception as e:
				warnings.warn(f'Could not establish connection with Telegram to send the progress status. Reason: {repr(e)}')
	
	def send_message(self, message_text, reply_to_message_id=None):
		# https://core.telegram.org/bots/api#sendmessage
		parameters = {
				'chat_id': self._telegram_chat_id,
				'text': message_text,
			}
		if reply_to_message_id is not None:
			parameters['reply_to_message_id'] = str(int(reply_to_message_id))
		response = self._session.get(
			f'https://api.telegram.org/bot{self._telegram_token}/sendMessage',
			data = parameters,
			timeout = 1, # https://stackoverflow.com/a/21966169/8849755
		)
		return response.json()

	def edit_message(self, message_text, message_id):
		# https://core.telegram.org/bots/api#editmessagetext
		self._session.post(
			f'https://api.telegram.org/bot{self._telegram_token}/editMessageText',
			data = {
				'chat_id': self._telegram_chat_id,
				'text': message_text,
				'message_id': str(message_id),
			},
			timeout = 1, # https://stackoverflow.com/a/21966169/8849755
		)
	
	def set_completed(self):
		if not hasattr(self, '_count'):
			raise RuntimeError(f'Before calling to <set_completed> you should create a context using "with TelegramProgressBar(...) as reporter:".')
		self._count = self._total
	
	def count(self, count):
		if not hasattr(self, '_count'):
			raise RuntimeError(f'Before calling to <count> you should create a context using "with TelegramProgressBar(...) as reporter:".')
		self._count += count
	
	def report(self):
		"""This is the method that actually sends a report to the Telegram
		chat. Normally you should not call this method, unless for some 
		reason you want to force the report."""
		message_string = f'{self._title}\n\n'
		message_string += f'{self._start_time.strftime("%Y-%m-%d %H:%M")} | Started\n'
		if self.expected_finish_time is not None:
			message_string += f'{self.expected_finish_time.strftime("%Y-%m-%d %H:%M")} | Expected finish\n'
			message_string += f'{humanize.naturaltime(datetime.datetime.now()-self.expected_finish_time)} | Remaining\n'
		else:
			message_string += f'Unknown | Expected finish\n'
			message_string += f'Unknown | Remaining\n'
		message_string += '\n'
		message_string += f'{self._count}/{self._total} | {int(self._count/self._total*100)} %'
		message_string += '\n'
		message_string += '\n'
		message_string += f'Last update of this message: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}\n'
		message_string += f'The next update of this message should be in {humanize.naturaldelta(self._minimum_update_time)}.'
		try:
			if hasattr(self, '_message_id'): # This should be the standard case, unless the message could not be sent in the __enter__ method.
				self.edit_message(
					message_text = message_string,
					message_id = self._message_id,
				)
			else: # If there was a problem in the __enter__ method while sending the message, let's send it now so later on we can edit it.
				response = self.send_message(message_string)
				self._message_id = response['result']['message_id']
		except KeyboardInterrupt:
			raise KeyboardInterrupt()
		except Exception as e:
			warnings.warn(f'Could not establish connection with Telegram to send the progress status. Reason: {repr(e)}')
	
	def update(self, count: int):
		"""Call this method regularly within the loop to update the status.
		<count> is an integer number telling how many loops were completed. 
		If you call this once per loop (the usual way) you should use <count=1>.
		If for some reason you skip N loops (handling some error or something) 
		then you should call <count=N>.
		When calling this method, updates are automatically sent to the 
		Telegram chat.
		This method will send the warnings too, in case they are accumulated."""
		if not hasattr(self, '_count'):
			raise RuntimeError(f'Before calling to <update> you should create a context using "with TelegramProgressBar(...) as reporter:".')
		if not isinstance(count, int):
			raise TypeError(f'<count> must be an integer number, received {count} of type {type(count)}.')
		if not hasattr(self, '_last_update'):
			self._last_update = datetime.datetime.now()
		self.count(count)
		if datetime.datetime.now() - self._last_update >= self._minimum_update_time:
			self.report()
			self._last_update = datetime.datetime.now()
		self._send_warnings()
	
	def warn(self, message: str):
		"""Sends a new message as an answer to the original message with
		some warning message. The minimum time between two consecutive
		warning messages is specified by the <minimum_warn_time_seconds>
		parameter in the __init__ method. If multiple calls to self.warn
		are performed in less than <minimum_warn_time_seconds> the messages
		are stored and dispatched later on all together in a single message. 
		This avoids spamming the Telegram account and avoids the bot being
		blocked by Telegram for "inhuman behavior".
		Raises TypeError if <message> is not a string."""
		if not isinstance(message, str):
			raise TypeError(f'<message> must be a string, received an object of type {type(message)}.')
		if not hasattr(self, '_accumulated_warnings'):
			self._accumulated_warnings = {}
		if message not in self._accumulated_warnings:
			self._accumulated_warnings[message] = 1
		else:
			self._accumulated_warnings[message] += 1 # Increase the count for this type of warning, in case it is reported multiple times within the "minimum warn time".
		self._send_warnings()
		
	def _send_warnings(self):
		"""This method handles all the bureaucracy of actually sending 
		the warnings to the Telegram bot, taking care of waiting the 
		correct amount of time, collect all the warnings that are waiting
		and of writing a nice message."""
		if not hasattr(self, '_accumulated_warnings') or self._accumulated_warnings == {}: # Nothing to send...
			return
		if not hasattr(self, '_last_warn'):
			self._last_warn = datetime.datetime.now() - 2*self._minimum_warn_time # Initialize it like this so the first warning is instantly sent.
		if datetime.datetime.now() - self._last_warn >= self._minimum_warn_time: # Send warnings.
			self._last_warn = datetime.datetime.now()
			if len(self._accumulated_warnings) == 1: # There is only a single warning to show, print a simple message easy to read.
				message2send = list(self._accumulated_warnings.keys())[0] # This is the message of the warning.
				if self._accumulated_warnings[message2send] > 1: # This means that the warning was "raised" multiple times. We have to inform this!
					message2send += f'\n\nThis warning happened {self._accumulated_warnings[message2send]} in the last {humanize.naturaldelta(self._minimum_warn_time)}.'
			else: # This means that there are multiple warnings waiting to be sent.
				message2send = f'Multiple warnings were accumulated in the last {humanize.naturaldelta(self._minimum_warn_time)}:'
				for msg, count in self._accumulated_warnings.items():
					message2send += '\n----\n'
					message2send += msg
					if count > 1:
						message2send += f'\nThis warning happened {count} times.'
			if not hasattr(self, '_message_id'): # This means that the original message was not yet sent. We just wait, sooner or later it will be sent. And we cannot do anything anyway...
				return
			try:
				self.send_message(
					message_text = message2send,
					reply_to_message_id = self._message_id,
				)
				self._accumulated_warnings = {} # Delete all warnings after having sent them.
			except KeyboardInterrupt:
				raise KeyboardInterrupt()
			except Exception as e:
				warnings.warn(f'Could not establish connection with Telegram to send the warnings. Reason: {repr(e)}')

if __name__ == '__main__':
	from data_processing_bureaucrat.Bureaucrat import TelegramReportingInformation
	from time import sleep
	
	MAX_K = 999
	
	with TelegramProgressReporter(
		MAX_K, 
		TelegramReportingInformation().token, 
		TelegramReportingInformation().chat_id, 
		f'Testing the TelegramProgressReporter class',
		miminum_update_time_seconds = 22, 
		minimum_warn_time_seconds = 11,
	) as reporter:
		for k in range(MAX_K):
			sleep(60*2/MAX_K)
			if k in {111,112}:
				reporter.warn('This warning should be notified two times, in two different messages.')
			if 222 < k < 333:
				reporter.warn("A very repetitive warning! Don't worry, you will not be spammed. They will be all collected in a small number of messages.")
			if k == 444:
				reporter.warn("Now I will report many different warnings at the same time.")
				reporter.warn("All these warnings will be collected in one message.")
				reporter.warn("Well, it may be in two messages. Because the first warning will be sent immediately, and the next warnings will be collected and sent later on. This, however, will depend on the time elapsed since the previous warning report and the <minimum_warn_time_seconds> passed when creating the TelegramProgressReporter.")
				reporter.warn("This is the last warning, I promise.")
			reporter.update(1)
