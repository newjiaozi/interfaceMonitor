#coding=utf-8

from openpyxl import load_workbook
import re
from cn.dongman.src.config import getCfgDict
import pymysql
import requests
from bs4 import BeautifulSoup
import faker
from multiprocessing import Process,Queue,Pool,Lock
import time



def getMWebUrl(env,envheaders):
    result=[]
    ssl = False
    mweb = getCfgDict(env)
    headers = getCfgDict(envheaders)
    if mweb.startswith("https"):
        ssl=True
    resp = getReq(mweb,headers=headers,timeout=10)
    resp_html = resp.text
    # print(resp_html)
    soup = BeautifulSoup(resp_html,"html.parser")
    ### 获取banner中的url
    a_eles = soup.find_all(attrs={"data-sc-name": "M_discover-page_banner"})
    result = handleReuslt(result, a_eles, mweb, ssl)

    ## 获取新作登场url  http://qam.dongmanmanhua.cn/new
    new = getReq(mweb+"/new",headers=headers,timeout=10)
    soup = BeautifulSoup(new.text, "html.parser")
    # print(new.text)
    a_eles = soup.find_all(attrs={"data-sc-name": "M_new-page_new-list-item"})
    result = handleReuslt(result, a_eles, mweb, ssl)

    ## 获取今日漫画url  http://qam.dongmanmanhua.cn/dailySchedule

    dailySchedule = getReq(mweb+"/dailySchedule",headers=headers,timeout=10)
    soup = BeautifulSoup(dailySchedule.text, "html.parser")
    a_eles = soup.find_all(attrs={"data-sc-name": re.compile(r"M_today-title-list-page_week-.*?-list-item")})
    result = handleReuslt(result, a_eles, mweb, ssl)

    ## 获取最爱的分类url https://qam.dongmanmanhua.cn/genre?genre=METROPOLIS
    ## https://qam.dongmanmanhua.cn/METROPOLIS/?sortOrder=READ_COUNT
    genre = getReq(mweb + "/genre",headers=headers,timeout=10)
    soup = BeautifulSoup(genre.text, "html.parser")
    # genre = getReq(mweb + "/METROPOLIS",params={"sortOrder":"READ_COUNT"},headers=headers)
    # soup = BeautifulSoup(genre.text, "html.parser")
    a_eles = soup.find_all(attrs={"data-sc-name":  re.compile(r"M_genre-page_.*?-genre-list-item")})
    result = handleReuslt(result, a_eles, mweb, ssl)

    ## 获取排行榜url  https://qam.dongmanmanhua.cn/top
    top = getReq(mweb + "/top",headers=headers,timeout=10)
    soup = BeautifulSoup(top.text, "html.parser")
    a_eles = soup.find_all(attrs={"data-sc-name": "M_rank-page_rank-list-item"})
    return mweb,headers,handleReuslt(result, a_eles, mweb, ssl)

##resp_html应该为list返回的html
def getViewerUrl(resp_html,env):
    result=[]
    ssl = False
    if env.startswith("https"):
        ssl=True
    soup = BeautifulSoup(resp_html,"html.parser")
    a_eles = soup.find_all(attrs={"data-sc-name": "M_detail-page_episode-list-btn"})
    result = handleReuslt(result, a_eles, env, ssl)
    # getViewerRequestUrl(headers,result)



def handleReuslt(result,a_eles,host,ssl):
    for a in a_eles:
        a_href = a["href"]
        if a_href.startswith("https"):
            pass
        elif a_href.startswith("http:"):
            pass
        elif a_href.startswith(r"//"):
            if ssl:
                a_href = "https:"+a_href
            else:
                a_href = "http:"+a_href
        elif a_href.startswith(r"/"):
            a_href = host+a_href

        if a_href not in result:
            result.append(a_href)
    return result


