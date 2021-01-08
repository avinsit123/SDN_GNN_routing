from mininet.node import Controller, OVSKernelSwitch, RemoteController
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.net import Mininet
from time import sleep

def topology():
    'Create a network and controller'

    # Define Mininet Network
    net = Mininet(controller=RemoteController, switch=OVSKernelSwitch)

    # Add Remote Controller
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)
    

    info("*** Creating nodes ***\n")

    # Add Hosts for all switches
    h1 = net.addHost('h1', ip='10.0.0.1/24', position='10,10,0')
    h2 = net.addHost('h2', ip='10.0.0.2/24', position='20,10,0')
    h3 = net.addHost('h3', ip='10.0.0.3/24', position='30,10,0')
    h4 = net.addHost('h4', ip='10.0.0.4/24', position='40,10,0')
    h5 = net.addHost('h5', ip='10.0.0.5/24', position='50,10,0')
    h6 = net.addHost('h6', ip='10.0.0.6/24', position='60,10,0')
    h7 = net.addHost('h7', ip='10.0.0.7/24', position='70,10,0')
    h8 = net.addHost('h8', ip='10.0.0.8/24', position='80,10,0')

    # Add all switches 
    sw1 = net.addSwitch('sw1', protocols="OpenFlow13", position='12,10,0')
    sw2 = net.addSwitch('sw2', protocols="OpenFlow13", position='15,20,0')
    sw3 = net.addSwitch('sw3', protocols="OpenFlow13", position='18,10,0')
    sw4 = net.addSwitch('sw4', protocols="OpenFlow13", position='14,10,0')
    sw5 = net.addSwitch('sw5', protocols="OpenFlow13", position='13,10,0')
    sw6 = net.addSwitch('sw6', protocols="OpenFlow13", position='19,10,0')
    sw7 = net.addSwitch('sw7', protocols="OpenFlow13", position='21,10,0')
    sw8 = net.addSwitch('sw8', protocols="OpenFlow13", position='24,10,0')

    info("*** Adding Links between Hosts and Switches ***\n")
    net.addLink(h1, sw1)
    net.addLink(h2, sw2)
    net.addLink(h3, sw3)
    net.addLink(h4, sw4)
    net.addLink(h5, sw5)
    net.addLink(h6, sw6)
    net.addLink(h7, sw7)
    net.addLink(h8, sw8)

    net.addLink(sw1,sw8)
    net.addLink(sw1,sw2)
    net.addLink(sw8,sw6)
    net.addLink(sw8,sw7)
    net.addLink(sw8,sw2)
    net.addLink(sw2,sw3)
    net.addLink(sw3,sw7)
    net.addLink(sw3,sw4)
    net.addLink(sw5,sw6)
    net.addLink(sw4,sw6)


    info("*** Starting network\n")
    net.build()
    c0.start()
    sw1.start([c0])
    sw2.start([c0])
    sw3.start([c0])
    sw4.start([c0])
    sw5.start([c0])
    sw6.start([c0])
    sw7.start([c0])
    sw8.start([c0])

    CLI( net )

    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()