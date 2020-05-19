import requests
from cn.dongman.src.tools.logger import logger


def adminLogin():
    session = requests.Session()
    url = "http://qaadmin02.dongmanmanhua.cn/login.nhn"
    headers = {
               "Content-Type":"application/x-www-form-urlencoded",
               "Host":"qaadmin02.dongmanmanhua.cn",
               "Origin":"http://qaadmin02.dongmanmanhua.cn",
               "Referer":"http://qaadmin02.dongmanmanhua.cn/?t=1563438667331",
               "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
               "X-Requested-With":"XMLHttpRequest",
               "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
               "Accept-Language": "zh-CN,zh;q=0.9",
               "charset": "utf-8",
               "Pragma": "no-cache",
               "Accept-Encoding": "gzip, deflate",
               "Upgrade-Insecure-Requests":"1",
               "Cache-Control":"no-cache",
               "Connection":"keep-alive"
               }

    data = {
            "userName":"cn001",
            "password": "e10adc3949ba59abbe56e057f20f883e",
            }

    cookies = {
        "timezoneOffset":"+8",
        "nhnuserlocale": "zh_CN",
        }

    resp = session.post(url,data=data,headers=headers,cookies=cookies)
    if resp.ok:
        logger.info("登陆admin成功")
        return session


def saveEpisode(session,startNo=13,endNo=14,titleNo=1249,isActivity=False):
    headers = {
               "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
               "Host":"qaadmin02.dongmanmanhua.cn",
               "Origin":"http://qaadmin02.dongmanmanhua.cn",
               "Referer":"http://qaadmin02.dongmanmanhua.cn/title/episodeInfo.nhn?titleNo=1577",
               "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
               "X-Requested-With":"XMLHttpRequest",
               "Accept":"*/*",
               "Accept-Language": "zh-CN,zh;q=0.9",
               "charset": "utf-8",
               "Pragma": "no-cache",
               }
    cookie = {
              "nhnuserlocale":"zh_CN",
              "Path": "/",
              }
    url = "http://qaadmin02.dongmanmanhua.cn/title/saveEpisode.nhn"


    for i in range(startNo,endNo):

        episodeTitle = "%s作品名称" % i
        shareMainTitle = "%s分享主标题" % i if isActivity else ""
        shareSubTitle = "%s分享副标题" % i if isActivity else ""
        imageListJson = '[{"titleNo":"%s","episodeNo":"%s","sortOrder":1,"cutId":1,"url":"/1563349229046150322.jpg","fileSize":"64622","width":"690","height":"1227","backgroundColor":null,"imageType":"COMMONIMG","episodeFunBtnImageList":[]},' \
                        '{"titleNo":"%s","episodeNo":"%s","sortOrder":2,"cutId":2,"url":"/1563349229514150323.jpg","fileSize":"254905","width":"690","height":"1227","backgroundColor":null,"imageType":"COMMONIMG","episodeFunBtnImageList":[]},' \
                        '{"titleNo":"%s","episodeNo":"%s","sortOrder":3,"cutId":3,"url":"/1563349229834150328.jpg","fileSize":"170341","width":"690","height":"1227","backgroundColor":null,"imageType":"COMMONIMG","episodeFunBtnImageList":[]}]' % (titleNo,i,titleNo,i,titleNo,i)

        data = {"type":"new",
                "titleNo":str(titleNo),
                "episodeNo":str(i),
                "episodeTitle": episodeTitle,
                "thumbnailImageUrl": "/1563350772113150325.png",
                "thumbnailAppBigImageUrl": "/1563349220828150320.png",
                "bgmUrl": "",
                "bgmSize": "",
                "bgmEncodingTargetYn": "N",
                "bgmStartImageUrl": "",
                "creatorNote": "作家的话",
                "serviceStatus": "STANDBY",
                "imageListJson": imageListJson,
                "isImmediatelyRegister": True,
                "reservationYmdt": "",
                "lastCutId": "3",
                "translatorSnapshotId": "",
                "dailyFeedImageUrl": "",
                "dailyFeedSnsImageUrl": "",
                "snsShareMessageWeibo": "",
                "shareMainTitle": shareMainTitle,
                "shareSubTitle": shareSubTitle,
                "topYN": "0",
                "snsShareMessageTwitter": "",
                "snsShareMessageTumblrName": "",
                "snsShareMessageTumblrDescription": "",
                "snsShareMessageReddit": "",
                "snsShareMessageLine": "",
                "exposureTime": "201907180600",
                "leadUp": "0",
                "price": "0",}
        resp = session.post(url,data=data,headers=headers,cookies=cookie)
        print(resp.text)


