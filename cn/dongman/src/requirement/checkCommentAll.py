from cn.dongman.src.tools.commentCookies import *
from cn.dongman.src.tools.handleSqlite import getSession,getCursor
from cn.dongman.src.tools.login import login
from cn.dongman.src.tools.handleRedis import *
from cn.dongman.src.tools.handleMongodb import testEdit
import redis
import time

def deleteRedis():
    # curTime = time.localtime()
    # str_timeB = str(curTime.tm_year)+str(curTime.tm_mon)+str(curTime.tm_mday)
    r = redis.Redis(host='r-2ze7889e17a315d4.redis.rds.aliyuncs.com', port=6379, password='dmred2017qUsa', db="0",decode_responses=True)
    pattern = "comment_frequency_*_*"
    k = r.keys(pattern=pattern)
    if k:
        r.delete(*k)
        logger.info("redis删除成功 %s" % k)
    else:
        logger.info("没有匹配到需要删除的redis")


def comment(titleNo,episodeNo,cookies,categoryImage="",categoryId="",imageNo="",text="",userType=""):
    commentData =  v1Comment(titleNo,episodeNo,cookies,categoryImage,categoryId,imageNo,text,userType)
    if commentData:
        if commentData["code"] == 200:
            return commentData["data"]["_id"]
        elif commentData["code"] == 10005:
            deleteRedis()
            return comment(titleNo, episodeNo, cookies, categoryImage, categoryId, imageNo, text, userType)
    return False

def replyComment(parentId,titleNo,episodeNo,cookies):
    commentData = v1CommentReply(parentId,titleNo,episodeNo,cookies)
    if commentData:
        if commentData["code"] == 200:
            return commentData["data"]["_id"]
        elif commentData["code"] == 10005:
            deleteRedis()
            return replyComment(parentId,titleNo,episodeNo,cookies)
    return False

def likeComment(id,titleNo,episodeNo,cookies,flag="like"):
    result = postV1CommentLike(id,titleNo,episodeNo,cookies,flag=flag)
    if result:
        if result["code"] == 200:
            return True
    return False

def likeReply(id,titleNo,episodeNo,cookies,flag="like"):
    result = postV1CommentReplyLike(id,titleNo,episodeNo,cookies,flag=flag)
    if result:
        if result["code"] == 200:
            return True
    return False

def cancelLikeComment(id,titleNo,episodeNo,cookies,flag="cancelLike"):
    result = postV1CommentLike(id,titleNo,episodeNo,cookies,flag=flag)
    if result:
        if result["code"] == 200:
            return True
    return False
def cancelLikeReply(id,titleNo,episodeNo,cookies,flag="cancelLike"):
    result = postV1CommentReplyLike(id,titleNo,episodeNo,cookies,flag=flag)
    if result:
        if result["code"] == 200:
            return True
    return False


def checkV2CommentData(result):
    if result:
        if result["code"] == 200:
            showTotalCount = result["data"]["showTotalCount"]
            count = result["data"]["count"]
            commentList = result['data']['commentList']
            if commentList:
                comment1 = commentList[0]
                return {"showTotalCount":showTotalCount,"count":count,"likeCount":comment1["likeCount"],"replyCount":comment1["replyCount"]}
            else:
                return {"showTotalCount":showTotalCount,"count":count,"likeCount":None,"replyCount":None}
    return False


def checkV1CommentReply(result,id=""):
    if result:
        if result["code"]==200:
            count = result["data"]["count"]
            commentReplyList = result["data"]["commentReplyList"]
            if commentReplyList:
                for i in commentReplyList:
                    if i["_id"] == id:
                        likeCount = i["likeCount"]
                        break
                return {"count":count,"likeCount":likeCount}
    return False


def checkV1CommentImageCount(result,id=""):
    if result:
        if result["code"]==200:
            data = result["data"]
            for i in data:
                if i["_id"] == id:
                    count = i["count"]
                    showTotalCount = i["showTotalCount"]
                    break
            return {"count":count,"showTotalCount":showTotalCount}
    return False