def getRequestUrl(host,headers,urls):
    # headers["X-Forwarded-For"] = getIP()
    for url in urls:
        resp = getReq(url,headers=headers,timeout=10)
        if resp:

            if resp.ok:
                # print("SUCCESS  CODE %s:URL %s" % (resp.status_code, url))
                getViewerUrl(resp.text,host)
            else:
                print("FAILURE  CODE %s:URL %s" % (resp.status_code,url))
                # print(resp.text)
        else:
            print("FAILURE  CODE %s:URL %s" % ("EXCEPTION", url))


def getViewerRequestUrl(headers,urls):
    # headers["X-Forwarded-For"] = getIP()
    for url in urls:
        resp = getReq(url,headers=headers,timeout=10)
        if resp:
            if resp.ok:
                # print("--SUCCESS  CODE %s:URL %s" % (resp.status_code, url))
                pass

            else:
                print("--FAILURE  CODE %s:URL %s" % (resp.status_code, url))
                # print(resp.text)
        else:
            print("FAILURE  CODE %s:URL %s" % ("EXCEPTION", url))


## 发送get 请求
def getReq(url,headers,timeout=10):
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        return resp

    except requests.exceptions.Timeout as e:
        print(e)



def getPCWebUrl(env,envheaders):
    result=[]
    ssl = False
    pcweb = getCfgDict(env)
    headers = getCfgDict(envheaders)
    if pcweb.startswith("https"):
        ssl=True
    resp = getReq(pcweb,headers=headers,timeout=10)
    resp_html = resp.text
    # print(resp_html)
    soup = BeautifulSoup(resp_html,"html.parser")
    ### 获取banner中的url
    a_eles = soup.find_all(attrs={"class": "banner_link"})
    result = handleReuslt(result, a_eles, pcweb, ssl)

    # ## 获取新作登场url  http://qam.dongmanmanhua.cn/new
    # new = getReq(pcweb+"/new",headers=headers,timeout=10)
    # soup = BeautifulSoup(new.text, "html.parser")
    # # print(new.text)
    # a_eles = soup.find_all(attrs={"data-sc-name": "M_new-page_new-list-item"})
    # result = handleReuslt(result, a_eles, pcweb, ssl)

    ## 获取今日漫画url  https://www.dongmanmanhua.cn/dailySchedule

    dailySchedule = getReq(pcweb+"/dailySchedule",headers=headers,timeout=10)
    soup = BeautifulSoup(dailySchedule.text, "html.parser")
    a_eles = soup.find_all(attrs={"class": re.compile(r"daily_card_item.*?")})
    result = handleReuslt(result, a_eles, pcweb, ssl)

    ## 获取最爱的分类url https://www.dongmanmanhua.cn/genre
    ## https://qam.dongmanmanhua.cn/METROPOLIS/?sortOrder=READ_COUNT
    genre = getReq(pcweb + "/genre",headers=headers,timeout=10)
    soup = BeautifulSoup(genre.text, "html.parser")
    # genre = getReq(mweb + "/METROPOLIS",params={"sortOrder":"READ_COUNT"},headers=headers)
    # soup = BeautifulSoup(genre.text, "html.parser")
    a_eles = soup.find_all(attrs={"class":  re.compile(r"card_item.*?")})
    result = handleReuslt(result, a_eles, pcweb, ssl)

    ## 获取排行榜url  https://www.dongmanmanhua.cn/top
    # top = getReq(pcweb + "/top",headers=headers,timeout=10)
    for i in range(1,11):
        for goal in ["MALE10","FEMALE10","MALE20","FEMALE20","MALE30","FEMALE30"]:
            top = getReq(pcweb + "/top?rankingGenre=%s&target=%s" % (i,goal),headers=headers,timeout=10)
            soup = BeautifulSoup(top.text, "html.parser")
            a_eles = soup.find_all(attrs={"data-sc-name": "PC_genre-rank-module_genre-rank-list-item"})
            result = handleReuslt(result, a_eles, pcweb, ssl)

    return pcweb,headers,handleReuslt(result, a_eles, pcweb, ssl)


