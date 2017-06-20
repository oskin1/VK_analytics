import json
from time import sleep
import vk

ACC_TOKEN = 'xxxxxxx-vk_access_token-xxxxxxxxx'
VER = '5.64'

TASK_IDS = {
    'Статистика по подписчикам группы': 1,
    'Получить диалоги вк': 2
}

STOP_WORDS = [
    'стопслово1',
    'стопслово2',
]


def dump_to_file(data, ext='json'):
    name = input('Введите имя файла: ')
    with open('results/{}.{}'.format(name, ext), 'w', encoding='utf8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def get_msg_history(api):
    msgs_set = []

    uid = int(input('Введите id пользователя: '))
    count = int(input('Кол-во сообщений: '))
    loops = int(input('Кол-во итераций: '))
    offset = int(input('Смещение: '))

    i = 0

    print('Ок! Начинаю сбор сообщений..')

    while i <= loops:
        msgs = api.messages.getHistory(user_id=uid,
                                       count=count,
                                       offset=offset,
                                       rev=1)['items']
        pack = []
        pre_pack = []
        toggle = int(msgs[0]['out'])

        for msg in msgs:
            if len(msg['body']) > 0 and len(msg['body']) < 66:
                if msg['body'] not in STOP_WORDS:
                    if int(msg['out']) == toggle:
                        pre_pack.append(msg['body'])
                    else:
                        pack.append(pre_pack)
                        pre_pack.clear()
                        toggle = int(msg['out'])

        msgs_set.append(pack)
        print(pack)

        i += 1
        offset += count

        sleep(0.4)

    print('Запись в файл..')

    dump_to_file(msgs_set)


def get_group_stats(api):
    group_id = input('Введите идентификатор анализируемой группы: ')
    count = int(input('Введите кол-во подписчиков для анализа: '))
    members = api.groups.getMembers(group_id=group_id,
                                    fields='sex, city',
                                    count=count)
    uids = [user['id'] for user in members['items']]

    print('Выбранные пользователи:')
    print(uids)

    group_list = []
    results = []
    srtd = []

    print('Начинаю собирать список групп..')

    for uid in uids:
        try:
            groups = api.groups.get(user_id=uid, extended=1, count=200)
        except vk.exceptions.VkAPIError:
            print('API error.. pass')
        else:
            try:
                items = groups['items']
            except KeyError:
                print('Key error.. pass')
            else:
                for item in items:
                    group = item['name']
                    group_list.append(group)
                    print(group)

        sleep(0.4)

    print('Начинаю считать..')

    for group in group_list:
        if group not in srtd:
            c = group_list.count(group)
            srtd.append(group)
            if c > 5:
                p = round((c/480)*100, 2)
                results.append(group + ' : ' + str(c) + '  /- ' + str(p) + '%')

    print('Начинаю запись..')
    print('Готово!')

    dump_to_file(results)


def main():
    session = vk.Session(access_token=ACC_TOKEN)
    api = vk.API(session, v=VER, lang='ru')

    task_id = int(input('Введите id задачи: '))

    if task_id is 1:
        get_group_stats(api)
    elif task_id is 2:
        get_msg_history(api)

if __name__ == '__main__':
    main()
