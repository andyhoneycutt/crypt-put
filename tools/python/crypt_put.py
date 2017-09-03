import requests
import json

class CryptPutClient:

    _url = '';
    _token = '';

    def __init__(self, url, username, password):
        self._url = url
        self._token = self.pullToken(username=username, password=password)

    def getUrl(self, add):
        return "{}{}".format(self._url, add)

    def getToken(self):
        return self._token

    def pullToken(self, username, password):
        url = self.getUrl('api-auth/');

        data = {
          'username': username,
          'password': password
        }

        headers = {
            'Content-type': 'application/json'
        }

        try:
            req = requests.post(url, headers=headers, json=data)
            response_json = json.loads(req.text)
            token = response_json['token']
        except Exception as e:
            print("Could not assign token from {}".format(url))
            token = None
        return token

    def rawRequest(self, data, headers, url, method=requests.post):
        response = method(url, headers=headers, json=data)
        return json.loads(response.text)

    def apiRequest(self, data, url, method=requests.post):
        headers = {
            "Content-type": "application/json",
            "Authorization": "JWT {}".format(self.getToken())
        }
        return self.rawRequest(data=data, headers=headers, url=url, method=method)

    def get(self, uid, decrypt=False):
        data = {'i': uid}
        if decrypt:
            data['d'] = '1'
        return self.apiRequest(data=data, url=self.getUrl('get/'))

    def put(self, data):
        data = {'d': data}
        url = self.getUrl('put/')
        response = self.apiRequest(data=data, url=self.getUrl('put/'))
        uid = response['id']
        return uid


# Test run
if __name__ == '__main__':
    username = ''
    password = ''
    c = CryptPutClient(
        url='http://crypto-put.zpmfhq6y4c.us-west-2.elasticbeanstalk.com/',
        username=username,
        password=password
    )
    uid = c.put(data="here is a secret message")
    data = c.get(uid=uid)
    print(data)
    data = c.get(uid=uid, decrypt=True)
    print(data)
