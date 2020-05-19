from cn.dongman.src.requirement.checkLikeIt import *
from cn.dongman.src.requirement.checkCommentAll import *
from cn.dongman.src.tools.admin import *
from cn.dongman.src.tools.handleRedis import *
from cn.dongman.src.tools.handleMongodb import *
from cn.dongman.src.tools.interface import *
from cn.dongman.src.tools.commentCookies import *
from cn.dongman.src.tools.handleCSV import *



def newTitleNewComment(new=True):
    if new:
        ##创建两种作品CUT和SCROLL：
        dataN = {"CUT":{},"SCROLL":{}}
        session  = adminLogin()
        for viewerType,value in dataN.items():
            titleName = "测试作品%s" % viewerType
            ## 创建title
            titleNo = saveTitle(session,titleName,viewerType=viewerType,status="READY")
            value["titleNo"] = titleNo
            ## 修改状态为STANDBY
            saveTitle(session,titleName,viewerType=viewerType,status="STANDBY",titleNo=titleNo)
            ## 新建章节
            saveEpisode(session,startNo=1,endNo=2,titleNo=titleNo)
            value["episodeNo"]=1
            if viewerType == "CUT":
                value["cutId"] = [1,2,3]
            ## 修改状态为SERVICE
            saveTitle(session,titleName,viewerType=viewerType,status="SERVICE",titleNo=titleNo)
    else:
        ##直接修改原来创建的作品
        dataN = {"CUT":{"titleNo":1464,"episodeNo":1,"cutId":[1,2,3]},"SCROLL":{"titleNo":1467,"episodeNo":1}}

    # logger.info("dataN:%s" % str(dataN))
    return dataN


def initCommentLikeit(dataN):
    client, db = getMongodbConnect()
    dbname_comment = client["qadmcomment"]
    dbname_likeit = client["qadmlikeit"]
    r = connectRedis()
    for viewerType, value in dataN.items():
        ##删除comment reply likeit mongodb数据
        titleNo = value["titleNo"]
        episodeNo = value["episodeNo"]
        cutId = value.get("cutId",[])
        ##删除评论数据
        deleteCommentDB(dbname_comment,titleNo)
        ##删除回复数据
        deleteReplyDB(dbname_comment,titleNo)
        ##删除likeit记录
        deletelikeItDB(dbname_likeit,titleNo)

        ##删除comment reply likeit redis数据
        ##set comment，reply 数为0
        setCommentCount(r,viewerType,titleNo,episodeNo,cutId)
        ##set likeit 数为0
        setLikeItCount(r,titleNo,episodeNo)

    logger.info("全部初始化成功，作品已没有任何点赞和评论数据")


