#ifndef __HEADER_H__
#define __HEADER_H__ 1

struct ingress_metadata_t {
    bit<32> nhop_ipv4;
}

@metadata
struct intrinsic_metadata_t {
    bit<48> ingress_global_timestamp;
    bit<32> lf_field_list;
    bit<16> mcast_grp;
    bit<16> egress_rid;
    bit<8>  resubmit_flag;
    bit<8>  recirculate_flag;
}

@metadata @name("queueing_metadata")
struct queueing_metadata_t {
    bit<48> enq_timestamp;
    bit<16> enq_qdepth;
    bit<32> deq_timedelta;
    bit<16> deq_qdepth;
}

@metadata @name("int_metadata")
struct int_metadata_t {
    bit<8> device_no;
}

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

header arp_t {
    bit<16> arpHdr;     /* format of hardware address */
    bit<16> arpPro;     /* format of protocol address */
    bit<8>  arpHln;     /* length of hardware address */
    bit<8>  arpPln;     /* length of protocol address */
    bit<16> arpOp;      /* ARP/RARP operation */
    bit<48> arpSha;     /* sender hardware address */
    bit<32> arpSpa;     /* sender protocol address */
    bit<48> arpTha;     /* target hardware address */
    bit<32> arpTpa;     /* target protocol address */
}

header ipv4_t {
    bit<4>  version;
    bit<4>  ihl;
    bit<8>  diffserv;
    bit<16> totalLen;
    bit<16> identification;
    bit<3>  flags;
    bit<13> fragOffset;
    bit<8>  ttl;
    bit<8>  protocol;       //udp 17, tcp 6
    bit<16> hdrChecksum;
    bit<32> srcAddr;
    bit<32> dstAddr;
}

header udp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<16> len;
    bit<16> hdrChecksum;
}

header sr_t {               //source routing header
    bit<512> routingList; 
}

header inthdr_t {
    bit<8>  device_no;
    bit<9>  ingress_port;
    bit<9>  egress_port;
    bit<48> ingress_global_timestamp;
    bit<32> enq_timestamp;
    bit<19> enq_qdepth;
    bit<32> deq_timedelta;
    bit<19> deq_qdepth;  
}

struct metadata {
    @name("ingress_metadata")
    ingress_metadata_t   ingress_metadata;
    @name("intrinsic_metadata")
    intrinsic_metadata_t intrinsic_metadata;
    @name("queueing_metadata")
    queueing_metadata_t queueing_metadata;
    @name("int_metadata")
    int_metadata_t int_metadata;
}

struct headers {
    @name("ethernet")
    ethernet_t  ethernet;
    @name("arp")
    arp_t       arp;
    @name("ipv4")
    ipv4_t      ipv4;
    @name("udp")
    udp_t       udp;
    @name("sr")
    sr_t        sr;
    @name("inthdr")
    inthdr_t    inthdr;
}

#endif // __HEADER_H__