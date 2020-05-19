# coding="utf-8"

import requests
import base64,hashlib
import time,datetime
import os
import json
import multiprocessing
import threading
import faker
import pymysql
import redis
from cn.dongman.src.tools.logger import logger
from cn.dongman.src.tools.login import Config,getUUID



oslinesep = os.linesep
fake = faker.Faker()

## 生成expires和md5
def getExpiresMd5(pathstr,skey="the_scret_key"):
    now30 = datetime.datetime.now() + datetime.timedelta(minutes=30)
    utime = str(int(time.mktime(now30.timetuple())))
    msg = utime+" "+pathstr+" "+skey
    m = hashlib.md5()
    m.update(msg.encode(encoding="utf-8"))
    msg_md5 = m.digest()
    msg_md5_base64 = base64.urlsafe_b64encode(msg_md5)
    msg_md5_base64_str = msg_md5_base64.decode("utf-8")
    msg_md5_base64_str = msg_md5_base64_str.replace("=", "")
    return {"md5":msg_md5_base64_str,"expires":utime}

##更新页数据
def appHomeCard2(weekday):
    # logger.info("appHomeCard2")
    path ="/app/home/card2"
    payload = {"weekday":weekday,"v":3}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"))
    if resp.ok:
        result = {}
        resp_json = resp.json()
        # print(resp.text)
        # print(resp_json)
        ####处理更新页
        resulttmp = resp_json["message"]["result"]
        # print(resulttmp)
        if weekday == "COMPLETE":
            resulttmp["titleAndEpisodeList"].sort(key=lambda x: (x["mana"],x["titleNo"]), reverse=True)
            result["title"] = resulttmp["titleAndEpisodeList"]

        else:
            resulttmp["titleAndEpisodeList"].sort(key=lambda x:(x["mana"],x["titleNo"]),reverse=True)
            result["title"] = resulttmp["titleAndEpisodeList"]
            resulttmp["noticeCard"].sort(key=lambda x:int(x["exposurePosition"]))
            result["banner"] = resulttmp["noticeCard"]
        telist = []
        genrelist = appGenrelist2(False)
        for i in result["title"]:
            rg = i["representGenre"]
            i["representGenreCN"]= genrelist[rg]
            telist.append("%s-%s" % (i["titleNo"], i["episodeNo"]))
        result["titleEpisodeNos"] = telist
        logger.info(resp.url)
        return result
    else:
        logger.info(resp.url)
        logger.info(resp.text)



def appHome3(weekday):
    path ="/app/home3"
    payload = {"weekday":weekday,"v":3}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))

    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"))
    if resp.ok:
        result = {}
        resp_json = resp.json()
        # print(resp_json)
        ####处理发现页bigbanner
        resulttmp = resp_json["message"]["result"]
        topBanner = resulttmp["topBanner"]["bannerList"]
        topBanner.sort(key=lambda x:x["bannerSeq"],reverse=True)
        result["bigbanner"] = topBanner
        ###咚漫推荐
        result["dongman"] = resulttmp["dongmanRecommendContentList"]
        ##barbanner
        result["barbanner"] = resulttmp["bannerPlacementList"]
        ##分类
        result["genre"] = resulttmp["genre"]
        ##主题
        result["theme"] = resulttmp["webtoon_collection_list"]
        ##排行榜，上升榜，新作榜，总榜
        result["uprank"] = resulttmp["ranking"]["titleWeeklyRanking"]
        result["newrank"] = resulttmp["ranking"]["titleNewRanking"]
        result["totalrank"] = resulttmp["ranking"]["titleTotalRanking"]
        ##新作登场
        result["new"] = resulttmp["homeNew"]
        ##佳作抢先看
        result["lead"] = resulttmp["leadUpLookList"]
        ##猜你喜欢
        result["like"] = resulttmp["recommend_map_list"]
        return result
    else:
        print(resp.text)

def appHome4(weekday="MONDAY"):
    path ="/app/home4"
    payload = {"weekday":weekday,"v":1}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))

    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"),cookies=Config("cookies"))
    try:
        if resp.ok:
            result = {}
            resp_json = resp.json()
            logger.info(resp.url)
            ####处理发现页bigbanner
            resulttmp = resp_json["message"]["result"]
            topBanner = resulttmp["topBanner"]["bannerList"]
            # topBanner.sort(key=lambda x:x["bannerSeq"],reverse=True)
            result["bigbanner"] = topBanner
            ###咚漫推荐
            result["dongman"] = resulttmp["dongmanRecommendContentList"]
            ##barbanner
            result["barbanner"] = resulttmp["bannerPlacementList"]
            ##分类
            result["genre"] = resulttmp["genres"]
            ##主题
            result["theme"] = resulttmp["webtoon_collection_list"]
            ##排行榜，上升榜，新作榜，总榜
            result["uprank"] = resulttmp["ranking"]["titleWeeklyRanking"]
            result["newrank"] = resulttmp["ranking"]["titleNewRanking"]
            result["totalrank"] = resulttmp["ranking"]["titleTotalRanking"]
            ##新作登场
            result["new"] = resulttmp["homeNew"]
            ##佳作抢先看
            result["lead"] = resulttmp["leadUpLookList"]
            ##猜你喜欢
            result["like"] = resulttmp["recommend_map_list"]
            return result
        else:
            # logger.error(resp.url)
            logger.error(resp.text)
            return False

    except Exception:
        # logger.error(resp.url)
        logger.exception(resp.text)
        return False