def checkCommentAlls(data):
    initCommentLikeit(data)
    neo_ses,neo_id = login("weixindogs@163.com","qwe123")
    cookiesO={"neo_ses":neo_ses,"uuid":neo_id}

    testData = []
    for viewerType, value in data.items():
        titleNo = value["titleNo"]
        episodeNo = value["episodeNo"]
        if viewerType == "CUT":
            episodeInfo = appEpisodeInfoV3(titleNo, episodeNo)
            testData.append({"titleNo":titleNo,"episodeNo":episodeNo,"cookies":cookiesO,"categoryImage":"https://cdn.dongmanmanhua.cn%s" % episodeInfo["imageInfo"][0]["url"],"categoryId":"1","imageNo":"1","text":"","userType":""})
        else:
            testData.append({"titleNo":titleNo,"episodeNo":episodeNo,"cookies":cookiesO,"categoryImage":"","categoryId":"","imageNo":"","text":"","userType":""},)

    initPhone = 14400004000
    actionTimes = 10
    conn, cursor = getCursor()

    for data in testData:
        categoryId = data["categoryId"]
        titleNo = data["titleNo"]
        episodeNo = data["episodeNo"]

        ###1个特殊用户A，多个普通用户B1～B10，A发表评论，A回复当前评论，B1～B10回复评论;并点赞A的评论和回复；
        ##A发表评论
        parentId = comment(**data)
        if parentId:
            ##通过v2/comment接口确认查询结果总数
            logger.info("预期结果 --> showTotalCount:%s,count:%s,likeCount:%s,replyCount:%s" % (1, 1, 0, 0))
            assertV2Comment(titleNo,episodeNo,cookiesO,categoryId=categoryId,showTotalCount=1,count=1,likeCount=0,replyCount=0)
            ##A发表回复
            id = replyComment(parentId,titleNo,episodeNo,cookiesO)
            if id:
                ##通过v2/comment接口确认查询结果总数
                logger.info("预期结果 --> showTotalCount:%s,count:%s,likeCount:%s,replyCount:%s" % (2, 1, 0, 1))
                assertV2Comment(titleNo,episodeNo,cookiesO,categoryId=categoryId,showTotalCount=2,count=1,likeCount=0,replyCount=1)
                replyCounter = 1
                likeCommentCounter = 0
                likeReplyCounter = 0
                replyIds = []
                ##多个普通用户B1～B10,循环操作，发表回复，A评论点赞，A回复点赞
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

                ###操作完之后v2/comment确认数量
                logger.info("预期结果 --> showTotalCount:%s,count:%s,likeCount:%s,replyCount:%s" % (1+replyCounter,1,likeCommentCounter,replyCounter))
                assertV2Comment(titleNo,episodeNo,cookies,categoryId=categoryId,showTotalCount=1+replyCounter,count=1,likeCount=likeCommentCounter,replyCount=replyCounter)

                ###点击回复查看回复数据
                replyData = v1CommentReplyGet(parentId)
                if replyData:
                    replyDataCheck = checkV1CommentReply(replyData,id)
                    logger.info("预期结果 --> 回复数:%s,likeCount:%s" % (replyCounter,likeReplyCounter))
                    assert replyDataCheck["count"] == replyCounter
                    assert replyDataCheck["likeCount"] == likeReplyCounter

                ##确认取消点赞的操作
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

                ##确认取消评论点赞和回复点赞后的数据
                logger.info("预期结果 --> showTotalCount:%s,count:%s,likeCount:%s,replyCount:%s" % (1+replyCounter,1,likeCommentCounter,replyCounter))
                assertV2Comment(titleNo,episodeNo,cookies,categoryId=categoryId,showTotalCount=1+replyCounter,count=1,likeCount=likeCommentCounter,replyCount=replyCounter)

                ###确认取消回复点赞后的数据
                replyData = v1CommentReplyGet(parentId)
                if replyData:
                    replyDataCheck = checkV1CommentReply(replyData,id)
                    logger.info("预期结果 --> 回复数:%s,likeCount:%s" % (replyCounter,likeReplyCounter))
                    assert replyDataCheck["count"] == replyCounter
                    assert replyDataCheck["likeCount"] == likeReplyCounter

                ####B1～B10的回复数据
                if categoryId:
                    for i in range(1,actionTimes):
                        mobile = str(initPhone+i)
                        session = getSession(cursor,mobile)
                        cookies = {"neo_ses":session}
                        deleteCommentReply(cookies,replyIds[i-1])
                        replyCounter-=1
                        logger.info("预期结果 --> showTotalCount:%s,count:%s,likeCount:%s,replyCount:%s" % (
                        1 + replyCounter, 1, likeCommentCounter, replyCounter))

                        assertV2Comment(titleNo, episodeNo, cookies, categoryId=categoryId,
                                        showTotalCount=1 + replyCounter, count=1, likeCount=likeCommentCounter,
                                        replyCount=replyCounter)
                    ##删除A的回复数据
                    deleteCommentReply(cookiesO,id)
                    replyCounter -= 1
                    logger.info("预期结果 --> showTotalCount:%s,count:%s,likeCount:%s,replyCount:%s" % (
                    1 + replyCounter, 1, likeCommentCounter, replyCounter))

                    assertV2Comment(titleNo, episodeNo, cookies, categoryId=categoryId,
                                    showTotalCount=1 + replyCounter, count=1, likeCount=likeCommentCounter,
                                    replyCount=replyCounter)
                    ##删除A的评论数据
                    deleteComment(cookiesO,parentId)
                    logger.info("预期结果 --> showTotalCount:%s,count:%s,likeCount:%s,replyCount:%s" % (0, 0, 0, 0))

                    assertV2Comment(titleNo, episodeNo, cookies, categoryId=categoryId, showTotalCount=0, count=0,
                                    likeCount = None, replyCount = None)
                else:

                    ##先删除A评论
                    deleteComment(cookiesO,parentId)
                    logger.info("预期结果 --> showTotalCount:%s,count:%s,likeCount:%s,replyCount:%s" % (
                    1 + replyCounter, 1, likeCommentCounter, replyCounter))
                    assertV2Comment(titleNo, episodeNo, cookies, categoryId=categoryId, showTotalCount=1 + replyCounter, count=1,
                                    likeCount = likeCommentCounter, replyCount = replyCounter)

                    ##删除B1～B10用户的所有回复
                    for i in range(1,actionTimes):
                        mobile = str(initPhone+i)
                        session = getSession(cursor,mobile)
                        cookies = {"neo_ses":session}
                        deleteCommentReply(cookies,replyIds[i-1])
                        replyCounter-=1
                        logger.info("预期结果 --> showTotalCount:%s,count:%s,likeCount:%s,replyCount:%s" % (
                            1 + replyCounter, 1, likeCommentCounter, replyCounter))
                        assertV2Comment(titleNo, episodeNo, cookies, categoryId=categoryId,
                                        showTotalCount=1 + replyCounter, count=1,
                                        likeCount=likeCommentCounter, replyCount=replyCounter)
                    ##删除A回复
                    deleteCommentReply(cookiesO,id)
                    logger.info("预期结果 --> showTotalCount:%s,count:%s,likeCount:%s,replyCount:%s" % (0, 0, 0, 0))
                    assertV2Comment(titleNo, episodeNo, cookies, categoryId=categoryId, showTotalCount=0, count=0,
                                    likeCount=None, replyCount=None)

        logger.info("评论功能✅" * 10)
    logger.info("评论功能ALL✅" * 10)


