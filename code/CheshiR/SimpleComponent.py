import sys
sys.path.append("../3rdParty")
import sleekxmpp.componentxmpp

class SimpleComponent :
  def __init__(self, jid, password, server, port, backend) :
    ## BEGIN NEW
    self.xmpp = sleekxmpp.componentxmpp.ComponentXMPP(jid, password, server, port)
    ## END NEW
    self.xmpp.add_event_handler("session_start", self.handleXMPPConnected)
    ## BEGIN NEW
    self.xmpp.add_event_handler("changed_subscription", 
        self.handleXMPPPresenceSubscription)
    self.xmpp.add_event_handler("got_presence_probe", 
        self.handleXMPPPresenceProbe)
    ## END NEW
    for event in ["message", "got_online", "got_offline", "changed_status"] :
      self.xmpp.add_event_handler(event, self.handleIncomingXMPPEvent)
    self.backend = backend
    self.backend.addMessageHandler(self.handleMessageAddedToBackend)

  def handleXMPPConnected(self, event) :
    ## BEGIN NEW
    for user in self.backend.getAllUsers() :
      self.xmpp.sendPresence(pto = self.backend.getJIDForUser(user))
    ## END NEW

  def handleIncomingXMPPEvent(self, event) :
    message = event["message"]
    user = self.backend.getUserFromJID(event["jid"])
    self.backend.addMessageFromUser(message, user)

  ## BEGIN NEW
  def handleXMPPPresenceProbe(self, event) :
    self.xmpp.sendPresence(pto = self.backend.getJIDForUser(user))
  ## END NEW

  ## BEGIN NEW
  def handleXMPPPresenceSubscription(self, subscription) :
    if subscription["type"] == "subscribe" :
      userJID = subscription["from"]
      self.xmpp.sendPresenceSubscription(pto=userJID, ptype="subscribed")
      self.xmpp.sendPresence(pto = userJID)
      self.xmpp.sendPresenceSubscription(pto=userJID, ptype="subscribe")
  ## END NEW

  def handleMessageAddedToBackend(self, message) :
    body = message.user + ": " + message.text
    for subscriberJID in self.backend.getSubscriberJIDs(message.user) :
      self.xmpp.sendMessage(subscriberJID, body)

  def start(self) :
    self.xmpp.connect()
    self.xmpp.process()
