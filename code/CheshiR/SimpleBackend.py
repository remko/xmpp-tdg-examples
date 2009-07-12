#!/usr/bin/env python

from Backend import Backend, Message, message_compare
import datetime

class SimpleBackend (Backend) :
  def __init__(self) :
    Backend.__init__(self)
    self.messages = {}
    self.contacts = {}

    # Dummy data
    self.messages = { 
      'peter' : [
          Message(datetime.datetime(2008, 01, 01), 'peter', 'Reading some XMPP specs'),
          Message(datetime.datetime(2008, 01, 03), 'peter', '@kevin Tell me about it')
        ],
      'kevin' : [
          Message(datetime.datetime(2008, 01, 02), 'kevin', 'Too little time to do all the things I want to')
        ],
      'remko' : [
          Message(datetime.datetime(2008, 01, 04), 'remko', 'Woohoow, holidays!')
        ]}
    self.contacts = { 'remko' : ['kevin', 'peter'] }
    self.subscribers = { 'kevin' : ['remko'], 'peter' : ['remko'] }
    self.jidToUser = {
        'remko@wonderland.lit' : 'remko',
        'peter@wonderland.lit' : 'peter',
        'kevin@wonderland.lit' : 'kevin',
      }
    self.userToJID = { 
        'remko' : 'remko@wonderland.lit',
        'peter' : 'peter@wonderland.lit',
        'kevin' : 'kevin@wonderland.lit' 
      }
    self.userPresenceMonitoring = {
        'kevin' : True,
        'remko' : False,
        'peter' : True,
      }
  
  def getMessages(self, user) :
    messages = []
    if self.messages.has_key(user) :
      messages += self.messages[user]

    for contact in self.contacts.get(user, []) :
      if self.messages.has_key(contact) :
        messages += self.messages[contact]
    messages.sort(reverse=True, cmp=message_compare)
    return messages

  def getLastMessage(self, user) :
    messages = self.getMessages(user)
    if len(messages) > 0 :
      return messages[0]
    else :
      return Message(None, user, '')

  def addMessageFromUser(self, text, user) :
    if len(text) > 0 and self.getLastMessage(user) != text :
      message = Message(datetime.datetime.today(), user, text)
      self.messages.setdefault(user,[]).append(message)
      self.notifyMessage(message)

  def getAllUsers(self) :
    return self.messages.keys()
  
  def getContacts(self, user) :
    return self.contacts.get(user, [])
  
  def getJIDForUser(self, user) :
    return self.userToJID[user]

  def getUserHasJID(self, user) :
    return self.userToJID.has_key(user)

  def getShouldMonitorPresenceFromUser(self, user):
    return self.userPresenceMonitoring[user]

  def setShouldMonitorPresenceFromUser(self, user, state):
    self.userPresenceMonitoring[user] = state

  def getSubscriberJIDs(self, user) :
    subscribers = []
    #for subscriber in self.subscribers.get(user, []) + [user] :
    for subscriber in self.subscribers.get(user, []) :
      if self.userToJID.has_key(subscriber) :
        subscribers.append(self.userToJID[subscriber])
    return subscribers
  
  def getUserFromJID(self, user) :
    return self.jidToUser.get(user.split('/',1)[0], None)

  def addContact(self, user, contact) :
    if not self.contacts.has_key(user) :
      self.contacts[user] = []
    self.contacts.setdefault(user, []).append(contact)

  def registerXMPPUser(self, user, password, fulljid) :
    barejid = fulljid.split('/', 1)[0]
    self.jidToUser[barejid] = user
    self.userToJID[user] = barejid
    return True

