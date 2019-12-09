import requests
import datetime
import json
from cn.dongman.src.tools.logger import logger
from cn.dongman.src.tools.login import Config
from cn.dongman.src.tools.interface import getExpiresMd5,appEpisodeInfoV3,appTitleInfo2,deleteRedis
from cn.dongman.src.tools.login import login,getConfig
from cn.dongman.src.tools.handleSqlite import getConfig as gc

### 发表评论
def v1Comment(titleNo,episodeNo,categoryImage="",categoryId="",imageNo="",text="",userType=""):
    path = "/v1/comment"
    titleNo = str(titleNo)
    episodeNo = str(episodeNo)
    text = str(text)
    objectId = "w_"+titleNo+"_"+episodeNo
    # print(objectId)
    time_now = datetime.datetime.now()
    otherStyleTime = time_now.strftime("%Y-%m-%d %H:%M:%S")
    if not text:
        contents = "自动生成回复_"+str(otherStyleTime)
    if userType:
        payload = {"categoryId":categoryId,
                   "categoryImage":categoryImage,
                   "contents":text,
                   "episodeNo":episodeNo,
                   "imageNo":imageNo,
                   "objectId":objectId,
                   "titleNo":titleNo,
                   "userType":userType}
    else:
        payload = {"categoryId":categoryId,
                   "categoryImage":categoryImage,
                   "contents":text,
                   "episodeNo":episodeNo,
                   "imageNo":imageNo,
                   "objectId":objectId,
                   "titleNo":titleNo,}
    payload.update(Config("baseparams"))
    try:
        resp = requests.post(Config("httphost")+path,params=getExpiresMd5(path),data=payload,headers=Config("headers"),cookies=Config("cookies"))
        result = resp.json()
        # logger.info(resp.url)
        # logger.info(resp.request.body)
        # logger.info(result)
        return result
    except Exception:
        logger.exception("v1Comment出现异常")


### 发表回复
def v1CommentReply(parentId,titleNo,episodeNo,text=""):
    path = "/v1/comment_reply"
    titleNo = str(titleNo)
    episodeNo = str(episodeNo)
    text = str(text)
    objectId = "w_"+titleNo+"_"+episodeNo
    # print(objectId)
    time_now = datetime.datetime.now()
    otherStyleTime = time_now.strftime("%Y-%m-%d %H:%M:%S")
    if text:
        contents = text+"_"+str(otherStyleTime)
    else:
        contents = "自动生成回复_"+str(otherStyleTime)

    payload = {
               "contents":contents,
               "parentId":parentId,
               "objectId":objectId}
    payload.update(Config("baseparams"))
    try:
        resp = requests.post(Config("httphost")+path,params=getExpiresMd5(path),data=payload,headers=Config("headers"),cookies=Config("cookies"))
        result = resp.json()
        # logger.info(resp.url)
        # logger.info(resp.request.body)
        # logger.info(result)
        return result
    except Exception:
        logger.exception("v1CommentReply发生异常")

###查看回复
def v1CommentReplyGet(commentId,pageNo,limit=10):
    path = "/v1/comment_reply"
    payload = {
               "commentId":commentId,
               "pageNo":pageNo,
               "limit":limit}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"),cookies=Config("cookies"))
        result = resp.json()
        if result["code"] == 200:
            pass
            # logger.info(result['data']["commentReplyList"][0].keys())
        return result
    except Exception:
        logger.exception("v1CommentReplyGet发生异常")


def v1CommentOwnAll(flag="",id="",pageNo=1):
    path="/v1/comment/ownall"
    payload= {"limit":20,"pageNo":pageNo,"flag":flag,"_id":id}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"),cookies=Config("cookies"))
    logger.info(resp.url)
    if resp.ok:
        result= resp.json()
        return result
    else:
        logger.exception("v1CommentOwnAll发生异常")



def appCommentTitleepisodeinfo2(telist):
    path="/app/comment/titleEpisodeInfo2"
    telist2Json = json.dumps(telist)
    payload = {"objectIdsJson":telist2Json}
    payload.update(Config("baseparams"))
    resp = requests.post(Config("httphost")+path,params=getExpiresMd5(path),data=payload,headers=Config("headers"))
    commentTitleEpisodeInfo = resp.json()["message"]["result"]["commentTitleEpisodeInfo"]
    return commentTitleEpisodeInfo


