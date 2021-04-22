from concurrent import futures
from bson.objectid import ObjectId
import logging
import grpc

import sn_pb2_grpc
import sn_pb2
from pymongo import MongoClient

def find_document(collection, elements):
# Поиск документов в коллекциях базы
    results = collection.find(elements)
    return [r for r in results]

def update_document(collection, query_elements, new_values):
# Обновление документов
    collection.update_one(query_elements, {'$set': new_values})

class SocNetServicer(sn_pb2_grpc.SocNetServicer):
    def Do(self, request, context):
        # возвращает перевернутую строку пользователю
        return sn_pb2.Response(message=request.message[::-1])

    def UserAddPost(self, request, context):
        user = {
            "name":request.username
        }
        data = {
            "name":request.username,
            "body":request.body,
            "comments":[],
            "likes":0
        }
        users_collection.insert_one(user)
        lenta_collection.insert_one(data)
        strresult = "Ваш пост добавлен!"
        return sn_pb2.Response(message=strresult)

    def UserCommentPost(self, request, context):
        results = lenta_collection.find_one({"_id" : ObjectId(request.idpost)})
        comment = results["comments"]
        comment.append(request.body)
        update_document(lenta_collection, {"_id":ObjectId(request.idpost)}, {"comments":comment})
        return sn_pb2.Response(message='')

    def UserLikePost(self, request, context):
        results = lenta_collection.find_one({"_id" : ObjectId(request.idpost)})
        likes = results["likes"]
        update_document(lenta_collection, {"_id":ObjectId(request.idpost)}, {"likes":likes + 1})
        strResult = 'Обновите ленту, лайк учтен!'
        return sn_pb2.Response(message=strResult)

    def UserList(self, request, context):
        # возвращает список пользователей системы
        # дергаем пользователей из базы данных
        results = users_collection.find()
        strresult = "Список пользователей системы: \n"
        # формируем строку ответа для клиента
        for r in results:
            strresult = strresult + "\t" + r["name"] + "\n"
        return sn_pb2.Response(message=strresult)

    def UserLenta(self, request, context):
        # возвращает ленту новостей указаного пользователя
        # если документов по этому пользователю нет то пишем клиенту об этом
        if lenta_collection.count_documents({"name" : request.message}) == 0:
            strresult = "У пользователя " + request.message + " нет новостей в ленте!"
            idsposts = ""
        else:
            # иначе получаем весь список постов и формируем в один большой блок текста
            results = find_document(lenta_collection, {"name" : request.message})
            strresult = "\tЛента пользователя :" + request.message + "\n \t =======\n"
            i = 1
            ids = []
            for r in results:
                # перебираем все посты пользователя
                strresult = strresult + "\t Пост " + str(i) + " : "+ r["body"] + "| \t Лайков: " + str(int(r["likes"]))
                strresult = strresult + "\n\t\t Комментарии: \n"
                ids.append(str(r["_id"]))
                # формируем комментарии к постам
                for j in range(0, len(r["comments"])):
                    strresult = strresult + "\n\t\t" + '---'
                    strresult = strresult + "\n\t\t" + r["comments"][j]
                strresult = strresult + "\n \t _______\n"
                i += 1
                idsposts = ','.join(ids)
        # отправляем полученый ответ клиенту
        return sn_pb2.ResponseLenta(message=strresult, idpost=idsposts)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sn_pb2_grpc.add_SocNetServicer_to_server(SocNetServicer(), server)
    server.add_insecure_port('[::]:50505')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    # создаем подключение
    client = MongoClient('localhost', 27017)
    # покдлючаемся к нашей базе соцсети
    db = client['snDB']
    # получаем коллекцию пользователей системы
    users_collection = db['users']
    lenta_collection = db['lenta']
    serve()