def commentPunishment(session,id,titleNo,episodeNo,source="1",status="2",punishmentStatus="3",punishmentType="2"):
    headers = {
               "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
               "Host":"qaadmin02.dongmanmanhua.cn",
               "Origin":"http://qaadmin02.dongmanmanhua.cn",
               "Referer":"http://qaadmin02.dongmanmanhua.cn/comment/list.nhn",
               "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
               "X-Requested-With":"XMLHttpRequest",
               "Accept":"*/*",
               "Accept-Language": "zh-CN,zh;q=0.9",
               "charset": "utf-8",
               "Pragma": "no-cache",
               }
    cookie = {
              "nhnuserlocale":"zh_CN",
              "Path": "/",
              }
    url = "http://qaadmin02.dongmanmanhua.cn/comment/punishment.nhn"

    data = {
        "ids": "%s_%s-%s_" % (id,titleNo,episodeNo),
        "source": source,    ##1:待审核
        "status": status,    #1：通过；2 ：屏蔽
        "punishmentStatus": punishmentStatus,  ## 3：非法信息
        "remark": "",
        "punishmentType": punishmentType,  ##2：单独屏蔽；1：整楼屏蔽
        "type": "1",   ##type=1：评论；2：回复
    }

    resp = session.post(url, data=data, headers=headers, cookies=cookie)
    logger.info(resp.text)


def commentPunishmentAll(session,args,source="1",status="2",punishmentStatus="3",punishmentType="2"): ##args=[(id,titleNo,episodeNo),(id,titleNo,episodeNo)]
    headers = {
               "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
               "Host":"qaadmin02.dongmanmanhua.cn",
               "Origin":"http://qaadmin02.dongmanmanhua.cn",
               "Referer":"http://qaadmin02.dongmanmanhua.cn/comment/list.nhn",
               "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
               "X-Requested-With":"XMLHttpRequest",
               "Accept":"*/*",
               "Accept-Language": "zh-CN,zh;q=0.9",
               "charset": "utf-8",
               "Pragma": "no-cache",
               }
    cookie = {
              "nhnuserlocale":"zh_CN",
              "Path": "/",
              }
    url = "http://qaadmin02.dongmanmanhua.cn/comment/punishment.nhn"

    idsList=[]

    for i in args:
        id = "%s_%s-%s_" % (i[0],i[1],i[2])
        idsList.append(id)

    print(",".join(idsList))
    data = {
        "ids": ",".join(idsList),
        "source": source,    ##1:待审核
        "status": status,    #1：通过；2 ：屏蔽
        "punishmentStatus": punishmentStatus,  ## 3：非法信息
        "remark": "",
        "punishmentType": punishmentType,  ##2：单独屏蔽；1：整楼屏蔽
        "type": "1",   ##type=1：评论；2：回复
    }

    resp = session.post(url, data=data, headers=headers, cookies=cookie)
    print(resp.text)


def commentReplyPunishment(session,id,titleNo,episodeNo,parentID,source="1",status="2",punishmentStatus="3",punishmentType="2"):
    headers = {
               "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
               "Host":"qaadmin02.dongmanmanhua.cn",
               "Origin":"http://qaadmin02.dongmanmanhua.cn",
               "Referer":"http://qaadmin02.dongmanmanhua.cn/comment/list.nhn",
               "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
               "X-Requested-With":"XMLHttpRequest",
               "Accept":"*/*",
               "Accept-Language": "zh-CN,zh;q=0.9",
               "charset": "utf-8",
               "Pragma": "no-cache",
               }
    cookie = {
              "nhnuserlocale":"zh_CN",
              "Path": "/",
              }
    url = "http://qaadmin02.dongmanmanhua.cn/comment/punishment.nhn"

    data = {
        "ids": "%s_%s-%s_%s" % (id,titleNo,episodeNo,parentID),
        "source": source,
        "status": status,    #1：通过；2 ：屏蔽
        "punishmentStatus": punishmentStatus,  ## 3：非法信息
        "remark": "",
        "punishmentType": punishmentType,  ##2：单独屏蔽；1：整楼屏蔽
        "type": "2",   ##type=1：评论；2：回复
    }

    resp = session.post(url, data=data, headers=headers, cookies=cookie)
    print(resp.text)


