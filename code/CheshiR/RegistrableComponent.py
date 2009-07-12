import sys
sys.path.append("../3rdParty")
import sleekxmpp.componentxmpp
from xml.etree import cElementTree as ET

class RegistrableComponent :
  def __init__(self, jid, password, server, port, backend) :
    self.xmpp = sleekxmpp.componentxmpp.ComponentXMPP(jid, password, server, port)
    self.xmpp.add_event_handler("session_start", self.handleXMPPConnected)
    self.xmpp.add_event_handler("changed_subscription", 
        self.handleXMPPPresenceSubscription)
    self.xmpp.add_event_handler("got_presence_probe", 
        self.handleXMPPPresenceProbe)
    for event in ["message", "got_online", "got_offline", "changed_status"] :
      self.xmpp.add_event_handler(event, self.handleIncomingXMPPEvent)
    self.backend = backend
    self.backend.addMessageHandler(self.handleMessageAddedToBackend)
    ## BEGIN NEW
    self.xmpp.registerPlugin("xep_0030")
    self.xmpp.plugin["xep_0030"].add_feature("jabber:iq:register")
    self.xmpp.add_handler("<iq type='get' xmlns='jabber:component:accept'>" + 
      "<query xmlns='jabber:iq:register'/></iq>", self.handleRegistrationFormRequest)
    self.xmpp.add_handler("<iq type='set' xmlns='jabber:component:accept'>" +
      "<query xmlns='jabber:iq:register'/></iq>", self.handleRegistrationRequest)
    ## END NEW

  ## BEGIN NEW
  def handleRegistrationFormRequest(self, request) :
    payload = ET.Element("{jabber:iq:register}query")
    payload.append(ET.Element("username"))
    payload.append(ET.Element("password"))
    self.sendRegistrationResponse(request, "result", payload)

  def handleRegistrationRequest(self, request) :
    jid = request.attrib["from"]
    user = request.find("{jabber:iq:register}query/{jabber:iq:register}username").text
    password = request.find("{jabber:iq:register}query/{jabber:iq:register}password").text
    if self.backend.registerXMPPUser(user, password, jid) :
      self.sendRegistrationResponse(request, "result")
      userJID = self.backend.getJIDForUser(user)
      self.xmpp.sendPresenceSubscription(pto=userJID, ptype="subscribe")
    else :
      error = self.xmpp.makeStanzaError("forbidden", "auth")
      self.sendRegistrationResponse(request, "error", error)

  def sendRegistrationResponse(self, request, type, payload = None) :
    iq = self.xmpp.makeIq(request.get("id"))
    iq.attrib["type"] = type
    iq.attrib["from"] = self.xmpp.fulljid
    iq.attrib["to"] = request.get("from")
    if payload :
      iq.append(payload)
    self.xmpp.send(iq)
  ## END NEW

  ## ...
  def handleXMPPConnected(self, event) :
    for user in self.backend.getAllUsers() :
      if self.backend.getUserHasJID(user) :
        self.xmpp.sendPresence(pto = self.backend.getJIDForUser(user))

  def handleIncomingXMPPEvent(self, event) :
    message = event["message"]
    user = self.backend.getUserFromJID(event["jid"])
    self.backend.addMessageFromUser(message, user)

  def handleXMPPPresenceProbe(self, event) :
    self.xmpp.sendPresence(pto = event["from"])

  def handleXMPPPresenceSubscription(self, subscription) :
    if subscription["type"] == "subscribe" :
      userJID = subscription["from"]
      self.xmpp.sendPresenceSubscription(pto=userJID, ptype="subscribed")
      self.xmpp.sendPresence(pto = userJID)
      self.xmpp.sendPresenceSubscription(pto=userJID, ptype="subscribe")

  def handleMessageAddedToBackend(self, message) :
    body = message.user + ": " + message.text
    for subscriberJID in self.backend.getSubscriberJIDs(message.user) :
      self.xmpp.sendMessage(subscriberJID, body)

  def start(self) :
    self.xmpp.connect()
    self.xmpp.process()
