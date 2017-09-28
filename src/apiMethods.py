'''
@author: keith



'''
import json
import requests
import apiConfig

class sessionObject(object):
    def __init__(self,username,password,url):
        self.username=username
        self.password=password
        self.apiUrl=url
        
        if username == '' or password=='' or url=='':
            print("Username, password and api url must be defined in apiConfig.py")
            exit()
        
        self.headers={'Accept':'application/vnd.alertme.zoo-6.3+json',
                      'X-Omnia-Client':'KG',
                      'Content-Type':'application/json'}
        
        # Login and get userId and sessionId
        url=self.apiUrl+'/omnia/auth/sessions'
        payload=json.dumps({'sessions':[ {'username':username,'password':password}]})
        r = requests.post(url, data=payload, headers=self.headers)
        self.headers['X-Omnia-Access-Token']=r.json()['sessions'][0]['sessionId']
        
        return
    def getNodeId(self,nodeName):
        """ Get the node ID for a given node name
        
        """
        success = False
        nodeId = None
        url = self.apiUrl + '/omnia/nodes/'
        r = requests.get(url, headers = self.headers)
        if r.status_code == 200:
            for n in r.json()['nodes']:
                if n['name'] == nodeName:
                    success = True
                    nodeId = n['id']
        return r,success,nodeId
    def setState(self,nodeName,state):
        """ Modify the state (on/off)
            PUT /omnia/nodes/{nodeId}
            payload = {"nodes":[{"attributes": {"state":{"targetValue":state}}}]}
        
        """
        if state==True:
            myState="ON"
        else:
            myState="OFF"
        
        r,success,payload=self.setAttribute(nodeName,'state',myState)

        return r,success,payload
    def setBrightness(self,nodeName,myBrightness):
        """ Modify the brightness 0-100
            PUT /omnia/nodes/{nodeId}
            payload = {"nodes":[{"attributes": {"brightness":{"targetValue":myBrightness}}}]}
        
        """    
        r,success,payload=self.setAttribute(nodeName,"brightness",myBrightness)
        return r,success,payload

    def setAttribute(self,nodeName,attribute,targetValue):
        """ Set the given node attribute targetValue
        
            PUT /omnia/nodes/{nodeId}
            payload = {"nodes":[{"attributes": {"attributeId":{"targetValue":targetValue}}}]}
        
        """
        r,success,nodeId = self.getNodeId(nodeName)
        payload=None
        if success:
            payload=json.dumps({"nodes":[{"attributes": {attribute:{"targetValue":targetValue}}}]})
            url = self.apiUrl + '/omnia/nodes/{}'.format(nodeId)
            r = requests.put(url, headers=self.headers,data=payload)
            if r.status_code==200: success=True
        return r,success,payload

if __name__=="__main__":
    username=apiConfig.username
    password=apiConfig.password
    url=apiConfig.url
    
    session=sessionObject(username,password,url)
    print(session.setState("Luca Plug", False))
    print(session.setBrightness('Sitt Colour', 20))