def appHome4Priority(weekday="MONDAY"):
    path ="/app/home4"
    payload = {"weekday":weekday,"v":1,"homeDetailDataStatus":"LEAD_UP_DATA"}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))

    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"))
    if resp.ok:
        logger.info(resp.url)
        resp_json = resp.json()
        # print(resp_json)
        ####处理发现页bigbanner
        resulttmp = resp_json["message"]["result"]
        ###咚漫推荐
        return resulttmp["leadUpLookList"]
    else:
        logger.error(resp.url)
        logger.error(resp.text)

def appHome4DM(weekday="MONDAY"):
    path ="/app/home4"
    payload = {"weekday":weekday,"v":1,"homeDetailDataStatus":"RECOMMEND_DATA"}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))

    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"))
    if resp.ok:
        resp_json = resp.json()
        # print(resp_json)
        ####处理发现页bigbanner
        resulttmp = resp_json["message"]["result"]
        ###咚漫推荐
        return resulttmp["dongmanRecommendContentList"]
    else:
        print(resp.text)






### 发现页的，
# [{
# titleNo: 1262,
# language: "SIMPLIFIED_CHINESE",
# viewer: "SCROLL",
# title: "QA 13",
# writingAuthorName: "1-antiboss",
# pictureAuthorName: "1-antiboss",
# representGenre: "ANCIENTCHINESE",
# restTerminationStatus: "SERIES",
# restNotice: "",
# newTitle: false,
# hotTitle: false,
# ageGradeNotice: false,
# theme: "white",
# registerYmdt: 1523968575000,
# genreNewNo: 7,
# filmAdaptation: false,
# coinType: 0,
# defaultPrice: 0,
# thumbnail: "/88c7c38c-81d4-4455-b9c2-1bf0ed53864f.png",
# thumbnailIpad: "/43d1885d-daf6-448b-8c39-a32136a41f24.jpg",
# bgNewMobile: "/b1fa954c-952e-4913-9c46-c9dfc6f995b1.jpg",
# bgNewIpad: "/8158663d-33b9-4686-9f42-060a21653560.jpg",
# wideThumbnail: "/533898b7-ca3f-4072-91a0-cc7726d3d694.jpg",
# starScoreAverage: 0,
# readCount: 2976,
# favoriteCount: 0,
# mana: 0,
# rankingMana: 0,
# lastEpisodeRegisterYmdt: 1524050394000,
# groupName: "1-antiboss",
# synopsis: "QA 13",
# shortSynopsis: "QA 13",
# likeitCount: 0,
# latestEpisodeNo: 0,
# subGenre: [],
# weekday: [],
# totalServiceEpisodeCount: 5,
# serviceStatus: "SERVICE",
# titleWeekday: {},
# titleForSeo: "qa-13"
# }]

def appTitleList2():
    path ="/app/title/list2"
    payload = {"v":1}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"))
    if resp.ok:
        result_dict = {}
        resp_json = resp.json()
        result = resp_json["message"]["result"]["titleList"]["titles"]
        genredict = appGenrelist2(False)
        for i in result:
            if i["serviceStatus"] == "SERVICE":
                i["representGenrezh"]=genredict[i["representGenre"]]
                result_dict[i["titleNo"]] = i
        logger.info(resp.url)
        # logger.info(result_dict)
        return result_dict
    else:
        logger.info(resp.url)
        logger.info(resp.text)


### 发现页的，排行
def appTitleRanking():
    path ="/app/title/ranking"
    payload = {"v":3,"rankingType":"ALL"}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"))
    if resp.ok:
        result = {}
        resp_json = resp.json()
        # print(resp_json)
        resulttmp = resp_json["message"]["result"]
        result["uprank"] = resulttmp["titleWeeklyRanking"]["rankList"]
        result["newrank"] = resulttmp["titleNewRanking"]["rankList"]
        result["totalrank"] = resulttmp["titleTotalRanking"]["rankList"]
        return result
    else:
        print(resp.text)

##获取genre  分类数据
###
#[
# {
# color: "FF337F",
# index: 1,
# code: "LOVE",
# name: "恋爱"
# },
# {
# color: "046AFA",
# index: 2,
# code: "BOY",
# name: "少年"
# }]
def appGenrelist2(all=True):
    path ="/app/genreList2"
    payload = {"v":2}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"),cookies=Config("cookies"))
    if resp.ok:
        resp_json = resp.json()
        tmp = resp_json["message"]["result"]["genreList"]["genres"]
        if all:
            logger.info(resp.url)
            # logger.info(tmp)
            return tmp
        else:
            dict1={}
            for i in tmp:
                dict1[i["code"]]=i["name"]
            logger.info(resp.url)
            # logger.info(dict1)
            return dict1
    else:
        logger.error(resp.url)
        logger.error(resp.text)
        return False


###返回三个titleName
def everyOneWatching(titleNoList=""):
    path="/app/myComics/everyoneWatching"
    if titleNoList:
        payload = {"respTitleCount":3,"titleNoList":titleNoList,"v":3}
    else:
        payload = {"respTitleCount":3,"v":3}

    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"))
    if resp.ok:
        logger.info(resp.url)
        ranklist = resp.json()["message"]["result"]["rankList"]
        return ranklist
    else:
        logger.error(resp.url)
        logger.error(resp.text)
        return False

def appFavouriteTotalList2():
    path="/app/favorite/totalList2"
    payload= {"v":3}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"),cookies=Config("cookies"))
    if resp.ok:
        logger.info(resp.url)
        titles = resp.json()["message"]["result"]["titlelist"]["titles"]
        # titleName = []
        # for i in titles:
        #     titleName.append(i["title"])
        return titles
    else:
        logger.error(resp.url)
        logger.error(resp.text)
        return False

