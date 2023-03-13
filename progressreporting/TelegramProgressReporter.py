import datetime
import warnings
import requests
import humanize

def send_message(requests_session:requests.Session, bot_token:str, **parameters):
	"""Send a message.
	
	Arguments
	---------
	requests_session: requests.Session
		An instance handling the session.
	bot_token: str
		The token of the bot to use, e.g. `'123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'`.
	**parameters:
		Any of the parameters specified in the API, see here https://core.telegram.org/bots/api#sendmessage.
		The most relevant are the `chat_id` and `text`.
	"""
	response = requests_session.get(
		f'https://api.telegram.org/bot{bot_token}/sendMessage',
		data = parameters,
		timeout = 1, # https://stackoverflow.com/a/21966169/8849755
	)
	return response.json()

def edit_message(requests_session:requests.Session, bot_token:str, **parameters):
	"""Edit a message that was previously sent.
	
	Arguments
	---------
	requests_session: requests.Session
		An instance handling the session.
	bot_token: str
		The token of the bot to use, e.g. `'123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'`.
	**parameters:
		Any of the parameters specified in the API, see here hthttps://core.telegram.org/bots/api#editmessagetexttps://core.telegram.org/bots/api#editmessagetext.
		The most relevant are the `chat_id` and `text`.
	"""
	requests_session.post(
		f'https://api.telegram.org/bot{bot_token}/editMessageText',
		data = parameters,
		timeout = 1, # https://stackoverflow.com/a/21966169/8849755
	)

class SafeTelegramReporter:
	"""A class that allows to send messages without raising any error,
	only warnings."""
	def __init__(self, bot_token:str, chat_id:str, **default_parameters):
		"""
		Arguments
		---------
		bot_token: str
			The token of the bot to use, e.g. `'123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'`.
		chat_id: str
			The ID of the chat to which to send the messages to.
		default_parameters:
			Any extra parameter that will be used by default, unless overridden 
			when calling the methods. See options in https://core.telegram.org/bots/api#sendmessage.
		"""
		self._bot_token = bot_token
		self._chat_id = chat_id
		self._default_parameters = default_parameters
		self._session = requests.Session() # https://stackoverflow.com/questions/25239650/python-requests-speed-up-using-keep-alive
	
	def send_message(self, text:str, **parameters):
		"""Send a message, any error will be converted into a warning.
		
		Arguments
		---------
		text: str
			The text you want to send.
		**parameters:
			Additional arguments to be passed to the Telegram API, see https://core.telegram.org/bots/api#sendmessage.
		"""
		try:
			return send_message(requests_session=self._session, bot_token=self._bot_token, chat_id=self._chat_id, text=text, **{**self._default_parameters,**parameters})
		except Exception as e:
			warnings.warn(f'Could not send message to Telegram, reason: {repr(e)}. ')
	
	def edit_message(self, text:str, message_id, **parameters):
		"""Edit a message, any error will be converted into a warning.
		
		Arguments
		---------
		text: str
			The text you want to send.
		message_id:
			The ID of the message you want to edit.
		**parameters:
			Additional arguments to be passed to the Telegram API, see https://core.telegram.org/bots/api#sendmessage.
		"""
		try:
			return edit_message(requests_session=self._session, bot_token=self._bot_token, chat_id=self._chat_id, text=text, message_id=message_id, **{**self._default_parameters,**parameters})
		except Exception as e:
			warnings.warn(f'Could not edit message in Telegram, reason: {repr(e)}.')
	
