#!/usr/bin/env python

import BaseHTTPServer, cgi


class HTTPFrontend :
	class RequestHandler (BaseHTTPServer.BaseHTTPRequestHandler) :
		def do_GET(self) :
			# CSS
			if self.path == "/cheshir.css" :
				self.send_response(200)
				self.send_header('Content-Type', 'text/css')
				self.end_headers()
				css = open("html/cheshir.css")
				self.wfile.write(css.read())
				css.close()
				return

			# User page
			self.send_response(200)
			self.send_header('Content-Type', 'text/html')
			self.end_headers()
			user = self.path[1:]
			if user : 
				self.wfile.write(self.getHomePage(user))
			else :
				# Print user list
				self.wfile.write('Users:')
				for user in self.server.backend.getAllUsers() :
					self.wfile.write("<li><a href='/%(user)s'>%(user)s</a></li>" % {'user' : user})

		def do_POST(self) :
			self.send_response(200)
			self.send_header('Content-Type', 'text/html')
			self.end_headers()
			user = self.path[1:]
			assert(user)
			length = int(self.headers.getheader('content-length'))
			data = cgi.parse_qs(self.rfile.read(length))
			if data.has_key('message') :
				self.server.backend.addMessageFromUser(data.get('message')[0], user)
			elif data.has_key('contact') :
				self.server.backend.addContact(user, data.get('contact')[0])
			self.wfile.write(self.getHomePage(user))

		def getHomePage(self, user) :
			templateFile = open("html/home.html")
			template = templateFile.read()
			templateFile.close()

			messages = ""
			for message in self.server.backend.getMessages(user) :
				messages += "<p><p class='home-message'>" + message.user + ": " + message.text + "</p><p class='home-date'>" + message.date.strftime("%Y-%m-%d %H:%M")  + "</p></li>\n"

			contacts = ""
			for contact in self.server.backend.getContacts(user) :
				contacts += "<li>" + contact + "\n"
			return template % { 
					'uri' : self.path, 
					'user' : user, 
					'messages' : messages,
					'contacts' : contacts }


	def __init__(self, port, backend) :
		self.server = BaseHTTPServer.HTTPServer(('',port), self.RequestHandler)
		self.server.backend = backend
		print "Web interface listening on http://localhost:" + str(port)
	
	def start(self) :
		self.server.serve_forever()
	
	def stop(self) :
		self.server.socket.close()
