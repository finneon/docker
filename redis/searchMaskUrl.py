#!/usr/bin/env python
""" Find all tenants which use Mask URL """
import redis
import re
import json
import argparse
import sys
import os


class SearchRedisAdmin(object):
    """ Search the host with filter domain"""

    def __init__(self, host, pattern):
        self.r = redis.Redis(host="{}".format(host), port=6379, db=0)
        self.pattern = pattern

    def search(self):
        """ Scan all the key in redis data. If the key contains custom_domain and not empty,
            write to the file with format
            key: mask url
        """
        result = dict()
        for key in self.r.scan_iter("*{0}*".format(self.pattern)):
            try:
                data = self.r.hgetall(key)
                for r_key, values in data.items():
                    if re.search("settings", r_key.decode("utf-8")):
                        json_dump = json.loads(values.decode("utf-8"))
                        for s_key, value in json_dump.items():
                            if re.search("custom_domain", s_key):
                                if value:
                                    result[key.decode("utf-8")] = value
            except Exception:
                pass

        file_output = os.path.join(os.getcwd(), "mask_url_output")
        if os.path.exists(file_output):
            os.remove(file_output)
        with open(file_output, 'w') as f:
            for k, v in result.items():
                f.write("{0}: {1}\n".format(k, v))


def parse_argument(args):
    parser = argparse.ArgumentParser(description="Find all tenants which use Mask URL",
                                     epilog="Input endpoint and search pattern",
                                     usage="searchMaskUrl -e example.com -p example.com")
    parser.add_argument("-e", "--endpoint", dest="host", nargs=1, help="Endpoint of the redis admin")
    parser.add_argument("-p", "--pattern", nargs=1, help="Pattern to filter the tenant")

    return parser.parse_args(args=args)


def main():
    if len(sys.argv) <= 1:
        print("Please input")
        sys.exit(1)
    options = parse_argument(sys.argv[1:])
    host = options.host
    pattern = options.pattern
    s = SearchRedisAdmin(host[0], pattern[0])
    s.search()


if __name__ == '__main__':
    main()