def getIP():
    fa = faker.Faker()
    return fa.ipv4()

def getSession():
    pass

def getData():
    pass


def initDataFromDB():
    ms = getCfgDict("qamysql")
    conn = pymysql.connect(ms['host'],ms['user'],ms['passwd'],ms['db'])
    cursor = conn.cursor()

def getTestData(sheet,exec=7):
    wb = load_workbook("IM.xlsx")
    sheet = wb[sheet]
    data_tuple = tuple(sheet.rows)[1:]
    parsedData = parseData(data_tuple,exec)
    return parsedData

##将excel读取出的数据cell获取真正的数据返回格式为[[],[],[]]
def parseData(data_tuple,exec=7):
    def genParams():
        for i in data_tuple:
            single = []
            for j in i:
                single.append(j.value)
            if single[exec] and single[exec].strip().lower() == "yes":
                single = parseParams(single)
                yield single
    return genParams


def handleUSD(dict_obj):
    if isinstance(dict_obj,dict):
        for k,v in dict_obj.items():
            if isinstance(v,dict):
                handleUSD(v)
            elif isinstance(v,str) and v.startswith("${") and v.endswith("}"):
                matchObj = re.match(r"^\$\{(.*?)\((.*?)\)\}$",v)
                meth = matchObj.group(1)
                trans_prams = matchObj.group(2)
                if meth and trans_prams:
                    dict_obj[k]=eval(meth)(trans_prams)
                elif meth:
                    dict_obj[k] = eval(meth)()
    return dict_obj


def parseParams(params):
    host = ""
    path = ""
    url =""
    method =""
    headers={}
    cookies={}
    data={}
    payload = {}

    if params[0] and params[1]: ## url
        url = params[0].strip() + params[1].strip()
    if params[0]:
        host = params[0].strip()
    if params[1]:
        path = params[1].strip()
    ## method
    if params[2]:
        method = params[2].strip()
    ##headers
    if params[3]:
        headers = eval(params[3].strip())
        headers = handleUSD(headers)

    ## cookies
    if params[4]:
        cookies = eval(params[4].strip())
        cookies = handleUSD(cookies)

    ## data
    if params[5]:
        data = eval(params[5].strip())
        data = handleUSD(data)
    ##params payload
    if params[6]:
        payload = eval(params[6].strip())
        payload = handleUSD(payload)

    return {"host":host,"path":path,"url":url,"method":method,"headers":headers,"cookies":cookies,"data":data,"payload":payload}


## 获取所有title
def getTitleFromMysql(platform,cursor):
    ## 获取所有title
    querySql = 'select genre_new.gn_title as gname,title_group.title_group_name as tname,title.title_no as tn,title.display_platform as dp from  title,title_group,genre_new  where title.title_group_no = title_group.title_group_no  and title.represent_genre_new_code=genre_new.gn_id and title.language_code="SIMPLIFIED_CHINESE" and title.service_status_code = "SERVICE";'
    cursor.execute(querySql)
    title_groups = cursor.fetchall()
    newtg = []
    for tg in title_groups: ##能被3整除pc可以访问，被5整除mweb可以访问
        if tg[3]%platform == 0:
            newtg.append(tg)
    # for genre,name,title in title_groups:
    #     print(genre,name,title)
    return newtg

## 获取所有title对应的episode
def getEpisodeFromMysql(cursor,title):
    ## 获取所有episode
    querySql = 'select episode_title,episode_no from episode where service_status_code= "SERVICE" and title_no = %s'
    cursor.execute(querySql % title)
    episodes = cursor.fetchall()
    # for etitle,eno in episodes:
    #     print(etitle.lower(),eno)
    return episodes

def getCursor(key):
    sqlcfg = getCfgDict(key)
    db = pymysql.connect(sqlcfg["host"], sqlcfg["user"], sqlcfg["passwd"], sqlcfg["db"],sqlcfg["port"])
    cursor = db.cursor()
    return cursor

