
"""
The service component for the port redirector.

The service runs over a DBus service, accepts requests to add, remove,
and modify port redirects.
"""

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('[' + __name__ + ']')

#
# For the interface to the service.
#
import dbus
import dbus.service

#
# For the main loop and timeouts.
#
import glib
from dbus.mainloop.glib import DBusGMainLoop
import gtk
import gobject

import portforward
import socket

gobject.threads_init()

def protocol_string_to_enum(portspec):
    return (portspec[0], portspec[1], portforward.Protocol.FromString[portspec[2]])

class PortRedirector(dbus.service.Object):
    def __init__(self):
        bus = dbus.service.BusName('org.new123456.Proxy', bus = dbus.SessionBus())
        dbus.service.Object.__init__(self, bus, '/org/new123456/Proxy')

    @dbus.service.method('org.new123456.Proxy',
                         in_signature = '(sis)(sis)',
                         out_signature='b')
    def AddMapping(self, src, dest):
        try:
            portforward.add_mapping(protocol_string_to_enum(src), protocol_string_to_enum(dest))
            logger.debug("Done")
            return True
        except socket.error as e:
            logger.debug("Fail\n\t-%s", e)
            return False

    @dbus.service.method('org.new123456.Proxy',
                         in_signature='(sis)',
                         out_signature='b')
    def RemoveMapping(self, src):
        try:
            portforward.del_mapping(protocol_string_to_enum(src))
            logger.debug("Done")
            return True
        except KeyError:
            logger.debug("Fail")
            return False

    @dbus.service.method('org.new123456.Proxy',
                         in_signature='',
                         out_signature='a(sissis)')
    def ReadMappings(self):
        src_to_dest = []
        for src in portforward.src_to_svr:
            svr = portforward.src_to_svr[src]
            dest = portforward.svr_to_dest[svr.fileno()]
            src_to_dest.append((src[0], src[1], portforward.Protocol.ToString[src[2]], dest[1], dest[2], portforward.Protocol.ToString[dest[3][1]]))
        return src_to_dest

DBusGMainLoop(set_as_default=True)
p = PortRedirector()
try:
    gtk.main()
except KeyboardInterrupt:
    portforward.quit()