def makeAdminComment(data,cTime=3,rTime=11):
    initPhone = 14400004000
    actionTimesComment = cTime
    actionTimesReply = rTime
    conn, cursor = getCursor()
    # logger.info("FORADMIN##" * 10)
    # logger.info("DATA:%s" % str(data))
    for viewerType, value in data.items():
        titleNo = value["titleNo"]
        episodeNo = value["episodeNo"]
        if viewerType == "CUT":
            episodeInfo = appEpisodeInfoV3(titleNo, episodeNo)
            testData = {"titleNo":titleNo,"episodeNo":episodeNo,"categoryImage":"https://cdn.dongmanmanhua.cn%s" % episodeInfo["imageInfo"][0]["url"],"categoryId":"1","imageNo":"1","text":"","userType":""}
        else:
            testData = {"titleNo":titleNo,"episodeNo":episodeNo,"categoryImage":"","categoryId":"","imageNo":"","text":"","userType":""}
        commentReplys = {}
        for i in range(1,actionTimesComment):
            mobile = str(initPhone + i)
            session = getSession(cursor, mobile)
            cookies = {"neo_ses": session}
            testData["cookies"] = cookies
            id = comment(**testData)
            if id:
                commentReplys[id]=[]
                for j in range(1,actionTimesReply):
                    mobileJ = str(initPhone + j)
                    sessionJ = getSession(cursor, mobileJ)
                    cookiesJ = {"neo_ses": sessionJ}
                    testData["cookies"] = cookiesJ
                    replyId = replyComment(id, titleNo, episodeNo, cookiesJ)
                    if replyId:
                        commentReplys[id].append(replyId)
        value["comment"] = commentReplys
    logger.info("makeAdminComment✅")
    return data


