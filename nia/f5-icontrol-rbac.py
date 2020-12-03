from icontrol.session import iControlRESTSession
from icontrol.exceptions import iControlUnexpectedHTTPError
from requests.exceptions import HTTPError
import argparse
import json
import os
import sys
import logging



# /mgmt/shared/authz/roles/iControl_REST_API_User

# /mgmt/shared/authz/resource-groups

# /mgmt/shared/authz/roles

class IcrRbac(object):

    def __init__(self,
                 target_user,
                 host="192.168.1.245",
                 username="admin",
                 password="admin",
                 token=None,
                 sync_group=None,
                 log_level="info",
                 trace=False,
                 persist=False,
                 remote_user=False):

        self._username = username
        self._password = password

        if "http" not in host:
            self.base_url = "https://%s/mgmt" %(host)
        else:
            self.base_url = host

        self.sync_group = sync_group
        self.log_level = log_level
        self.trace = trace
        self.persist = persist
        self.target_user = target_user

        if token:
            self.icr = iControlRESTSession(username, password, token='tmos')
        else:
            self.icr = iControlRESTSession(username, password)
        if remote_user:
            self.remote_user = True
        else:
            self.remote_user = False
    def _get(self,uri):
        try:
            return self.icr.get(self.base_url + uri)
        except HTTPError as exc:
            # override icontrol 404 error
            if exc.response.status_code == 404 or exc.response.status_code == 204:
                return exc.response
            else:
                raise
    def _delete(self,uri):
        try:
            return self.icr.delete(self.base_url + uri)
        except HTTPError as exc:
            # override icontrol 404 error
            if exc.response.status_code == 404 or exc.response.status_code == 204:
                return exc.response
            else:
                raise
    def _post(self,uri,data):
        try:
            return self.icr.post(self.base_url + uri,data=data)
        except HTTPError as exc:
            # override icontrol 404 error
            if exc.response.status_code == 404 or exc.response.status_code == 204:
                return exc.response
            else:
                raise
    def _put(self,uri,data):
        try:
            return self.icr.put(self.base_url + uri,data=data)
        except HTTPError as exc:
            # override icontrol 404 error
            if exc.response.status_code == 404 or exc.response.status_code == 204:
                return exc.response
            else:
                raise


    def create_resource_group(self,name='eventDrivenResourceGroup'):
        rg = """{"name":"%s", "resources":[ {"restMethod":"GET", "resourceMask":"/mgmt/tm/net/self" },
                                            {"restMethod":"GET", "resourceMask":"/mgmt/shared/service-discovery/task" },
                                            {"restMethod":"GET", "resourceMask":"/mgmt/shared/service-discovery/task/**" },
                                            {"restMethod":"POST", "resourceMask":"/mgmt/shared/service-discovery/task/**" },
                                            {"restMethod":"GET", "resourceMask":"/mgmt/shared/appsvcs/info" } ]}""" %(name)
        resp = self._post('/shared/authz/resource-groups',data=rg)
        return resp

    def delete_resource_group(self,name='eventDrivenResourceGroup'):
        resp = self._get('/shared/authz/resource-groups')
        id  = None
        for item in resp.json()['items']:
            if item['name'] == name:
                id = item['id']
        if id:
            resp = self._delete('/shared/authz/resource-groups/%s' %(id))
        return resp
    def create_custom_role(self,name='eventRole',username=None,resource_group='eventDrivenResourceGroup'):
        if not username:
            username = self.target_user
        user_ref = "https://localhost/mgmt/shared/authz/users/%s" %(username)
        if self.remote_user:
            resp = self._get('/cm/system/authn/providers/tmos')
            id = resp.json()['items'][0]['id']
            resp = self._get('/cm/system/authn/providers/tmos/%s/users' %(id))
            user_ref = None
            for item in resp.json()['items']:
                if item['name'] == username:
                    user_ref = item['selfLink']

        resp = self._get('/shared/authz/resource-groups')
        id  = None
        for item in resp.json()['items']:
            if item['name'] == resource_group:
                id = item['id']

        role = """{"name":"%s", "userReferences":[ {"link":"%s"} ], "resourceGroupReferences":[{"link":"https://localhost/mgmt/shared/authz/resource-groups/%s"}]}""" %(name,user_ref,id)
        resp = self._post('/shared/authz/roles',data=role)
        return resp
    def delete_custom_role(self,name='eventRole'):
        resp = self._get('/shared/authz/roles')
        id  = None
        for item in resp.json()['items']:
            if item['name'] == name:
                id = item['name']
        if id:
            resp = self._delete('/shared/authz/roles/%s' %(id))
        return resp
    def remove_user_from_role(self,username=None,role='iControl_REST_API_User'):
        if not username:
            username = self.target_user
        # find user
        # local
