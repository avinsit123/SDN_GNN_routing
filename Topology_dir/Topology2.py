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
    h5 = net.addHost('h5', ip='10.0.0.4/24', position='50,10,0')
    h6 = net.addHost('h6', ip='10.0.0.4/24', position='60,10,0')
    h7 = net.addHost('h7', ip='10.0.0.4/24', position='70,10,0')
    h8 = net.addHost('h8', ip='10.0.0.4/24', position='80,10,0')
    h9 = net.addHost('h9', ip='10.0.0.4/24', position='90,10,0')
    h10 = net.addHost('h10', ip='10.0.0.4/24', position='100,10,0')
    h11 = net.addHost('h11', ip='10.0.0.4/24', position='110,10,0')
    h12 = net.addHost('h12', ip='10.0.0.4/24', position='120,10,0')
    h13 = net.addHost('h13', ip='10.0.0.4/24', position='130,10,0')
    h14 = net.addHost('h14', ip='10.0.0.4/24', position='140,10,0')


    # Add all switches 
    sw1 = net.addSwitch('sw1', protocols="OpenFlow13", position='12,10,0')
    sw2 = net.addSwitch('sw2', protocols="OpenFlow13", position='15,20,0')
    sw3 = net.addSwitch('sw3', protocols="OpenFlow13", position='18,10,0')
    sw4 = net.addSwitch('sw4', protocols="OpenFlow13", position='14,10,0')
    sw5 = net.addSwitch('sw5', protocols="OpenFlow13", position='13,10,0')
    sw6 = net.addSwitch('sw6', protocols="OpenFlow13", position='19,10,0')
    sw7 = net.addSwitch('sw7', protocols="OpenFlow13", position='21,10,0')
    sw8 = net.addSwitch('sw8', protocols="OpenFlow13", position='24,10,0')
    sw9 = net.addSwitch('sw9', protocols="OpenFlow13", position='26,10,0')
    sw10 = net.addSwitch('sw10', protocols="OpenFlow13", position='27,10,0')
    sw11 = net.addSwitch('sw11', protocols="OpenFlow13", position='31,10,0')
    sw12 = net.addSwitch('sw11', protocols="OpenFlow13", position='28,10,0')
    sw13 = net.addSwitch('sw12', protocols="OpenFlow13", position='29,10,0')
    sw14 = net.addSwitch('sw13', protocols="OpenFlow13", position='36,10,0')
    

    

    info("*** Adding Links between Hosts and Switches ***\n")
    net.addLink(h1, sw1)
    net.addLink(h2, sw2)
    net.addLink(h3, sw3)
    net.addLink(h4, sw4)
    net.addLink(h5, sw5)
    net.addLink(h6, sw6)
    net.addLink(h7, sw7)
    net.addLink(h8, sw8)
    net.addLink(h9, sw9)
    net.addLink(h10, sw10)
    net.addLink(h11, sw11)
    net.addLink(h12, sw12)
    net.addLink(h13, sw13)
    net.addLink(h14, sw14)


    info("*** Adding Duplex Links between switches")
    net.addLink(sw1,sw2)
    net.addLink(sw1,sw3)
    net.addLink(sw1,sw4)
    net.addLink(sw2,sw4)
    net.addLink(sw2,sw7)
    net.addLink(sw3,sw5)
    net.addLink(sw3,sw8)
    net.addLink(sw4,sw11)
    net.addLink(sw5,sw6)
    net.addLink(sw6,sw7)
    net.addLink(sw7,sw10)
    net.addLink(sw8,sw9)
    net.addLink(sw8,sw14)
    net.addLink(sw9,sw10)
    net.addLink(sw9,sw13)
    net.addLink(sw10,sw14)
    net.addLink(sw10,sw12)
    net.addLink(sw11,sw12)
    net.addLink(sw11,sw13)
    net.addLink(sw13,sw14)

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
    sw9.start([c0])
    sw10.start([c0])
    sw11.start([c0])
    sw12.start([c0])
    sw13.start([c0])
    sw14.start([c0])

    CLI( net )

    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()