def makeAdminCommentComplaint(data,cTime=3,rTime=11):
    initPhone = 14400004000
    actionTimesComment = cTime
    actionTimesReply = rTime
    conn, cursor = getCursor()
    logger.info("FORADMIN##" * 10)

    neo_ses,neo_id = login("weixindogs@163.com","qwe123")
    cookiesO={"neo_ses":neo_ses,"uuid":neo_id}

    for viewerType, value in data.items():
        titleNo = value["titleNo"]
        episodeNo = value["episodeNo"]
        if viewerType == "CUT":
            episodeInfo = appEpisodeInfoV3(titleNo, episodeNo)
            testData = {"titleNo":titleNo,"episodeNo":episodeNo,"categoryImage":"https://cdn.dongmanmanhua.cn%s" % episodeInfo["imageInfo"][0]["url"],"categoryId":"1","imageNo":"1","text":"","userType":""}
        else:
            testData = {"titleNo":titleNo,"episodeNo":episodeNo,"categoryImage":"","categoryId":"","imageNo":"","text":"","userType":""}

        commentReplys = {}
        for i in range(1,actionTimesComment):
            mobile = str(initPhone + i)
            session = getSession(cursor, mobile)
            cookies = {"neo_ses": session}
            testData["cookies"] = cookies
            id = comment(**testData)
            if id:
                commentReplys[id]=[]
                commentComplaint(cookiesO,id)
                for j in range(1,actionTimesReply):
                    mobileJ = str(initPhone + j)
                    sessionJ = getSession(cursor, mobileJ)
                    cookiesJ = {"neo_ses": sessionJ}
                    testData["cookies"] = cookiesJ
                    replyId = replyComment(id, titleNo, episodeNo, cookiesJ)
                    if replyId:
                        commentReplys[id].append(replyId)
                        replyComplaint(cookiesO,replyId)
        value["comment"] = commentReplys
    return data


def actionFromCsvComment(session,data):
    ##args=[(),()],resport代表是不是举报，result代表是不是再次审核;type=1是评论type=2是回复;
    ##source=1通过或者待审核，2屏蔽；status：1通过，2通过；
    ##punishmentType,  ##2：单独屏蔽；1：整楼屏蔽 punishmentStatus,  ## 3：非法信息
    cases = read_csv("comment.csv")
    caseNum = 0
    for case in cases:
        caseNum+=1
        logger.info("正在执行第 %s 个 CASE" % caseNum)
        initCommentLikeit(data)
        dataN = makeAdminComment(data)
        for viewerType, value in dataN.items():
            titleNo = value["titleNo"]
            episodeNo = value["episodeNo"]
            commentData = value["comment"]  ##2条评论，20条回复
            if viewerType == "CUT":
                testData = {"titleNo": titleNo, "episodeNo": episodeNo, "categoryId": "1"}
            else:
                testData = {"titleNo": titleNo, "episodeNo": episodeNo, "categoryId": ""}

            keys_tuple = tuple(commentData.keys())
            if eval(case[18]):##第一步是否批量，## id,titleNo,episodeNo,
                args = [(keys_tuple[0],titleNo,episodeNo),(keys_tuple[1],titleNo,episodeNo)]
                logger.info("第1步批量操作")
                commentPunish(session, args, eval(case[0]), eval(case[1]), case[2], case[3], case[4], case[5], case[6])
            else:
                for id in keys_tuple:
                    args=[(id,titleNo,episodeNo)]
                    logger.info("第1步单独操作操作")
                    commentPunish(session, args, eval(case[0]), eval(case[1]), case[2], case[3], case[4], case[5], case[6])
            # time.sleep(2)
            if eval(case[19]):##第二部是否批量，## id,titleNo,episodeNo,
                logger.info("第2步批量操作")
                args = [(keys_tuple[0],titleNo,episodeNo),(keys_tuple[1],titleNo,episodeNo)]
                commentPunish(session, args, eval(case[7]), eval(case[8]), case[9], case[10], case[11], case[12],case[13])
            else:
                for id in keys_tuple:
                    args=[(id,titleNo,episodeNo)]
                    logger.info("第2步单独操作操作")
                    commentPunish(session, args, eval(case[7]), eval(case[8]), case[9], case[10], case[11], case[12],case[13])

            testData["cookies"]=""
            testData["showTotalCount"] = int(case[15])
            testData["count"] = int(case[14])
            if case[16] == "None":
                testData["replyCount"] = eval(case[16])
            else:
                testData["replyCount"] = int(case[16])
            if case[17] == "None":
                testData["likeCount"] = eval(case[17])
            else:
                testData["likeCount"] = int(case[17])
            assertV2Comment(**testData)
    logger.info("CHECK ADMIN COMMENT FINISH " * 10)


