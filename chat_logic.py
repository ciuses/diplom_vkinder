from datetime import date

import requests
from token_other import vk_token_soc as token_soc
from vk_api import get_user_first_name, user_search, top_three_v2, data_constructor, base_url, chat_sender, get_user


def chat_listener(token: str = token_soc):
    '''
    Основная функция чат-бота.
    '''
    url = f'{base_url}messages.getLongPollServer'
    data_dict = requests.get(url, params={'access_token': token, 'v': '5.131', 'lp_version': '3'}).json()
    # print(data_dict)
    ts_number = data_dict['response']['ts']
    searcher_id = None
    answer = None
    gender = None
    row_city = None
    row_city_id = None
    row_age = None
    off = 0
    first = None
    last = None


    while True:

        url_lp = f"https://{data_dict['response']['server']}?act=a_check&" \
                 f"key={data_dict['response']['key']}&" \
                 f"ts={ts_number}&wait=60&mode=2&version=3"
        response = requests.get(url_lp).json()
        print(response)

        if response.get('updates'):

            for event_list in response['updates']:

                if event_list[0] == 4 and event_list[5].lower() in ['найди пару', 'пару', 'подругу']:
                    searcher_id = event_list[6]['from']
                    chat_sender(chat_id=event_list[3],
                                mesaga=f"{get_user_first_name(user=searcher_id)[0]} укажи пол, возраст и город как указано "
                                       f"в образце:\n\n\nПол: ж\nВозраст: 27\nГород: Томск\n\n\n"
                                       f"Или напиши МНЕ или ДЛЯ МЕНЯ для поиска пары по твоим данным.")

                elif event_list[0] == 4 and event_list[5].startswith('Пол:'):
                    searcher_id = event_list[6]['from']
                    chat_sender(chat_id=event_list[3],
                                mesaga=f"Будет исполнено {get_user_first_name(user=searcher_id)[0]}!")

                    answer = event_list[5].split('<br>')
                    print(answer)

                    if answer[0][-1] == 'ж':
                        gender = 1
                    elif answer[0][-1] == 'м':
                        gender = 2
                    else:
                        gender = 1

                    row_city = answer[2][7:]
                    row_age = answer[1][-2:]
                    first, last = get_user_first_name(user=searcher_id)

                    search_results = user_search(age=row_age, city=row_city, sex=gender)
                    all_data_dict = data_constructor(search_results, additional_data=(searcher_id, row_city, first, last))
                    persons = top_three_v2(all_data_dict)

                    # print(persons)
                    if len(persons) > 0:
                        for user_id, person in persons.items():
                            # print(person)
                            message1 = f"Профиль: https://vk.com/id{user_id}"
                            chat_sender(chat_id=event_list[3], mesaga=message1)
                            for pers in person:
                                chat_sender(chat_id=event_list[3],
                                            mesaga=f"{pers['f_name']} {pers['l_name']}\n",
                                            attach=f"photo{user_id}_{pers['photo_id']}")

                elif event_list[0] == 4 and event_list[5].lower() in ['мне', 'для меня']:
                    searcher_id = event_list[6]['from']
                    all_user_data = get_user(searcher_id)
                    print(all_user_data)
                    row_age = date.today().year - int(all_user_data['response'][0]['bdate'][-4:])
                    row_city_id = all_user_data['response'][0]['city']['id']
                    first = all_user_data['response'][0]['first_name']
                    last = all_user_data['response'][0]['last_name']
                    gender = all_user_data['response'][0]['sex']

                    if gender == '1':
                        gender = 2
                    else:
                        gender = 1

                    search_results = user_search(age=str(row_age), city_id=row_city_id, sex=gender)
                    all_data_dict = data_constructor(search_results, additional_data=(searcher_id, row_city_id, first, last))
                    persons = top_three_v2(all_data_dict)

                    if len(persons) > 0:
                        for user_id, person in persons.items():
                            # print(person)
                            message1 = f"Профиль: https://vk.com/id{user_id}"
                            chat_sender(chat_id=event_list[3], mesaga=message1)
                            for pers in person:
                                chat_sender(chat_id=event_list[3],
                                            mesaga=f"{pers['f_name']} {pers['l_name']}\n",
                                            attach=f"photo{user_id}_{pers['photo_id']}")

                elif event_list[0] == 4 and event_list[5].lower() in ['ещё', 'еще', 'дальше', 'следующая', 'следующий']:

                    chat_sender(chat_id=event_list[3], mesaga=f"Ок, поищу!")
                    off += 3

                    if row_city:

                        search_results = user_search(age=row_age, city=row_city, sex=gender, off_num=off)

                        if search_results:
                            all_data_dict = data_constructor(search_results, additional_data=(searcher_id, row_city, first, last))
                            persons = top_three_v2(all_data_dict)

                            if len(persons) > 0:
                                for user_id, person in persons.items():
                                    message1 = f"Профиль: https://vk.com/id{user_id}"
                                    chat_sender(chat_id=event_list[3], mesaga=message1)
                                    for pers in person:
                                        chat_sender(chat_id=event_list[3],
                                                    mesaga=f"{pers['f_name']} {pers['l_name']}\n",
                                                    attach=f"photo{user_id}_{pers['photo_id']}")

                    elif row_city_id:

                        search_results = user_search(age=row_age, city_id=row_city_id, sex=gender, off_num=off)

                        if search_results:
                            all_data_dict = data_constructor(search_results,
                                                             additional_data=(searcher_id, row_city_id, first, last))
                            persons = top_three_v2(all_data_dict)

                            if len(persons) > 0:
                                for user_id, person in persons.items():
                                    message1 = f"Профиль: https://vk.com/id{user_id}"
                                    chat_sender(chat_id=event_list[3], mesaga=message1)
                                    for pers in person:
                                        chat_sender(chat_id=event_list[3],
                                                    mesaga=f"{pers['f_name']} {pers['l_name']}\n",
                                                    attach=f"photo{user_id}_{pers['photo_id']}")


                    else:
                        chat_sender(chat_id=event_list[3], mesaga=f"Больше нету! :(")


        ts_number = response['ts']




if __name__ == '__main__':
    chat_listener()