#        client._get('/shared/authz/users').json()['items']
        # remote
#        client._get('/cm/system/authn/providers/tmos').json()
        # client._get('/cm/system/authn/providers/tmos').json()['items'][0]['id']

        resp = self._get('/shared/authz/roles/%s' %(role))
        output = resp.json()
        orig = resp.json()['userReferences']
        if self.remote_user:
            resp = self._get('/cm/system/authn/providers/tmos')
            id = resp.json()['items'][0]['id']
            resp = self._get('/cm/system/authn/providers/tmos/%s/users' %(id))
            user_ref = None
            for item in resp.json()['items']:
                if item['name'] == username:
                    user_ref = item['id']
            resp = self._get('/shared/authz/roles/%s' %(role))
            updated =  [a for a in resp.json()['userReferences'] if not a['link'].endswith("/%s" %(user_ref))]
        else:
            updated =  [a for a in resp.json()['userReferences'] if not a['link'].endswith("/%s" %(username))]
        if orig != updated:
            output['userReferences'] = updated
            resp = self._put('/shared/authz/roles/%s' %(role),data=json.dumps(output))

        return resp

    def add_user_to_role(self,username=None,role='eventRole'):
        if not username:
            username = self.target_user
        # find user
        # local
#        client._get('/shared/authz/users').json()['items']
        # remote
#        client._get('/cm/system/authn/providers/tmos').json()
        # client._get('/cm/system/authn/providers/tmos').json()['items'][0]['id']

        resp = self._get('/shared/authz/roles/%s' %(role))
        output = resp.json()
        orig = resp.json()['userReferences']
        if self.remote_user:
            resp = self._get('/cm/system/authn/providers/tmos')
            id = resp.json()['items'][0]['id']
            resp = self._get('/cm/system/authn/providers/tmos/%s/users' %(id))
            user_ref = None
            for item in resp.json()['items']:
                if item['name'] == username:
                    user_ref = item['id']
            resp = self._get('/shared/authz/roles/%s' %(role))
            updated =  [a for a in resp.json()['userReferences'] if not a['link'].endswith("/%s" %(user_ref))]
        else:
            user_ref = "https://localhost/mgmt/shared/authz/users/%s" %(username)
            updated =  [a for a in resp.json()['userReferences'] if not a['link'].endswith("/%s" %(username))]
        if orig == updated:
            updated.append({'link':user_ref})
            output['userReferences'] = updated
            resp = self._put('/shared/authz/roles/%s' %(role),data=json.dumps(output))

        return resp


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Script to manage an AS3 declaration')
    parser.add_argument("--host",             help="The IP/Hostname of the BIG-IP device",default='https://192.168.1.245/mgmt')
    parser.add_argument("-u", "--username",default='admin')
    parser.add_argument("-p", "--password",default='admin')
    parser.add_argument("--password-file",   help="The BIG-IP password stored in a file", dest='password_file')
    parser.add_argument("-a","--action",help="deploy,dry-run,delete,stub,redeploy,list(partitions),list-tenants,list-ages")

    parser.add_argument("--token",help="use token (remote auth)",action="store_true",default=False)
    parser.add_argument("--remote-user",help="target remote user",action="store_true",default=False,dest='remote_user')
    parser.add_argument("--target-user",dest='target_user',default='event')
    parser.add_argument("-f","--file",help="declaration JSON file")
    args = parser.parse_args()

    username = args.username
    password = args.password

    if 'F5_USERNAME' in os.environ:
        username = os.environ['F5_USERNAME']

    if 'F5_PASSWORD' in os.environ:
        password = os.environ['F5_PASSWORD']

    if args.password_file:
        password = open(args.password_file).readline().strip()

    if 'F5_HOST' in os.environ:
        host = os.environ['F5_HOST']
    else:
        host = args.host

    kwargs = {'host':host,
              'username':username,
              'password':password,
              'token':args.token,
              'remote_user':args.remote_user}

    client = IcrRbac(args.target_user,**kwargs)
    if args.action == 'add_user':
        # remove from iControl_REST_API_User
        client.remove_user_from_role()
        # add to eventRole
        client.add_user_to_role()
    elif args.action == 'cleanup':
        client.delete_custom_role()
        client.delete_resource_group()
    elif args.action == 'setup':
        client.create_resource_group()
        client.create_custom_role()
