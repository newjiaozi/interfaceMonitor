from pymongo import MongoClient
from bson.objectid import ObjectId



def getConnect():
    client = MongoClient('s-2ze2526365b24054.mongodb.rds.aliyuncs.com',3717)
    db = client["dmcommentreal"]
    db.authenticate(name="commentAdmin",password="123!@#")
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
if __name__ == "__main__":
    client,db = getConnect()
    getAllIDByNeoId(db)