def checkV1CommentData(data,cKeys):
    if data:
        data_keys = list(data.keys())
        logger.info(data_keys)
        for i in cKeys:
            assert i in data_keys

def cutomizeV1Comment(titleNo,episodeNo,categoryImage="",categoryId="",imageNo="",text="",userType=""):
    resp = v1Comment(titleNo, episodeNo, categoryImage, categoryId, imageNo, text, userType)
    if resp["code"] == 200:
        checkV1CommentData(resp["data"],
                           ['_id', 'titleNo', 'episodeNo', 'categoryId', 'imageNo', 'contents', 'createTime', 'modifyTime',
                            'replyCount', 'neoId', 'deleted', 'likeCount', 'unLikeCount', 'forbid', 'visible', 'objectId',
                            'originalContents', 'commentType', 'deleteDescription', 'secret', 'extra_status',
                              '__v'])
        id = resp["data"]["_id"]
        return id

    elif resp["code"] == 10005:
        logger.info("评论次数限制 ：%s" % resp["message"])
        deleteRedis(gc("neo_id"))
        return cutomizeV1Comment(titleNo, episodeNo, categoryImage, categoryId, imageNo, text, userType)

    elif resp["code"] == 10002:
        logger.info("评论失败：%s" % resp["message"])
        assert resp["message"] == "在留言内容中包含限制文句。\r\n请修改后再上传。"



def customizeV1CommentReply(parentId,titleNo,episodeNo,text=""):
    replyResp = v1CommentReply(parentId, titleNo, episodeNo, text=text)
    if replyResp["code"] == 200:
        checkV1CommentData(replyResp['data'],
                           ['_id', 'parentId', 'contents', 'createTime', 'modifyTime', 'neoId', 'deleted', 'likeCount',
                            'unLikeCount', 'visible', 'objectId', 'originalContents', 'commentType',
                            'deleteDescription', 'secret', 'extra_status', 
                             'titleNo', 'episodeNo', 'imageNo', '__v'])
        id = replyResp["data"]["_id"]
        return id
    elif replyResp["code"] == 10005:
        logger.info("评论次数限制 ：%s" % replyResp["message"])
        deleteRedis(gc("neo_id"))
        return customizeV1CommentReply(parentId,titleNo,episodeNo,text=text)

    elif replyResp["code"] == 10002:
        logger.info("评论失败：%s" % replyResp["message"])
        assert replyResp["message"] == "在留言内容中包含限制文句。\r\n请修改后再上传。"

def postV1CommentLike(id,titleNo,episodeNo,flag="like"):
    path = "/v1/comment/%s/like" % id
    titleNo = str(titleNo)
    episodeNo = str(episodeNo)

    payload = {
               "flag":flag,
               "titleNo":titleNo,
               "episodeNo":episodeNo,}
    payload.update(Config("baseparams"))
    try:
        resp = requests.post(Config("httphost")+path,params=getExpiresMd5(path),data=payload,headers=Config("headers"),cookies=Config("cookies"))
        result = resp.json()
        logger.info(resp.url)
        # logger.info(resp.request.headers)
        logger.info(resp.request.body)
        logger.info(result)
        return result
    except Exception:
        logger.exception("postV1CommentLike发生异常")

def postV1CommentReplyLike(id,titleNo,episodeNo,flag="like"):
    path = "/v1/comment_reply/%s/like" % id
    titleNo = str(titleNo)
    episodeNo = str(episodeNo)
    payload = {
               "flag":flag,
               "titleNo":titleNo,
               "episodeNo":episodeNo,}
    payload.update(Config("baseparams"))
    try:
        resp = requests.post(Config("httphost")+path,params=getExpiresMd5(path),data=payload,headers=Config("headers"),cookies=Config("cookies"))
        result = resp.json()
        logger.info(resp.url)
        # logger.info(resp.request.headers)
        logger.info(resp.request.body)
        logger.info(result)
        return result
    except Exception:
        logger.exception("vpostV1CommentReplyLike发生异常")


def checkV1CommentLike(data):
    code = data["code"]
    if code==200:
        logger.info(data["message"])
    elif code == 10084:
        logger.info("无法为自己的留言点赞！")
        assert data["message"] == "无法为自己的留言点赞！"
    elif code == 400:
        logger.error(data["message"])
        assert data["message"] == "非法请求！"

