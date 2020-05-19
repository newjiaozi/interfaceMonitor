from cn.dongman.src.tools.handleSqlite import *
from cn.dongman.src.tools.login import *
from cn.dongman.src.tools.interface import *
import json


def initSession(conn,cursor):
    ##生成用户
    initPhone = 14400004000
    for i in range(1,100):
        mobile = str(initPhone+i)
        res = login(mobile,"563828","PHONE_VERIFICATION_CODE")
        if res:
            neoses = res[0]
            neoid = res[1]
            updateSession(conn,cursor,mobile,neoid,neoses)



def modifyNickname(tCount=100):
    initPhone = 14400004000
    conn, cursor = getCursor()
    for i in range(1,tCount):
        mobile = str(initPhone+i)
        session = getSession(cursor, mobile)
        cookies = {"neo_ses": session}
        saveNickname(cookies,mobile)



if __name__ == "__main__":
    pass
    # conn,cursor = getCursor()
    # initSession(conn,cursor)
    # conn.close()
    modifyNickname(30)