def v1CommentOwnAll():
    path="/v1/comment/ownall"
    payload= {"limit":20,"pageNo":1,"flag":None,"_id":None}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"),cookies=Config("cookies"))
    commentObjectId=[]
    commentList= resp.json()["data"]["commentList"]
    for comment in commentList:
        commentObjectId.append(comment["objectId"])
    commentObjectId = list(set(commentObjectId))
    titleEpisodeinfo = appCommentTitleepisodeinfo2(commentObjectId)
    result=[]
    for comment in commentList:
        result.append(commentList["contents"])
    return result


def v1CommentOwnAllOnlyIds():
    path="/v1/comment/ownall"
    payload= {"limit":20,"pageNo":1,"flag":None,"_id":None}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"),cookies=Config("cookies"))
        commentList= resp.json()["data"]["commentList"]
        commentIds = list(map(lambda x:x["_id"],commentList))
        logger.info(resp.url)
        return commentIds
    except Exception:
        logger.error(resp.url)
        logger.error(resp.text)
        return False




def deleteComment(id):
    path = "/v1/comment/%s" % id
    payload  = getExpiresMd5(path)
    resp = requests.delete(Config("httphost")+path,params=payload,headers=Config("headers"),cookies=Config("cookies"))
    if resp.ok:
        logger.info(resp.url)
        if resp.json()['code'] == 200:
            return True
    logger.error(resp.url)
    logger.error(resp.text)




def getGenreData(genre="all",status="all",sortby="人气"):
    genreDict = {"恋爱":"LOVE",
                 "少年":"BOY",
                 "古风":"ANCIENTCHINESE",
                 "奇幻":"FANTASY",
                 "搞笑": "COMEDY",
                 "校园": "CAMPUS",
                 "都市": "METROPOLIS",
                 "治愈": "HEALING",
                 "悬疑": "SUSPENSE",
                 "励志": "INSPIRATIONAL",
                 # "影视化":"FILMADAPTATION"
                 }
    statusDict = {"连载":"SERIES","完结":"TERMINATION"}
    sortList = ['人气','最新']
    path ="/app/title/list2"
    payload = {"v":1}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"))
    if resp.ok:
        result = []
        resp_json = resp.json()
        # print(resp_json)
        resulttmp = resp_json["message"]["result"]
        titles= resulttmp["titleList"]["titles"]
        genre = genre.strip().lower()
        status = status.strip().lower()
        sortby =  sortby.strip().lower()
        if genre == "all":
            if status == "all":
                if sortby == "人气":
                    titles.sort(key=lambda x:(x["mana"],x["titleNo"]),reverse=True)
                    print("ALL、ALL、人气:%s个" % len(titles))
                    for i in titles:
                        print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)

                elif sortby == "最新":
                    titles.sort(key=lambda x:(x["lastEpisodeRegisterYmdt"],x["titleNo"]),reverse=True)
                    print("ALL、ALL、最新:%s个" % len(titles))
                    for i in titles:
                        print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)
            elif status in statusDict:
                if sortby == "人气":
                    if status == "完结":
                        titles.sort(key=lambda x:(x["likeitCount"],x["titleNo"]),reverse=True)
                        result = list(filter(lambda x:x["restTerminationStatus"]==statusDict[status],titles))
                        print("ALL、%s、人气:%s个" % (status,len(result)))
                        for i in result:
                            print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)
                    else:
                        titles.sort(key=lambda x: (x["mana"], x["titleNo"]), reverse=True)
                        result = list(filter(lambda x: x["restTerminationStatus"] == statusDict[status], titles))
                        print("ALL、%s、人气:%s个" % (status, len(result)))
                        for i in result:
                            print(i['title'], i["subGenre"], i['restTerminationStatus'], i["mana"], i["titleNo"],
                                  "%s" % oslinesep)
                elif sortby == "最新":
                    titles.sort(key=lambda x:(x["lastEpisodeRegisterYmdt"],x["titleNo"]),reverse=True)
                    result = list(filter(lambda x:x["restTerminationStatus"]==statusDict[status],titles))
                    print("ALL、%s、最新:%s个" % (status,len(result)))
                    for i in result:
                        print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)

        elif genre in genreDict:
            if status == "all":
                if sortby == "人气":
                    titles.sort(key=lambda x:(x["mana"],x["titleNo"]),reverse=True)
                    result = list(filter(lambda x:genreDict[genre] in x["subGenre"] or genreDict[genre] == x["representGenre"] ,titles))
                    print("%s、ALL、人气:%s个" % (genre,len(result)))
                    for i in result:
                        print(i['title'],i["representGenre"],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)
                elif sortby == "最新":
                    titles.sort(key=lambda x:(x["lastEpisodeRegisterYmdt"],x["titleNo"]),reverse=True)
                    result = list(filter(lambda x:genreDict[genre] in x["subGenre"] or genreDict[genre] == x["representGenre"],titles))
                    print("%s、ALL、最新:%s个" % (genre,len(result)))
                    for i in result:
                        print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)
            elif status in statusDict:
                if sortby == "人气":
                    if status == "完结":
                        titles.sort(key=lambda x:(x["likeitCount"],x["titleNo"]),reverse=True)
                        result = list(filter(lambda x:x["restTerminationStatus"]==statusDict[status],titles))
                        result = list(filter(lambda x:genreDict[genre] in x["subGenre"] or genreDict[genre] == x["representGenre"],result))
                        print("%s、%s、人气:%s个" % (genre,status,len(result)))
                        for i in result:
                            print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)
                    else:
                        titles.sort(key=lambda x:(x["mana"],x["titleNo"]),reverse=True)
                        result = list(filter(lambda x:x["restTerminationStatus"]==statusDict[status],titles))
                        result = list(filter(lambda x:genreDict[genre] in x["subGenre"] or genreDict[genre] == x["representGenre"],result))
                        print("%s、%s、人气:%s个" % (genre,status,len(result)))
                        for i in result:
                            print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)
                elif sortby == "最新":
                    titles.sort(key=lambda x:(x["lastEpisodeRegisterYmdt"],x["titleNo"]),reverse=True)
                    result = list(filter(lambda x:x["restTerminationStatus"]==statusDict[status],titles))
                    result = list(filter(lambda x:genreDict[genre] in x["subGenre"] or genreDict[genre] == x["representGenre"],result))
                    print("%s、%s、最新:%s个" % (genre,status,len(result)))
                    for i in result:
                        print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)

        elif genre == "影视化":
            if status == "all":
                if sortby == "人气":
                    titles.sort(key=lambda x:(x["mana"],x["titleNo"]),reverse=True)
                    result = list(filter(lambda x:x["filmAdaptation"],titles))
                    print("%s、ALL、人气:%s个" % (genre,len(result)))
                    for i in result:
                        print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)
                elif sortby == "最新":
                    titles.sort(key=lambda x:(x["lastEpisodeRegisterYmdt"],x["titleNo"]),reverse=True)
                    result = list(filter(lambda x:x["filmAdaptation"],titles))
                    print("%s、ALL、最新:%s个" % (genre,len(result)))
                    for i in result:
                        print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)
            elif status in statusDict:
                if sortby == "人气":
                    if status == "完结":
                        titles.sort(key=lambda x:(x["likeitCount"],x["titleNo"]),reverse=True)
                        result = list(filter(lambda x:x["restTerminationStatus"]==statusDict[status],titles))
                        result = list(filter(lambda x:x["filmAdaptation"],result))
                        print("%s、%s、人气:%s个" % (genre,status,len(result)))
                        for i in result:
                            print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)
                    else:
                        titles.sort(key=lambda x:(x["mana"],x["titleNo"]),reverse=True)
                        result = list(filter(lambda x:x["restTerminationStatus"]==statusDict[status],titles))
                        result = list(filter(lambda x:genreDict[genre] in x["subGenre"] or genreDict[genre] == x["representGenre"],result))
                        print("%s、%s、人气:%s个" % (genre,status,len(result)))
                        for i in result:
                            print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)
                elif sortby == "最新":
                    titles.sort(key=lambda x:(x["lastEpisodeRegisterYmdt"],x["titleNo"]),reverse=True)
                    result = list(filter(lambda x:x["restTerminationStatus"]==statusDict[status],titles))
                    result = list(filter(lambda x:x["filmAdaptation"],result))
                    print("%s、%s、最新:%s个" % (genre,status,len(result)))
                    for i in result:
                        print(i['title'],i["subGenre"],i['restTerminationStatus'],i["mana"],i["titleNo"],"%s" % oslinesep)


