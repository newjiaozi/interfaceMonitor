import requests


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
        # print(resp.status_code)
        print(resp.text)


if __name__ == "__main__":
    session = adminLogin()
    saveEpisode(session,5,20,1507)