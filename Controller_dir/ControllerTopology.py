from ryu.base import app_manager
from ryu.controller import mac_to_port, ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet, arp, ethernet, ipv4, ipv6, ether_types, udp, tcp
from ryu.lib import mac, ip, hub
from ryu.ofproto import inet
from ryu.topology.api import get_all_switch, get_all_link, get_host, get_switch, get_link
from ryu.topology import event, switches
from ryu.app.wsgi import ControllerBase
import numpy as np
from collections import defaultdict
from operator import itemgetter
import heapq
import sys
import threading
import os
import random
import time
import array 

class GraphNeuralNet():
    """
    Graph Neural Net Class for Link-Link
    """
    def __init__(self, n_link, dim_list, link_matrix):
        """
        initialize Neural net
        """
        self.n_link = n_link
        self.weight_list = []
        
        self.link_matrix = link_matrix
        for i in range(len(dim_list) - 1):
            self.weight_list.append(np.random.rand(dim_list[i] , dim_list[i+1]))
    
    def Relu(self,x):
        x[x < 0] = 0
        return x
        
    def forward(self, embedding):
        """
        Forward Pass through Neural Net
        """
        self.result = embedding
        for i in range(len(self.weight_list) - 1):
            self.result =  self.Relu(np.dot(np.dot(self.link_matrix,self.result),self.weight_list[i]))
        self.result =  np.dot(np.dot(self.link_matrix,self.result),self.weight_list[-1])
        return self.result


