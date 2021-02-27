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

	MAX_K = 99

	with TelegramProgressReporter(MAX_K, BOT_TOKEN, CHAT_ID, 'I am anxious about this loop') as reporter:
		for k in range(MAX_K):
			print(k)
			reporter.update(1)
			time.sleep(1)
	
	"""
	def __init__(self, total: int, telegram_token: str, telegram_chat_id: str, title=None, miminum_update_time_seconds=10):
		self._telegram_token = telegram_token
		self._telegram_chat_id = telegram_chat_id
		self._title = title if title is not None else ('Loop started on ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
		if not isinstance(total, int):
			raise TypeError(f'<total> must be an integer number, received {total} of type {type(total)}.')
		self._total = total
		self._session = requests.Session() # https://stackoverflow.com/questions/25239650/python-requests-speed-up-using-keep-alive
		self._minimum_update_time = datetime.timedelta(seconds=miminum_update_time_seconds)
	
	
	@property
	def now(self):
		return datetime.datetime.now()
	
	@property
	def expected_finish_time(self):
		return self._start_time + (self.now-self._start_time)/self._count*self._total if self._count != 0 else None
	
	def __enter__(self):
		try:
			response = self.send_message(f'Starting {self._title}...')
			self._message_id = response['result']['message_id']
		except Exception as e:
			warnings.warn(f'Could not establish connection with Telegram to send the progress status. Reason: {repr(e)}')
		self._count = 0
		self._start_time = self.now
		return self
		
	def __exit__(self, exc_type, exc_value, exc_traceback):
		
		if hasattr(self, '_message_id'):
			message_string = f'{self._title}\n\n'
			if self._count != self._total:
				message_string += f'FINISHED WITHOUT REACHING 100 %\n\n'
			message_string += f'Finished on {self.now.strftime("%Y-%m-%d %H:%M")}\n'
			message_string += f'Total elapsed time: {humanize.naturaldelta(self.now-self._start_time)}\n'
			if self._count != self._total:
				message_string += f'Percentage reached: {int(self._count/self._total*100)} %\n'
				if self.expected_finish_time is not None:
					message_string += f'Expected missing time: {humanize.naturaldelta(self.now-self.expected_finish_time)}\n'
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
			data = parameters
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
			}
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
		if hasattr(self, '_message_id'):
			message_string = f'{self._title}\n\n'
			message_string += f'{self._start_time.strftime("%Y-%m-%d %H:%M")} | Started\n'
			if self.expected_finish_time is not None:
				message_string += f'{self.expected_finish_time.strftime("%Y-%m-%d %H:%M")} | Expected finish\n'
				message_string += f'{humanize.naturaltime(self.now-self.expected_finish_time)} | Remaining\n'
			else:
				message_string += f'Unknown | Expected finish\n'
				message_string += f'Unknown | Remaining\n'
			message_string += '\n'
			message_string += f'{self._count}/{self._total} | {int(self._count/self._total*100)} %'
			message_string += '\n'
			message_string += '\n'
			message_string += f'Last update of this message: {self.now.strftime("%Y-%m-%d %H:%M")}'
			try:
				self.edit_message(
					message_text = message_string,
					message_id = self._message_id,
				)
			except KeyboardInterrupt:
				raise KeyboardInterrupt()
			except Exception as e:
				warnings.warn(f'Could not establish connection with Telegram to send the progress status. Reason: {repr(e)}')
	
	def update(self, count: int):
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
