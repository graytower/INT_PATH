parser ParserImpl(packet_in packet, out headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    @name("start")
    state start {
        transition parse_ethernet;
    }
    @name("parse_ethernet")
    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            16w0x0800: parse_ipv4;
            16w0x0806: parse_arp;
            default: accept;
        }
    }
    @name("parse_arp")
    state parse_arp {
        packet.extract(hdr.arp);
        transition accept;
    }
    @name("parse_ipv4")
    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            8w0x11:parse_udp;
            default:accept;
        }
    }
    @name("parse_udp")
    state parse_udp {
        packet.extract(hdr.udp);
        transition select(hdr.udp.dstPort) {
            16w0x8AE:parse_sr;      //port 2222
            default:accept;
        }
    }
    @name("parse_sr")
    state parse_sr {
        packet.extract(hdr.sr);
        transition accept;
    }
}

control DeparserImpl(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.arp);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.udp);
        packet.emit(hdr.sr);
        packet.emit(hdr.inthdr);
}
}

control verifyChecksum(in headers hdr, inout metadata meta) {
}

control computeChecksum(inout headers hdr, inout metadata meta) {
}