def appCommentTitleepisodeinfo2(telist):
    path="/app/comment/titleEpisodeInfo2"
    telist2Json = json.dumps(telist)
    payload = {"objectIdsJson":telist2Json}
    payload.update(Config("baseparams"))
    resp = requests.post(Config("httphost")+path,params=getExpiresMd5(path),data=payload,headers=Config("headers"))
    commentTitleEpisodeInfo = resp.json()["message"]["result"]["commentTitleEpisodeInfo"]
    return commentTitleEpisodeInfo


def appTitleList2oo(args):
    path ="/app/title/list2"
    payload = {"v":1}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"))
        print(args, resp.status_code)
    except Exception as e:
        print(e.args)


def callBack(args):
    if args[1] != 200:
        print(args)

def multiProcess(target,pcount=10000,callback=callBack):
    pool = multiprocessing.Pool()
    for i in range(0,pcount):
        pool.apply_async(target,args=(i,),callback=callback)
    pool.close()
    start = datetime.datetime.now()
    print("multiprocessing start:%s " % start.strftime("%Y-%m-%d %H:%M:%S"))
    pool.join()
    end = datetime.datetime.now()
    print("multiprocessing end:%s " % end.strftime("%Y-%m-%d %H:%M:%S"))
    # print(type((end-start).total_seconds()))
    print("TPS: %.2f/s" % (pcount/(end-start).total_seconds()) )


def multiThread(target,pcount=1000):
    thread_list =[]
    for i in range(0,pcount):
        t = threading.Thread(target=target,args=(i,))
        thread_list.append(t)

    start = datetime.datetime.now()
    print("multiprocessing start:%s " % start.strftime("%Y-%m-%d %H:%M:%S"))
    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()
    end = datetime.datetime.now()
    print("multiprocessing end:%s " % end.strftime("%Y-%m-%d %H:%M:%S"))
    print("TPS: %.2f/s" % (pcount/(end-start).total_seconds()) )

