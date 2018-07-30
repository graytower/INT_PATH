# -*- coding:utf-8 -*-

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import RemoteController, OVSSwitch
from p4_mininet import P4Switch, P4Host

import os
import copy


class MakeSwitchTopo(Topo):
    """
    Mapping the topology in controller to Mininet
    """

    def __init__(self, sw_path, json_path, app_topo, **opts):
        """
        Make Mininet Host, Switch and Link entity

        :param sw_path: switch path (use bmv2's simple_switch target in this case)
        :param json_path: a compiled JSON file from P4 code
        :param app_topo: the Ctrl class instance to get informatin
        """
        Topo.__init__(self, **opts)

        self.switchSum = len(app_topo.switches)
        self.hostSum = len(app_topo.hosts)

        self.mn_switches = []
        self.mn_hosts = []
        for i in range(self.switchSum):
            self.mn_switches.append(self.addSwitch(app_topo.switches[i].name,
                                                   sw_path=sw_path,
                                                   json_path=json_path,
                                                   thrift_port=app_topo.switches[i].thriftPort,
                                                   pcap_dump=False))
        for i in range(self.hostSum):
            if app_topo.hosts[i] != None:
                self.mn_hosts.append(self.addHost(app_topo.hosts[i].name,
                                                  ip=app_topo.hosts[i].ipAddress + "/24",
                                                  mac=app_topo.hosts[i].macAddress))
            else:
                self.mn_hosts.append(None)
        for i in range(self.switchSum):
            for j in range(app_topo.switches[i].portSum):
                deviceNum = int(
                    app_topo.switches[i].ports[j].deviceName[1:])
                if app_topo.switches[i].ports[j].deviceName.startswith('s'):
                    if i < deviceNum:
                        self.addLink(
                            self.mn_switches[i], self.mn_switches[deviceNum])
                else:
                    self.addLink(
                        self.mn_switches[i], self.mn_hosts[deviceNum])


class TopoMaker(object):
    """
    Make topology in Mininet
    """

    def __init__(self, switchPath, jsonPath, topoObj):
        """
        Initial topology maker

        :param sw_path: switch path (use bmv2's simple_switch target in this case)
        :param json_path: a compiled JSON file from P4 code
        :param topoObj: the Ctrl class instance to get informatin
        """
        self.topo = MakeSwitchTopo(switchPath, jsonPath, topoObj)
        self.topoObj = topoObj

    def genMnTopo(self):
        """
        Launch Mininet topology and add some commands (like disable IPv6, open INT sender/packet client/INT parser) to host and switch & start OVS and ryu controller
        """
        setLogLevel('debug')
        self.net = Mininet(topo=self.topo,
                           host=P4Host,
                           switch=P4Switch,
                           controller=None)
        controller_list = []
        c = self.net.addController('mycontroller', controller=RemoteController)
        controller_list.append(c)
        ovs = self.net.addSwitch('s999', cls=OVSSwitch)

        hostIpList = [
            host.ipAddress for host in self.topoObj.hosts if host is not None]

        j = 0
        for i in range(self.topo.hostSum):
            if self.topo.mn_hosts[i] != None:
                self.net.addLink(self.net.hosts[j], ovs)
                self.net.hosts[j].cmd(
                    "sysctl -w net.ipv6.conf.all.disable_ipv6=1")
                self.net.hosts[j].cmd(
                    "sysctl -w net.ipv6.conf.default.disable_ipv6=1")
                self.net.hosts[j].cmd(
                    "sysctl -w net.ipv6.conf.lo.disable_ipv6=1")
                name = self.topoObj.hosts[i].name
                ipAddr = self.topoObj.hosts[i].ovsIpAddress
                action = 'ip a a ' + ipAddr + '/24 dev ' + name + '-eth1'
                self.net.hosts[j].cmd(action)
                self.net.hosts[j].cmd('ifconfig')
                j = j + 1

        ovs.start(controller_list)

        self.net.start()
        os.popen('ovs-vsctl add-port s999 ens38')

        j = 0
        for i in range(self.topo.hostSum):
            if self.topo.mn_hosts[i] != None:

                packetSender = ' python ~/P4_DC/packet/sendint.py ' + \
                    str(i) + ' &'
                self.net.hosts[j].cmd(packetSender)

                intReceiver = '~/P4_DC/packet/receiveint ' + \
                    str(i) + ' >/dev/null &'
                self.net.hosts[j].cmd(intReceiver)
                j = j + 1

    def getCLI(self):
        """
        Open Mininet CLI
        """
        CLI(self.net)

    def stopMnTopo(self):
        """
        Stop Mininet envirnoment
        """
        self.net.stop()

    def cleanMn(self):
        """
        Clean all mininet trace
        """
        os.system('sudo mn -c')
        os.system(
            'ryu-manager /usr/local/lib/python2.7/dist-packages/ryu/app/simple_switch.py 2>/dev/null >/dev/null &')
        pass


if __name__ == '__main__':
    pass