def actionFromCsvReply(session,data):
    ##args=[(),()],resport代表是不是举报，result代表是不是再次审核;type=1是评论type=2是回复;
    ##source=1通过或者待审核，2屏蔽；status：1通过，2通过；
    ##punishmentType,  ##2：单独屏蔽；1：整楼屏蔽 punishmentStatus,  ## 3：非法信息
    cases = read_csv("reply.csv")
    caseNum = 0
    for case in cases:
        caseNum+=1
        logger.info("正在执行第 %s 个 CASE" % caseNum)
        initCommentLikeit(data)
        dataN = makeAdminComment(data,cTime=2,rTime=3)
        for viewerType, value in dataN.items():
            titleNo = value["titleNo"]
            episodeNo = value["episodeNo"]
            commentData = value["comment"] ##一条评论，两条回复
            if viewerType == "CUT":
                testData = {"titleNo": titleNo, "episodeNo": episodeNo, "categoryId": "1"}
            else:
                testData = {"titleNo": titleNo, "episodeNo": episodeNo, "categoryId": ""}

            testData["cookies"] = ""
            keys_tuple = tuple(commentData.keys())
            ###case[3]是""就是不需要审核评论，就是 case[6] == "1" 就是评论整楼屏蔽情况，这时只有两步操作
            ###第一步，对评论进行处理，四种情况，待审核，审核通过，非整楼屏蔽，整楼屏蔽
            if case[3]:
                args = [(keys_tuple[0],titleNo,episodeNo)]
                commentPunish(session, args, eval(case[0]), eval(case[1]), case[2], case[3], case[4], case[5], case[6])
            testData["showTotalCount"] = int(case[8])
            testData["count"] = int(case[7])
            case9 = case[9]
            case10 = case[10]
            if case9 == "None":
                testData["replyCount"] = eval(case9)
            else:
                testData["replyCount"] = int(case9)
            if case10 == "None":
                testData["likeCount"] = eval(case10)
            else:
                testData["likeCount"] = int(case10)

            assertV2Comment(**testData)

            ###第二步，初次审核回复；如果第一步评论是整楼屏蔽状态，则就是最后一步
            if case[6] == "1":
                ###最后一步
                if eval(case[22]):
                    args = []
                    for parentid,ids in commentData.items():
                        for id in ids:
                            args.append((id,titleNo,episodeNo,parentid))
                    logger.info("最后一步批量操作")
                    commentPunish(session, args, eval(case[11]), eval(case[12]), case[13], case[14], case[15], case[16],case[17])
                else:
                    for parentid,ids in commentData.items():
                        for id in ids:
                            args= [(id,titleNo,episodeNo,parentid)]
                            logger.info("最后一步单独操作")
                            commentPunish(session, args, eval(case[11]), eval(case[12]), case[13], case[14], case[15],case[16], case[17])

                testData["showTotalCount"] = int(case[19])
                testData["count"] = int(case[18])
                case20 = case[20]
                case21 = case[21]
                if case20 == "None":
                    testData["replyCount"] = eval(case20)
                else:
                    testData["replyCount"] = int(case20)
                if case21 == "None":
                    testData["likeCount"] = eval(case21)
                else:
                    testData["likeCount"] = int(case21)

                assertV2Comment(**testData)
            else:
                ###第二步
                if eval(case[22]):
                    args = []
                    for parentid, ids in commentData.items():
                        for id in ids:
                            args.append((id, titleNo, episodeNo, parentid))
                    logger.info("第2步批量操作")
                    commentPunish(session, args, eval(case[11]), eval(case[12]), case[13], case[14], case[15], case[16],
                                  case[17])
                else:
                    for parentid, ids in commentData.items():
                        for id in ids:
                            args = [(id, titleNo, episodeNo, parentid)]
                            logger.info("第2步单独操作")
                            commentPunish(session, args, eval(case[11]), eval(case[12]), case[13], case[14], case[15],
                                          case[16], case[17])

                testData["showTotalCount"] = int(case[19])
                testData["count"] = int(case[18])
                case20 = case[20]
                case21 = case[21]
                if case20 == "None":
                    testData["replyCount"] = eval(case20)
                else:
                    testData["replyCount"] = int(case20)
                if case21 == "None":
                    testData["likeCount"] = eval(case21)
                else:
                    testData["likeCount"] = int(case21)

                assertV2Comment(**testData)
                ###第三步：

                if eval(case[34]):
                    args = []
                    for parentid, ids in commentData.items():
                        for id in ids:
                            args.append((id, titleNo, episodeNo, parentid))
                    logger.info("最后一步批量操作")
                    commentPunish(session, args, eval(case[23]), eval(case[24]), case[25], case[26], case[27], case[28],case[29])
                else:
                    for parentid, ids in commentData.items():
                        for id in ids:
                            args = [(id, titleNo, episodeNo, parentid)]
                            logger.info("最后一步单独操作")
                            commentPunish(session, args, eval(case[23]), eval(case[24]), case[25], case[26], case[27],case[28], case[29])

                testData["showTotalCount"] = int(case[31])
                testData["count"] = int(case[30])
                case32 = case[32]
                case33 = case[33]
                if case32 == "None":
                    testData["replyCount"] = eval(case32)
                else:
                    testData["replyCount"] = int(case32)
                if case33 == "None":
                    testData["likeCount"] = eval(case33)
                else:
                    testData["likeCount"] = int(case33)

                assertV2Comment(**testData)
    logger.info("CHECK ADMIN REPLY FINISH " * 10)


