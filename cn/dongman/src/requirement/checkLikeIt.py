from cn.dongman.src.tools.handleSqlite import getSession,getCursor
from cn.dongman.src.tools.login import Config,getExpiresMd5
from cn.dongman.src.tools.logger import logger
from cn.dongman.src.tools.handleRedis import *
import requests



### 点赞章节
def likeIt(cookies,titleNo,episodeNo,like=True):
    path = "/v1/title/%s/episode/%s/like" % (titleNo,episodeNo)
    if like:
        flag = "like"
    else:
        # print("取消点赞%s-%s" % (titleNo,episodeNo))
        flag = "cancelLike"

    payload = {"flag":flag}
    payload.update(Config("baseparams"))
    try:
        resp = requests.post(Config("httphost")+path,params=getExpiresMd5(path),data=payload,headers=Config("headers"),cookies=cookies)
        return resp.json()
    except Exception:
        logger.info(resp.text)
        logger.exception("点赞章节异常")

### 查询章节点赞数
def likeAndCount(cookies,titleNo,episodeNo):
    path = "/v1/title/%s/episode/likeAndCount" % titleNo
    payload = {"episodeNos":episodeNo}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"),cookies=cookies)
        if resp.ok:
            resp_json = resp.json()
            return resp_json["data"][0]
        else:
            logger.error("点赞章节错误")
            logger.info(resp.text)
    except Exception:
        logger.exception("点赞章节异常")
        logger.info(resp.text)


def checkLikeAndCount(titleNo,episodeNo):
    initPhone = 14400004000
    actionTimes = 11
    conn, cursor = getCursor()
    initRes = likeAndCount("", titleNo, episodeNo)
    if initRes:
        logger.info("初始化数据为 {}".format(initRes))
        initData = initRes["count"]
        for i in range(1, actionTimes):
            mobile = str(initPhone + i)
            session = getSession(cursor, mobile)
            cookies = {"neo_ses": session}
            res = likeIt(cookies,titleNo,episodeNo)
            if res:
                if res["code"] ==200:
                    resCount = likeAndCount(cookies, titleNo, episodeNo)
                    if resCount:
                        logger.info("请求结果数据为 {}".format(resCount))
                        assert resCount["count"] == initData + 11*i
                        assert resCount["like"] == 1


def checkUnlikeAndCount(titleNo,episodeNo):
    initPhone = 14400004000
    actionTimes = 11
    conn, cursor = getCursor()
    initRes = likeAndCount("", titleNo, episodeNo)
    if initRes:
        logger.info("初始化数据为 {}".format(initRes))
        initData = initRes["count"]
        for i in range(1, actionTimes):
            mobile = str(initPhone + i)
            session = getSession(cursor, mobile)
            cookies = {"neo_ses": session}
            res = likeIt(cookies,titleNo,episodeNo,False)
            if res:
                if res["code"] ==200:
                    resCount = likeAndCount(cookies, titleNo, episodeNo)
                    if resCount:
                        logger.info("请求结果数据为 {}".format(resCount))
                        assert resCount["count"] == initData - 11*i
                        assert resCount["like"] == 0

if __name__ == "__main__":
    checkList = [
        (762,1),
        # (762, 2),
        # (1428,2),
        # (918,1),
        # (1457,1)
    ]

    ##定时任务，修改redis
    # r = connectRedis()
    #
    #
    # logger.info(int(getHash(r,"title_like_count","762")))
    # logger.info(int(getHash(r,"title_like_count","1428")))
    # logger.info(int(getHash(r,"title_like_count","918")))
    # logger.info(int(getHash(r,"title_like_count","1457")))
    # logger.info(int(getHash(r,"episode_like_count","762-1")))
    # logger.info(int(getHash(r,"episode_like_count","762-2")))
    # logger.info(int(getHash(r,"episode_like_count","1428-2")))
    # logger.info(int(getHash(r,"episode_like_count","918-1")))
    # logger.info(int(getHash(r,"episode_like_count","1457-1")))
    #
    #
    # setHash(r,"title_like_count","762",0)
    # setHash(r,"title_like_count","1428",0)
    # setHash(r,"title_like_count","918",0)
    # setHash(r,"title_like_count","1457",0)
    # setHash(r,"episode_like_count","762-1",0)
    # setHash(r,"episode_like_count","762-2",0)
    # setHash(r,"episode_like_count","1428-2",0)
    # setHash(r,"episode_like_count","918-1",0)
    # setHash(r,"episode_like_count","1457-1",0)


    for i in checkList:
        logger.info("请求的titleNo:{}，episodeNo:{}".format(*i))
        checkLikeAndCount(i[0],i[1])
        checkUnlikeAndCount(i[0],i[1])
    logger.info("CHECK FINISH " * 10)


    # logger.info(int(getHash(r,"title_like_count","762")))
    # logger.info(int(getHash(r,"title_like_count","1428")))
    # logger.info(int(getHash(r,"title_like_count","1428")))
    # logger.info(int(getHash(r,"title_like_count","918")))
    # logger.info(int(getHash(r,"title_like_count","1457")))
    # logger.info(int(getHash(r,"episode_like_count","762-1")))
    # logger.info(int(getHash(r,"episode_like_count","762-2")))
    # logger.info(int(getHash(r,"episode_like_count","1428-2")))
    # logger.info(int(getHash(r,"episode_like_count","918-1")))
    # logger.info(int(getHash(r,"episode_like_count","1457-1")))