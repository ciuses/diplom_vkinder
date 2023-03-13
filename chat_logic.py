import requests
from datetime import date
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from token_other import vk_token_soc as token_soc
from token_other import vk_access_token as user_token
from vk_api_metods import user_search, top_three_v2, data_constructor, base_url, chat_sender, get_user_v2

def chat_listener(token: str = token_soc):
    '''
    Основная функция чат-бота.
    '''
    url = f'{base_url}messages.getLongPollServer'

    try:
        data_dict = requests.get(url, params={'access_token': token, 'v': '5.131', 'lp_version': '3'}).json()
    except ConnectionError as con:
        print('Ошибка соединения с API.', con)
    except Exception as other:
        print(other)

    ts_number = data_dict.get('response').get('ts')
    searcher_id = None
    user_token = None
    answer = None
    gender = None
    row_city = None
    row_age = None
    off = 0
    first = None
    last = None


    while True:

        url_lp = f"https://{data_dict.get('response').get('server')}?act=a_check&" \
                 f"key={data_dict.get('response').get('key')}&" \
                 f"ts={ts_number}&wait=60&mode=2&version=3"
        try:
            response = requests.get(url_lp).json()
        except ConnectionError as con:
            print('Ошибка соединения с API.', con)
            continue
        except Exception as other:
            print(other)
            continue

        print(response)

        if response.get('error'):
            print(f'Код ошибки --> {response.get("error").get("error_code")}, '
                  f'Причина --> {response.get("error").get("error_msg")}')
            continue

        elif response.get('updates'):

            for event_list in response['updates']:

                if event_list[0] == 4 and event_list[5].lower() in ['найди пару', 'пару']:
                    searcher_id = event_list[6]['from']
                    all_user_data = get_user_v2(user=searcher_id)
                    if all_user_data:
                        row_age = str(date.today().year - int(all_user_data['response'][0]['bdate'][-4:]))
                        row_city = all_user_data['response'][0]['city']['title']
                        first = all_user_data['response'][0]['first_name']
                        last = all_user_data['response'][0]['last_name']
                        gender = all_user_data['response'][0]['sex']

                        chat_sender(chat_id=event_list[3], mesaga=f"{first} предоставь мне свой токен для поиска "
                                                                  f"в таком виде\nМой токен: vk1.a.5xxx...x\n")
                    else:
                        print('Что-то пошло не так при получении данных пользователя из API.')
                        continue

                elif event_list[0] == 4 and searcher_id and first and event_list[5].startswith('Мой токен: vk1.a.'):
                    row_user_token = event_list[5]
                    u_token = row_user_token.split()[2]

                    if len(u_token) == 220:
                        user_token = u_token
                        chat_sender(chat_id=event_list[3], mesaga=f"{first} токен принят. Укажи пол, возраст и город "
                                                                  f"как указанов образце:\n\n\n"
                                                                  f"Пол: ж\nВозраст: 27\nГород: Томск\n\n\n"
                                                                  f"Или напиши МНЕ или ДЛЯ МЕНЯ для поиска "
                                                                  f"пары по твоим данным.")
                    else:
                        chat_sender(chat_id=event_list[3], mesaga=f"{first} неверный токен")

                elif event_list[0] == 4 and user_token and event_list[5].startswith('Пол:'):
                    chat_sender(chat_id=event_list[3], mesaga=f"Будет исполнено {first}!")
                    answer = event_list[5].split('<br>')

                    if answer[0][-1] == 'ж':
                        gender = 1
                    elif answer[0][-1] == 'м':
                        gender = 2
                    else:
                        gender = 1

                    row_city = answer[2][7:]
                    row_age = answer[1][-2:]

                    search_results = user_search(age=row_age, city=row_city, sex=gender, token=user_token)
                    if search_results:
                        all_data_dict = data_constructor(search_results, token=user_token, additional_data=(searcher_id, row_city, first, last))
                        persons = top_three_v2(all_data_dict)
                        for user_id, person in persons.items():
                            message1 = f"Профиль: https://vk.com/id{user_id}"
                            chat_sender(chat_id=event_list[3], mesaga=message1)
                            for pers in person:
                                chat_sender(chat_id=event_list[3],
                                            mesaga=f"{pers['f_name']} {pers['l_name']}\n",
                                            attach=f"photo{user_id}_{pers['photo_id']}")

                        chat_sender(chat_id=event_list[3], mesaga=f"Напиши: ещё, еще, дальше, что бы продолжить.")
                    else:
                        print('Что-то пошло не так при поиске кандидатов.')
                        continue

                elif event_list[0] == 4 and user_token and event_list[5].lower() in ['мне', 'для меня']:
                    all_user_data = get_user_v2(user=searcher_id)

                    if all_user_data:
                        row_age = date.today().year - int(all_user_data['response'][0]['bdate'][-4:])
                        row_city = all_user_data['response'][0]['city']['title']
                        first = all_user_data['response'][0]['first_name']
                        last = all_user_data['response'][0]['last_name']
                        gender = all_user_data['response'][0]['sex']

                        if gender == '1':
                            gender = 2
                        else:
                            gender = 1

                        search_results = user_search(age=str(row_age), city=row_city, sex=gender, token=user_token)
                        if search_results:
                            all_data_dict = data_constructor(search_results, token=user_token, additional_data=(searcher_id, row_city, first, last))
                            persons = top_three_v2(all_data_dict)

                            for user_id, person in persons.items():
                                message1 = f"Профиль: https://vk.com/id{user_id}"
                                chat_sender(chat_id=event_list[3], mesaga=message1)
                                for pers in person:
                                    chat_sender(chat_id=event_list[3],
                                                mesaga=f"{pers['f_name']} {pers['l_name']}\n",
                                                attach=f"photo{user_id}_{pers['photo_id']}")
                            chat_sender(chat_id=event_list[3], mesaga=f"Напиши: ещё, еще, дальше, что бы продолжить.")
                        else:
                            print('Что-то пошло не так при поиске кандидатов.')
                            continue

                    else:
                        print('Что-то пошло не так при получении данных пользователя из API.')
                        continue

                elif event_list[0] == 4 and row_city and event_list[5].lower() in ['ещё', 'еще', 'дальше']:

                    chat_sender(chat_id=event_list[3], mesaga=f"Ок, поищу!")
                    off += 3

                    search_results = user_search(age=row_age, city=row_city, sex=gender, off_num=off, token=user_token)

                    if search_results:
                        all_data_dict = data_constructor(search_results, token=user_token, additional_data=(searcher_id, row_city, first, last))
                        persons = top_three_v2(all_data_dict)

                        if persons:

                            for user_id, person in persons.items():
                                message1 = f"Профиль: https://vk.com/id{user_id}"
                                chat_sender(chat_id=event_list[3], mesaga=message1)
                                for pers in person:
                                    chat_sender(chat_id=event_list[3],
                                                mesaga=f"{pers['f_name']} {pers['l_name']}\n",
                                                attach=f"photo{user_id}_{pers['photo_id']}")
                            chat_sender(chat_id=event_list[3], mesaga=f"Напиши: ещё, еще, дальше, что бы продолжить.")

                    else:
                        chat_sender(chat_id=event_list[3], mesaga=f"Больше нету! :(")

            ts_number = response['ts']

        else:
            continue