def closeCursor(cursor):
    try:
        cursor.close()
    except Exception as e:
        print(e)


def createUrl(urls,host,genre,name,titleno,ename,eno):
    p = re.compile(r'[-!/\[\]【】,（）$\)\(\^\%#\+&\*\.@？\?\\]')
    ename = re.sub(p,"",ename)
    ename = ename.lower()
    # print(ename)
    title_path = "/%s/%s/list?title_no=%s" % (genre,name,titleno)
    episode_path = "/%s/%s/%s/viewer?title_no=%s&episode_no=%s" % (genre,name,ename,titleno,eno)
    title_path = host + title_path
    episode_path = host + episode_path
    if title_path not in urls:
        urls.append(title_path)
    if episode_path not in urls:
        urls.append(episode_path)
    return urls


def initUrls(platform,sqlkey,webkey):
    cursor = getCursor(sqlkey)
    urls=[]
    host = getCfgDict(webkey)
    tg = getTitleFromMysql(platform,cursor)
    for g,n,t,p in tg:
        ep = getEpisodeFromMysql(cursor,t)
        for e,p in ep:
            urls = createUrl(urls,host,g,n,t,e,p)
    print("*****获取URLS成功！*****")
    closeCursor(cursor)
    return urls

##默认请求qam
def getReqUrls(platform=5,headers="qamheaders",sqlkey="qamysql",webkey="qamweb"):
    urls = initUrls(platform,sqlkey,webkey)
    headdata = getCfgDict(headers)
    successCount = 0
    for url in urls:
        # try:
        #     resp = requests.get(url,headers=headdata,timeout=20)
        #     rsc = resp.status_code
        #     if rsc == 200:
        #         successCount+=1
        #         # print(resp.status_code,successCount,url)
        #     elif rsc == 503:
        #         resp = requests.get(url, headers=headdata, timeout=20)
        #     else:
        #         print(resp.status_code,url)
        # except Exception as e:
        #     print(e, url)
        successCount = handleByCode(url,headdata,successCount=successCount,count=0)
    print("*****共%s个URL，成功%s个！*****" % (len(urls),successCount))


def multiprocessTarget(url,headers):
    handleByCode(url, headers, successCount=0, count=0)


def multiprocessHandle(platform=5,headers="qamheaders",sqlkey="qamysql",webkey="qamweb"):
    headdata = getCfgDict(headers)
    urls = initUrls(platform=platform,sqlkey=sqlkey,webkey=webkey)
    pool = Pool()
    for url in urls:
        pool.apply_async(multiprocessTarget,(url,headdata))
    print("*****构建多进程请求完成！*****")
    print("*****开始多进程请求！*****")
    pool.close()
    pool.join()
    print("*****共%s个URL！*****,请求完成！" % len(urls))



def handleByCode(url,headers,successCount=0,count=0):
    try:
        resp = requests.get(url,headers=headers,timeout=20)
        rsc = resp.status_code
        if rsc == 200:
            successCount+=1
            # print(resp.status_code,successCount,url)
        elif rsc == 503:
            if count > 3:
                print(resp.status_code)
                print(url)
            else:
                handleByCode(url, headers, successCount=successCount,count=count)
                count+=1
        elif rsc == 502:
            if count > 3:
                print(resp.status_code)
                print(url)
            else:
                handleByCode(url, headers, successCount=successCount,count=count)
                count+=1
        else:
            print(resp.status_code)
            print(url)
    except Exception as e:
        if count > 3:
            print(e, url)
        else:
            handleByCode(url, headers, successCount=successCount, count=count)
            count += 1
    return successCount







if __name__ == "__main__":
    # host,headers,result = getMWebUrl("qamweb","qamheaders")
    # getRequestUrl(host,headers,result)
    ## 默认qam
    # getReqUrls()
    ##pc
    getReqUrls(3,"qapcheaders","qamysql","qapcweb")
    # multiprocessHandle(3,"qapcheaders","qamysql","qapcweb")
