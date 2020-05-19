from pymongo import MongoClient,DESCENDING,ASCENDING
from cn.dongman.src.tools.logger import logger
from bson.objectid import ObjectId


def getMongodbConnect():
    client = MongoClient('s-2ze2526365b24054.mongodb.rds.aliyuncs.com',3717)
    db = client["admin"]
    db.authenticate(name="root",password="dmdb2016qgHk")
    return client,db

def getCommentByTitleEpisode(dbname,title,episode):
    comment = dbname.get_collection("comment")
    objectId = "w_%s_%s" % (title,episode)
    count = comment.count_documents({"objectId":objectId})
    if count >= 20:
        alist=[]
        res = comment.find_one({"objectId": objectId}, ["_id"])
        return alist.append(res)

def getReplyByTitleEpisode(dbname,title,episode):
    reply = dbname.get_collection("comment_reply")
    objectId = "w_%s_%s" % (title,episode)
    res = reply.find({"objectId":objectId},["parentId","_id"])
    result = []
    for i in res:
        i["_id"] = str(i["_id"])
        result.append([str(i["_id"]),i["parentId"]])
    return result

def closeMongodb(client):
    client.close()

def getCommentGroupByObjectId(dbname):
    comment = dbname.get_collection("comment")
    pipeline = [{'$group':{'_id':'$objectId','count':{'$sum':1}}}]
    res = comment.aggregate(pipeline)
    for i in res:
        print(i)

def getAllReply(dbname):
    reply = dbname.get_collection("comment_reply")
    res = reply.find({"deleted":False,"visible":True},["parentId","_id","titleNo","episodeNo"])
    result = []
    for i in res:
        i["_id"] = str(i["_id"])
        i["episodeNo"] = i["episodeNo"].split("-")[-1]
        result.append([str(i["_id"]),i["parentId"],i["titleNo"],i["episodeNo"]])
    return result


def getAllObjectIds(dbname):
    comm = dbname.get_collection("comment")
    res = comm.find({"deleted":False,"visible":True},["objectId"])
    result = []
    for i in res:
        tmp =[]
        tmp.append(i["objectId"])
        result.append([str(tmp)])
    return result

def getAllIDByNeoId(dbname,neoid="3f92b1d0-0331-11e9-9c05-00163e06a3f6"):
    comm = dbname.get_collection("comment")
    res = comm.find({"deleted":False,"visible":True,"neoId":neoid},["_id"])
    result = []
    for i in res:
        result.append(str(i["_id"]))
    return result

def getReplyLikeCount(dbname,objectId):
    comm = dbname.get_collection("comment")
    res = comm.find({"objectId":objectId,"likeCount":{"$gte":10}},["likeCount","replyCount","createTime","contents","objectId","unLikeCount"]).sort([
                    ('likeCount', DESCENDING),
                    ('createTime', ASCENDING)]).limit(3)
    result = []
    for i in res:
        result.append(i)
    return result

def getCommentCount(dbname,objectId):
    comm = dbname.get_collection("comment")
    res = comm.count_documents({"objectId":objectId})
    return res

def editComment(dbname,id,replyCount,likeCount):
    comm = dbname.get_collection("comment")
    comm.update_one({"_id":ObjectId(id)},{"$set":{"replyCount":replyCount,"likeCount":likeCount}})

def editReply(dbname,id,likeCount):
    reply = dbname.get_collection("comment_reply")
    reply.update_one({"_id": ObjectId(id)}, {"$set": {"likeCount": likeCount}})


def testEdit():
    commentId = ["5dedb74c38197e76fadb660f","5dedb7559106f47711ad7995"]
    replyId = ["5dedb74d598cd9770f816d37","5dedb756598cd9770f816d3d"]

    client,db = getMongodbConnect()
    dbname = client["qadmcomment"]

    for i in commentId:
        editComment(dbname,i,626,626)
    for i in replyId:
        editReply(dbname,i,626)


def deleteCommentDB(dbname,titleNo):
    comm = dbname.get_collection("comment")
    res = comm.delete_many({"titleNo":str(titleNo)} )
    # logger.info("删除comment数据%s个" % res.deleted_count)



def deleteReplyDB(dbname,titleNo):
    comm = dbname.get_collection("comment_reply")
    res = comm.delete_many({"titleNo":str(titleNo)} )
    # logger.info("删除comment_reply数据%s个" % res.deleted_count)


def deletelikeItDB(dbname,titleNo):
    comm = dbname.get_collection("episode_likeit_history")
    res = comm.delete_many({"titleNo":str(titleNo)} )
    # logger.info("删除episode_likeit_history数据%s个" % res.deleted_count)


if __name__ == "__main__":


    # commentId = ["5dedb74c38197e76fadb660f","5dedb7559106f47711ad7995"]
    # replyId = ["5dedb74d598cd9770f816d37","5dedb756598cd9770f816d3d"]
    #
    client,db = getMongodbConnect()
    dbname = client["qadmcomment"]
    #
    # for i in commentId:
    #     editComment(dbname,i,626,626)
    # for i in replyId:
    #     editReply(dbname,i,626)

    deleteComment(dbname,1467)
    deleteReply(dbname,1467)