def postV1CommentComplaint(id):
    path = "/v1/comment/%s/complaint" % id
    payload = Config("baseparams")
    try:
        resp = requests.post(Config("httphost")+path,params=getExpiresMd5(path),data=payload,headers=Config("headers"),cookies=Config("cookies"))
        return resp.json()
    except Exception:
        logger.exception("postV1CommentComplaint发生异常")


def postV1CommentReplyComplaint(id):
    path = "/v1/comment_reply/%s/complaint" % id
    payload = Config("baseparams")
    try:
        resp = requests.post(Config("httphost")+path,params=getExpiresMd5(path),data=payload,headers=Config("headers"),cookies=Config("cookies"))
        return resp.json()
    except Exception:
        logger.exception("postV1CommentReplyComplaint发生异常")


def checkV1CommentComplaint(data):
    code = data['code']
    if code == 200:
        logger.info(data["message"])
    elif code == 10140:
        logger.info(data["message"])
        assert data["message"] == "无法举报自己的留言！"
    elif code == 400:
        logger.error(data["message"])
        assert data["message"] == "非法请求！"

def deleteComment(id):
    path = "/v1/comment/%s" % id
    payload = Config("baseparams")
    try:
        resp = requests.delete(Config("httphost")+path,params=getExpiresMd5(path),data=payload,headers=Config("headers"),cookies=Config("cookies"))
        logger.info(resp.url)
        if resp.ok:
            result = resp.json()
            logger.info(result)
            assert result["code"] == 200
            assert result["message"] == "请求成功！"
    except Exception:
        logger.exception("deleteComment发生异常")

def deleteCommentReply(id):
    path = "/v1/comment_reply/%s" % id
    payload = Config("baseparams")
    try:
        resp = requests.delete(Config("httphost")+path,params=getExpiresMd5(path),data=payload,headers=Config("headers"),cookies=Config("cookies"))
        logger.info(resp.url)
        if resp.ok:
            result = resp.json()
            logger.info(result)
            assert result["code"] == 200
            assert result["message"] == "请求成功！"
    except Exception:
        logger.exception("deleteCommentReply发生异常")


