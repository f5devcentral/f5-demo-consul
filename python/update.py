import consul
from f5.bigip import ManagementRoot
from icontrol.session import iControlRESTSession
import pprint
import argparse
import csv
import logging
import json

#logger = logging.getLogger()
#logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to create a pool on a BIG-IP device')
    parser.add_argument("-P", "--partition", help="The partition name (Common)", default="Common")
    parser.add_argument("-u", "--username", help="The BIG-IP username (admin)", default="admin")
    parser.add_argument("-p", "--password", help="The BIG-IP password (admin)", default="admin")
    parser.add_argument("-f","--file",help="CSV file input")
    parser.add_argument("-a","--action",help="create/read/update/delete")
    parser.add_argument("--bigip-host",dest="bigip_host",default="192.168.1.245")
    parser.add_argument("--consul-host",dest="consul_host",default="127.0.0.1")
    parser.add_argument("--bigip-port",dest="bigip_port",default=443)
    parser.add_argument("--consul-port",dest="consul_port",default=8500)
    parser.add_argument("--consul-service",dest="consul_service")
    parser.add_argument("--pool-name",dest="pool_name")
    args = parser.parse_args()

    c = consul.Consul(host=args.consul_host, port=args.consul_port)
    nodes = c.catalog.service(args.consul_service)
    pool_members = [{"name":"%s:%s" %(a['Address'],a['ServicePort']),"partition":args.partition} for a in nodes[1]]

    mgmt = ManagementRoot(args.bigip_host, args.username, args.password, token='tmos')
    pool = mgmt.tm.ltm.pools.pool.load(partition=args.partition, name=args.pool_name)
    session = mgmt._meta_data['bigip']._meta_data['icr_session']

    # https://devcentral.f5.com/questions/icontrol-rest-pool-member-add-delete-replace-examples
    members = session.put(pool._meta_data['uri'],data=json.dumps({'members':pool_members}))
    cmd = mgmt.tm.sys.config
    cmd.exec_cmd('save')
    token = session.session.auth.token
    t = mgmt.shared.authz.tokens_s.token.load(name=token)
    t.delete()
