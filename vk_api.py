import requests
from token_other import vk_access_token as vk_token
from token_other import vk_user_id as vk_id
from token_other import vk_token_soc as token_soc


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
#
#
# access_token = vk_token
# user_id = vk_id
# vk = VK(access_token, user_id)
# print(vk.users_info())

# url = 'https://api.vk.com/method/users.get'
# par = {'access_token': token_soc, 'user_ids': vk_id, 'v': '5.131'}
# resp = requests.get(url, params=par)
# print(resp, resp.text)

# url = 'https://api.vk.com/method/apps.get'
# par = {'access_token': vk_token, 'v': '5.131', 'app_id': '51499873', 'extended': '1'}
# resp = requests.get(url, params=par)
# print(resp, resp.text)

def chat_listener(token: str = token_soc):
    '''
    Принимает на вход токен, печатает то что пишут в чате
    '''
    url = 'https://api.vk.com/method/messages.getLongPollServer'
    data_dict = requests.get(url, params={'access_token': token, 'v': '5.131'}).json()
    # print(data_dict)
    serv = data_dict['response']['server']
    key = data_dict['response']['key']
    ts_number = data_dict['response']['ts']
    # print(serv, key, ts_number)

    while True:

        url_lp = f'https://{serv}?act=a_check&key={key}&ts={ts_number}&wait=90&mode=2&version=2'
        resp2 = requests.get(url_lp).json()
        udp = resp2['updates']
        if udp and udp[0][0] == 4:  # 4 - событие текст
            # print(udp[0]) # [4, 18, 532481, 2000000001, 1675240870, 'sjtjtjtajtajt', {'from': '7385081'}]
            print(udp[0][5])
            print(udp[0][6]['from'])

        ts_number = resp2['ts']


if __name__ == '__main__':

    chat_listener()