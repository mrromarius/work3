import logging
import grpc

import sn_pb2_grpc
import sn_pb2

    # with grpc.insecure_channel('localhost:50505') as channel:
    #     stub = sn_pb2_grpc.SocNetStub(channel)
    #     response = stub.Do(sn_pb2.Request(message=send_serv))
def commands(command):
    if command == "rq":
        # команда на переворот строки
        strres = input('Введите строку:')
        response = stub.Do(sn_pb2.Request(message=strres))
        print(response.message)
    elif command == "ul":
        # команда на список пользователей
        response = stub.UserList(sn_pb2.Request(message=''))
        print(response.message)
    elif command == "ls":
        # команда на просмотр ленты пользователя
        global userName
        userName = input("Укажите ленту какого пользователя хотите просмотреть: ")
        response = stub.UserLenta(sn_pb2.Request(message=userName))
        global ids
        ids = response.idpost.split(',')
        print(response.message)
    elif command == "lp":
        # команда на лайк поста
        if userName =='':
            print("Вы не просматривали лент пользователей!")
        else:
            numberPost = int(input(f"Какой пост пользователя {userName} хотите лайкнуть?(укажите номер):\t"))
            if numberPost > len(ids):
                print('Неправильно указан номер поста или пост отсутсвует')
            else:
                idPostNumber = ids[numberPost - 1]
                stub.UserLikePost(sn_pb2.PostData(username=userName, idpost= idPostNumber, body = ''))
                print("Обновите ленту, лайк учтен!")
    elif command == "cp":
        # команда на комент поста
        if userName =='':
            print("Вы не просматривали лент пользователей!")
        else:
            numberPost = int(input(f"Комментарий к какому посту пользователя {userName} хотите оставить?(укажите номер):\t"))
            if numberPost > len(ids):
                print('Неправильно указан номер поста или пост отсутсвует')
            else:
                idPostNumber = ids[numberPost - 1]
                commPost = input("Ваш комментарий: \t")
                stub.UserCommentPost(sn_pb2.PostData(username=userName, idpost= idPostNumber, body = commPost))
                print("Комментарий добавлен! Обновите ленту!")
    elif command =="ip":
        # Добавляем пост
        postBody = input("Что постим барин?")
        response = stub.UserAddPost(sn_pb2.PostData(username=userLogin, postnumber = 0, body = postBody))
        print(response)
    else:
        print("Неизвестная комманда!")


def run():
    global userLogin
    userLogin = input('User login: ')
    print(f"Привет, {userLogin}")
    print("Список команд: \n\trq - возвращает перевернутую строку, которую ввел пользователь \n\tul - список пользователей системы \n\tls - показать ленту пользователя")
    print("\tip - добавить пост в свою ленту \n\tlp - лайкнуть пост \n\tcp - оставить комментарий к посту")
    print("\tq - выход")
    
    while True:
        command = input("Введите команду:")
        if command == 'q':
            break
        else:
            commands(command)

if __name__ == '__main__':
    logging.basicConfig()
    userName =''
    userLogin =''
    ids = []
    channel = grpc.insecure_channel('localhost:50505')
    stub = sn_pb2_grpc.SocNetStub(channel)
    run()