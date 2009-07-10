from __future__ import with_statement
from . import base
import logging
import types
from xml.etree import cElementTree as ET
from sleekxmpp.xmlstream.handler.callback import Callback
from sleekxmpp.xmlstream.matcher.xmlmask import MatchXMLMask
from sleekxmpp.xmlstream.matcher.many import MatchMany
from sleekxmpp.xmlstream.matcher.xpath import MatchXPath

NS = {'PUBSUB_OWNER':  'http://jabber.org/protocol/pubsub#owner',
'JC': 'jabber:client',
'PUBSUB': 'http://jabber.org/protocol/pubsub',
'FORM': 'jabber:x:data',
}

class xep_0060_server(base.base_plugin):
	"""
	XEP-0060 Publish Subscribe
	"""

	def plugin_init(self):
		self.xep = '0060_server'
		self.description = 'Publish-Subscribe Server'
		
		self.nodes = {'default': Node(self, self.xmpp, 'default')}
		self.xmpp.registerHandler(Callback('getConfig', MatchXMLMask("<iq type='get' xmlns='%(JC)s'><pubsub xmlns='%(PUBSUB_OWNER)s'><configure/></pubsub></iq>" % NS), self.handle_getConfig, thread=False))
		self.xmpp.registerHandler(Callback('getDefaultConfig', MatchXMLMask("<iq type='get' xmlns='%(JC)s'><pubsub xmlns='%(PUBSUB_OWNER)s'><default/></pubsub></iq>" % NS), self.handle_getDefaultConfig, thread=False))
		self.xmpp.registerHandler(Callback('setConfig', MatchXMLMask("<iq type='set' xmlns='%(JC)s'><pubsub xmlns='%(PUBSUB_OWNER)s'><configure/></pubsub></iq>" % NS), self.handle_setConfig, thread=False))
		self.xmpp.registerHandler(Callback('createNode', MatchXMLMask("<iq type='set' xmlns='%(JC)s'><pubsub xmlns='%(PUBSUB)s'><create/><configure/></pubsub></iq>" % NS), self.handle_createNode, thread=False))
		self.xmpp.registerHandler(Callback('deleteNode', MatchXMLMask("<iq type='set' xmlns='%(JC)s'><pubsub xmlns='%(PUBSUB_OWNER)s'><delete/></pubsub></iq>" % NS), self.handle_getConfig, thread=False))
		self.xmpp.registerHandler(Callback('subscribe', MatchXMLMask("<iq type='set' xmlns='%(JC)s'><pubsub xmlns='%(PUBSUB)s'><subscribe /></pubsub></iq>" % NS), self.handle_subscribe, thread=False))
		self.xmpp.registerHandler(Callback('unsubscribe', MatchXMLMask("<iq type='set' xmlns='%(JC)s'><pubsub xmlns='%(PUBSUB)s'><unsubscribe /></pubsub></iq>" % NS), self.handle_unsubscribe, thread=False))
		self.xmpp.registerHandler(Callback('getSubscriptions', MatchXMLMask("<iq type='get' xmlns='%(JC)s'><pubsub xmlns='%(PUBSUB_OWNER)s'><subscriptions/></pubsub></iq>" % NS), self.handle_getSubscriptions, thread=False))
		self.xmpp.registerHandler(Callback('getAffiliations', MatchXMLMask("<iq type='get' xmlns='%(JC)s'><pubsub xmlns='%(PUBSUB_OWNER)s'><affiliations/></pubsub></iq>" % NS), self.handle_getAffiliations, thread=False))
		self.xmpp.registerHandler(Callback('setItem', MatchXMLMask("<iq type='set' xmlns='%(JC)s'><pubsub xmlns='%(PUBSUB)s'><publish /></pubsub></iq>" % NS), self.handle_setItem, thread=False))
		self.xmpp.registerHandler(Callback('deleteItem', MatchXMLMask("<iq type='set' xmlns='%(JC)s'><pubsub xmlns='%(PUBSUB)s'><retract /></pubsub></iq>" % NS), self.handle_deleteItem, thread=False))
		self.xmpp.registerHandler(Callback('modifyAffiliations', MatchXMLMask("<iq type='set' xmlns='%(JC)s'><pubsub xmlns='%(PUBSUB_OWNER)s'><affiliations/></pubsub></iq>" % NS), self.handle_getConfig, thread=False))
	
	def handle_getConfig(self, stanza):
		xml = stanza.xml
		cn = xml.find('{%(PUBSUB_OWNER)s}pubsub/{%(PUBSUB_OWNER)s}configure' % NS)
		node = cn.get('node', False)
		jid = xml.get('from')
		id = xml.get('id')
		if not node or node not in self.nodes:
			self.nodeNotFound(xml)
		else:
			self.nodes[node].getConfig(jid, id)
	
	def handle_getDefaultConfig(self, xml):
		print "Getting default config"
	 	pass
	
	def handle_setConfig(self, stanza):
		print "Set config called, bitches"
		xml = stanza.xml
		cn = xml.find('{%(PUBSUB_OWNER)s}pubsub/{%(PUBSUB_OWNER)s}configure' % NS)
		node = cn.get('node', False)
		jid = xml.get('from')
		id = xml.get('id')
		if not node or node not in self.nodes:
			self.nodeNotFound(xml)
		else:
			self.nodes[node].setConfig(stanza)
	
	def handle_createNode(self, xml):
		pass
	
	def handle_deleteNode(self, xml):
		pass
	
	def handle_subscribe(self, xml):
		pass
	
	def handle_unsubscribe(self, xml):
		pass
	
	def handle_getSubscriptions(self, xml):
		pass
	
	def handle_getAffiliations(self, xml):
		pass
	
	def handle_setItem(self, xml):
		pass
	
	def handle_deleteItem(self, xml):
		pass
	
	def handle_modifyAffiliations(self, xml):
		pass
	
	def nodeNotFound(self, xml):
		pass

