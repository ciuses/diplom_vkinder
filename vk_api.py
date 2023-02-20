import time
import requests
from random import randrange
from token_other import vk_access_token as vk_token
from token_other import vk_token_soc as token_soc
from operator import itemgetter
from db_models import my_session, Black_List, Users, Photos, Requester

base_url = 'https://api.vk.com/method/'

def get_user_v2(user: str = '7385081', token: str = vk_token):
    '''
    Получает данные юзера по бирер токена.
    '''
    par = {'access_token': token, 'v': '5.131', 'user_ids': user, 'fields': 'bdate, city, sex'}
    resp = requests.get(f'{base_url}users.get', params=par).json()
    return resp


def get_user_first_name(token: str = token_soc, user: str = '7385081') -> tuple:
    '''
    Получает id, возвращает Имя.
    '''
    par = {'access_token': token, 'v': '5.131', 'user_ids': user, 'fields': 'bdate, city, sex'}
    resp = requests.get(f'{base_url}users.get', params=par).json()
    # print(resp)
    return resp['response'][0]['first_name'], resp['response'][0]['last_name']


def user_search(age: str, city: str = None, token: str = vk_token, sex: int = 1, off_num: int = None, city_id: int = None):
    '''
    Ищет пользователей контача по критериям
    'bdate, career, contacts, interests, photo_100, universities'
    '''
    par = {'access_token': token,
           'v': '5.131',
           'count': '3',  # 1000
           'offset': off_num,
           'hometown': city,
           'sex': sex,  # 1- дев, 2 - муж
           'status': '1',
           'age_from': age,
           'age_to': age,
           'city_id': city_id,
           'relation': '6',  # 0, 1, 5, 6
           'has_photo': '1'}

    resp = requests.get(f'{base_url}users.search', params=par).json()
    print(resp)
    if resp.get('response') and len(resp.get('response').get('items')) > 0:

        list_of_tupls = [(str_data['id'], str_data['first_name'], str_data['last_name'])
                         for str_data in resp['response']['items']
                         if str_data['can_access_closed']]

        black_list = [str_data['id']
                      for str_data in resp['response']['items']
                      if str_data['can_access_closed'] == False]

        return list_of_tupls, black_list

    else:
        return False


def photo_info(user, token: str = vk_token, album: str = 'profile') -> dict:
    '''
    Функция запоса аватарки
    :param user: юзер айди
    :param token: токен
    :param album: альбом по дифолту, фотки профиля
    :return: джейсона
    '''
    par = {'access_token': token,
           'v': '5.131',
           'owner_id': user,
           'album_id': album,
           'extended': 1,
           'photo_sizes': 1}
    resp = requests.get(f'{base_url}photos.get', params=par).json()
    # print(user, resp)

    if resp.get('response') and len(resp.get('response').get('items')) > 0:
        return resp

    # else:
    #     print(user, resp)


def data_constructor(w_list_b_list_tupl: tuple, additional_data=None) -> dict:
    '''
    :param w_list_b_list_tupl: [606233587, 44151122, 138103064]
    :return: {180015464: [{'likes': 18,
                            'comments': 0,
                            'f_name': 'Лидия',
                            'l_name': 'Абрамова',
                            'photo_id': 286935869,
                            'link': 'https://'}],
                506039351: [{'likes': 56,
                            'comments': 0,
                            'f_name': 'Лиза',
                            'l_name': 'Колесникова',
                            'photo_id': 456239032,
                            'link': 'https://'}],
                299467993: [{'likes': 2,
                            'comments': 0,
                            'f_name': 'Поля',
                            'l_name': 'Гора',
                            'photo_id': 417859251,
                            'link': 'https://'}]}
    '''
    like_comment_photo = {}
    if w_list_b_list_tupl:

        for user_id, f_name, l_name in w_list_b_list_tupl[0]:
            response_dict = photo_info(user_id)
            like_comment_photo[user_id] = []

            for item in response_dict['response']['items']:
                like_comment_photo[user_id].append({'likes': item['likes']['count'],
                                                    'comments': item['comments']['count'],
                                                    'f_name': f_name,
                                                    'l_name': l_name,
                                                    'photo_id': item['id'],
                                                    'link': item['sizes'][-1]['url']})


            time.sleep(0.5)


        db_writer(black_list=w_list_b_list_tupl[1], main_dict=like_comment_photo, add_searcher_data=additional_data)
        return like_comment_photo