## 获取人气页关注列表
def appMyFavorite2():
    path ="/app/myFavorite2"
    payload = {"v":3,"sortOrder":"UPDATE"}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"),cookies=Config("cookies"))
        logger.info(resp.url)
        titleEpisodeList = resp.json()["message"]["result"]["titleAndEpisodeList"]
        # telist=[]
        # for i in titleEpisodeList:
        #     telist.append("%s-%s" % (i["titleNo"],i["episodeNo"]))
        genrelist = appGenrelist2(False)
        for i in titleEpisodeList:
            rg = i["representGenre"]
            i["representGenreCN"]= genrelist[rg]
        return titleEpisodeList

    except Exception:
        logger.error(resp.url)
        logger.error(resp.text)
        return False

## 获取章节点赞数
def v1TitleLikeAndCount(titleEpisodeNos):
    path ="/v1/title/likeAndCount"
    payload = {"titleEpisodeNos":",".join(map(lambda x:str(x),titleEpisodeNos))}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"),cookies=Config("cookies"))
        data = resp.json()["data"]
        logger.info(resp.url)
        return data

    except Exception:
        logger.info(resp.url)
        logger.info(resp.text)
        return False



##获取关注列表
def appFavouriteTotalList2():
    path="/app/favorite/totalList2"
    payload = {"v":3}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"),cookies=Config("cookies"))
        logger.info(resp.url)
        return resp.json()["message"]["result"]["titleList"]["titles"]
    except Exception:
        logger.error(resp.url)
        logger.error(resp.text)
        return False


## 获取热词
def appGetHotWordNew():
    path = "/app/getHotWordNew"
    payload = {}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"))
        logger.info(resp.url)
        return resp.json()["message"]["result"]["hotWordList"]
    except Exception:
        logger.error(resp.url)
        logger.error(resp.text)
        return False

### 发表评论
def v1Comment(titleNo,episodeNo,text=""):
    path = "/v1/comment"
    titleNo = str(titleNo)
    episodeNo = str(episodeNo)
    text = str(text)
    objectId = "w_"+titleNo+"_"+episodeNo
    print(objectId)
    time_now = datetime.datetime.now()
    otherStyleTime = time_now.strftime("%Y-%m-%d %H:%M:%S")
    contents = text+"自动生成评论"+str(otherStyleTime)
    payload = {"categoryId":"",
               "categoryImage":"",
               "contents":contents,
               "episodeNo":episodeNo,
               "imageNo":"",
               "objectId":objectId,
               "titleNo":titleNo}
    payload.update(Config("baseparams"))
    try:
        resp = requests.post(Config("httphost")+path,params=getExpiresMd5(path),data=payload,headers=Config("headers"),cookies=Config("cookies"))
        print(resp.text)
        return resp.json()["code"]
    except Exception as e:
        print(e.args)


def initDataFromDB():
    ms = Config("qamysql")
    conn = pymysql.connect(ms['host'],ms['user'],ms['passwd'],ms['db'],ms["port"])
    cursor = conn.cursor()
    return conn,cursor

def getTitleFromMysql(platform,cursor):
    ## 获取所有title
    querySql = 'select title.title_no as tn,title.display_platform as dp from  title ' \
               'where title.language_code="SIMPLIFIED_CHINESE" ' \
               'and title.service_status_code = "SERVICE" ' \
               'order by title.title_no;'
    cursor.execute(querySql)
    title_platforms = cursor.fetchall()
    titles = []
    for tg in title_platforms: ##能被3整除pc可以访问，被5整除mweb可以访问7，和11，应该是app
        if tg[1] % platform == 0:
            titles.append(tg[0])
    # for genre,name,title in title_groups:
    #     print(genre,name,title)
    return titles

## 获取所有title对应的episode
def getEpisodeFromMysql(cursor,title):
    # print(title)
    ## 获取所有episode
    querySql = 'select episode_no from episode ' \
               'where service_status_code = "SERVICE" and title_no = %s'
    cursor.execute(querySql % title)
    episodes = cursor.fetchall()
    # print(episodes)
    newepisodes = []
    for e in episodes:
        newepisodes.append(e[0])
    # for etitle,eno in episodes:
    #     print(etitle.lower(),eno)
    # print(newepisodes)
    return newepisodes


def getAllTitleEpisode(platform):
    conn,cursor = initDataFromDB()
    title_episode = {}
    titles = getTitleFromMysql(platform,cursor)
    for title in titles:
        episodes = getEpisodeFromMysql(cursor,title)
        title_episode[title] = episodes
    conn.close()
    cursor.close()
    return title_episode

def deleteRedis(neo_id):
    # curTime = time.localtime()
    # str_timeB = str(curTime.tm_year)+str(curTime.tm_mon)+str(curTime.tm_mday)
    r = redis.Redis(host='r-2ze7889e17a315d4.redis.rds.aliyuncs.com', port=6379, password='dmred2017qUsa', db="0",decode_responses=True)
    pattern = "comment_frequency_*_%s" % neo_id
    k = r.keys(pattern=pattern)
    if k:
        r.delete(*k)
        logger.info("redis删除成功 %s" % k)
    else:
        logger.info("没有匹配到需要删除的redis")

### 点赞章节
def likeIt(titleNo,episodeNo,like=True):
    "https://qaapis02.dongmanmanhua.cn/v1/title/1288/episode/1/like?md5=hjORhXHriOgH0t2U3x6lXg&expires=1561087385855"
    path = "/v1/title/%s/episode/%s/like" % (titleNo,episodeNo)
    if like:
        flag = "like"
    else:
        print("取消点赞%s-%s" % (titleNo,episodeNo))
        flag = "cancelLike"
    # titleNo = str(titleNo)
    # episodeNo = str(episodeNo)

    payload = {"flag":flag}
    payload.update(Config("baseparams"))
    try:
        resp = requests.post(Config("httphost")+path,params=getExpiresMd5(path),data=payload,headers=Config("headers"),cookies=Config("cookies"))
        logger.info(resp.text)
        return resp.json()["code"]
    except Exception as e:
        print(e.args)