class SafeTelegramReporter4Loops(SafeTelegramReporter):
	def __init__(self, bot_token:str, chat_id:str, **default_parameters):
		super().__init__(
			bot_token = bot_token,
			chat_id = chat_id,
			**default_parameters,
		)
		self._now_reporting = False
	
	def report_loop(self, total_loop_iterations:int, loop_name:str=None, miminum_update_time_seconds:float=60, minimum_warn_time_seconds:float=60):
		"""Configure the object to report a loop.
		
		Arguments
		---------
		total_loop_iterations: int
			Total number of loop iterations expected.
		loop_name: str, optional
			An optional name for the loop. If not provided a default
			name with a timestamp will be created.
		miminum_update_time_seconds: float, default 60
			Minimum time to wait before sending updated to the chat. If
			this value is too small (say 1 second) then the bot will be
			able to send one message every second with the risk of spamming
			the chat and being temporarily disabled by Telegram so be careful.
			With 60 seconds it works fine for most applications.
		minimum_warn_time_seconds: float, default 60
			Minimum time for sending warnings. The same as for `miminum_update_time_seconds`
			holds if this value is too small.
		"""
		self._title = loop_name if loop_name is not None else ('Loop started on ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
		if not isinstance(total_loop_iterations, int):
			raise TypeError(f'`total_loop_iterations` must be an integer, received object of type {type(total_loop_iterations)}.')
		self._total_iterations = total_loop_iterations
		self._minimum_update_time = datetime.timedelta(seconds=miminum_update_time_seconds)
		self._minimum_warn_time = datetime.timedelta(seconds=minimum_warn_time_seconds)
		return self
	
	def create_subloop_reporter(self):
		"""Creates a new instance of `SafeTelegramReporter4Loops` which
		is tied to the current instance in the sense that all its messages
		will by default answer to the current loop reporting message.
		"""
		if not self._now_reporting:
			raise RuntimeError('You can only report a subloop if you are already reporting a loop!')
		default_params = dict(self._default_parameters)
		default_params.pop('reply_to_message_id',None) # If the current instance was already replying to some message, because e.g. it is already a subloop reporter, remove this!
		subreporter = SafeTelegramReporter4Loops(
			bot_token = self._bot_token,
			chat_id = self._chat_id,
			reply_to_message_id = self._message_id_reporting_loop_progress,
			**default_params,
		)
		return subreporter
	
	def report_subloop(self, total_loop_iterations:int, loop_name:str=None, miminum_update_time_seconds:float=60, minimum_warn_time_seconds:float=60):
		"""Creates a new instance of `SafeTelegramReporter4Loops` which
		will answer to the current instance and configures it to report
		a loop, i.e. it calls the method `report_loop` on the new instance
		upon creation.
		
		Arguments
		---------
		See `SafeTelegramReporter4Loops.report_loop`.
		
		Returns
		-------
		subreporter: SafeTelegramReporter4Loops
			A new instance that will handle the subloop.
		"""
		subreporter = self.create_subloop_reporter()
		subreporter.report_loop(
			total_loop_iterations = total_loop_iterations, 
			loop_name = loop_name, 
			miminum_update_time_seconds = miminum_update_time_seconds, 
			minimum_warn_time_seconds = minimum_warn_time_seconds
		)
		return subreporter
	
	@property
	def expected_finish_time(self):
		return self._start_time + (datetime.datetime.now()-self._start_time)/self._count*self._total_iterations if self._count != 0 and self._now_reporting==True else None
	
	def __enter__(self):
		if self._now_reporting == True:
			raise RuntimeError(f'This instance is already reporting a loop named {repr(self._title)}, cannot report another loop before this one is finished.')
		self._count = 0
		self._start_time = datetime.datetime.now()
		try:
			response = self.send_message(
				f'🕰️ Starting "{self._title}"...\nToday/now it is {self._start_time.strftime("%Y-%m-%d %H:%M")}\nThe next update of this message should be in {humanize.naturaldelta(self._minimum_update_time)} or the time it takes for the loop to complete one iteration, whatever happens first.'
			)
			self._message_id_reporting_loop_progress = response['result']['message_id']
		except Exception as e:
			warnings.warn(f'Could not establish connection with Telegram to send the progress status. Reason: {repr(e)}')
		self._now_reporting = True
		return self
		
	def __exit__(self, exc_type, exc_value, exc_traceback):
		try:
			self._send_warnings(force=True) # If there are warnings accumulated, sent them.
			
			message_string = f'{self._title}\n\n'
			if self._count < self._total_iterations:
				message_string += f'💥 FINISHED WITHOUT REACHING 100 %\n\n'
				message_string += f'Reason: {repr(exc_value)}\n\n'
			else:
				message_string = '✅ ' + message_string
			message_string += f'Finished on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}\n'
			message_string += f'Total elapsed time: {humanize.naturaldelta(datetime.datetime.now()-self._start_time)}\n'
			if self._count != self._total_iterations:
				message_string += f'Progress: {self._count} iterations ({int(self._count/self._total_iterations*100)} %)\n'
				if self.expected_finish_time is not None:
					message_string += f'Expected missing time: {humanize.naturaldelta(datetime.datetime.now()-self.expected_finish_time)}\n'
			
			self.edit_message(
				text = message_string,
				message_id = self._message_id_reporting_loop_progress,
			)
			self.send_message(
				text = 'Finished!',
				reply_to_message_id = self._message_id_reporting_loop_progress,
			)
		except Exception as e:
			warnings.warn(f'Could not establish connection with Telegram to send the progress status. Reason: {repr(e)}')
		finally:
			self._now_reporting = False
	
	def set_completed(self):
		"""Sets the total number of iterations as complete, even if the
		count is not yet complete. This method should be used when you
		break a loop intentionally by some reason and you still want to
		inform that it was completed successfully. Example:
		for k in range(99):
			if k == 10:
				reporter.set_completed() # Indicate that even though k is not yet 99, the loop was completed successfully.
				break
			reporter.update(1)"""
		if self._now_reporting == False:
			raise RuntimeError(f'This method must be called from inside a context, i.e. inside a `with` statement.')
		self._count = self._total_iterations
	
	def count(self, count):
		"""This method increases the count of the loop by certain amount
		and does not report anything to the Telegram chat, unless after
		increasing the count it becomes higher than the total iterations
		informed when creating the object."""
		if self._now_reporting == False:
			raise RuntimeError(f'This method must be called from inside a context, i.e. inside a `with` statement.')
		self._count += count
		if self._count > self._total_iterations:
			self.warn(f'The iterations count has surpassed the number of iterations expected. The number of iterations expected was {self._total_iterations} and now I have already counted {self._count} iterations.')
	
	def report(self):
		"""This is the method that actually sends a report to the Telegram
		chat. Normally you should not call this method, unless for some 
		reason you want to force the report."""
		if self._now_reporting == False:
			raise RuntimeError(f'This method must be called from inside a context, i.e. inside a `with` statement.')
		message_string = f'🕰️ {self._title}\n\n'
		message_string += f'{self._start_time.strftime("%Y-%m-%d %H:%M")} | Started\n'
		if self.expected_finish_time is not None:
			message_string += f'{self.expected_finish_time.strftime("%Y-%m-%d %H:%M")} | Expected finish\n'
			message_string += f'{humanize.naturaltime(datetime.datetime.now()-self.expected_finish_time)} | Remaining\n'
		else:
			message_string += f'Unknown | Expected finish\n'
			message_string += f'Unknown | Remaining\n'
		message_string += '\n'
		message_string += f'{self._count}/{self._total_iterations} | {int(self._count/self._total_iterations*100)} %'
		message_string += '\n'
		message_string += '\n'
		message_string += f'Last update of this message: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}\n'
		message_string += f'The next update of this message should be in {humanize.naturaldelta(self._minimum_update_time)}.'
		try:
			if hasattr(self, '_message_id_reporting_loop_progress'): # This should be the standard case, unless the message could not be sent in the __enter__ method.
				self.edit_message(
					text = message_string,
					message_id = self._message_id_reporting_loop_progress,
				)
			else: # If there was a problem in the __enter__ method while sending the message, let's send it now so later on we can edit it.
				response = self.send_message(message_string)
				self._message_id_reporting_loop_progress = response['result']['message_id']
		except Exception as e:
			warnings.warn(f'Could not establish connection with Telegram to send the progress status. Reason: {repr(e)}')
	
	def update(self, count:int):
		"""Update the progress of the loop and automatically report to the
		Telegram chat.
		
		Arguments
		---------
		count: int
			Number of loops to add to the count. Normally you call this
			method once per loop iteration and so `count=1` should be
			the correct value. If you call this method once every `N`
			iterations, then you have to use `count=N`.
		"""
		if self._now_reporting == False:
			raise RuntimeError(f'This method must be called from inside a context, i.e. inside a `with` statement.')
		if not isinstance(count, int):
			raise TypeError(f'<count> must be an integer number, received object of type {type(count)}.')
		if not hasattr(self, '_last_update'):
			self._last_update = datetime.datetime.now() - 2*self._minimum_update_time
		self.count(count)
		if datetime.datetime.now() - self._last_update >= self._minimum_update_time:
			self.report()
			self._last_update = datetime.datetime.now()
		self._send_warnings()
	
	def warn(self, message:str):
		"""Send a warning to the Telegram chat. The difference between this
		and just sending a message is that this method automatically replies
		to the original message that is reporting the loop and also moderates
		the number of warnings per unit time that can be sent to the chat,
		so if a warning is reported many times in a loop (say 100 times in
		one second) this method will collect them all in a single message
		and send that instead of 100 messages.
		
		Arguments
		---------
		message: str
			Warning message.
		"""
		if self._now_reporting == False:
			raise RuntimeError(f'This method must be called from inside a context, i.e. inside a `with` statement.')
		if not hasattr(self, '_accumulated_warnings'):
			self._accumulated_warnings = {}
		if message not in self._accumulated_warnings:
			self._accumulated_warnings[message] = 1
		else:
			self._accumulated_warnings[message] += 1 # Increase the count for this type of warning, in case it is reported multiple times within the "minimum warn time".
		self._send_warnings()
		
	def _send_warnings(self, force:bool=False):
		"""This method handles all the bureaucracy of actually sending 
		the warnings to the Telegram bot, taking care of waiting the 
		correct amount of time, collect all the warnings that are waiting
		and of writing a nice message.
		
		Arguments
		---------
		force: bool, default False
			Force sending the warnings no matter if they will spam the chat.
		"""
		if not hasattr(self, '_accumulated_warnings') or len(self._accumulated_warnings) == 0: # Nothing to send...
			return
		if not hasattr(self, '_last_warn_time'):
			self._last_warn_time = datetime.datetime.now() - 2*self._minimum_warn_time # Initialize it like this so the first warning is instantly sent.
		if datetime.datetime.now() - self._last_warn_time >= self._minimum_warn_time or force==True: # Send warnings.
			self._last_warn_time = datetime.datetime.now()
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
			if not hasattr(self, '_message_id_reporting_loop_progress'): # This means that the original message was not yet sent. We just wait, sooner or later it will be sent. And we cannot do anything anyway...
				return
			try:
				self.send_message(
					text = message2send,
					reply_to_message_id = self._message_id_reporting_loop_progress,
				)
				self._accumulated_warnings = {} # Delete all warnings after having sent them.
			except Exception as e:
				warnings.warn(f'Could not establish connection with Telegram to send the warnings. Reason: {repr(e)}')
