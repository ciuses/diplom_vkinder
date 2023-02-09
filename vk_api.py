import time
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
                    # print(mu_list)
                    # print(mu_list[0][-1]) # пол
                    # print(mu_list[1][-2:]) # возраст
                    # print(mu_list[2][7:]) # город
                    print(user_search(mu_list[1][-2:], mu_list[2][7:]))

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
    par = {'access_token': token, 'v': '5.131', 'user_ids': user,
           'fields': 'photo_id, photo_400_orig'}  # 'sex, bdate, city, relation'
    resp = requests.get(url, params=par).json()

    return resp


def get_user_first_name(token: str = token_soc, user: str = '7385081') -> str:
    '''
    Получает id, возвращает Имя.
    '''
    url = 'https://api.vk.com/method/users.get'
    par = {'access_token': token, 'v': '5.131', 'user_ids': user}
    resp = requests.get(url, params=par).json()
    return resp['response'][0]['first_name']


def user_search(age: str, city: str, token: str = vk_token, sex: str = '1') -> list:
    '''
    Ищет пользователей контача по критериям
    'bdate, career, contacts, interests, photo_100, universities'
    '''
    url = 'https://api.vk.com/method/users.search'
    par = {'access_token': token, 'v': '5.131',
           'count': '10',  # 1000
           'hometown': city,
           'sex': sex,  # 1- дев, 2 - муж
           'status': '1',
           'age_from': age,
           'age_to': age,
           'relation': '6',  # 0, 1, 5, 6
           'has_photo': '1'}
    # 'fields': 'photo_100'}

    resp = requests.get(url, params=par).json()
    # print(resp)
    # return resp
    # return [(str_data['id'], str_data['first_name'], str_data['last_name']) for str_data in resp['response']['items']]
    return [str_data['id'] for str_data in resp['response']['items']]


def photo_info(user, token: str = vk_token, album: str = 'profile') -> dict:
    '''
    Функция запоса аватарки
    :param user: юзер айди
    :param token: токен
    :param album: альбом по дифолту, фотки профиля
    :return: джейсона
    '''
    url = 'https://api.vk.com/method/photos.get'
    par = {'access_token': token,
           'v': '5.131',
           'owner_id': user,
           'album_id': album,
           'extended': 1,
           'photo_sizes': 1}  # Фото профиля
    resp = requests.get(url, params=par).json()
    return resp


def data_constructor(my_list: list) -> dict:
    like_comment_photo = {}
    print(len(my_list))

    for id_user in my_list:
        like_comment_photo[id_user] = []
        my_dict = photo_info(id_user)
        # print(my_dict)
        if 'response' in my_dict:
            # print(my_dict['response']['count'])
            # print(id_user)
            for item in my_dict['response']['items']:
                # print(f"likes-{item['likes']['count']} comments-{item['comments']['count']}", item['sizes'][-1]['url'])
                like_comment_photo[id_user].append({'likes': item['likes']['count'],
                                                    'comments': item['comments']['count'],
                                                    'link': item['sizes'][-1]['url']})

            time.sleep(1)

        else:
            print(id_user, 'Профиль запривачен')

    return like_comment_photo


def top_three(any_dict):
    topchik_likes = {}
    topchik_comments = {}

    for user, lk_com_li in any_dict.items():
        # print(user, lk_com_li)
        topchik_likes[user] = []
        topchik_comments[user] = []

        for like_dict in lk_com_li:
            # l.append(like_dict['likes'])
            topchik_likes[user].append(like_dict['likes'])
            topchik_comments[user].append(like_dict['comments'])

        # print(user, max(l), l)
    # print(topchik_likes)
    # print(topchik_likes.values())
    # print(max(topchik_likes.get(138103064)))

    for user, lk_com_li in any_dict.items():
        for like_dict in lk_com_li:
            if like_dict['likes'] == max(topchik_likes.get(user)):

                print(like_dict)

    # for user, lk_com_li in any_dict.items():
    #     for like_dict in lk_com_li:
    #         if like_dict['comments'] == max(topchik_comments.get(user)):

                # print(like_dict)

    # print(topchik_likes)
    # print(topchik_comments)



if __name__ == '__main__':

    '''Чат'''
    # chat_listener()
    # chat_sender(mesaga='Дороу')
    '''Данные юзера'''
    # get_user()
    # print(get_user_first_name())
    '''Поиск юзеров по критериям'''
    # my_d = user_search('20', 'Томск')
    # for dev in my_d['response']['items']:
    #     # print(dev)
    #     print(dev['id'], dev['first_name'], dev['last_name'])
    # for id_fname_lname in my_d:
    #     print(id_fname_lname)
    # for my_id in my_d:
    #     print(get_user(user=my_id))
    #     time.sleep(1)
    '''Данные про фотки'''
    # print(photo_info('240188532'))
    # print(photo_info('779690380'))
    '''Получить структуру данных'''
    # for k, v in data_constructor(user_search('27', 'Томск')).items():
    #     print(k, len(v), v)
    di = data_constructor(user_search('27', 'Томск'))
    top_three(di)




