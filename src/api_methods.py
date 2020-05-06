'''
@author: keith

'''
import sys
import json
import requests
import api_config

class SessionObject:
    """ Session object class
    """
    def __init__(self, username, password, url):
        self.username = username
        self.password = password
        self.api_url = url

        if username == '' or password == '' or url == '':
            print("Username, password and api url must be defined in api_config.py")
            sys.exit()

        self.headers = {'Accept':'application/vnd.alertme.zoo-6.3+json',
                        'X-Omnia-Client':'KG',
                        'Content-Type':'application/json'}

        # Login and get userId and sessionId
        url = self.api_url + '/omnia/auth/sessions'
        payload = json.dumps({'sessions':[{'username':username, 'password':password}]})
        resp = requests.post(url, data=payload, headers=self.headers)
        self.headers['X-Omnia-Access-Token'] = resp.json()['sessions'][0]['sessionId']

    def get_node_id(self, node_name):
        """ Get the node ID for a given node name

        """
        success = False
        node_id = None
        url = self.api_url + '/omnia/nodes/'
        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            for node in resp.json()['nodes']:
                if node['name'] == node_name:
                    success = True
                    node_id = node['id']
        return resp, success, node_id
    def set_state(self, node_name, state):
        """ Modify the state (on/off)
            PUT /omnia/nodes/{nodeId}
            payload = {"nodes":[{"attributes": {"state":{"targetValue":state}}}]}

        """
        if state:
            my_state = "ON"
        else:
            my_state = "OFF"

        resp, success, payload = self.set_attribute(node_name, 'state', my_state)

        return resp, success, payload
    def set_brightness(self, node_name, brightness):
        """ Modify the brightness 0-100
            PUT /omnia/nodes/{nodeId}
            payload = {"nodes":[{"attributes": {"brightness":{"targetValue":brightness}}}]}

        """
        resp, success, payload = self.set_attribute(node_name, "brightness", brightness)
        return resp, success, payload

    def set_attribute(self, node_name, attribute, target_value):
        """ Set the given node attribute target_value

            PUT /omnia/nodes/{node_id}
            payload = {"nodes":[{"attributes": {"attributeId":{"target_value":target_value}}}]}

        """
        resp, success, node_id = self.get_node_id(node_name)
        payload = None
        if success:
            payload = json.dumps({"nodes":[{
                "attributes":{attribute:{"target_value":target_value}}
                }]})

            url = self.api_url + '/omnia/nodes/{}'.format(node_id)
            resp = requests.put(url, headers=self.headers, data=payload)
            if resp.status_code == 200:
                success = True
        return resp, success, payload

if __name__ == "__main__":
    SESSION = SessionObject(api_config.USERNAME, api_config.PASSWORD, api_config.URL)
    print(SESSION.set_state("Luca Plug", False))
    print(SESSION.set_brightness('Sitt Colour', 20))