class Node(object):
	"""
	Publish-Subscribe Node
	"""

	def __init__(self, pubsub, xmpp, node):
		self.pubsub = pubsub
		self.xmpp = xmpp
		self.node = node
		self.configxml = """<x xmlns='jabber:x:data' type='form'>
<field var='FORM_TYPE' type='hidden'>
	<value>http://jabber.org/protocol/pubsub#node_config</value>
</field>
 <field var='pubsub#title' type='text-single' label='A friendly name for the node'/>
</x>
"""
		self.configxml = ET.fromstring(self.configxml)
	
	def getConfig(self, jid, id):
		iq = self.xmpp.makeIqResult(id)
		iq.attrib['to'] = jid
		pubsub = ET.Element('{%(PUBSUB_OWNER)s}pubsub' % NS)
		configure = ET.Element('{%(PUBSUB_OWNER)s}configure' % NS, {'node': self.node})
		configure.append(self.configxml)
		pubsub.append(configure)
		iq.append(pubsub)
		self.xmpp.send(iq)
	
	def setConfig(self, stanza):
		config = stanza.xml.find('{%(PUBSUB_OWNER)s}pubsub/{%(PUBSUB_OWNER)s}configure/{%(FORM)s}x' % NS)
		if config is None:
			print "Return an error"
		else:
			self.loadConfig(config)
		iq = self.xmpp.makeIqResult(stanza.xml.attrib.get('id'))
		iq.attrib['to'] = stanza.xml.attrib.get('from')
		self.xmpp.send(iq)
	
	def loadConfig(self, xml):
		if type(xml) == types.StringType:
			xml = ET.fromstring(xml)
		self.configform = self.xmpp.plugin['xep_0004'].buildForm(xml)
		self.config = self.configform.getValues()
		for field in self.configform.getValues():
			fieldp = None
			try:
				fieldp = getattr(self, "field_%s" % field.var.replace('#', '_'))
			except AttributeError:
				pass
			else:
				fieldp(self.configform.fields[field])
	
	def field_pubsub_title(self, value):
		print "Field title has a value of %s!" % value
	
	def subscribe(self):
		pass
	
	def unsubscribe(self):
		pass
	
	def getSubsriptions(self):
		pass
	
	def setItem(self, xml):
		pass
	
	def deleteItem(self):
		pass
	
	def modifyAffiliation(self, xml):
		pass

