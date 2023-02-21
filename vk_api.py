import time
import requests
from random import randrange
from token_other import vk_access_token as vk_token
from token_other import vk_token_soc as token_soc
from operator import itemgetter
from db_models import my_session, Black_List, Users, Photos, Requester

base_url = 'https://api.vk.com/method/'

def get_user_v2(user: str = '7385081', token: str = token_soc) -> dict:
    '''
    Получает данные юзера по токену.
    :param user: user_id из ВК
    :param token: токен юзера
    :return: данные пользователя
    '''
    par = {'access_token': token, 'v': '5.131', 'user_ids': user, 'fields': 'bdate, city, sex'}

    try:
        resp = requests.get(f'{base_url}users.get', params=par).json()
    except ConnectionError as con:
        print('Ошибка соединения с API.', con)
    except Exception as other:
        print(other)

    if resp.get('error'):
        print(f'Код ошибки --> {resp.get("error").get("error_code")}, '
              f'Причина --> {resp.get("error").get("error_msg")}')
        return False

    return resp


# def get_user_first_name(token: str = token_soc, user: str = '7385081') -> tuple:
#     '''
#     Получает id, возвращает Имя.
#     :param token: токен бота
#     :param user: user_id из ВК
#     :return: Имя и Фамилию
#     '''
#     par = {'access_token': token, 'v': '5.131', 'user_ids': user, 'fields': 'bdate, city, sex'}
#     resp = requests.get(f'{base_url}users.get', params=par).json()
#     # return resp
#     return resp['response'][0]['first_name'], resp['response'][0]['last_name']


def user_search(age: str, city: str = None, token: str = vk_token, sex: int = 1, off_num: int = None, city_id: int = None):
    '''
    Ищет пользователей контача по критериям
    :param age: Возраст
    :param city: Город
    :param token: токен юзера
    :param sex: пол
    :param off_num: оффсет
    :param city_id: город айди
    :return: либо 2 списка в тьюпле либо фолз
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

    try:
        resp = requests.get(f'{base_url}users.search', params=par).json()
    except ConnectionError as con:
        print('Ошибка соединения с API.', con)
    except Exception as other:
        print(other)

    if resp.get('error'):
        print(f'Код ошибки --> {resp.get("error").get("error_code")}, '
              f'Причина --> {resp.get("error").get("error_msg")}')
        return False

    elif resp.get('response') and len(resp.get('response').get('items')) > 0:

        list_of_tupls = [(str_data['id'], str_data['first_name'], str_data['last_name'])
                         for str_data in resp['response']['items']
                         if str_data['can_access_closed']]

        black_list = [str_data['id']
                      for str_data in resp['response']['items']
                      if str_data['can_access_closed'] == False]

        return list_of_tupls, black_list

    else:
        return False


def photo_info(user, token: str = None, album: str = 'profile'):
    '''
    Функция запоса аватарки
    :param user: юзер айди
    :param token: токен
    :param album: альбом по дифолту, фотки профиля
    :return: словарь данных с лайками, коментами и прочим
    '''
    par = {'access_token': token,
           'v': '5.131',
           'owner_id': user,
           'album_id': album,
           'extended': 1,
           'photo_sizes': 1}
    try:
        resp = requests.get(f'{base_url}photos.get', params=par).json()
    except ConnectionError as con:
        print('Ошибка соединения с API.', con)
    except Exception as other:
        print(other)

    # print(resp)
    if resp.get('error'):
        print(f'Код ошибки --> {resp.get("error").get("error_code")}, '
              f'Причина --> {resp.get("error").get("error_msg")}')
        return False

    elif resp.get('response') and len(resp.get('response').get('items')) > 0:
        return resp


def data_constructor(w_list_b_list_tupl: tuple, token: str = None, additional_data=None):
    '''
    Основная функция построения даннх по пользователю.
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
            response_dict = photo_info(user_id, token=token)
            if response_dict:
                like_comment_photo[user_id] = []

                for item in response_dict.get('response').get('items'):
                    like_comment_photo[user_id].append({'likes': item['likes']['count'],
                                                        'comments': item['comments']['count'],
                                                        'f_name': f_name,
                                                        'l_name': l_name,
                                                        'photo_id': item['id'],
                                                        'link': item['sizes'][-1]['url']})

                time.sleep(0.5)

            else:
                print(f'Ничего нет у этого юзера {user_id}')
                time.sleep(0.5)
                continue

        db_writer(black_list=w_list_b_list_tupl[1], main_dict=like_comment_photo, add_searcher_data=additional_data)
        # print(like_comment_photo)
        return like_comment_photo

    else:
        print('Нет списка юзеров.')

def top_three_v2(my_struct_dict: dict) -> dict:
    '''
    Функция сортировки фоток по критериям.
    :param my_struct_dict: словарь данных как в data_constructor()
    :return: список тьюплов вида (346034388, {'likes': 4, 'comments': 0, 'link': 'https://}),
                                (107342491, {'likes': 982, 'comments': 3, 'link': 'https://})
    '''
    if my_struct_dict:
        top_dict = {}
        for user_id, lk_com_li in my_struct_dict.items():
            sorted_list_of_dicts = sorted(lk_com_li, key=itemgetter('likes'), reverse=True)

            if len(sorted_list_of_dicts) > 3:
                top_dict[user_id] = sorted_list_of_dicts[:3]
            else:
                top_dict[user_id] = sorted_list_of_dicts

        return top_dict

    else:
        print(my_struct_dict)


def db_writer(main_dict=None, black_list=None, add_searcher_data=None):
    '''
    Просто пишет данные в базу.
    :param main_dict: Словарь данных из data_constructor
    :param black_list: Список айдишников пользователя
    :param add_searcher_data: Доп данные по юзеру, город, имя, фамилия.
    '''

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
    Функция отправки всякого в чат.
    :param token: токен бота
    :param chat_id: айди чата
    :param mesaga: сообщение
    :param attach: приложение к сообщению
    '''
    par = {'access_token': token,
           'v': '5.131',
           'peer_id': chat_id,
           'message': mesaga,
           'attachment': attach,
           'random_id': randrange(10 ** 7)}
    try:
        requests.post(f'{base_url}messages.send', params=par).json()
    except ConnectionError as con:
        print('Ошибка соединения с API.', con)
    except Exception as other:
        print(other)

# if __name__ == '__main__':
    # print(get_user_first_name(user='610757410'))
    # print(get_user_v2(user='610757410', token=token_soc))
    # print(get_user_v2(user='190925331', token=token_soc))
    # print(photo_info(user=50465142, token=vk_token))