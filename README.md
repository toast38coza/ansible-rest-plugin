# ansible-rest-plugin
A REST plugin for use with Ansible

## Usage: 

```
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
```
