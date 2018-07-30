
CREATE TABLE IF NOT EXISTS `fnl_int` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_no` int(11) DEFAULT NULL,
  `ingress_port` int(11) DEFAULT NULL,
  `egress_port` int(11) DEFAULT NULL,
  `ingress_global_timestamp` bigint(20) DEFAULT NULL,
  `enq_timestamp` bigint(20) DEFAULT NULL,
  `enq_qdepth` int(11) DEFAULT NULL,
  `deq_timedelta` bigint(20) DEFAULT NULL,
  `deq_qdepth` int(11) DEFAULT NULL,
  `udp_port` int(11) DEFAULT NULL,
  `timestamp` int(11) DEFAULT NULL,
  `packet_id` text,
  `action_id` int(11) DEFAULT NULL,
  KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
