import requests
from random import randrange
from token_other import vk_token_soc as token_soc
from vk_api import get_user_first_name, user_search, top_three_v2, data_constructor


def chat_listener(token: str = token_soc):
    '''
    Принимает на вход токен, печатает то что пишут в чате
    '''
    url = 'https://api.vk.com/method/messages.getLongPollServer'
    data_dict = requests.get(url, params={'access_token': token, 'v': '5.131', 'lp_version': '3'}).json()
    # print(data_dict)
    ts_number = data_dict['response']['ts']
    gender = None
    off = 0

    while True:

        url_lp = f"https://{data_dict['response']['server']}?act=a_check&" \
                 f"key={data_dict['response']['key']}&" \
                 f"ts={ts_number}&wait=60&mode=2&version=3"
        resp2 = requests.get(url_lp).json()
        print(resp2)

        if resp2.get('updates'):

            for event_list in resp2['updates']:

                if event_list[0] == 4 and event_list[5].lower() in ['найди пару', 'пару', 'подругу']:
                    chat_sender(chat_id=event_list[3], mesaga=f"{get_user_first_name(user=event_list[6]['from'])} "
                                                           f"укажи пол, возраст и город как показано в образце:\n"
                                                           f"Пол: ж\nВозраст: 27\nГород: Томск")

                elif event_list[0] == 4 and event_list[5].startswith('Пол:'):
                    chat_sender(chat_id=event_list[3], mesaga=f"Будет исполнено {get_user_first_name(user=event_list[6]['from'])}!")
                    answer = event_list[5].split('<br>')
                    print(answer)

                    if answer[0][-1] == 'ж':
                        gender = 1
                    elif answer[0][-1] == 'м':
                        gender = 2
                    else:
                        gender = 1

                    persons = top_three_v2(data_constructor(user_search(age=answer[1][-2:], city=answer[2][7:], sex=gender)))
                    # print(persons)
                    for user_id, person in persons.items():
                        # print(person)
                        message1 = f"Профиль: https://vk.com/id{user_id}"
                        chat_sender(mesaga=message1)
                        for pers in person:
                            chat_sender(mesaga=f"{pers['f_name']} {pers['l_name']}\n",
                                        attach=f"photo{user_id}_{pers['photo_id']}")

                elif event_list[0] == 4 and event_list[5].lower() in ['ещё', 'дальше', 'следующая', 'следующий']:

                    chat_sender(chat_id=event_list[3], mesaga=f"Ок, поищу!")
                    off += 3
                    persons = top_three_v2(data_constructor(user_search(age=answer[1][-2:],
                                                                        city=answer[2][7:],
                                                                        sex=gender,
                                                                        off_num=off)))
                    # print(persons)

                    if len(persons) > 0:

                        for user_id, person in persons.items():
                            message1 = f"Профиль: https://vk.com/id{user_id}"
                            chat_sender(mesaga=message1)

                            for pers in person:
                                chat_sender(mesaga=f"Фото {pers['f_name']} {pers['l_name']}:\n",
                                            attach=f"photo{user_id}_{pers['photo_id']}")

                    else:
                        chat_sender(chat_id=event_list[3], mesaga=f"Больше нету! :(")



        ts_number = resp2['ts']


def chat_sender(token: str = token_soc, chat_id: str = '2000000001', mesaga: str = 'hello', attach: str = None):
    '''
    Пишет в чат чё то
    '''
    url = 'https://api.vk.com/method/messages.send'
    data_dict = requests.post(url, params={'access_token': token,
                                           'v': '5.131',
                                           'peer_id': chat_id,
                                           'message': mesaga,
                                           'attachment': attach,
                                           'random_id': randrange(10 ** 7)}).json()
    # print(data_dict)


if __name__ == '__main__':
    chat_listener()