class GNNController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(GNNController, self).__init__(*args, **kwargs)
        self.nrequest = 0
        self.mac_to_port = {}
        self.hosts = {}
        self.arp_table = {}
        self.packets = {}
        self.nnodes = 8
        self.nlink = 0
        self.link_dict = {}
        self.embed_size = 15
        self.neigh = {}
        self.decay = 0.974
        self.ttl = 64
        self.alpha = 0.6
        self.beta = 0.4
        self.qprocesstime = 3
        self.epsilon = 1
        self.topology_api_app = self
        self.total_packets = 0
        self.packets_dropped = 0
        self.packets_routed = 0
        self.connection_dict = [ [1, 7] ,
                                 [0, 7, 2],
                                 [1, 6, 3],
                                 [2, 5, 4],
                                 [3, 5, 6],
                                 [3, 4, 7] ,
                                 [2, 4, 7] ,
                                 [0, 1, 2, 6]
                              ]
        self.InitLinkMatrix()
        self.queue_size = np.zeros(self.nnodes)
        self.dim_list = [15, 11, 8, 4, 1]
        self.link_delay = [int(np.random.uniform(2,10)) for i  in range(self.nlink)]
        self.GNN = GraphNeuralNet(self.nlink, self.dim_list, self.link_matrix)
        self.links = {}

        self.ip_dict = {
        "10.0.0.1" : "sw1" ,
        "10.0.0.2" : "sw2" ,
        "10.0.0.3" : "sw3" ,
        "10.0.0.4" : "sw4" ,
        "10.0.0.5" : "sw5" ,
        "10.0.0.6" : "sw6" ,
        "10.0.0.7" : "sw7" ,
        "10.0.0.8" : "sw8" ,
    } 
        self.switch_dict = {
        "sw1" : 0,
        "sw2" : 1,
        "sw3" : 2,
        "sw4" : 3,
        "sw5" : 4,
        "sw6" : 5,
        "sw7" : 6,
        "sw8" : 7,
    }


    def InitLinkMatrix(self):
        """
        Construct Link Matrix
        """
        for i in range(len(self.connection_dict)):
            for j in range(len(self.connection_dict[i])):
                self.link_dict[self.nlink] = (i,self.connection_dict[i][j])
                self.nlink += 1

        self.link_matrix = np.zeros((self.nlink,self.nlink))
        for i in range(self.nlink):
            for j in range(self.nlink):
                if self.link_dict[i][1] == self.link_dict[j][0]:
                    self.link_matrix[i][j] = self.link_matrix[j][i] = 1

        self.link_available = np.ones(self.nlink)

    def Generate_Embeddings(self, curr_sw, dest_sw):
        """
        Generate Network state matrix for given network state
        """
        nsm_matrix = np.zeros((self.nlink, self.embed_size))
        for i in range(self.nlink):
            if dest_sw == self.link_dict[i][1]:
                nsm_matrix[i][0] = 1
            if curr_sw == self.link_dict[i][0]:
                nsm_matrix[i][1] = 1
            nsm_matrix[i][2] = self.link_delay[i]
            nsm_matrix[i][3] = self.queue_size[self.link_dict[i][1]]
            nsm_matrix[i][4] = self.link_available[i]
            nsm_matrix[i][5] = self.ttl - self.link_delay[i]

        return nsm_matrix

    def select_greedy_epsilon(self, Q_values):
        p = np.random.rand()
        if p < self.epsilon:
            return random.randint(0,self.nlink - 1)
        else:
            return np.argmax(np.array(Q_values))

    def assign_reward(self):
        return 9
        
    def selectNextSwitch(self, msg, curr_sw, dest_sw, src_sw):
        """
        Select Next Switch using forward pass
        """
        dp = msg.datapath
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        in_port = msg.match['in_port']
        self.epsilon = self.epsilon * self.decay
        embed = self.Generate_Embeddings(curr_sw, dest_sw)
        Q_values = self.GNN.forward(embed)

        
        next_link = self.select_greedy_epsilon(Q_values)
        while self.link_dict[next_link][0] != curr_sw:
            next_link = self.select_greedy_epsilon(Q_values)
        next_sw = self.link_dict[next_link][1]

        print("Next Switch Destination is :", next_sw)
        return next_link, next_sw


    def NetSumary(self):
        print("Total Packets ---->", self.packets_dropped + self.packets_routed)
        print("Routed Packets ---->", self.packets_routed)
        print("Dropped Packets ---->", self.packets_dropped)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        """
        Assign Packet to next node
        """

        msg = ev.msg
        self.nrequest += 1
        pkt = packet.Packet(array.array('B', ev.msg.data))
        dp = msg.datapath
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        in_port = msg.match['in_port']
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        arp_pkt = pkt.get_protocol(arp.arp)
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        self.mac_to_port.setdefault(dp.id - 1, {})
        
        dst = eth.dst
        src = eth.src
        dpid = dp.id - 1
        self.queue_size[dpid] += 1
        next_sw, src_sw, dest_sw  = -1, -1, -1
        
        if eth.ethertype == ether_types.ETH_TYPE_IP:
            nw = pkt.get_protocol(ipv4.ipv4)
            if nw.proto == inet.IPPROTO_UDP:
                l4 = pkt.get_protocol(udp.udp)
            elif nw.proto == inet.IPPROTO_TCP:
                l4 = pkt.get_protocol(tcp.tcp)     

        if src not in self.hosts:
            self.hosts[src] = (dpid, in_port)

        if arp_pkt is not None and arp_pkt.opcode == arp.ARP_REQUEST:
                 
            src_ip = arp_pkt.src_ip
            dst_ip = arp_pkt.dst_ip
            src_mac = arp_pkt.src_mac
            dst_mac = arp_pkt.dst_mac
            if arp_pkt.opcode == arp.ARP_REPLY:
                print("Packet is of form ARP Reply")
                self.arp_table[src_ip] = src
                h1 = self.hosts[src]
                h2 = self.hosts[dst]
                if src_ip + dst_ip not in self.packets.keys():
                    self.packets[src_ip + dst_ip] = 0 
                    self.total_packets += 1
                print("Source IP Addr: ", src_ip, "Dest IP Addr ", dst_ip)
                print("Source Switch --> ", src_sw)
                print("Destination Switch --> ", dest_sw)
                print("Current Switch --> ", dpid)
                if dpid == dest_sw :
                    print("Total Packet Delay is: ", self.packets[src_ip + dst_ip])
                    self.packets_routed += 1
                    self.queue_size[dpid] += 1
                    print("Reached Destination Switch can terminate packet action now")
                    self.NetSumary()
                    print("------------------------------------------------------------------------------")
                    print("------------------------------------------------------------------------------")
                    return


            elif arp_pkt.opcode == arp.ARP_REQUEST:
                self.arp_table[src_ip] = src
                src_sw = self.switch_dict[self.ip_dict[src_ip]]
                dest_sw = self.switch_dict[self.ip_dict[dst_ip]]
                if src_ip + dst_ip not in self.packets.keys():
                    self.packets[src_ip + dst_ip] = 0 
                    self.total_packets += 1
                
                print("ARP Request")
                print("Source IP Addr: ", src_ip, "Dest IP Addr ", dst_ip)
                print("Source Switch --> ", src_sw)
                print("Destination Switch --> ", dest_sw)
                print("Current Switch --> ", dpid)
                if dpid == dest_sw :
                    print("Total Packet Delay is: ", self.packets[src_ip + dst_ip])
                    self.packets_routed += 1
                    self.queue_size[dpid] -= 1
                    print("Reached Destination Switch can terminate packet action now")
                    self.NetSumary()
                    print("------------------------------------------------------------------------------")
                    print("------------------------------------------------------------------------------")
                    return

                linkn, next_sw = self.selectNextSwitch( msg , dpid , dest_sw , src_sw, self.ttl)
                curr_sw = dpid


                if (curr_sw,next_sw) not in self.links.keys():
                    print("Drop Packet as link not found")
                    self.packets_dropped += 1
                    self.NetSumary()
                    self.queue_size[dpid] -= 1
                    print("Reward Assigned: ", -20 )
                    print("-------------------------------------------------------------")
                    print("-------------------------------------------------------------")
                    return
                else:
                    self.packets[arp_pkt.src_ip + arp_pkt.dst_ip] += self.link_delay[linkn]
                    out_port = self.links[(curr_sw,next_sw)]
                    print("SEnding through port :", self.links[(curr_sw,next_sw)])

                self.queue_size[dpid] -= 1
                actions = [ofp_parser.OFPActionOutput(out_port)]
                out = ofp_parser.OFPPacketOut(
                    datapath=dp, buffer_id=msg.buffer_id, in_port=in_port,
                    actions=actions)
                if next_sw == dest_sw:
                    print("Reward Assigned: ", 50 + self.alpha * self.link_delay[linkn]  + self.beta * self.queue_size[dpid] )
                else:
                    print("Reward Assigned: ", 20 + self.alpha * self.link_delay[linkn]  + self.beta * self.queue_size[dpid] )
                print("-------------------------------------------------------------")
                dp.send_msg(out)

                

        elif eth.ethertype == ether_types.ETH_TYPE_IP and nw.proto == inet.IPPROTO_TCP:
            src_ip = arp_pkt.src_ip
            dst_ip = arp_pkt.dst_ip
            src_sw = self.switch_dict[self.ip_dict[src_ip]]
            dest_sw = self.switch_dict[self.ip_dict[dst_ip]]
            
            linkn, next_sw = self.selectNextSwitch( msg , dpid , dest_sw , src_sw)

            curr_sw = dpid
            if curr_sw == dest_sw :
                print("Reached Destination Switch can terminate packet action now")
                print("-------------------------------------------------------------")

            if (curr_sw,next_sw) not in self.links.keys():
                print("Drop Packet as link not found")
                return
            else:
                self.link_delay[arp_pkt.src_ip + arp_pkt.dst_ip] += self.link_delay[linkn]
                out_port = self.links[(curr_sw,next_sw)]

                print("SEnding through port :", self.links[(curr_sw,next_sw)])

            actions = [ofp_parser.OFPActionOutput(out_port)]
            out = ofp_parser.OFPPacketOut(
                datapath=dp, buffer_id=msg.buffer_id, in_port=in_port,
                actions=actions)
            print("A")
            print("-------------------------------------------------------------")
            dp.send_msg(out)


    @set_ev_cls(event.EventSwitchEnter)
    def get_topology_data(self, ev):
        switch_list = get_switch(self.topology_api_app, None)
        self.switches=[switch.dp.id for switch in switch_list]
        links_list = get_link(self.topology_api_app, None)
        for link in links_list:
            self.links[(link.src.dpid - 1,link.dst.dpid - 1)] = link.src.port_no
        print("-----------------------------------------------")
        print("Initating Topology Discovery Mechanism")
        print(self.links)
        