def v1CommentOwnAll4XingNeng(flag="",id="",pageNo=1,limit =30):
    path="/v1/comment/ownall"
    payload= {"limit":limit,"pageNo":pageNo,"flag":flag,"_id":id}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    resp = requests.get(Config("httphost")+path,params=payload,headers=Config("headers"),cookies=Config("cookies"))
    resp_json = resp.json()
    if resp_json["code"] == 200:
        print(resp_json)
        flag = "next"
        id = resp_json["data"]["commentList"][-1]["_id"]
        pageNo+=1
        return flag,id,pageNo
    else:
        print(resp.text)

### 发表回复
def v1CommentReply(titleNo,episodeNo,text=""):
    path = "/v1/comment_reply"
    titleNo = str(titleNo)
    episodeNo = str(episodeNo)
    text = str(text)
    objectId = "w_"+titleNo+"_"+episodeNo
    print(objectId)
    time_now = datetime.datetime.now()
    otherStyleTime = time_now.strftime("%Y-%m-%d %H:%M:%S")
    contents = text+"自动生成回复"+str(otherStyleTime)
    payload = {
               "contents":contents,
               "parentId":"5d230dc735c6c96b2dc0d2ba",
               "objectId":objectId}
    payload.update(Config("baseparams"))
    try:
        resp = requests.post(Config("httphost")+path,params=getExpiresMd5(path),data=payload,headers=Config("headers"),cookies=Config("cookies"))
        logger.info(resp.text)
        return resp.json()["code"]
    except Exception as e:
        print(e.args)

##获取自定义菜单
def appHomeMenus():
    path = '/app/home/menus'
    payload = {}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"))
        return resp.json()["message"]["result"]["menuList"]
    except Exception as e:
        print(e.args)


def appHomeMenuDetail(menuId):
    path='/app/home/menu/detail'
    payload = {"menuId":menuId}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"))
        return resp.json()["message"]["result"]
    except Exception as e:
        print(e.args)


def appHomeMenuModuleMore(menuId,moduleId):
    path='/app/home/menu/module/more'
    payload = {"menuId":menuId,"moduleId":moduleId}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"))
        result = resp.json()["message"]["result"]
        logger.info(resp.url)
        return result
    except Exception:
        logger.info(resp.url)
        logger.info(resp.text)
        return False



def appEpisodeInfoV3(titleNo,episodeNo,purchase=0,v=10):
    path='/app/episode/info/v3'
    payload = {"titleNo":titleNo,"episodeNo":episodeNo,"purchase":purchase,"v":v}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"))
        result = resp.json()["message"]["result"]["episodeInfo"]
        # logger.info(resp.url)
        # logger.info(result)
        return result
    except Exception:
        logger.exception(resp.url)
        logger.exception(resp.text)
        logger.exception("执行appEpisodeInfoV3异常")



def v1TitleEpisodeLikeCount(titleNo,episodeNos):
    path='/v1/title/%s/episode/likeAndCount' % titleNo
    payload = {"episodeNos":",".join(map(lambda x:str(x),episodeNos))}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"),cookies=Config("cookies"))
        result = resp.json()["data"]
        logger.info(resp.url)
        logger.info("v1TitleEpisodeLikeCount:%s" % resp.text)
        return result
    except Exception as e:
        logger.info(resp.url)
        logger.exception("v1TitleEpisodeLikeCount执行出异常")


def appTitleInfo2(titleNo):
    path='/app/title/info2'
    payload = {"titleNo":titleNo}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"))
        result = resp.json()["message"]["result"]["titleInfo"]
        logger.info(resp.url)
        # logger.info(result)
        return result
    except Exception as e:
        logger.info(resp.url)
        logger.info(resp.text)
        logger.exception("appTitleInfo2执行异常")

def appTitleRecommend2(titleNo):
    path='/app/title/recommend2'
    payload = {"titleNo":titleNo}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"),cookies=Config("cookies"))
        return resp.json()["message"]["result"]["recommend"]
    except Exception as e:
        print(e.args)

def appHomeLeaduplook():
    path = "/app/home/leadUpLook"
    payload = Config("baseparams")
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"),cookies=Config("cookies"))
        return resp.json()["message"]["result"]["leadUpLook"]
    except Exception as e:
        print(e.args)


def appHomeRecommend2():
    path='/app/home/recommend2'
    payload = Config("baseparams")
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"),cookies=Config("cookies"))
        return resp.json()["message"]["result"]["dongmanRecommendContentList"]
    except Exception as e:
        print(e.args)

def appPPLInfo(titleNo,episodeNo,v=5):
    path='/app/ppl/info'
    payload = {"titleNo":titleNo,"episodeNo":episodeNo,"v":v}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"),cookies=Config("cookies"))
        logger.info(resp.url)
        return resp.json()["message"]["result"]
    except Exception:
        logger.error(resp.url)
        logger.error(resp.text)
        return False

def appAuthorInfo2(titleNo):
    path = "/app/author/info2"
    payload = {"titleNo":titleNo}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"),cookies=Config("cookies"))
        logger.info(resp.url)
        return resp.json()["message"]["result"]["authorInfo"]
    except Exception:
        logger.error(resp.url)
        logger.error(resp.text)
        return False