def assertV2Comment(titleNo,episodeNo,cookies,categoryId="",showTotalCount=0,count=0,likeCount=0,replyCount=0):
    if categoryId:  ##cut
        dataV2CommentImageNo = v2Comment(titleNo, episodeNo, cookies, imageNo=categoryId)
        dataV2Comment = v2Comment(titleNo, episodeNo, cookies)
        dataV1CommentImageCount = v1CommentImageCount(titleNo, episodeNo, ids=categoryId)

        ###
        dataV2CommentImageNoCheck = checkV2CommentData(dataV2CommentImageNo)
        if dataV2CommentImageNoCheck:
            assert dataV2CommentImageNoCheck["showTotalCount"] == showTotalCount
            assert dataV2CommentImageNoCheck["count"] == count
            assert dataV2CommentImageNoCheck["likeCount"] == likeCount
            assert dataV2CommentImageNoCheck["replyCount"] == replyCount
        dataV2CommentCheck = checkV2CommentData(dataV2Comment)
        if dataV2CommentCheck:
            assert dataV2CommentCheck["showTotalCount"] == showTotalCount
            assert dataV2CommentCheck["count"] == count
            assert dataV2CommentCheck["likeCount"] == likeCount
            assert dataV2CommentCheck["replyCount"] == replyCount
        dataV1CommentImageCountCheck = checkV1CommentImageCount(dataV1CommentImageCount, categoryId)
        if dataV1CommentImageCountCheck:
            assert dataV1CommentImageCountCheck["showTotalCount"] == showTotalCount
            assert dataV1CommentImageCountCheck["count"] == count
    else:  ##非cut
        dataV2Comment = v2Comment(titleNo, episodeNo, cookies)
        dataV2CommentCheck = checkV2CommentData(dataV2Comment)
        if dataV2CommentCheck:
            assert dataV2CommentCheck["showTotalCount"] == showTotalCount
            assert dataV2CommentCheck["count"] == count
            assert dataV2CommentCheck["likeCount"] == likeCount
            assert dataV2CommentCheck["replyCount"] == replyCount


def caculateBest():
    neo_ses,neo_id = login("weixindogs@163.com","qwe123")
    cookiesO={"neo_ses":neo_ses,"uuid":neo_id}
    testData = [{"titleNo":1428,"episodeNo":14,"cookies":cookiesO,"categoryImage":"","categoryId":"","imageNo":"","text":"","userType":""},
                {"titleNo":762,"episodeNo":110,"cookies":cookiesO,"categoryImage":"https://cdn.dongmanmanhua.cn/15374049045057621102.jpg?x-oss-process=image/format,webp","categoryId":"1","imageNo":"1","text":"","userType":""}]

    initPhone = 14400004000
    anotherInitPhone = 14400004020
    actionTimes = 11
    conn, cursor = getCursor()

    for data in testData:
        titleNo = data["titleNo"]
        episodeNo = data["episodeNo"]
        for i in range(1, actionTimes):
            mobile = str(initPhone + i)
            session = getSession(cursor, mobile)
            cookies = {"neo_ses": session}
            data["cookies"] = cookies
            parentId = comment(**data)
            if parentId:
                for i in range(1,actionTimes):
                    mobile = str(anotherInitPhone+i)
                    session = getSession(cursor,mobile)
                    cookiesReply = {"neo_ses":session}
                    ##发表回复
                    replyComment(parentId, titleNo, episodeNo, cookiesReply)

                    ##评论点赞
                    likeComment(parentId,titleNo,episodeNo,cookiesReply)

            logger.info("STOP#A#" * 20)
        logger.info("STOP#B#" * 20)
    logger.info("STOP#C#" * 20)