def commentReplyPunishmentAll(session,args,source="1",status="2",punishmentStatus="3",punishmentType="2"): ##args=[(id,titleNo,episodeNo),(id,titleNo,episodeNo)]
    headers = {
               "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
               "Host":"qaadmin02.dongmanmanhua.cn",
               "Origin":"http://qaadmin02.dongmanmanhua.cn",
               "Referer":"http://qaadmin02.dongmanmanhua.cn/comment/list.nhn",
               "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
               "X-Requested-With":"XMLHttpRequest",
               "Accept":"*/*",
               "Accept-Language": "zh-CN,zh;q=0.9",
               "charset": "utf-8",
               "Pragma": "no-cache",
               }
    cookie = {
              "nhnuserlocale":"zh_CN",
              "Path": "/",
              }
    url = "http://qaadmin02.dongmanmanhua.cn/comment/punishment.nhn"

    idsList=[]
    for i in args:
        id = "%s_%s-%s_%s" % (i[0],i[1],i[2],i[3])
        idsList.append(id)

    print(",".join(idsList))
    data = {
        "ids": ",".join(idsList),
        "source": source,
        "status": status,    #1：通过；2 ：屏蔽
        "punishmentStatus": punishmentStatus,  ## 3：非法信息
        "remark": "",
        "punishmentType": punishmentType,  ##2：单独屏蔽；1：整楼屏蔽
        "type": "2",   ##type=1：评论；2：回复
    }

    resp = session.post(url, data=data, headers=headers, cookies=cookie)
    print(resp.text)


def commentPunish(session,args,report=False,result=False,type="1",source="1",status="2",punishmentStatus="3",punishmentType="2"):
    ##args=[(),()],resport代表是不是举报，result代表是不是再次审核，type=1是评论type=2是回复，
    ##source=1通过或者待审核，2屏蔽；status：1通过，2通过；
    ##punishmentType,  ##2：单独屏蔽；1：整楼屏蔽 punishmentStatus,  ## 3：非法信息
    if report:
        url = "http://qaadmin02.dongmanmanhua.cn/comment/report/punishment.nhn"
        if result:
            referer = "http://qaadmin02.dongmanmanhua.cn/comment/report/result/list.nhn"
        else:
            referer = "http://qaadmin02.dongmanmanhua.cn/comment/report/list.nhn"
    else:
        url = "http://qaadmin02.dongmanmanhua.cn/comment/punishment.nhn"
        if result:
            referer = "http://qaadmin02.dongmanmanhua.cn/comment/result/list.nhn"
        else:
            referer = "http://qaadmin02.dongmanmanhua.cn/comment/list.nhn"

    headers = {
               "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
               "Host":"qaadmin02.dongmanmanhua.cn",
               "Origin":"http://qaadmin02.dongmanmanhua.cn",
               "Referer":referer,
               "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
               "X-Requested-With":"XMLHttpRequest",
               "Accept":"*/*",
               "Accept-Language": "zh-CN,zh;q=0.9",
               "charset": "utf-8",
               "Pragma": "no-cache",
               }
    cookie = {
              "nhnuserlocale":"zh_CN",
              "Path": "/",
              }

    idsList = []
    if type == "1": ##评论
        for i in args: ## id,titleNo,episodeNo,
            id = "%s_%s-%s_" % (i[0],i[1],i[2])
            idsList.append(id)
    elif type == "2": ##回复
        for i in args:  ## id,titleNo,episodeNo,parentid
            id = "%s_%s-%s_%s" % (i[0], i[1], i[2], i[3])
            idsList.append(id)
    data = {
        "ids": ",".join(idsList)+",",
        "source": source,
        "status": status,    #1：通过；2 ：屏蔽
        "punishmentStatus": punishmentStatus,  ## 3：非法信息
        "remark": "",
        "punishmentType": punishmentType,  ##2：单独屏蔽；1：整楼屏蔽
        "type": type,   ##type=1：评论；2：回复
    }

    # logger.info(data)
    resp = session.post(url, data=data, headers=headers, cookies=cookie)
    logger.info(resp.url)
    logger.info(resp.request.body)
    logger.info(resp.text)


