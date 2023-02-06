import requests
from random import randrange
from token_other import vk_access_token as vk_token
from token_other import vk_user_id as vk_id
from token_other import vk_token_soc as token_soc


def chat_listener(token: str = token_soc):
    '''
    Принимает на вход токен, печатает то что пишут в чате
    '''
    url = 'https://api.vk.com/method/messages.getLongPollServer'
    data_dict = requests.get(url, params={'access_token': token, 'v': '5.131', 'lp_version': '3'}).json()
    # print(data_dict)
    ts_number = data_dict['response']['ts']
    # print(serv, key, ts_number)

    while True:

        url_lp = f"https://{data_dict['response']['server']}?act=a_check&" \
                 f"key={data_dict['response']['key']}&" \
                 f"ts={ts_number}&wait=60&mode=2&version=3"
        resp2 = requests.get(url_lp).json()
        print(resp2)

        if resp2['updates']:

            for my_list in resp2['updates']:

                # if my_list[0] == 4 and my_list[5].lower() in ['найди пару', 'пару', 'подругу']:
                #     chat_sender(chat_id=my_list[3], mesaga=f"{get_user_first_name(user=my_list[6]['from'])} какую тебе?")
                #
                # elif my_list[0] == 4 and my_list[5].lower() in ['красивую']:
                #     chat_sender(chat_id=my_list[3], mesaga=f"{get_user_first_name(user=my_list[6]['from'])} ща буит!")

                if my_list[0] == 4 and my_list[5].lower() in ['найди пару', 'пару', 'подругу']:
                    chat_sender(chat_id=my_list[3], mesaga=f"{get_user_first_name(user=my_list[6]['from'])} "
                                                           f"укажи пол, возраст и город как показано в образце:\n"
                                                           f"Пол: ж\nВозраст: 27\nГород: Томск")

                elif my_list[0] == 4 and my_list[5].startswith('Пол:'):
                    chat_sender(chat_id=my_list[3], mesaga=f"{get_user_first_name(user=my_list[6]['from'])} ща буит!")
                    mu_list = my_list[5].split('<br>')
                    print(mu_list)
                    print(mu_list[0][-1]) # пол
                    print(mu_list[1][-2:]) # возраст
                    print(mu_list[2][7:]) # город




        ts_number = resp2['ts']


def chat_sender(token: str = token_soc, chat_id: str = '2000000001', mesaga: str = 'hello'):
    '''
    Пишет в чат чё то
    '''
    url = 'https://api.vk.com/method/messages.send'
    data_dict = requests.post(url, params={'access_token': token,
                                          'v': '5.131',
                                          'peer_id': chat_id,
                                          'message': mesaga,
                                          'random_id': randrange(10 ** 7)}).json()
    # print(data_dict)

def get_user(token: str = vk_token, user: str = '7385081'):
    '''
    Берёт данные пользака из апи
    sex, bdate, city, relation
    '''
    url = 'https://api.vk.com/method/users.get'
    par = {'access_token': token, 'v': '5.131', 'user_ids': user, 'fields': 'sex, bdate, city, relation'}
    resp = requests.get(url, params=par).json()
    print(resp)
    print('bdate:', resp['response'][0]['bdate'])
    print('city:', resp['response'][0]['city']['title'])
    print('relation:', resp['response'][0]['relation'])
    print('sex:', resp['response'][0]['sex'])

def get_user_first_name(token: str = token_soc, user: str = '7385081') -> str:
    '''
    Получает id, возвращает Имя.
    '''
    url = 'https://api.vk.com/method/users.get'
    par = {'access_token': token, 'v': '5.131', 'user_ids': user}
    resp = requests.get(url, params=par).json()
    return resp['response'][0]['first_name']

def user_search(token: str = vk_token):
    '''
    Ищет пользователей контача по критериям
    '''
    url = 'https://api.vk.com/method/users.search'
    par = {'access_token': token, 'v': '5.131',
           'count': '20',
           'hometown': 'Томск',
           'sex': '1',
           'status': '1',
           'age_from': '18',
           'age_to': '40',
           'has_photo': '1',
           'fields': 'bdate, career, contacts, interests, photo_100, universities'}

    resp = requests.get(url, params=par).json()
    return resp


if __name__ == '__main__':

    chat_listener()
    # chat_sender(mesaga='Дороу')
    # get_user()
    # my_d = user_search()
    # for dev in my_d['response']['items']:
    #     print(dev)
    # print(get_user_first_name())
