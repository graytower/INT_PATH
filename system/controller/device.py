# -*- coding:utf-8 -*-


class Port(object):
    """
    Describe a switch port

    it contains the num of this port and the name of device which contains this port
    """

    def __init__(self, portNum, deviceName):
        self.portNum = portNum
        self.deviceName = deviceName


class Table(object):
    """
    Describe a flow table in a switch

    it contains a name ,an action, a key and a value
    """
    def __init__(self, name, action, key, value):
        self.name = name
        self.action = action
        self.key = key
        self.value = value


class Device(object):
    """
    Describe a device in a network

    it contains a name, port list and the count of port
    """

    def __init__(self, name):
        self.name = name
        self.ports = []
        self.portSum = 0

    def addLink(self, deviceName):
        self.portSum = self.portSum + 1
        port = Port(self.portSum, deviceName)
        self.ports.append(port)


class Switch(Device):
    """
    Describe a switch in a network (inherit the Device class)

    it contains tables, thrift port and thrift Runtime
    it has 2 actions: add table and clear table
    """

    def __init__(self, name, thriftPort=9090, runtime=None):
        super(Switch, self).__init__(name)
        self.tables = []
        self.thriftPort = thriftPort
        self.runtime = runtime

    def addTable(self, name, action, key, value):
        self.tables.append(Table(name, action, key, value))

    def clearTable(self):
        self.tables = []


class Host(Device):
    """
    Describe a host in a netwrok (interit the Device class)

    it contains a MAC address, an IP address and an OpenVSwitch Ip address
    """

    def __init__(self, name, mac='', ip='', ovsIp=''):
        super(Host, self).__init__(name)
        self.macAddress = mac
        self.ipAddress = ip
        self.ovsIpAddress = ovsIp


if __name__ == '__main__':
    device = Host('hahah')
    print(device.name)