##likeit测试
def checkLikeit(data):
    for viewerType,value in data.items():
        titleNo = value["titleNo"]
        episodeNo = value["episodeNo"]
        logger.info("请求的titleNo:{}，episodeNo:{}".format(titleNo,episodeNo))
        ##点赞确认
        checkLikeAndCount(titleNo,episodeNo)
        ##取消点赞
        checkUnlikeAndCount(titleNo,episodeNo)
    logger.info("CHECK LIKEIT FINISH " * 10)



##一条评论，10条评论：评论APP中删除，查看数据，10
def testAppDeleteComment(data):
    initCommentLikeit(data)
    neo_ses,neo_id = login("weixindogs@163.com","qwe123")
    cookiesO={"neo_ses":neo_ses,"uuid":neo_id}
    data = handleData(data)
    for i in data:
        i["cookies"] = cookiesO
        commentId = comment(**i)
        if commentId:
            for j in range(0,10):
                replyComment(commentId,i["titleNo"],i["episodeNo"],cookiesO)
            assertV2Comment(i['titleNo'],i['episodeNo'],"",i['categoryId'],showTotalCount=11,count=1,likeCount=0,replyCount=10)
            deleteComment(cookiesO,commentId)
            assertV2Comment(i['titleNo'],i['episodeNo'],"",i['categoryId'],showTotalCount=11,count=1,likeCount=0,replyCount=10)
    logger.info("testAppDeleteComment✅")