def main_logic():

    vk = vk_api.VkApi(token=token_soc)
    vk2 = vk_api.VkApi(token=user_token)

    longpoll = VkLongPoll(vk)

    f_name = None
    l_name = None
    chat = None
    gender = None
    city = None
    age = None
    searcher = None
    off = 0

    while True:

        for events in longpoll.listen():
            print(events.type)

            if events.type == VkEventType.MESSAGE_NEW and events.text not in ['мне', 'для меня', 'ещё', 'еще', 'дальше']:
                print(events.text)
                # print(events.chat_id)
                chat = 2000000000 + events.chat_id
                searcher = events.user_id

                user_data = get_user_v2(user=searcher, token=token_soc)

                print(user_data)

                if user_data['response']:
                    f_name, l_name = user_data['response'][0]['first_name'], user_data['response'][0]['last_name']
                    try:
                        gender = 3 - user_data['response'][0]['sex']
                        city = user_data['response'][0]['city']['title']
                        age = date.today().year - int(user_data['response'][0]['bdate'][-4:])
                    except KeyError as key:
                        print(key)
                        chat_sender(token=token_soc, chat_id=chat, mesaga='Мало данных о тебе!')
                        continue
                    except IndexError as index:
                        print(index)
                        chat_sender(token=token_soc, chat_id=chat, mesaga='Мало данных о тебе!')
                        continue

                    print(f_name, l_name, gender, city, age)
                    chat_sender(token=token_soc, chat_id=chat, mesaga=f'Привет {f_name} {l_name}')

                else:
                    continue

            elif events.type == VkEventType.MESSAGE_NEW and events.text in ['мне', 'для меня']:

                chat_sender(token=token_soc, chat_id=chat, mesaga=f'{f_name} пойду искать...')

                if gender and city and age:
                    search_results = user_search(age=str(age), city=city, sex=gender, token=user_token)
                    print(search_results)

                    if search_results:
                        all_data_dict = data_constructor(search_results, token=user_token, additional_data=(searcher, city, f_name, l_name))
                        persons = top_three_v2(all_data_dict)

                        for user_id, person in persons.items():
                            message1 = f"Профиль: https://vk.com/id{user_id}"
                            chat_sender(chat_id=chat, mesaga=message1)
                            for pers in person:
                                chat_sender(chat_id=chat,
                                            mesaga=f"{pers['f_name']} {pers['l_name']}\n",
                                            attach=f"photo{user_id}_{pers['photo_id']}")
                        chat_sender(chat_id=chat, mesaga=f"Напиши: ещё, еще, дальше, что бы продолжить.")
                    else:
                        print('Что-то пошло не так при поиске кандидатов.')
                        continue

                else:
                    continue

            elif events.type == VkEventType.MESSAGE_NEW and events.text in ['ещё', 'еще', 'дальше']:

                chat_sender(chat_id=chat, mesaga=f"Ок, поищу!")
                off += 3

                if gender and city and age:
                    search_results = user_search(age=age, city=city, sex=gender, off_num=off, token=user_token)

                    if search_results:
                        all_data_dict = data_constructor(search_results, token=user_token,
                                                         additional_data=(searcher, city, f_name, l_name))
                        persons = top_three_v2(all_data_dict)

                        if persons:

                            for user_id, person in persons.items():
                                message1 = f"Профиль: https://vk.com/id{user_id}"
                                chat_sender(chat_id=chat, mesaga=message1)
                                for pers in person:
                                    chat_sender(chat_id=chat,
                                                mesaga=f"{pers['f_name']} {pers['l_name']}\n",
                                                attach=f"photo{user_id}_{pers['photo_id']}")
                            chat_sender(chat_id=chat, mesaga=f"Напиши: ещё, еще, дальше, что бы продолжить.")

                    else:
                        chat_sender(chat_id=chat, mesaga=f"Больше нету! :(")
                else:
                    continue

            if events.type == VkEventType.MESSAGE_NEW and events.text.startswith('Пол:'):

                chat_sender(chat_id=chat, mesaga=f"Будет исполнено {f_name}!")
                answer = events.text.split('\n')

                if answer[0][-1] == 'ж':
                    gender = 1
                elif answer[0][-1] == 'м':
                    gender = 2
                else:
                    gender = 1

                city = answer[2][7:]
                age = answer[1][-2:]

                search_results = user_search(age=age, city=city, sex=gender, token=user_token)
                if search_results:
                    all_data_dict = data_constructor(search_results, token=user_token,
                                                     additional_data=(searcher, city, f_name, l_name))
                    persons = top_three_v2(all_data_dict)
                    for user_id, person in persons.items():
                        message1 = f"Профиль: https://vk.com/id{user_id}"
                        chat_sender(chat_id=chat, mesaga=message1)
                        for pers in person:
                            chat_sender(chat_id=chat,
                                        mesaga=f"{pers['f_name']} {pers['l_name']}\n",
                                        attach=f"photo{user_id}_{pers['photo_id']}")

                    chat_sender(chat_id=chat, mesaga=f"Напиши: ещё, еще, дальше, что бы продолжить.")
                else:
                    print('Что-то пошло не так при поиске кандидатов.')
                    continue



if __name__ == '__main__':
    # chat_listener()
    main_logic()