def appEpisodeListV3(titleNo):
    path = "/app/episode/list/v3"
    # if lastUpdate:
    #     payload = {"titleNo":titleNo,"v":v,"startIndex":0}
    # else:
    #     payload = {"titleNo":titleNo,"v":v,"startIndex":startIndex,"pageSize":pageSize}
    payload = {"titleNo": titleNo, "v": 10}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"),cookies=Config("cookies"))
        result = resp.json()["message"]["result"]["episodeList"]
        # logger.info(resp.url)
        return result
    except Exception:
        logger.error(resp.url)
        logger.error("执行appEpisodeListV3异常")
        return False

def appEpisodeListHide(titleNo):
    path = "/app/episode/list/hide"
    # if lastUpdate:
    #     payload = {"titleNo":titleNo,"v":v,"startIndex":0}
    # else:
    #     payload = {"titleNo":titleNo,"v":v,"startIndex":startIndex,"pageSize":pageSize}
    payload = {"titleNo": titleNo, "v": 7}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"),cookies=Config("cookies"))
        return resp.json()["message"]["result"]["episodeList"]
    except Exception as e:
        print(e.args)




def appMemeberInfoV2():
    path = "/app/member/info/v2"
    payload = {}
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"),cookies=Config("cookies"))
        return resp.json()["message"]["result"]["member"]
    except Exception as e:
        print(e.args)


##0:12岁以下，1:13～15岁，2:16～18岁，3:19～22岁，4:23～25岁，5:26～35岁，6:36岁以上
##
def appUserpreferenceNewadd(ancientchinese,boy,campus,comedy,
                            fantasy,filmadaptation,healing,
                            inspirational,love,metropolis,suspense,termination,
                            isNewUser,age,gender):
    path = "/app/userPreference/newAdd"
    if age:
        if ancientchinese or boy or campus or comedy or fantasy or filmadaptation or healing or inspirational or love or metropolis or suspense or termination:
            payload = {"age":age,
                       "ancientChinese":ancientchinese,
                       "boy":boy,
                       "campus":campus,
                       "comedy":comedy,
                       "fantasy":fantasy,
                       "filmAdaptation":filmadaptation,
                       "gender":gender,
                       "healing":healing,
                       "inspirational":inspirational,
                       "love":love,
                       "metropolis":metropolis,
                       "suspense":suspense,
                       "termination":termination,
                       "isNewUser":isNewUser,
                       }
        else:
            payload = {"age":age,
                       "gender": gender,
                       "isNewUser":isNewUser,
                       }
    else:
        if ancientchinese or boy or campus or comedy or fantasy or filmadaptation or healing or inspirational or love or metropolis or suspense or termination:
            payload = {
                       "ancientChinese":ancientchinese,
                       "boy":boy,
                       "campus":campus,
                       "comedy":comedy,
                       "fantasy":fantasy,
                       "filmAdaptation":filmadaptation,
                       "gender":gender,
                       "healing":healing,
                       "inspirational":inspirational,
                       "love":love,
                       "metropolis":metropolis,
                       "suspense":suspense,
                       "termination":termination,
                       "isNewUser":isNewUser,
                       }
        else:
            payload = {
                        "gender": gender,
                        "isNewUser":isNewUser,
                       }
    payload.update(Config("baseparams"))
    payload.update(getExpiresMd5(path))
    try:
        # uuid = getUUID()
        uuid = "00000086592F46A59D81777788889999"
        # print(uuid)
        resp = requests.get(Config("httphost")+path, params=payload,headers=Config("headers"),cookies={"uuid":uuid})
        print(resp.url)
        return resp.json()["message"]["result"]["recommendList"]
    except Exception as e:
        # print("#"*20)
        print(e.args)



def getImageFromCDN(imagePath):
    host = "https://cdn.dongmanmanhua.cn"

    headers = {
               # ":method": "GET",
               # ":scheme": "https",
               # ":path": imagePath,
               # ":authority":"cdn.dongmanmanhua.cn",
               "accept": "image/*",
               "referer": "https://qam.dongmanmanhua.cn/",
               "user-agent": "dongman/2.2.0_qa_0826 (iPhone; iOS 12.3.1; Scale/3.00)",
               "accept-language": "zh-cn",
               "accept-encoding": "br, gzip, deflate",
               }
    resp = requests.get(host+imagePath,headers=headers,stream=True)
    if resp.ok:
        # print(resp.content)
        a = base64.b64encode(resp.content)
        # print(a.decode())
        return a.decode()

def convert_n_bytes(n, b):
    bits = b * 8
    return (n + 2 ** (bits - 1)) % 2 ** bits - 2 ** (bits - 1)

def convert_4_bytes(n):
    return convert_n_bytes(n, 4)

def getHashCode(s):
    h = 0
    n = len(s)
    for i, c in enumerate(s):
        h = h + ord(c) * 31 ** (n - 1 - i)
    return convert_4_bytes(h)

def caculateWhichTable(uuid):
    return abs(getHashCode(uuid)) % 50

def transArgs(*args):

    for i in args:
        print(i)

def appClientVersionLatest():
    path = "/app/client/version/latest"
    payload = Config("baseparams")
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"))
        logger.info(resp.url)
        return resp.json()["message"]["result"]["clientVersion"]
    except Exception:
        logger.error(resp.url)
        logger.error(resp.text)
        return False

def appClientVersion():
    path = "/app/client/version"
    payload = Config("baseparams")
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"))
        logger.info(resp.url)
        return resp.json()["message"]["result"]["clientVersion"]
    except Exception:
        logger.info(resp.url)
        logger.info(resp.text)
        return False