##有titleNo就是编辑，没有就是新建##CUT，SCROLL，ACTIVITYAREA，MOTION##READY，STANDBY，SERVICE，PAUSE，FINISH
def saveTitle(session,titleName,viewerType="CUT",status="READY",titleNo=""):
    headers = {
               "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
               "Host":"qaadmin02.dongmanmanhua.cn",
               "Origin":"http://qaadmin02.dongmanmanhua.cn",
               "Referer":"http://qaadmin02.dongmanmanhua.cn/title/titleInfo.nhn",
               "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
               "X-Requested-With":"XMLHttpRequest",
               "Accept":"*/*",
               "Accept-Language": "zh-CN,zh;q=0.9",
               "charset": "utf-8",
               "Pragma": "no-cache",
               }
    cookie = {
              "nhnuserlocale":"zh_CN",
              "Path": "/",
              }
    url = "http://qaadmin02.dongmanmanhua.cn/title/saveTitle.nhn"
    data ={
        "writingAuthorNo": "1746",
        "pictureAuthorNo": "1746",
        "writingAuthorName": "author_neal",
        "pictureAuthorName": "author_neal",
        "representGenre": "DRAMA",
        "representGenreNew": "1",
        "weekday": "MONDAY",
        "storyType": "SHORT_STORY",
        "subGenre": "DRAMA",
        "subGenre": "HEARTWARMING",
        "subGenreNew": "6",
        "target": "MALE10",
        "target": "FEMALE10",
        "viewer": viewerType,  ##CUT，SCROLL，ACTIVITYAREA，MOTION
        "feeling": "HUMOR",
        "pictureStyle": "REAL",
        "title": titleName,
        "coinType": "1",
        "coinType": "2",
        "defaultPrice": "1",
        "synopsis": "简介简介",
        "shortSynopsis": "超短简介",
        "copyPhrase": "COPY PHRASE",
        "thumbnailMobileUrl": "/b6d7d7c5-a990-47ea-afb2-1c03a2241d87.jpg",
        "thumbnailIpadUrl": "/9c7e5c0d-58b0-4801-b25f-42d8e597347d.jpg",
        "thumbnailAppBigImageUrl": "/82b04a63-8aef-4283-a7a7-8a1a5e5bf83d.jpg",
        "bgNewMobileUrl": "/fbaf1fb2-7212-43cb-9538-401527dbf7a8.png",
        "bgNewIpadUrl": "/7dd2ab29-6fac-45ac-a384-5909429ef54f.jpg",
        "backgroundMobileUrl": "/dda00f7c-0fff-40d2-9f60-c450277de7bc.jpg",
        "backgroundIpadUrl": "",
        "theme": "white",
        "serviceStatus": status, ##READY，STANDBY，SERVICE，PAUSE，FINISH
        "restTerminationStatus": "SERIES",
        "restNotice": "",
        "newTitle": False,
        "pcMainWideThumbnailUrl": "/46ad13b0-63b6-4941-83d9-e6453506df54.jpg",
        "pcInfoImageUrl": "/ddbdd25d-9726-429a-9c16-0481908484de.png",
        "pcInfoBackgroundUrl": "/1d8b996e-78de-4302-9033-f5ad61494b97.jpg",
        "titleGroupNo": "1144",
        "seoTitleDescription": "",
        "seoViewerDescription": "",
        "userTranslationYN": False,
        "ageGradeNoticeYN": False,
        "dailyFeed": False,
        "snsShareMessageWeibo": "",
        "snsShareMessageTwitter": "",
        "snsShareMessageLine": "",
        "recommend": "0",
        "recommendImage": "/fa3032a7-68fa-4107-8f30-39104593276c.jpg",
        "fontColor": "1",
        "titleDesc": "作品简介。。",
        "filmadaptation": False,
        "shareMainTitle": "",
        "shareSubTitle": "",
        "titleNo":titleNo,
    }
    if not titleNo:
        data.pop("titleNo")
    resp = session.post(url, data=data, headers=headers, cookies=cookie)
    resp_json = resp.json()
    if resp_json["success"] == True:

        return resp_json['title']["titleNo"]


if __name__ == "__main__":
    session = adminLogin()
    # saveEpisode(session,5,20,1507)
    # commentPunishmentAll("sss",[(1,2,3),(4,5,6)])

    ## 第一步，创建作品
    ##CUT，SCROLL，ACTIVITYAREA，MOTION
    viewerType = "SCROLL"
    titleName = "测试作品%s" % viewerType
    titleNo = saveTitle(session,titleName,viewerType=viewerType,status="READY")
    ## 修改状态为STANDBY
    saveTitle(session,titleName,viewerType=viewerType,status="STANDBY",titleNo=titleNo)
    ## 新建章节
    saveEpisode(session,startNo=1,endNo=2,titleNo=titleNo)
    ## 修改状态为SERVICE
    saveTitle(session,titleName,viewerType=viewerType,status="SERVICE",titleNo=titleNo)