def checkCommentRelpyLikeDelete():
    neo_ses,neo_id = login("weixindogs@163.com","qwe123")
    cookiesO={"neo_ses":neo_ses,"uuid":neo_id}
    testData = [{"titleNo":1428,"episodeNo":14,"cookies":cookiesO,"categoryImage":"","categoryId":"","imageNo":"","text":"","userType":""},
                {"titleNo":762,"episodeNo":110,"cookies":cookiesO,"categoryImage":"https://cdn.dongmanmanhua.cn/15374049045057621102.jpg?x-oss-process=image/format,webp","categoryId":"1","imageNo":"1","text":"","userType":""}]

    initPhone = 14400004000
    actionTimes = 11
    conn, cursor = getCursor()

    for data in testData:
        categoryId = data["categoryId"]
        titleNo = data["titleNo"]
        episodeNo = data["episodeNo"]
        parentId = comment(**data)
        if parentId:
            assertV2Comment(titleNo,episodeNo,cookiesO,categoryId=categoryId,showTotalCount=1,count=1,likeCount=0,replyCount=0)
            id = replyComment(parentId,titleNo,episodeNo,cookiesO)
            if id:
                assertV2Comment(titleNo, episodeNo, cookiesO, categoryId=categoryId, showTotalCount=2, count=1,
                                likeCount=0, replyCount=1)

                replyCounter = 1
                likeCommentCounter = 0
                likeReplyCounter = 0
                replyIds = []
                for i in range(1,actionTimes):
                    mobile = str(initPhone+i)
                    session = getSession(cursor,mobile)
                    cookies = {"neo_ses":session}

                    ##发表回复
                    replyId = replyComment(parentId, titleNo, episodeNo, cookies)
                    if replyId:
                        replyCounter+=1
                        replyIds.append(replyId)

                    ##评论点赞
                    if likeComment(parentId,titleNo,episodeNo,cookies):
                        likeCommentCounter+=1

                    #回复点赞
                    if likeReply(id,titleNo,episodeNo,cookies):
                        likeReplyCounter+=1
                assertV2Comment(titleNo,episodeNo,cookies,categoryId=categoryId,showTotalCount=11,count=1,likeCount=9,replyCount=10)
                replyData = v1CommentReplyGet(parentId)
                if replyData:
                    replyDataCheck = checkV1CommentReply(replyData,id)
                    assert replyDataCheck["count"] == 10
                    assert replyDataCheck["likeCount"] == 9


                for i in range(1,actionTimes):
                    mobile = str(initPhone+i)
                    session = getSession(cursor,mobile)
                    cookies = {"neo_ses":session}
                    #取消评论点赞
                    if cancelLikeComment(parentId,titleNo,episodeNo,cookies):
                        likeCommentCounter-=1
                    #取消回复点赞
                    if cancelLikeReply(id,titleNo,episodeNo,cookies):
                        likeReplyCounter-=1
                assertV2Comment(titleNo,episodeNo,cookies,categoryId=categoryId,showTotalCount=11,count=1,likeCount=0,replyCount=10)


                replyData = v1CommentReplyGet(parentId)
                if replyData:
                    replyDataCheck = checkV1CommentReply(replyData,id)
                    assert replyDataCheck["count"] == 10
                    assert replyDataCheck["likeCount"] == 0

                if categoryId:
                    for i in range(1,actionTimes):
                        mobile = str(initPhone+i)
                        session = getSession(cursor,mobile)
                        cookies = {"neo_ses":session}
                        deleteCommentReply(cookies,replyIds[i-1])
                        assertV2Comment(titleNo, episodeNo, cookies, categoryId=categoryId, showTotalCount=11-i, count=1,
                                        likeCount=0, replyCount=10-i)
                    deleteCommentReply(cookiesO,id)
                    assertV2Comment(titleNo, episodeNo, cookies, categoryId=categoryId, showTotalCount=1, count=1,
                                    likeCount=0, replyCount=0)
                    deleteComment(cookiesO,parentId)
                    assertV2Comment(titleNo, episodeNo, cookies, categoryId=categoryId, showTotalCount=0, count=0,
                                    likeCount = None, replyCount = None)
                else:
                    deleteComment(cookiesO,parentId)
                    assertV2Comment(titleNo, episodeNo, cookies, categoryId=categoryId, showTotalCount=11, count=1,
                                    likeCount = 0, replyCount = 10)
                    for i in range(1,actionTimes):
                        mobile = str(initPhone+i)
                        session = getSession(cursor,mobile)
                        cookies = {"neo_ses":session}
                        deleteCommentReply(cookies,replyIds[i-1])
                        assertV2Comment(titleNo, episodeNo, cookies, categoryId=categoryId, showTotalCount=11-i, count=1,
                                        likeCount=0, replyCount=10-i)
                    deleteCommentReply(cookiesO,id)
                    assertV2Comment(titleNo, episodeNo, cookies, categoryId=categoryId, showTotalCount=0, count=0,
                                    likeCount=None, replyCount=None)
        logger.info("STOP##" * 20)


    logger.info("FORADMIN##" *20)
    for i in range(1, actionTimes):
        mobile = str(initPhone + i)
        session = getSession(cursor, mobile)
        cookies = {"neo_ses": session}
        data = {"titleNo": 1428, "episodeNo": 7, "cookies": cookies, "categoryImage": "", "categoryId": "",
                "imageNo": "", "text": "", "userType": ""}

        id = comment(**data)
        if id:
            titleNo = data["titleNo"]
            episodeNo = data["episodeNo"]
            for i in range(1, actionTimes):
                mobile = str(initPhone + i)
                session = getSession(cursor, mobile)
                cookies = {"neo_ses": session}
                replyComment(id,titleNo,episodeNo,cookies)
    logger.info("ALL STOP ##" *20)


if __name__ == "__main__":

    # caculateBest()
    r = connectRedis()
    ###cut
    imageTitleNo = 762
    imageEpisodeNo = 110
    imageNo = 1
    ##cut
    setHash(r,"image_comment_count","%s-%s-%s" % (imageTitleNo,imageEpisodeNo,imageNo),"1000")
    setHash(r,"image_comment_reply_count","%s-%s-%s" % (imageTitleNo,imageEpisodeNo,imageNo),"1000")
    setHash(r,"episode_comment_count","%s-%s" % (imageTitleNo,imageEpisodeNo),"1000")
    setHash(r,"episode_comment_reply_count","%s-%s" % (imageTitleNo,imageEpisodeNo),"1000")


    ###其他
    titleNo = 1428
    episodeNo = 14
    ##其他
    setHash(r,"episode_comment_count","%s-%s" % (titleNo,episodeNo),"1000")
    setHash(r,"episode_comment_reply_count","%s-%s" % (titleNo,episodeNo),"1000")

    testEdit()




