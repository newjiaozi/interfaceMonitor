from cn.dongman.src.tools.getMongodb import *
from cn.dongman.src.tools.interface import *
import time


if __name__ == "__main__":

    client,db = getMongodbConnect()
    dbname = client["qadmcomment"]

    data = appTitleList2()
    for titleNo,title in data.items():
            if titleNo in [849,1228]:
                tsec = title["totalServiceEpisodeCount"]
                for episodeNo in range(1,tsec+1):
                    objectId = "w_%s_%s" % (titleNo,episodeNo)
                    if getCommentCount(dbname,objectId) >= 10:
                        res = getReplyLikeCount(dbname,objectId)
                        if res:
                            for i in res:
                                logger.info((title["title"],episodeNo,i["likeCount"],i["unLikeCount"],i["objectId"],i["contents"]))
                            time.sleep(30)

    logger.info("结束 "*50)