##测试分页展示，评论和回复,50条评论，第一条评论30条评论
def testPageData(data):
    initCommentLikeit(data)
    neo_ses, neo_id = login("weixindogs@163.com", "qwe123")
    cookiesO = {"neo_ses": neo_ses, "uuid": neo_id}
    data = handleData(data)
    for i in data:
        logger.info(i)
        i["cookies"] = cookiesO
        firstId = ""
        for c in range(0,50):
            commentId = comment(**i)
            if commentId:
                if not firstId:
                    firstId = commentId

        for r in range(0, 30):
            replyComment(firstId, i["titleNo"], i["episodeNo"], cookiesO)

        assertV2Comment(i['titleNo'], i['episodeNo'], "", i['categoryId'], showTotalCount=80, count=50, likeCount=0,replyCount=30)

        for cp in range(1,6):
            res = v2Comment(i['titleNo'], i['episodeNo'], "", i['categoryId'],cp,"favorite",20)
            assert res["data"]["showTotalCount"] == 80
            assert res["data"]["count"] == 50

        for rp in range(1,4):
            res = v1CommentReplyGet(firstId,rp)
            assert res["data"]["count"] == 30
    logger.info("testPageData✅")


def handleData(data):
    testData= []
    for viewerType, value in data.items():
        titleNo = value["titleNo"]
        episodeNo = value["episodeNo"]
        if viewerType == "CUT":
            episodeInfo = appEpisodeInfoV3(titleNo, episodeNo)
            testData.append({"titleNo":titleNo,"episodeNo":episodeNo,"cookies":"","categoryImage":"https://cdn.dongmanmanhua.cn%s" % episodeInfo["imageInfo"][0]["url"],"categoryId":"1","imageNo":"1","text":"","userType":""})
        else:
            testData.append({"titleNo":titleNo,"episodeNo":episodeNo,"cookies":"","categoryImage":"","categoryId":"","imageNo":"","text":"","userType":""})
    return testData


##生成best
def caculateBest(data):
    initCommentLikeit(data)
    neo_ses, neo_id = login("weixindogs@163.com", "qwe123")
    cookiesO = {"neo_ses": neo_ses, "uuid": neo_id}
    data = handleData(data)

    initPhone = 14400004000
    actionTimes = 21
    conn, cursor = getCursor()
    for title in data:
        logger.info(title)
        title["cookies"] = cookiesO
        commentIds=[]
        ###三个要被成为best的评论
        for i in range(0,3):
            title["text"] = "✅%s" % i
            commentId = comment(**title)
            if commentId:
                commentIds.append(commentId)
        logger.info("生成三个原始BEST完成")

        ##再生成10个评论，并点赞以上三个评论共10个
        for i in range(1,actionTimes):
            mobile = str(initPhone+i)
            title["text"] = mobile
            session = getSession(cursor,mobile)
            cookies = {"neo_ses":session}
            title["cookies"] = cookies
            comment(**title)
            likeComment(commentIds[0],title["titleNo"],title["episodeNo"],cookies)
            likeComment(commentIds[1],title["titleNo"],title["episodeNo"],cookies)
            likeComment(commentIds[2],title["titleNo"],title["episodeNo"],cookies)
            logger.info("第%s个用户点赞，评论完成" % i)


if __name__ == "__main__":
    pass
    data = newTitleNewComment(False)   ###生成新的作品或者返回已经存在的作品
    session = adminLogin()   ##登陆admin获取session
    actionFromCsvComment(session,data) ###admin，comment的功能
    actionFromCsvReply(session,data)   ###adminn，reply的功能
    checkLikeit(data)      #### likeit的功能
    checkCommentAlls(data)   ####api评论的功能
    testAppDeleteComment(data)  ##app删除评论，数量是否减了，有回复数据
    testPageData(data)   ##测试评论和回复的分页数据中的count
    # caculateBest(data) ##生成能够成为best的数据