def deleteAllComments():
    result = v1CommentOwnAll()
    if result["code"] == 200:
        count = result["data"]["count"]
        commentList = result["data"]["commentList"]
        pageNo = 2
        for i in range(0,count//20):
            lastId = commentList[-1]["_id"]
            res = v1CommentOwnAll("next",lastId,pageNo+i)
            if res["code"] == 200:
                commentList.extend(res["data"]["commentList"])
        for comment in commentList:
            if comment["type"] == 1:
                checkV1CommentData(comment,["_id","titleNo","episodeNo","contents","createTime","modifyTime","replyCount","likeCount",
                                            "unLikeCount","visible","objectId","commentType","deleteDescription","secret",
                                            "extra_status","extra_content_spam_status","ip","type"])
                deleteComment(comment["_id"])
            elif comment["type"] == 2:
                checkV1CommentData(comment,["_id","titleNo","episodeNo","contents","createTime","modifyTime","parentId","likeCount",
                                            "unLikeCount","visible","objectId","commentType","deleteDescription","secret",
                                            "extra_status","extra_content_spam_status","ip","type"])
                deleteCommentReply(comment["_id"])



def v2Comment(titleNo,episodeNo,imageNo="",pageNo="",sortBy="",limit=""):
    path = "/v2/comment"
    payload = {"titleNo":titleNo,
               "episodeNo":episodeNo,
               "imageNo":imageNo,
                "pageNo":pageNo,
               "sortBy":sortBy,
               "limit":limit}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"),cookies=Config("cookies"))
        logger.info(resp.url)
        if resp.ok:
            result = resp.json()
            if result["code"] == 200:
                pass
                # logger.info(result.keys())
                # logger.info(result["data"].keys())
                # logger.info(result["data"]["commentList"][0].keys())
                # logger.info(result["data"]["commentList"][0]["commentReplyList"][0].keys())
                # logger.info(result["data"]["bestList"][0].keys())
                # logger.info(result["data"]["bestList"][0]["commentReplyList"][0].keys())

            return result
    except Exception:
        logger.exception("v2Comment发生异常")


def v1CommentDetail(titleNo,episodeNo,commentId,replyCommentId="",commentLimit=20,commentReplyLimit=10,imageNo=""):
    path = "/v1/comment/detail"
    payload = {"titleNo":titleNo,
               "episodeNo":episodeNo,
               "imageNo":imageNo,
                "commentId":commentId,
               "replyCommentId":replyCommentId,
               "commentLimit":commentLimit,
               "commentReplyLimit": commentReplyLimit,}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"),cookies=Config("cookies"))
        logger.info(resp.url)
        if resp.ok:
            result = resp.json()
            if result["code"] == 200:
                pass
                # logger.info(result.keys())
                # logger.info(result["data"].keys())
                # logger.info(result["data"]["comment"].keys())
                # logger.info(result["data"]["comment"]["commentList"][0].keys())
                # logger.info(result["data"]["comment"]["pageModel"].keys())
                # logger.info(result["data"]["comment"]["bestList"][0].keys())
                # logger.info(result["data"]["replyComment"].keys())
                # logger.info(result["data"]["replyComment"]["commentReplyList"][0].keys())
                # logger.info(result["data"]["replyComment"]["pageModel"].keys())
            return result
    except Exception:
        logger.exception("v1CommentDetail发生异常")

##v1comment回复查询翻页check
def checkV1CommentGet(commentId,pageNo=1,limit=10):
    result = v1CommentReplyGet(commentId,pageNo,limit)
    if result["code"] == 200:
        count = result["data"]["count"]
        commentList = result["data"]["commentReplyList"]
        pageNo = 2
        for i in range(0,count//limit):
            res = v1CommentReplyGet(commentId,pageNo+i,limit)
            if res["code"] == 200:
                commentList.extend(res["data"]["commentReplyList"])
        for i in commentList:
            # logger.info(i)
            checkV1CommentData(i,['_id', 'parentId', 'contents', 'createTime', 'modifyTime', 'neoId', 'deleted', 'likeCount', 'unLikeCount', 'visible', 'objectId', 'commentType', 'deleteDescription', 'secret', 'extra_status',   'titleNo', 'episodeNo', 'imageNo','userName', 'userCertType', 'like'])
    logger.info("checkV1CommentGet")

##v2comment翻页check
def checkV2Comment(titleNo,episodeNo,imageNo="",pageNo=1,sortBy="",limit=20):
    result = v2Comment(titleNo,episodeNo,imageNo,pageNo,sortBy,limit)
    if result["code"] == 200:
        count = result["data"]["count"]
        commentList = result["data"]["commentList"]
        pageNo = 2
        for i in range(0,count//limit):
            res = v2Comment(titleNo,episodeNo,imageNo,pageNo+i,sortBy,limit)
            if res["code"] == 200:
                commentList.extend(res["data"]["commentList"])
        for i in commentList:
            checkV1CommentData(i, ['_id', 'titleNo', 'episodeNo', 'categoryId', 'imageNo', 'contents', 'createTime',
                                   'modifyTime', 'replyCount', 'neoId', 'deleted', 'likeCount', 'unLikeCount', 'forbid',
                                   'visible', 'objectId', 'commentType', 'deleteDescription', 'secret', 'extra_status', 'best', 'commentReplyList','like', 'userName', 'userCertType'])
    logger.info("checkV2Comment")


def checkV2CommentJson(res):
    ###v2commentcheck
    checkV1CommentData(res,['code', 'data', 'message'])
    checkV1CommentData(res['data'],['hide', 'bestList', 'commentList', 'count', 'showTotalCount'])
    for i in res['data']["commentList"]:
        checkV1CommentData(i,['_id', 'titleNo', 'episodeNo', 'categoryId', 'imageNo', 'contents', 'createTime', 'modifyTime', 'replyCount', 'neoId', 'deleted', 'likeCount', 'unLikeCount', 'forbid', 'visible', 'objectId', 'commentType', 'deleteDescription', 'secret','extra_status', 'best', 'commentReplyList', 'like', 'userName', 'userCertType'])
        for j in i["commentReplyList"]:
            checkV1CommentData(j,['_id', 'parentId', 'contents', 'createTime', 'modifyTime', 'neoId', 'deleted', 'likeCount', 'unLikeCount', 'visible', 'objectId', 'originalContents', 'commentType', 'deleteDescription', 'secret', 'extra_status',   'titleNo', 'episodeNo', 'imageNo', 'like', 'userName', 'userCertType'])

    for i in res['data']["bestList"]:
        checkV1CommentData(i,['_id', 'titleNo', 'episodeNo', 'categoryId', 'imageNo', 'contents', 'createTime', 'modifyTime', 'replyCount', 'neoId', 'deleted', 'likeCount', 'unLikeCount', 'forbid', 'visible', 'userType', 'objectId', 'commentNo', 'commentType', 'deleteDescription', 'secret', 'best', 'commentReplyList', 'like', 'userName', 'userCertType'])
        for j in i["commentReplyList"]:
            checkV1CommentData(j,['_id', 'titleNo', 'episodeNo', 'imageNo', 'parentId', 'contents', 'createTime', 'modifyTime', 'neoId', 'deleted', 'likeCount', 'unLikeCount', 'visible', 'userType', 'objectId', 'commentNo', 'originalContents', 'commentType', 'deleteDescription', 'secret', 'like', 'userName', 'userCertType'])
    logger.info("checkV2CommentJson")

def checkV1CommentDetailJson(res):
    #v1commentdetailcheck
    checkV1CommentData(res,['code', 'data', 'message'])
    checkV1CommentData(res["data"],['hide', 'comment'])
    checkV1CommentData(res["data"]["comment"],['commentList', 'pageModel'])
    for i in res["data"]["comment"]["commentList"]:
        checkV1CommentData(i,['_id', 'titleNo', 'episodeNo', 'categoryId', 'imageNo', 'contents', 'createTime', 'modifyTime', 'replyCount', 'neoId', 'deleted', 'likeCount', 'unLikeCount', 'forbid', 'visible', 'objectId', 'commentType', 'deleteDescription', 'secret', 'extra_status',   'best', 'replyCommentList', 'userName', 'userCertType'])
    checkV1CommentData(res["data"]["comment"]['pageModel'],['page', 'pageSize', 'startRow', 'endRow', 'totalRows', 'showTotalCount', 'totalPages', 'prevPage', 'nextPage'])
    if res["data"]["comment"].get("bestList",None):
        for i in res["data"]["comment"]['bestList']:
            checkV1CommentData(i,['_id', 'titleNo', 'episodeNo', 'categoryId', 'imageNo', 'contents', 'createTime', 'modifyTime', 'replyCount', 'neoId', 'deleted', 'likeCount', 'unLikeCount', 'forbid', 'visible', 'userType', 'objectId', 'commentNo', 'commentType', 'deleteDescription', 'secret', 'best', 'replyCommentList', 'userName', 'userCertType'])

    logger.info("checkV1CommentDetailJson")

def checkV1ReplyCommentDetailJson(res):
    #v1commentdetailcheck
    checkV1CommentData(res,['code', 'data', 'message'])
    checkV1CommentData(res["data"],['hide', 'comment'])
    checkV1CommentData(res["data"]["comment"],['commentList', 'pageModel'])
    for i in res["data"]["comment"]["commentList"]:
        checkV1CommentData(i,['_id', 'titleNo', 'episodeNo', 'categoryId', 'imageNo', 'contents', 'createTime', 'modifyTime', 'replyCount', 'neoId', 'deleted', 'likeCount', 'unLikeCount', 'forbid', 'visible', 'objectId', 'commentType', 'deleteDescription', 'secret', 'extra_status',   'best', 'replyCommentList', 'userName', 'userCertType'])
    checkV1CommentData(res["data"]["comment"]['pageModel'],['page', 'pageSize', 'startRow', 'endRow', 'totalRows', 'showTotalCount', 'totalPages', 'prevPage', 'nextPage'])

    if res["data"]["comment"].get("bestList",None):
        for i in res["data"]["comment"]['bestList']:
            checkV1CommentData(i,['_id', 'titleNo', 'episodeNo', 'categoryId', 'imageNo', 'contents', 'createTime', 'modifyTime', 'replyCount', 'neoId', 'deleted', 'likeCount', 'unLikeCount', 'forbid', 'visible', 'userType', 'objectId', 'commentNo', 'commentType', 'deleteDescription', 'secret', 'best', 'replyCommentList', 'userName', 'userCertType'])

    for i in res["data"]["replyComment"]["commentReplyList"]:
        checkV1CommentData(i,['_id', 'parentId', 'contents', 'createTime', 'modifyTime', 'neoId', 'deleted', 'likeCount', 'unLikeCount', 'visible', 'objectId', 'originalContents', 'commentType', 'deleteDescription', 'secret', 'extra_status',  'titleNo', 'episodeNo', 'imageNo', 'userName', 'userCertType'])
    checkV1CommentData(res["data"]["replyComment"]['pageModel'],['page', 'pageSize', 'startRow', 'endRow', 'totalRows', 'showTotalCount', 'totalPages', 'prevPage', 'nextPage'])


    logger.info("checkV1ReplyCommentDetailJson")



def getParentsId(titleNo):
    parentids = {} ##{"neo_id":{"parentidA":["id3","id4"]},""parentidB":["id1","id2']}
    cdnHost = "https://cdn.dongmanmanhua.cn"
    deleteAllComments()
    datas=[]
    # for titleNo in titleNos:
    logger.info("#####：%s" % titleNo)
    resp = appTitleInfo2(titleNo)
    if resp:
        datas.append(resp)
    for title in datas:
        logger.info("@@@@@：%s" % title["title"])
        if title["serviceStatus"] == "SERVICE":
            totalServiceEpisodeCount = title["totalServiceEpisodeCount"]
            titleNo = title["titleNo"]
            titleName = title["title"]
            viewerType = title["viewer"]
            for episodeNo in range(1,totalServiceEpisodeCount+1):
                episodeInfo = appEpisodeInfoV3(titleNo,episodeNo)
                if episodeInfo:
                    # episodeNo = episodeInfo["episodeNo"]
                    episodeTitle = episodeInfo["episodeTitle"]
                    serviceStatus = episodeInfo["serviceStatus"]
                    if serviceStatus == "SERVICE":
                        commentIllegal = True
                        commentLike = True
                        commentComplaint = True
                        replyCommentIllegal = True
                        replyCommentLike = True
                        replyCommentComplaint = True
                        if viewerType == "CUT":
                            imageInfos = episodeInfo["imageInfo"]
                            for image in imageInfos:
                                categoryImage = cdnHost+image["url"]
                                categoryId = image["cutId"]
                                text = episodeTitle+"_"+str(categoryId)
                                ##评论非法词
                                if commentIllegal:
                                    cutomizeV1Comment(titleNo,episodeNo,categoryImage,categoryId,categoryId,"admin",userType="MANAGER")
                                    commentIllegal = False
                                for t in range(0,21):
                                    logger.info("%s-第%s次发表评论" % (titleNo, t))
                                    id = cutomizeV1Comment(titleNo,episodeNo,categoryImage,categoryId,categoryId,getFormateTime()+text,userType="MANAGER")
                                    if id:
                                        parentids[id]=[titleNo,episodeNo]
                                        ##为自己评论点赞
                                        if commentLike:
                                            resp = postV1CommentLike(id, titleNo, episodeNo)
                                            checkV1CommentLike(resp)
                                            commentLike = False
                                        ##举报自己的评论
                                        if commentComplaint:
                                            resp = postV1CommentComplaint(id)
                                            checkV1CommentComplaint(resp)
                                            commentComplaint = False
                                        ##回复非法词
                                        if replyCommentIllegal:
                                            customizeV1CommentReply(id, titleNo, episodeNo, "admin")
                                            replyCommentIllegal = False
                                        for rt in range(0,11):
                                            logger.info("%s-第%s次发表评论，第%s次发表回复" % (titleNo, t, rt))
                                            replyid = customizeV1CommentReply(id, titleNo, episodeNo, text + "_"+str(rt))
                                            if replyid:
                                                parentids[id].append(replyid)
                                                ##为自己回复点赞
                                                if replyCommentLike:
                                                    resp = postV1CommentReplyLike(replyid, titleNo, episodeNo)
                                                    checkV1CommentLike(resp)
                                                    replyCommentLike = False
                                                ##举报自己的回复
                                                if replyCommentComplaint:
                                                    resp = postV1CommentReplyComplaint(replyid)
                                                    checkV1CommentComplaint(resp)
                                                    replyCommentComplaint = False
                                break

                        else:
                            text = titleName+"_"+str(episodeNo)
                            ##评论非法词
                            if commentIllegal:
                                cutomizeV1Comment(titleNo,episodeNo,text="admin")
                                commentIllegal = False
                            for t in range(0, 21):
                                logger.info("%s-第%s次发表评论" % (titleNo, t))
                                # text = getFormateTime()+text
                                id = cutomizeV1Comment(titleNo,episodeNo,text=getFormateTime()+text)
                                if id:
                                    parentids[id] = [titleNo, episodeNo]
                                    ##为自己评论点赞
                                    if commentLike:
                                        resp = postV1CommentLike(id,titleNo, episodeNo)
                                        checkV1CommentLike(resp)
                                        commentLike = False
                                    ##举报自己的评论
                                    if commentComplaint:
                                        resp = postV1CommentComplaint(id)
                                        checkV1CommentComplaint(resp)
                                        commentComplaint = False
                                    ##回复非法词
                                    if replyCommentIllegal:
                                        customizeV1CommentReply(id, titleNo, episodeNo, "admin")
                                        replyCommentIllegal = False

                                    for rt in range(0, 11):
                                        logger.info("%s-第%s次发表评论，第%s次发表回复" % (titleNo,t,rt))
                                        replyid = customizeV1CommentReply(id, titleNo, episodeNo, text + "_" + str(rt))
                                        if replyid:
                                            parentids[id].append(replyid)
                                            ##为自己回复点赞
                                            if replyCommentLike:
                                                resp = postV1CommentReplyLike(replyid, titleNo, episodeNo)
                                                checkV1CommentLike(resp)
                                                replyCommentLike = False
                                            ##举报自己的回复
                                            if replyCommentComplaint:
                                                resp = postV1CommentReplyComplaint(replyid)
                                                checkV1CommentComplaint(resp)
                                                replyCommentComplaint = False

                        break
    return parentids



def likeComplaint(parentids):
    login(Config("email"),Config("passwd"))
    ###，点赞，举报
    for id,titleinfo in parentids.items():
        titleNo = titleinfo[0]
        episodeNo = titleinfo[1]
        data = postV1CommentLike(id,titleNo,episodeNo)
        checkV1CommentLike(data)
        data = postV1CommentComplaint(id)
        checkV1CommentComplaint(data)
        for replyId in titleinfo[2:]:
            data = postV1CommentReplyLike(replyId,titleNo,episodeNo)
            checkV1CommentLike(data)
            data = postV1CommentReplyComplaint(replyId)
            checkV1CommentComplaint(data)

    ##取消点赞
    for id,titleinfo in parentids.items():
        titleNo = titleinfo[0]
        episodeNo = titleinfo[1]
        data = postV1CommentLike(id,titleNo,episodeNo,flag='cancelLike')
        checkV1CommentLike(data)
        for replyId in titleinfo[2:]:
            data = postV1CommentReplyLike(replyId,titleNo,episodeNo,flag='cancelLike')
            checkV1CommentLike(data)

def queryComment(parentids):
    ##定位查询，v2comment查询,v1comment_reply回复查询
    for id,titleinfo in parentids.items():
        titleNo = titleinfo[0]
        episodeNo = titleinfo[1]
        res1 = v2Comment(titleNo,episodeNo)
        checkV2CommentJson(res1)
        res2 = v2Comment(titleNo,episodeNo,sortBy="favourite")
        checkV2CommentJson(res2)
        res3 = v1CommentDetail(titleNo,episodeNo,id)
        checkV1CommentDetailJson(res3)
        for replyid in titleinfo[2:]:
            res4 = v1CommentDetail(titleNo,episodeNo,id,replyid)
            checkV1ReplyCommentDetailJson(res4)
        checkV2Comment(titleNo,episodeNo)
        checkV2Comment(titleNo,episodeNo,sortBy="favourite")
        checkV1CommentGet(id)


def getFormateTime():
    time_now = datetime.datetime.now()
    otherStyleTime = time_now.strftime(" %Y-%m-%d %H:%M:%S ")
    return otherStyleTime


def UnnormalTest():
    pass


if __name__ == "__main__":
    # logger.info("\n"*10)
    # logger.info("*"*100)
    # titleNos = [423,1419,918,1428]
    # # titleNos = [1419]
    # for titleNo in titleNos:
    #     login(Config("mobile"), Config("passwd"), loginType="PHONE_NUMBER")
    #     parentids = getParentsId(titleNos)
    #     if parentids:
    #         likeComplaint(parentids)
    #         queryComment(parentids)
    #         login(Config("mobile"), Config("passwd"), loginType="PHONE_NUMBER")
    #         #删除所有评论
    #         deleteAllComments()
    #         logger.info("*"*100)

    # login(Config("email"),Config("passwd"),Config("loginType"))
    pass