def appFavoriteAdd(titleNo):
    path = "/app/favorite/add"
    payload = Config("baseparams")
    payload.update(getExpiresMd5(path))
    payload.update({"titleNo":titleNo})
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"),cookies=Config("cookies"))
        logger.info(resp.url)
        return resp.json()["message"]["result"]
    except Exception:
        logger.error(resp.url)
        logger.error(resp.text)
        return False


def appFavoriteAdd(titleNo):
    path = "/app/favorite/add"
    payload = Config("baseparams")
    payload.update(getExpiresMd5(path))
    payload.update({"titleNo":titleNo})
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"),cookies=Config("cookies"))
        logger.info(resp.url)
        return resp.json()["message"]["result"]
    except Exception:
        logger.error(resp.url)
        logger.error(resp.text)
        return False


def appFavoriteTotalRemoveAll():
    path = "/app/favorite/totalRemoveAll"
    payload = Config("baseparams")
    payload.update(getExpiresMd5(path))
    try:
        resp = requests.get(Config("httphost") + path, params=payload, headers=Config("headers"),cookies=Config("cookies"))
        logger.info(resp.url)
        return resp.json()["message"]["result"]
    except Exception:
        logger.error(resp.url)
        logger.error(resp.text)
        return False




def testingConfigInfo(version="2.2.4"):
    path = "/testing/configInfo"
    payload = Config("baseparams")
    payload.update(getExpiresMd5(path))
    payload.update({"version":version})
    try:
        resp = requests.get("https://qaptsapis.dongmanmanhua.cn" + path, params=payload, headers=Config("headers"),cookies={"uuid":getUUID()})
        if resp.ok:
            logger.info(resp.url)
            result = resp.json()["message"]["result"]["data"]["oneKeyLogin"]
            logger.info(result)
            return result
    except Exception:
        logger.error(resp.url)
        return False


def saveNickname(cookies,nickname):
    path = "/app/member/save"
    payload = Config("baseparams")
    payload.update(getExpiresMd5(path))
    payload.update({"birthday":"2012 . 02 . 22","gender":"G","nickname":"✅%s" % nickname })
    try:
        resp = requests.get(Config("httphost")+ path, params=payload, headers=Config("headers"),cookies=cookies)
        if resp.ok:
            logger.info(resp.text)
            return resp.json()
    except Exception:
        logger.error(resp.url)
        return False





if __name__=="__main__":
    pass
    # login("13683581996","1988oooo")
    # genreDict = {"恋爱":"LOVE",
    #              "少年":"BOY",
    #              "古风":"ANCIENTCHINESE",
    #              "奇幻":"FANTASY",
    #              "搞笑": "COMEDY",
    #              "校园": "CAMPUS",
    #              "都市": "METROPOLIS",
    #              "治愈": "HEALING",
    #              "悬疑": "SUSPENSE",
    #              "励志": "INSPIRATIONAL",
    #              "影视化":"FILMADAPTATION"
    #              }
    # statusDict = {"连载":"SERIES","完结":"TERMINATION"}
    # sortList = ['人气','最新']
    #
    # getGenreData(
    #              genre="all",
    #              status="all",
    #              sortby="人气")
    # print(v1CommentOwnAll())
    # multiThread(appTitleList2oo,pcount=1000)
    # res =appHomeCard2("SUNDAY")
    # for i in res["title"]:
    #     print(i["title"],i["titleNo"],i["lastEpisodeRegisterYmdt"],i['mana'],i["updateKey"],i["likeitCount"])



    # 请求评论，以及点赞
    # title_episode = getAllTitleEpisode(11)
    # for title,episodes in title_episode.items():
    #     for episode in episodes:
    #         for i in range(0,15):
    #             code = v1Comment(title,episode,text=i)
    #             if code == 10005:
    #                 deleteRedis(neo_id)
            # likecode = likeIt(title,episode)
            # if likecode == 10010:
            #     likeIt(title, episode,like=False)
            #     likeIt(title, episode)


    ## 查询自己的评论，一页一页查询
    # result = v1CommentOwnAll4XingNeng()
    # while result:
    #     result = v1CommentOwnAll4XingNeng(*result)
    # print("运行结束")
    # for i in range(1,10000):
    #     code = v1CommentReply(1249,1,str(i))
    #     if code == 10005:
    #         deleteRedis(neo_id)
    #         v1CommentReply(1249, 1, str(i))

    # createEpisode()
    # print(appGetHotWordNew())

    # getImageFromCDN("/1547800799069133217.jpg?x-oss-process=image/format,webp")
    # print(appTitleInfo2(1428))
    # print(caculateWhichTable("A0C62E3FFA854545B361FF1C28CC090C"))
    # print(caculateWhichTable("D01F31657CAE4A119373FF78AB71FF0C"))
    # print(caculateWhichTable("A0C62E3FFA854545B361FF1C28CC090C"))
    # transArgs(1,23,4)
    # transArgs(1,23,4,False)
    # transArgs(1,23,4,True)
    # transArgs(1)
    # print(appClientVersion(),type(appClientVersion()))
    # print(v1TitleEpisodeLikeCount(1268,[76,75,74,72,73]))
    # trueCount = 0
    # totalCount = 1000
    # for i in range(0,totalCount):
    #     res = testingConfigInfo("2.2.4")
    #     if res:
    #         trueCount+=1
    # print("执行%s次，返回true %s次" % (totalCount,trueCount))
    # testingConfigInfo()
    # print(appHome4())
    appEpisodeInfoV3(1464,1)
