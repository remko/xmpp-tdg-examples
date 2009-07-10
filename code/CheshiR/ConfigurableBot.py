import sys
sys.path.append("../3rdParty")
import sleekxmpp

class ConfigurableBot :
  def __init__(self, jid, password, backend, url) :
    self.url = url
    self.xmpp = sleekxmpp.ClientXMPP(jid, password)
    ## BEGIN NEW
    for plugin in ["xep_0004", "xep_0030", "xep_0050"] :
      self.xmpp.registerPlugin(plugin) 
		## END NEW
    self.xmpp.add_event_handler("session_start", self.handleXMPPConnected)
    self.xmpp.add_event_handler("message", self.handleIncomingXMPPEvent)
    ## BEGIN NEW
    for event in ["got_online", "got_offline", "changed_status"] :
      self.xmpp.add_event_handler(event, self.handleIncomingXMPPPresence)
		## END NEW
    self.backend = backend
    self.backend.addMessageHandler(self.handleMessageAddedToBackend)
		## BEGIN NEW
    configurationForm = self.xmpp.plugin["xep_0004"].makeForm("form", "Configure")
    configurationForm.addField(
        var="monitorPresence", label="Use my status messages",
        ftype="boolean", required=True, value=True)
    self.xmpp.plugin["xep_0050"].addCommand("configure", "Configure",
        configurationForm, self.handleConfigurationCommand)
    ## END NEW

  ## BEGIN NEW
  def handleConfigurationCommand(self, form, sessionId):
    values = form.getValues()
    monitorPresence = True if values["monitorPresence"] == "1" else False
    jid = self.xmpp.plugin["xep_0050"].sessions[sessionId]["jid"]
    user = self.backend.getUserFromJID(jid)
    self.backend.setShouldMonitorPresenceFromUser(user, monitorPresence)
  ## END NEW

  ## BEGIN NEW
  def handleIncomingXMPPPresence(self, event):
    user = self.backend.getUserFromJID(event["jid"])
    if self.backend.getShouldMonitorPresenceFromUser(user):
      self.handleIncomingXMPPEvent(event)
  ## END NEW

  def handleXMPPConnected(self, event):
    self.xmpp.sendPresence()

  def handleIncomingXMPPEvent(self, event):
    message = event["message"]
    user = self.backend.getUserFromJID(event["jid"])
    self.backend.addMessageFromUser(message, user)
  
  def handleMessageAddedToBackend(self, message) :
    body = message.user + ": " + message.text
    htmlBody = "<a href=\"%(uri)s\">%(user)s</a>: %(message)s" % {
      "uri": self.url + "/" + message.user,
      "user" : message.user, "message" : message.text }
    for subscriberJID in self.backend.getSubscriberJIDs(message.user) :
      self.xmpp.sendMessage(subscriberJID, body, mhtml=htmlBody)
  
  def start(self) :
    self.xmpp.connect()
    self.xmpp.process()
