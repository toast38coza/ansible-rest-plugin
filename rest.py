#!/usr/bin/python

DOCUMENTATION = '''
---
module: rest
short_description: Interface to RESTful APIs

'''

EXAMPLES = '''
# Create a resource 
- rest: 
    base_url: test 
    resource_path: example.com
    data: {}
    headers: {}
    state: present

# Make sure that a resource is at its latest, will create it if not exists
- rest: 
    base_url: example.com
    resource_path: test
    resource_id: 123
    data: {}
    headers: {}
    state: latest

# Upsert a resource. 
# Will try find a resource using search dict. 
# will look in result_path to see if there are any results. 
# will then PUT and updated version of the data returned from search
# If nothing found, then it will create
- rest: 
    base_url: example.com
    resource_path: test
    data: {}
    headers: {}
    state: latest
    search_params:
      key: Value
    result_path: .
    expect_many: no


'''

import json, requests, os
DEBUG_MODE=True

class REST:
    
    def __init__(self, base_url):
        self.base_url = base_url

    def call(self, path, data={}, headers={}, method='get', id=False):

        url = "{0}{1}" . format (self.base_url, path)
        create_verbs = ["post", "get"]
        data = json.dumps(data)

        if DEBUG_MODE:
            print "import requests, json"
            print "url={0}" .format(url)
            print "headers={0}" .format(headers)
            print "data=json.dumps({0})" .format(data)
            print "requests.{0}(url, data=data, headers=headers)". format(method)
        
        if method == "put":
            
            # try get the resource: 
            resource_url = "{}/{}" . format (url, id)
            response = requests.get(resource_url, headers=headers)
            if response.status_code == 404:
                create_verbs.append("put")
            else:
            
                return requests.put(resource_url, data=data, headers=headers)

        if method in create_verbs:
            return requests.post(url, data, headers=headers)
            

        if method == "delete":
            return requests.delete(url, headers=headers)



def main():
    '''
    ../../ansible/hacking/test-module -m ./rest.py -a "state=list resource_path=/projects/1222014 base_url=https://www.pivotaltracker.com/services/v5"
    '''
    global module

    args = dict(
        base_url = dict(required=True, type='str'),
        resource_path = dict(required=True, type='str'),
        state = dict(required=True, choices=['present', 'absent', 'latest', 'list'], type='str'),    
        
        data = dict(required=False, default={}, type='dict'),
        headers = dict(required=False, default={}, type='dict'),
        status_code = dict(required=False, default=[200], type='list'),
        resource_id = dict(required=False, default=False, type='str'),
    )

    state_map = {
        "present": "post",
        "absent": "delete",
        "latest": "put",
        "list": "get",
    }

    module = AnsibleModule(argument_spec=args,supports_check_mode=False)

    state = module.params["state"]
    resource_path = module.params['resource_path']
    resource_id = module.params['resource_id']
    base_url = module.params['base_url']
    data = module.params['data']
    headers = module.params['headers']
    status_code = module.params['status_code']


    method = state_map.get(state)

    rest = REST(base_url)

    response = rest.call(resource_path, data=data, headers=headers, method=method, id=resource_id)

    if response.status_code in module.params.get("status_code"):
        if method != "delete":
            module.exit_json(msg="SUCCESS", content=json.loads(response.content))
        else:
            module.exit_json(msg="SUCCESS", content=response.content)
    else:
        status_codes_as_strings = (",").join([str(item) for item in status_code])
        error_message = "invalid status code was returned. expected one of: {0}. Got: {1}" \
            . format (status_codes_as_strings, response.status_code)
        module.fail_json(changed=False, content=json.loads(response.content), msg=error_message)
    

from ansible.module_utils.basic import *
main()
