import sys
sys.path.append("../3rdParty")
import sleekxmpp.componentxmpp

class Component :
  def __init__(self, jid, password, server, port, backend) :
    self.componentDomain = jid
    self.xmpp = sleekxmpp.componentxmpp.ComponentXMPP(jid, password, server, port)
    self.xmpp.add_event_handler("session_start", self.handleXMPPConnected)
    self.xmpp.add_event_handler("changed_subscription",
        self.handleXMPPPresenceSubscription)
    self.xmpp.add_event_handler("got_presence_probe",
        self.handleXMPPPresenceProbe)
    self.xmpp.add_event_handler("message", self.handleIncomingXMPPMessage)
    for event in ["got_online", "got_offline", "changed_status"] :
      self.xmpp.add_event_handler(event, self.handleIncomingXMPPPresence)
    self.backend = backend
    self.backend.addMessageHandler(self.handleMessageAddedToBackend)

  def handleXMPPConnected(self, event) :
    for user in self.backend.getAllUsers() :
      self.sendPresenceOfAllContactsForUser(user)

  def handleIncomingXMPPMessage(self, event) :
    message = self.addRecipientToMessage(event["message"], event["to"])
    user = self.backend.getUserFromJID(event["jid"])
    self.backend.addMessageFromUser(message, user)

  def handleIncomingXMPPPresence(self, event) :
    if event["to"] == self.componentDomain :
      user = self.backend.getUserFromJID(event["jid"])
      self.backend.addMessageFromUser(event["message"], user)

  def handleXMPPPresenceProbe(self, event) :
    self.sendPresenceOfContactToUser(contactJID=event["to"], userJID=event["from"])

  def handleXMPPPresenceSubscription(self, subscription) :
    if subscription["type"] == "subscribe" :
      userJID = subscription["from"]
      user = self.backend.getUserFromJID(userJID)
      contactJID = subscription["to"]
      self.xmpp.sendPresenceSubscription(
          pfrom=contactJID, pto=userJID, ptype="subscribed", pnick=user)
      self.sendPresenceOfContactToUser(contactJID=contactJID, userJID=userJID)
      if contactJID == self.componentDomain :
        self.sendAllContactSubscriptionRequestsToUser(userJID)

  def handleMessageAddedToBackend(self, message) :
    userJID = self.getComponentJIDFromUser(message.user)
    for subscriberJID in self.backend.getSubscriberJIDs(message.user) :
      self.xmpp.sendMessage(mfrom=userJID, mto=subscriberJID, mbody=message.text)
      self.xmpp.sendPresence(pfrom=userJID, pto=subscriberJID, pstatus=message.text)
  
  ## ...
  
  def sendPresenceOfAllContactsForUser(self, user) :
    userJID = self.backend.getJIDForUser(user)
    for contact in self.backend.getContacts(user) :
      contactJID = self.getComponentJIDFromUser(contact)
      self.sendPresenceOfContactToUser(contactJID = contactJID, userJID = userJID)

  def sendPresenceOfContactToUser(self, contactJID, userJID) :
    message = self.backend.getLastMessage(contactJID).text
    self.xmpp.sendPresence(pto = userJID, pfrom = contactJID, pshow = message)

  def sendAllContactSubscriptionRequestsToUser(self, userJID) :
    user = self.backend.getUserFromJID(userJID)
    for contact in self.backend.getContacts(user) :
      contactJID = self.getComponentJIDFromUser(contact)
      self.xmpp.sendPresenceSubscription(
          pfrom=contactJID, pto=userJID, ptype="subscribe", pnick=contact)
  
  def addRecipientToMessage(self, message, recipientJID) :
    contact = self.getUserFromComponentJID(recipientJID)
    return ("@" + contact if contact else "") + " " + message

  def getUserFromComponentJID(self, jid) :
    return jid.split("@",1)[0] if "@" in jid else None

  def getComponentJIDFromUser(self, user) :
    return user + "@" + self.componentDomain

  def start(self) :
    self.xmpp.connect()
    self.xmpp.process()
