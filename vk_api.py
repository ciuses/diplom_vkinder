import time
import requests
from random import randrange
from token_other import vk_access_token as vk_token
from token_other import bearer_token as b_token
from token_other import vk_user_id as vk_id
from token_other import vk_token_soc as token_soc
from operator import itemgetter


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


def get_user(user: str = '7385081'):
    '''

    '''
    url = 'https://api.vk.com/method/users.get'
    head = {'Authorization': f'Bearer {b_token}'}
    par = {'v': '5.131', 'user_ids': user, 'fields': 'bdate'}
    resp = requests.get(url, params=par, headers=head).json()

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
           'count': '1000',  # 1000
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
    # print(user, resp)

    if resp.get('response') and len(resp.get('response').get('items')) > 0:
        return resp
    # elif resp.get('error'):
    #     print(resp.get('error').get('error_msg'))
    # return {user: resp.get('error').get('error_msg')}
    # else:
    #     print(user, resp)


def data_constructor(list_of_user_id: list) -> dict:
    '''
    :param list_of_user_id: [606233587, 44151122, 138103064]
    :return:
    {606233587: [{'likes': 93, 'comments': 3, 'link': 'https://'}],
    44151122: [{'likes': 133, 'comments': 3, 'link': 'https://'},
                {'likes': 153, 'comments': 1, 'link': 'https://'}],
    138103064: [{'likes': 84, 'comments': 0, 'link': 'https://'}]}
    '''
    like_comment_photo = {}

    for user_id in list_of_user_id:
        response_dict = photo_info(user_id)
        # print(id_user, my_dict)

        if response_dict:
            like_comment_photo[user_id] = []
            for item in response_dict['response']['items']:
                like_comment_photo[user_id].append({'likes': item['likes']['count'],
                                                    'comments': item['comments']['count'],
                                                    'link': item['sizes'][-1]['url']})

        # else:
        #     print(id_user, my_dict)

        time.sleep(0.5)

    return like_comment_photo


def top_three(any_dict):
    topchik_likes = {}  # нужны для определения самой залайканой фотки
    topchik_comments = {}  # нужны для определения самой закоменчиной фотки

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
                # print(f'У юзера {user} сумма лайков -> {sum(topchik_likes.get(user))}')
                print(user, like_dict)

    # for user, lk_com_li in any_dict.items():
    #     for like_dict in lk_com_li:
    #         if like_dict['comments'] == max(topchik_comments.get(user)):

    # print(like_dict)
    # print(topchik_likes)
    # print(topchik_comments)


def top_three_v2(my_struct_dict: dict):
    '''
    :param my_struct_dict: словарь данных как в data_constructor()
    :return: список тьюплов вида (346034388, {'likes': 4, 'comments': 0, 'link': 'https://}),
                                (107342491, {'likes': 982, 'comments': 3, 'link': 'https://})
    '''
    top_dict = {}
    sorter_top_dict = {}
    for user_id, lk_com_li in my_struct_dict.items():
        # print(user_id, lk_com_li)
        sorted_list_of_dicts = sorted(lk_com_li, key=itemgetter('likes'))
        top_dict[user_id] = sorted_list_of_dicts[-1]

    list_of_tuples = sorted(top_dict.items(), key=lambda like: like[1].get('likes'), reverse=True)

    return list_of_tuples


def sieve(list_of_user_id: list, token: str = vk_token) -> list:
    '''
    Чистит список юрез айди от приватных.
    :param list_of_user_id: список юзеров
    :return: чистый список
    '''
    clean_user_id = []
    dirty_user_id = []

    for user_id in list_of_user_id:
        url = 'https://api.vk.com/method/users.get'
        par = {'access_token': token, 'v': '5.131', 'user_ids': user_id}
        resp = requests.get(url, params=par).json()
        # print(resp)
        # print(user_id, resp.get('response')[0].get('can_access_closed'))

        if resp.get('response')[0].get('can_access_closed'):
            clean_user_id.append(user_id)
        else:
            dirty_user_id.append(user_id)
        time.sleep(0.5)

    # print(len(clean_user_id), clean_user_id)
    # print(len(dirty_user_id), dirty_user_id)
    return clean_user_id


if __name__ == '__main__':

    '''Чат'''
    # chat_listener()
    # chat_sender(mesaga='Дороу')
    '''Данные юзера'''
    # print(get_user(user='93600308'))
    # print(get_user(user='111189286'))
    # print(get_user(user='763845157'))
    # print(photo_info('93600308'))
    # print(get_user_first_name('93600308'))
    # print(sieve(['346034388', '107342491', '65515441', '134989778', '136412187', '473433452']))
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
    # print(get_user(user='65515441'))
    # print(photo_info('65515441'))
    '''Получить структуру данных'''
    # print(data_constructor(user_search('27', 'Томск')))
    # for k, v in data_constructor(user_search('23', 'Томск')).items():
    #     print(k, len(v), v)
    # di = data_constructor(user_search('27', 'Томск'))
    # top_three(di)
    # print('#' * 120)
    # print(top_three_v2(data_constructor(user_search('23', 'Томск'))))
    # for u_id, m_di in top_three_v2(data_constructor(user_search('20', 'Томск'))).items():
    #     print(u_id, m_di)

    for tu in top_three_v2(data_constructor(sieve(user_search('28', 'Томск')))):  # можно срезать 3 первых - [:3]
        print(tu)
    # top_three_v2(data_constructor(user_search('27', 'Кемерово')))

    '''дебаг '''
    # for u_id in user_search('34', 'Томск'):
    #     print(photo_info(u_id))
    #     time.sleep(1)
