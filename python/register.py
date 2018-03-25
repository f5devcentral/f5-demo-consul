import consul
import pprint
import argparse
import csv
import logging
import json

#logger = logging.getLogger()
#logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to create a pool on a BIG-IP device')
    parser.add_argument("--consul-host",dest="consul_host",default="127.0.0.1")
    parser.add_argument("--consul-port",dest="consul_port",default=8500)
    parser.add_argument("--service",dest="consul_service")
    parser.add_argument("--service-id",dest="consul_service_id")
    parser.add_argument("--host")
    parser.add_argument("--port")
    parser.add_argument("--action")
    args = parser.parse_args()

    c = consul.Consul(host=args.consul_host, port=args.consul_port)
    service = {
        "Service": args.consul_service,
        "ID": args.consul_service_id,
        "Tags": [
            "f5"
        ],
        "Port": 8080
    }
    if args.action == 'register':
        print c.catalog.register(args.host,args.host,service=service)
    elif args.action == 'deregister':
        print c.catalog.deregister(args.host,service_id=args.consul_service_id)