def top_three_v2(my_struct_dict: dict) -> dict:
    '''
    :param my_struct_dict: словарь данных как в data_constructor()
    :return: список тьюплов вида (346034388, {'likes': 4, 'comments': 0, 'link': 'https://}),
                                (107342491, {'likes': 982, 'comments': 3, 'link': 'https://})
    '''
    top_dict = {}
    for user_id, lk_com_li in my_struct_dict.items():
        # print(user_id, lk_com_li)
        sorted_list_of_dicts = sorted(lk_com_li, key=itemgetter('likes'), reverse=True)
        # print(len(sorted_list_of_dicts), sorted_list_of_dicts)
        if len(sorted_list_of_dicts) > 3:
            top_dict[user_id] = sorted_list_of_dicts[:3]
        else:
            top_dict[user_id] = sorted_list_of_dicts

    return top_dict


def db_writer(main_dict=None, black_list=None, add_searcher_data=None):

    searcher_id = None
    criterion_city = None
    first = None
    last = None

    if add_searcher_data:
        searcher_id = add_searcher_data[0]
        first = add_searcher_data[2]
        last = add_searcher_data[3]
        criterion_city = add_searcher_data[1]



    if main_dict:
        any_requester = Requester(requester_id=searcher_id, f_name=first, l_name=last)
        my_session.add(any_requester)
        my_session.commit()

        for u_id, photos in main_dict.items():

            any_user = Users(requ_id=any_requester.id,
                             user_id=u_id,
                             f_name=photos[0]['f_name'],
                             l_name=photos[0]['l_name'],
                             city=criterion_city)
            my_session.add(any_user)
            my_session.commit()

            for photo in photos:

                any_photo = Photos(use_id=any_user.id,
                                   photo_id=photo['photo_id'],
                                   likes=photo['likes'],
                                   comments=photo['comments'],
                                   link=photo['link'])
                my_session.add(any_photo)
                my_session.commit()

    if black_list:
        for user_id in black_list:
            my_session.add(Black_List(user_id=user_id))
            my_session.commit()


def chat_sender(token: str = token_soc, chat_id: str = '2000000001', mesaga: str = 'hello', attach: str = None):
    '''
    Пишет в чат чё то
    '''
    par = {'access_token': token,
           'v': '5.131',
           'peer_id': chat_id,
           'message': mesaga,
           'attachment': attach,
           'random_id': randrange(10 ** 7)}
    requests.post(f'{base_url}messages.send', params=par).json()



if __name__ == '__main__':

    '''Чат'''
    # chat_listener()
    # chat_sender(mesaga='Дороу')
    '''Данные юзера'''
    # print(get_user())
    print(get_user_v2(user='93600308'))
    # print(get_user(user='111189286'))
    # print(get_user(user='763845157'))
    # print(photo_info('93600308'))
    # print(get_user_first_name())
    # print(sieve(['346034388', '107342491', '65515441', '134989778', '136412187', '473433452']))
    '''Поиск юзеров по критериям'''
    # my_d = user_search('20', 'Томск')
    # for row in my_d['response']['items']:
    #     print(row)
    # for row in my_d:
    #     print(row)
    # for dev in my_d['response']['items']:
    #     print(dev)
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

    # for tu in top_three_v2(data_constructor(sieve(user_search('28', 'Томск')))):  # можно срезать 3 первых - [:3]
    #     print(tu)
    # top_three_v2(data_constructor(user_search('27', 'Кемерово')))

    # print(data_constructor(user_search('20', 'Томск')))
    # for k, v in data_constructor(user_search('20', 'Томск')).items():
    #     print(k, len(v), v)

    '''Сортировка'''
    # top_three_v2(data_constructor(user_search('20', 'Томск')))
    # for k, v in top_three_v2(data_constructor(user_search('20', 'Новосибирск'))).items():
    #     print(k, len(v), v)

    # off = 3
    # while top_three_v2(data_constructor(user_search('20', 'Новосибирск', off_num=off))):
    #     for k, v in top_three_v2(data_constructor(user_search('20', 'Новосибирск', off_num=off))).items():
    #         print(k, len(v), v)
    #     off += 3
    #     print(off)
    #     time.sleep(0.5)

    '''дебаг '''
    # for u_id in user_search('34', 'Томск'):
    #     print(photo_info(u_id))
    #     time.sleep(1)
