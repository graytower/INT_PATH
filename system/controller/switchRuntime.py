# -*- coding:utf-8 -*-

import cmd
import os
import sys
import struct
import json
from functools import wraps
import bmpy_utils as utils

from bm_runtime.standard import Standard
from bm_runtime.standard.ttypes import *
from sswitch_runtime import SimpleSwitch
try:
    from bm_runtime.simple_pre import SimplePre
except:
    pass
try:
    from bm_runtime.simple_pre_lag import SimplePreLAG
except:
    pass


class SwitchRuntime(object):
    """
    Rewrite based on runtime_CLI written by Barefoot

    Use Thrift API communicate with BMV2 P4 switch

    Only can down tables now
    """

    class Table(object):
        def __init__(self, runtime, name, id_):
            self.name = name
            self.id_ = id_
            self.match_type_ = None
            self.actions = {}
            self.key = []
            self.default_action = None
            self.type_ = None
            self.support_timeout = False
            self.action_prof = None

            runtime.TABLES[name] = self

        def num_key_fields(self):
            return len(self.key)

        def key_str(self):
            return ",\t".join([name + "(" + MatchType.to_str(t) + ", " + str(bw) + ")" for name, t, bw in self.key])

        def table_str(self):
            ap_str = "implementation={}".format(
                "None" if not self.action_prof else self.action_prof.name)
            return "{0:30} [{1}, mk={2}]".format(self.name, ap_str, self.key_str())

    class ActionProf(object):
        def __init__(self, runtime, name, id_):
            self.name = name
            self.id_ = id_
            self.with_selection = False
            self.actions = {}
            self.ref_cnt = 0

            runtime.ACTION_PROFS[name] = self

        def action_prof_str(self):
            return "{0:30} [{1}]".format(self.name, self.with_selection)

    class Action(object):
        def __init__(self, runtime, name, id_):
            self.name = name
            self.id_ = id_
            self.runtime_data = []

            runtime.ACTIONS[name] = self

        def num_params(self):
            return len(self.runtime_data)

        def runtime_data_str(self):
            return ",\t".join([name + "(" + str(bw) + ")" for name, bw in self.runtime_data])

        def action_str(self):
            return "{0:30} [{1}]".format(self.name, self.runtime_data_str())

    class MeterArray(object):
        def __init__(self, runtime, name, id_):
            self.name = name
            self.id_ = id_
            self.type_ = None
            self.is_direct = None
            self.size = None
            self.binding = None
            self.rate_count = None

            runtime.METER_ARRAYS[name] = self

        def meter_str(self):
            return "{0:30} [{1}, {2}]".format(self.name, self.size,
                                              MeterType.to_str(self.type_))

    class CounterArray(object):
        def __init__(self, runtime, name, id_):
            self.name = name
            self.id_ = id_
            self.is_direct = None
            self.size = None
            self.binding = None

            runtime.COUNTER_ARRAYS[name] = self

        def counter_str(self):
            return "{0:30} [{1}]".format(self.name, self.size)

    class RegisterArray(object):
        def __init__(self, runtime, name, id_):
            self.name = name
            self.id_ = id_
            self.width = None
            self.size = None

            runtime.REGISTER_ARRAYS[name] = self

        def register_str(self):
            return "{0:30} [{1}]".format(self.name, self.size)

    class MatchType(object):
        EXACT = 0
        LPM = 1
        TERNARY = 2
        VALID = 3
        RANGE = 4

        @staticmethod
        def to_str(x):
            return {0: "exact", 1: "lpm", 2: "ternary", 3: "valid", 4: "range"}[x]

        @staticmethod
        def from_str(x):
            return {"exact": 0, "lpm": 1, "ternary": 2, "valid": 3, "range": 4}[x]

    def get_thrift_services(self, pre_type):
        services = [("standard", Standard.Client)]

        if pre_type == self.PreType.SimplePre:
            services += [("simple_pre", SimplePre.Client)]
        elif pre_type == self.PreType.SimplePreLAG:
            services += [("simple_pre_lag", SimplePreLAG.Client)]
        else:
            services += [(None, None)]

        return services

    def ssget_thrift_services(self):
        return [("simple_switch", SimpleSwitch.Client)]

    def __init__(self, thriftIp='localhost', thriftPort=9090, thriftPre='simplePre', jsonPath=None):

        self.thriftIp = thriftIp
        self.thriftPort = thriftPort
        self.thriftPre = thriftPre
        self.jsonPath = jsonPath

        self.TABLES = {}
        self.ACTION_PROFS = {}
        self.ACTIONS = {}
        self.METER_ARRAYS = {}
        self.COUNTER_ARRAYS = {}
        self.REGISTER_ARRAYS = {}
        self.CUSTOM_CRC_CALCS = {}

        self.PreType = self.enum(
            'PreType', 'None', 'SimplePre', 'SimplePreLAG')
        self.MeterType = self.enum('MeterType', 'packets', 'bytes')
        self.TableType = self.enum(
            'TableType', 'simple', 'indirect', 'indirect_ws')
        self._match_types_mapping = {
            self.MatchType.EXACT: BmMatchParamType.EXACT,
            self.MatchType.LPM: BmMatchParamType.LPM,
            self.MatchType.TERNARY: BmMatchParamType.TERNARY,
            self.MatchType.VALID: BmMatchParamType.VALID,
            self.MatchType.RANGE: BmMatchParamType.RANGE,
        }

    def makeThriftLink(self, qdepth, qrate):
        services = self.get_thrift_services(self.thriftPre)
        services.extend(self.ssget_thrift_services())
        self.standard_client, self.mc_client, self.sswitch_client = utils.thrift_connect(
            self.thriftIp, self.thriftPort, services)
        # self.standard_client, self.mc_client = utils.thrift_connect(
        #     self.thriftIp, self.thriftPort, self.get_thrift_services(self.thriftPre))
        self.json_str = utils.get_json_config(
            self.standard_client, self.jsonPath)
        self.load_json_str()
        # self.sswitch_client.set_egress_queue_depth(port, qdepth)
        self.sswitch_client.set_all_egress_queue_depths(qdepth)
        self.sswitch_client.set_all_egress_queue_rates(qrate)

    def enum(self, type_name, *sequential, **named):
        enums = dict(zip(sequential, range(len(sequential))), **named)
        reverse = dict((value, key) for key, value in enums.iteritems())

        @staticmethod
        def to_str(x):
            return reverse[x]
        enums['to_str'] = to_str

        @staticmethod
        def from_str(x):
            return enums[x]

        enums['from_str'] = from_str
        return type(type_name, (), enums)

    def bytes_to_string(self, byte_array):
        form = 'B' * len(byte_array)
        return struct.pack(form, *byte_array)

    def ipv4Addr_to_bytes(self, addr):
        s = addr.split('.')
        return [int(b) for b in s]

    def macAddr_to_bytes(self, addr):
        s = addr.split(':')
        return [int(b, 16) for b in s]

    def ipv6Addr_to_bytes(self, addr):
        from ipaddr import IPv6Address
        ip = IPv6Address(addr)
        return [ord(b) for b in ip.packed]

    def int_to_bytes(self, i, num):
        byte_array = []
        while i > 0:
            byte_array.append(i % 256)
            i = i / 256
            num -= 1
        while num > 0:
            byte_array.append(0)
            num -= 1
        byte_array.reverse()
        return byte_array

    def parse_param(self, input_str, bitwidth):
        if bitwidth == 32:
            return self.ipv4Addr_to_bytes(input_str)
        elif bitwidth == 48:
            return self.macAddr_to_bytes(input_str)
        elif bitwidth == 128:
            return self.ipv6Addr_to_bytes(input_str)
        else:
            if isinstance(input_str, str):
                input_ = int(input_str, 0)
            else:
                input_ = input_str
            return self.int_to_bytes(input_, (bitwidth + 7) / 8)

    def reset_config(self):
        self.TABLES.clear()
        self.ACTION_PROFS.clear()
        self.ACTIONS.clear()
        self.METER_ARRAYS.clear()
        self.COUNTER_ARRAYS.clear()
        self.REGISTER_ARRAYS.clear()
        self.CUSTOM_CRC_CALCS.clear()

    def load_json_str(self):
        def get_header_type(header_name, j_headers):
            for h in j_headers:
                if h["name"] == header_name:
                    return h["header_type"]
            assert(0)

        def get_field_bitwidth(header_type, field_name, j_header_types):
            for h in j_header_types:
                if h["name"] != header_type:
                    continue
                for t in h["fields"]:
                    # t can have a third element (field signedness)
                    f, bw = t[0], t[1]
                    if f == field_name:
                        return bw
            assert(0)

        self.reset_config()
        json_ = json.loads(self.json_str)

        def get_json_key(key):
            return json_.get(key, [])

        for j_action in get_json_key("actions"):
            action = self.Action(self, j_action["name"], j_action["id"])
            for j_param in j_action["runtime_data"]:
                action.runtime_data += [(j_param["name"], j_param["bitwidth"])]

        for j_pipeline in get_json_key("pipelines"):
            if "action_profiles" in j_pipeline:  # new JSON format
                for j_aprof in j_pipeline["action_profiles"]:
                    action_prof = self.ActionProf(
                        self, j_aprof["name"], j_aprof["id"])
                    action_prof.with_selection = "selector" in j_aprof

            for j_table in j_pipeline["tables"]:
                table = self.Table(self, j_table["name"], j_table["id"])
                table.match_type = self.MatchType.from_str(
                    j_table["match_type"])
                table.type_ = self.TableType.from_str(j_table["type"])
                table.support_timeout = j_table["support_timeout"]
                for action in j_table["actions"]:
                    table.actions[action] = self.ACTIONS[action]

                if table.type_ in {self.TableType.indirect, self.TableType.indirect_ws}:
                    if "action_profile" in j_table:
                        action_prof = self.ACTION_PROFS[j_table["action_profile"]]
                    else:  # for backward compatibility
                        assert("act_prof_name" in j_table)
                        action_prof = self.ActionProf(self, j_table["act_prof_name"],
                                                      table.id_)
                        action_prof.with_selection = "selector" in j_table
                    action_prof.actions.update(table.actions)
                    action_prof.ref_cnt += 1
                    table.action_prof = action_prof

                for j_key in j_table["key"]:
                    target = j_key["target"]
                    match_type = self.MatchType.from_str(j_key["match_type"])
                    if match_type == self.MatchType.VALID:
                        field_name = target + "_valid"
                        bitwidth = 1
                    elif target[1] == "$valid$":
                        field_name = target[0] + "_valid"
                        bitwidth = 1
                    else:
                        field_name = ".".join(target)
                        header_type = get_header_type(target[0],
                                                      json_["headers"])
                        bitwidth = get_field_bitwidth(header_type, target[1],
                                                      json_["header_types"])
                    table.key += [(field_name, match_type, bitwidth)]

        for j_meter in get_json_key("meter_arrays"):
            meter_array = self.MeterArray(self, j_meter["name"], j_meter["id"])
            if "is_direct" in j_meter and j_meter["is_direct"]:
                meter_array.is_direct = True
                meter_array.binding = j_meter["binding"]
            else:
                meter_array.is_direct = False
                meter_array.size = j_meter["size"]
            meter_array.type_ = self.MeterType.from_str(j_meter["type"])
            meter_array.rate_count = j_meter["rate_count"]

        for j_counter in get_json_key("counter_arrays"):
            counter_array = self.CounterArray(
                self, j_counter["name"], j_counter["id"])
            counter_array.is_direct = j_counter["is_direct"]
            if counter_array.is_direct:
                counter_array.binding = j_counter["binding"]
            else:
                counter_array.size = j_counter["size"]

        for j_register in get_json_key("register_arrays"):
            register_array = self.RegisterArray(self,
                                                j_register["name"], j_register["id"])
            register_array.size = j_register["size"]
            register_array.width = j_register["bitwidth"]

        for j_calc in get_json_key("calculations"):
            calc_name = j_calc["name"]
            if j_calc["algo"] == "crc16_custom":
                self.CUSTOM_CRC_CALCS[calc_name] = 16
            elif j_calc["algo"] == "crc32_custom":
                self.CUSTOM_CRC_CALCS[calc_name] = 32

    def parse_runtime_data(self, action, params):
        bitwidths = [bw for(_, bw) in action.runtime_data]
        byte_array = []
        for input_str, bitwidth in zip(params, bitwidths):
            byte_array += [self.bytes_to_string(
                self.parse_param(input_str, bitwidth))]
        return byte_array

    def parse_match_key(self, table, key_fields):

        def parse_param_(field, bw):
            return self.parse_param(field, bw)

        params = []
        match_types = [t for (_, t, _) in table.key]
        bitwidths = [bw for (_, _, bw) in table.key]
        for idx, field in enumerate(key_fields):
            param_type = self._match_types_mapping[match_types[idx]]
            bw = bitwidths[idx]
            if param_type == BmMatchParamType.EXACT:
                key = self.bytes_to_string(parse_param_(field, bw))
                param = BmMatchParam(type=param_type,
                                     exact=BmMatchParamExact(key))
            elif param_type == BmMatchParamType.LPM:
                prefix, length = field.split("/")
                key = bytes_to_string(parse_param_(prefix, bw))
                param = BmMatchParam(type=param_type,
                                     lpm=BmMatchParamLPM(key, int(length)))
            elif param_type == BmMatchParamType.TERNARY:
                key, mask = field.split("&&&")
                key = bytes_to_string(parse_param_(key, bw))
                mask = bytes_to_string(parse_param_(mask, bw))
                if len(mask) != len(key):
                    pass
                param = BmMatchParam(type=param_type,
                                     ternary=BmMatchParamTernary(key, mask))
            elif param_type == BmMatchParamType.VALID:
                key = bool(int(field))
                param = BmMatchParam(type=param_type,
                                     valid=BmMatchParamValid(key))
            elif param_type == BmMatchParamType.RANGE:
                start, end = field.split("->")
                start = bytes_to_string(parse_param_(start, bw))
                end = bytes_to_string(parse_param_(end, bw))
                if len(start) != len(end):
                    pass
                if start > end:
                    pass
                param = BmMatchParam(type=param_type,
                                     range=BmMatchParamRange(start, end))
            else:
                assert(0)
            params.append(param)
        return params

    def table_clear(self, table_name):
        table = self.TABLES[table_name]
        self.standard_client.bm_mt_clear_entries(0, table_name, False)

    def table_add(self, table_name, action_name, match_key, action_params, priority=None):
        table = self.TABLES[table_name]
        if table.match_type in {self.MatchType.TERNARY, self.MatchType.RANGE}:
            try:
                priority = int(priority)
            except:
                # here need to throw a exception but I don't care
                pass
        else:
            priority = 0

        action = self.ACTIONS[action_name]
        if not isinstance(action_params, tuple):
            action_params = (action_params, )
        runtime_data = self.parse_runtime_data(action, action_params)

        match_key = self.parse_match_key(table, match_key)

        entry_handle = self.standard_client.bm_mt_add_entry(
            0, table_name, match_key, action_name, runtime_data,
            BmAddEntryOptions(priority=priority)
        )

    def counter_read(self, counter_name, counter_index):
        value = self.standard_client.bm_counter_read(
            0, counter_name, counter_index)
        return value

    def counter_reset(self, counter_name):
        value = self.standard_client.bm_counter_reset_all(0, counter_name)


if __name__ == '__main__':
    sr = SwitchRuntime()
    sr.makeThriftLink()
    sr.table_add('doarp', 'arpreply', ('00:00:00:00:00:00',
                                       '10.0.0.101'), '00:01:00:00:00:01')

    # sr.table_clear('doarp')
