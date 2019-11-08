'''
@author: keith

'''
import sys
import json
import requests
import apiConfig

class sessionObject():
    """ Session object class
    """
    def __init__(self, username, password, url):
        self.username = username
        self.password = password
        self.apiUrl = url

        if username == '' or password == '' or url == '':
            print("Username, password and api url must be defined in apiConfig.py")
            sys.exit()

        self.headers = {'Accept':'application/vnd.alertme.zoo-6.3+json',
                        'X-Omnia-Client':'KG',
                        'Content-Type':'application/json'}

        # Login and get userId and sessionId
        url = self.apiUrl + '/omnia/auth/sessions'
        payload=json.dumps({'sessions':[ {'username':username,'password':password}]})
        resp = requests.post(url, data=payload, headers=self.headers)
        self.headers['X-Omnia-Access-Token'] = resp.json()['sessions'][0]['sessionId']

        return
    def getNodeId(self, nodeName):
        """ Get the node ID for a given node name

        """
        success = False
        nodeId = None
        url = self.apiUrl + '/omnia/nodes/'
        resp = requests.get(url, headers = self.headers)
        if resp.status_code == 200:
            for node in resp.json()['nodes']:
                if node['name'] == nodeName:
                    success = True
                    nodeId = node['id']
        return resp, success, nodeId
    def setState(self, nodeName, state):
        """ Modify the state (on/off)
            PUT /omnia/nodes/{nodeId}
            payload = {"nodes":[{"attributes": {"state":{"targetValue":state}}}]}

        """
        if state:
            myState = "ON"
        else:
            myState = "OFF"

        resp, success, payload = self.setAttribute(nodeName, 'state', myState)

        return resp, success, payload
    def setBrightness(self, nodeName, myBrightness):
        """ Modify the brightness 0-100
            PUT /omnia/nodes/{nodeId}
            payload = {"nodes":[{"attributes": {"brightness":{"targetValue":myBrightness}}}]}

        """
        resp, success,payload = self.setAttribute(nodeName, "brightness", myBrightness)
        return resp, success, payload

    def setAttribute(self,nodeName,attribute,targetValue):
        """ Set the given node attribute targetValue

            PUT /omnia/nodes/{nodeId}
            payload = {"nodes":[{"attributes": {"attributeId":{"targetValue":targetValue}}}]}

        """
        resp, success, nodeId = self.getNodeId(nodeName)
        payload = None
        if success:
            payload = json.dumps({"nodes":[{"attributes": {attribute:{"targetValue":targetValue}}}]})
            url = self.apiUrl + '/omnia/nodes/{}'.format(nodeId)
            resp = requests.put(url, headers=self.headers, data=payload)
            if resp.status_code==200: success=True
        return resp, success, payload

if __name__=="__main__":
    SESSION = sessionObject(apiConfig.username, apiConfig.password, apiConfig.url)
    print(SESSION.setState("Luca Plug", False))
    print(SESSION.setBrightness('Sitt Colour', 20))
