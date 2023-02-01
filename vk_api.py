import requests
from token_other import vk_access_token as vk_token
from token_other import vk_user_id as vk_id
from token_other import vk_token_soc as token_soc
#
# class VK:
#
#    def __init__(self, access_token, user_id, version='5.131'):
#        self.token = access_token
#        self.id = user_id
#        self.version = version
#        self.params = {'access_token': self.token, 'v': self.version}
#
#    def users_info(self):
#        url = 'https://api.vk.com/method/users.get'
#        params = {'user_ids': self.id}
#        response = requests.get(url, params={**self.params, **params})
#        return response.json()


# access_token = vk_token
# user_id = vk_id
# vk = VK(access_token, user_id)
# print(vk.users_info())

# url = 'https://api.vk.com/method/users.get'
# par = {'access_token': vk_token, 'user_ids': vk_id, 'v': '5.131'}
# resp = requests.get(url, params=par)
# print(resp, resp.text)

# url = 'https://api.vk.com/method/apps.get'
# par = {'access_token': vk_token, 'v': '5.131', 'app_id': '51499873', 'extended': '1'}
# resp = requests.get(url, params=par)
# print(resp, resp.text)


url = 'https://api.vk.com/method/messages.getLongPollServer'
par = {'access_token': token_soc, 'v': '5.131'}
resp = requests.get(url, params=par)
data_dict = resp.json()['response']
# print(data_dict)

serv = data_dict['server']
key = data_dict['key']
ts_number = data_dict['ts']

# print(serv, key, ts_number)

url_lp = f'https://{serv}?act=a_check&key={key}&ts={ts_number}&wait=30&mode=2&version=2'

resp2 = requests.get(url_lp)
print(resp2, resp2.text)





