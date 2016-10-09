from __future__ import absolute_import
from __future__ import print_function
import time
import threading
from six.moves import range
try :
	import irc.client as irc
except ImportError :
	import irclib as irc

class IRC(irc.SimpleIRCClient) :
	JOIN_TIMEOUT = 120
	PING_TIMEOUT = 120
	PING_FREQUENCY = 60

	def __init__(self, server, nick, chan) :
		self.dead = False
		self._ping_s = None
		self._ping_r = None
		self._create_t = time.time()

		irc.SimpleIRCClient.__init__(self)
		self._server = server
		self._nick = nick
		self._chan = chan

	def conn(self) :
		self.disconnecting = False
		self.connect(self._server, 6667, self._nick)
		self.connection.join(self._chan)

	def maybe_send_ping(self) :
		if self._ping_s is None or self._ping_r is None :
			return

		if time.time() > self._ping_s + IRC.PING_FREQUENCY :
			self.connection.ping(self.connection.real_server_name)
			self._ping_s = time.time()

	@property
	def pinged_out(self) :
		if self._ping_s is None or self._ping_r is None :
			return time.time() - self._create_t > IRC.JOIN_TIMEOUT

		return time.time() - self._ping_r > IRC.PING_TIMEOUT

	def on_pong(self, c, e) :
		self._ping_r = time.time()

	def clean_shutdown(self) :
		if not self.disconnecting :
			self.disconnecting = True
			try :
				self.disconnect("Quit")
			except :
				pass
		print('irc shut down cleanly')
		self.dead = True
	
	def on_disconnect(self, c, e) :
		print('got disconnect')
		self.dead = True

	def on_join(self, c, e) :
		self.initialize_pinger()

	def initialize_pinger(self) :
		if self._ping_s is None or self._ping_r is None :
			self._ping_s = time.time()
			self._ping_r = time.time()

class IRCThread(threading.Thread) :
	RETRY_SEC = 10

	def __init__(self) :
		self.ok = True
		threading.Thread.__init__(self)

	def stop(self) :
		self.ok = False
		if hasattr(self, 'client') :
			self.client.clean_shutdown()
		if hasattr(self, 'stop_hook') :
			self.stop_hook()

	def checkedwait(self, secs) :
		for i in range(secs * 10) :
			if not self.ok :
				break
			time.sleep(0.1)

	def run(self) :
		while self.ok :
			print('creating new irc connection')
			self.client = self.bot_create()
			try :
				self.client.conn()
			except irc.ServerConnectionError :
				print('could not connect to irc server for some reason, retrying in %d' % IRCThread.RETRY_SEC)
				self.checkedwait(IRCThread.RETRY_SEC)

			while self.ok and not self.client.dead and not self.client.pinged_out :
				self.client.maybe_send_ping()
				self.client.ircobj.process_once(0.2)
				if hasattr(self.client, 'do_work') :
					self.client.do_work()

			if self.ok :
				print('shutting down irc connection before reconnect')
				self.client.clean_shutdown()
