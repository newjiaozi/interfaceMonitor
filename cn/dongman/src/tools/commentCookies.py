from cn.dongman.src.tools.login import Config
from cn.dongman.src.tools.interface import getExpiresMd5
from cn.dongman.src.tools.logger import logger
import datetime
import requests



### 发表评论
def v1Comment(titleNo,episodeNo,cookies,categoryImage="",categoryId="",imageNo="",text="",userType=""):
    path = "/v1/comment"
    titleNo = str(titleNo)
    episodeNo = str(episodeNo)
    text = str(text)
    objectId = "w_"+titleNo+"_"+episodeNo
    time_now = datetime.datetime.now()
    otherStyleTime = time_now.strftime("%Y-%m-%d %H:%M:%S")
    if not text:
        text = "自动生成评论_"+str(otherStyleTime)
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
        resp = requests.post(Config("httphost")+path,params=getExpiresMd5(path),data=payload,headers=Config("headers"),cookies=cookies)
        logger.info(resp.url)
        result = resp.json()
        return result
    except Exception:
        logger.exception("v1Comment出现异常")


### 发表回复
def v1CommentReply(parentId,titleNo,episodeNo,cookies,text=""):
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
        resp = requests.post(Config("httphost")+path,params=getExpiresMd5(path),data=payload,headers=Config("headers"),cookies=cookies)
        logger.info(resp.url)
        result = resp.json()
        return result
    except Exception:
        logger.exception("v1CommentReply发生异常")


def postV1CommentLike(id,titleNo,episodeNo,cookies,flag="like"):
    path = "/v1/comment/%s/like" % id
    titleNo = str(titleNo)
    episodeNo = str(episodeNo)

    payload = {
               "flag":flag,
               "titleNo":titleNo,
               "episodeNo":episodeNo,}
    payload.update(Config("baseparams"))
    try:
        resp = requests.post(Config("httphost")+path,params=getExpiresMd5(path),data=payload,headers=Config("headers"),cookies=cookies)
        logger.info(resp.url)

        result = resp.json()
        return result
    except Exception:
        logger.exception("postV1CommentLike发生异常")

def postV1CommentReplyLike(id,titleNo,episodeNo,cookies,flag="like"):
    path = "/v1/comment_reply/%s/like" % id
    titleNo = str(titleNo)
    episodeNo = str(episodeNo)
    payload = {
               "flag":flag,
               "titleNo":titleNo,
               "episodeNo":episodeNo,}
    payload.update(Config("baseparams"))
    try:
        resp = requests.post(Config("httphost")+path,params=getExpiresMd5(path),data=payload,headers=Config("headers"),cookies=cookies)
        logger.info(resp.url)

        result = resp.json()
        return result
    except Exception:
        logger.exception("vpostV1CommentReplyLike发生异常")


def v2Comment(titleNo,episodeNo,cookies,imageNo="",pageNo="",sortBy="",limit=""):
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
        resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"),cookies=cookies)
        logger.info(resp.url)
        if resp.ok:
            result = resp.json()
            if result["code"] == 200:
                return result
    except Exception:
        logger.exception("v2Comment发生异常")

def v1CommentImageCount(titleNo,episodeNo,ids):
    path = "/v1/comment/image/count"
    payload = {"titleNo":titleNo,
               "episodeNo":episodeNo,
               "ids":ids,
               "v":1}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"))
        logger.info(resp.url)
        if resp.ok:
            result = resp.json()
            if result["code"] == 200:
                return result
    except Exception:
        logger.exception("v1CommentImageCountt发生异常")



###查看回复
def v1CommentReplyGet(commentId,pageNo=1,limit=10):
    path = "/v1/comment_reply"
    payload = {
               "commentId":commentId,
               "pageNo":pageNo,
               "limit":limit}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"))
        logger.info(resp.url)

        result = resp.json()
        if result["code"] == 200:

            # logger.info(result['data']["commentReplyList"][0].keys())
            return result
    except Exception:
        logger.exception("v1CommentReplyGet发生异常")


##删除评论
def deleteComment(cookies,id):
    path = "/v1/comment/%s" % id
    payload = Config("baseparams")
    try:
        resp = requests.delete(Config("httphost")+path,params=getExpiresMd5(path),data=payload,headers=Config("headers"),cookies=cookies)
        logger.info(resp.url)
        if resp.ok:
            result = resp.json()
            logger.info(result)
            assert result["code"] == 200
            assert result["message"] == "请求成功！"
    except Exception:
        logger.exception("deleteComment发生异常")

##删除回复
def deleteCommentReply(cookies,id):
    path = "/v1/comment_reply/%s" % id
    payload = Config("baseparams")
    try:
        resp = requests.delete(Config("httphost")+path,params=getExpiresMd5(path),data=payload,headers=Config("headers"),cookies=cookies)
        logger.info(resp.url)
        if resp.ok:
            result = resp.json()
            logger.info(result)
            assert result["code"] == 200
            assert result["message"] == "请求成功！"
    except Exception:
        logger.exception("deleteCommentReply发生异常")


if __name__ == "__main__":
    pass