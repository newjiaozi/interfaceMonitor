from cn.dongman.src.tools.interface import *




if __name__ == "__main__":
    logger.info("#"*100)
    titleData = appTitleList2()
    if titleData:
        for titleNo,title in titleData.items():
            totalServiceEpisodeCount = title["totalServiceEpisodeCount"]
            episodeList = appEpisodeListV3(titleNo)
            # logger.info(episodeList)
            if episodeList:
                episodes = episodeList["episode"]
                for i in episodes:
                    if i["serviceStatus"] == "SERVICE":
                        episodeNo = i["episodeNo"]
                        episodeSeq = i["episodeSeq"]
                        if episodeNo != episodeSeq:
                            logger.info("TSEC:%s,No:%s,SEQ:%s,NAME:%s" % (totalServiceEpisodeCount,episodeNo,episodeSeq,title["title"]))
                        elif episodeNo != totalServiceEpisodeCount:
                            logger.info("TSEC:%s,No:%s,SEQ:%s,NAME:%s" % (totalServiceEpisodeCount,episodeNo,episodeSeq,title["title"]))
                        break
    logger.info("$"*100)



