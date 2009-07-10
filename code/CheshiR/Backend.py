def message_compare(m1, m2) :
	return cmp(m1.date, m2.date)

class Message :
	def __init__(self, date, user, text) :
		self.date = date
		self.user = user
		self.text = text

class Backend :
	def __init__(self) :
		self.handlers = []

	def addMessageHandler(self, handler) :
		self.handlers.append(handler)
	
	def notifyMessage(self, message) :
		for handler in self.handlers :
			handler(message)
