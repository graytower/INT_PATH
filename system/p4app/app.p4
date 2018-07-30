#include <core.p4>
#include <v1model.p4>

#include "header.p4"
#include "parser.p4"

#define COUNTER_SIZE 32w16

control egress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {

    counter(COUNTER_SIZE,CounterType.packets) egress_counter;

    @name("_drop")
    action _drop() {
        mark_to_drop();
    }
    @name("do_int") 
    action do_int() {
        hdr.udp.len = hdr.udp.len+16w22;
        hdr.udp.hdrChecksum = 16w0;
        hdr.ipv4.totalLen=hdr.ipv4.totalLen+16w22;
        hdr.ipv4.hdrChecksum=hdr.ipv4.hdrChecksum-16w22;
        hdr.inthdr.setValid();
        hdr.inthdr.device_no = meta.int_metadata.device_no;
        hdr.inthdr.ingress_port = standard_metadata.ingress_port;
        hdr.inthdr.egress_port = standard_metadata.egress_port;
        hdr.inthdr.ingress_global_timestamp = standard_metadata.ingress_global_timestamp;
        hdr.inthdr.enq_timestamp = standard_metadata.enq_timestamp;
        hdr.inthdr.enq_qdepth = standard_metadata.enq_qdepth;
        hdr.inthdr.deq_timedelta = standard_metadata.deq_timedelta;
        hdr.inthdr.deq_qdepth = standard_metadata.deq_qdepth;
    }
    @name("udp_int")
    table udp_int {
        actions = {
            do_int;
        }
        key = {}
        size = 1024;
        default_action = do_int();
    }
    apply {
        egress_counter.count((bit<32>)standard_metadata.egress_port);
        if (hdr.sr.isValid()) {
            udp_int.apply();
        }
    }
}

control ingress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {

    counter(COUNTER_SIZE,CounterType.packets) ingress_counter;

    @name("_drop")
    action _drop() {
        mark_to_drop();
    }
    @name("l2setmetadata")
    action l2setmetadata(bit<9> port) {
        standard_metadata.egress_spec = port;
        standard_metadata.egress_port = port;
    }
    @name("l2setmetadataecmp")
    action l2setmetadataecmp(bit<2> routeNum, bit<16> portData) {
        bit<32> result=32w0;
        random(result,32w0,(bit<32>)(routeNum-2w1));
        bit<16> data=portData;
        if (result == 32w1) {
            data=portData>>4;
        }else if(result == 32w2){
            data=portData>>8;
        }else if(result==32w3){
            data=portData>>4;
            data=portData>>8;
        }
        bit<9> port=(bit<9>)((bit<4>)data);
        standard_metadata.egress_spec = port;
        standard_metadata.egress_port = port;
    }
    @name("arpreply")
    action arpreply(bit<48>repmac) {
        standard_metadata.egress_spec = standard_metadata.ingress_port;
        standard_metadata.egress_port = standard_metadata.ingress_port;
        hdr.ethernet.srcAddr=repmac;
        hdr.ethernet.dstAddr=hdr.arp.arpSha;
        bit<32> tempip;
        tempip=hdr.arp.arpSpa;
        hdr.arp.arpSpa=hdr.arp.arpTpa;
        hdr.arp.arpTpa=tempip;
        hdr.arp.arpTha=hdr.arp.arpSha;
        hdr.arp.arpSha=repmac;
    }
    @name("srrouting")
    action srrouting() {
        // read 4 bit from routingList use listPosition
        // and set it to egress metadata
        bit<4> port=(bit<4>)hdr.sr.routingList;
        hdr.sr.routingList=hdr.sr.routingList>>4;
        standard_metadata.egress_spec = (bit<9>)port+9w1;
        standard_metadata.egress_port = (bit<9>)port+9w1;
    }
    @name("setdeviceno")
    action setdeviceno(bit<8> device_no) {
        meta.int_metadata.device_no=device_no;
    }

    @name("dotrans")
    table dotrans {
        actions = {
            l2setmetadataecmp;
            NoAction;
        }
        key = {
            hdr.ethernet.srcAddr:exact;
            hdr.ethernet.dstAddr:exact;
        }
        size=512;
        default_action=NoAction();
    }
    @name("dosocket")
    table dosocket {
        actions = {
            l2setmetadata;
            NoAction;
        }
        key = {
            hdr.udp.dstPort:exact;
        }
        size=512;
        default_action=NoAction();
    }
    @name("doarp")
    table doarp {
        actions = {
            arpreply;
            NoAction;
        }
        key = {
            hdr.arp.arpTha:exact;
            hdr.arp.arpTpa:exact;
        }
        size=512;
        default_action=NoAction();
    }
    @name("dosr")
    table dosr {
        actions = {
            srrouting;
        }
        key={}
        size=512;
        default_action=srrouting();
    }
    @name("setmetadata")
    table setmetadata {
        actions = {
            setdeviceno;
            NoAction;
        }
        key={}
        size=512;
        default_action=NoAction();
    }
    apply { 
        setmetadata.apply();
        if (hdr.ipv4.isValid()) {
            if(hdr.sr.isValid()) {
                dosr.apply();
            }else{
                dotrans.apply();
                dosocket.apply();
            }
        } else if(hdr.arp.isValid()) {
            doarp.apply();
        }
        ingress_counter.count((bit<32>)standard_metadata.ingress_port);
    }
}

V1Switch(ParserImpl(), verifyChecksum(), ingress(), egress(), computeChecksum(), DeparserImpl()) main;