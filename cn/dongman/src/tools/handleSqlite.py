import sqlite3
from cn.dongman.src.tools.logger import logger
import os

def createConfig():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    # cursor.execute('''create table configInter(cfgKey varchar(20) primary key,cfgValue varchar(200)) ''')
    cursor.execute('''create table userSession(mobile varchar(11) primary key,neoid varchar(50),neoses varchar(300)) ''')
    conn.commit()
    conn.close()


def getCursor():
    sqlite3_path = os.path.join(os.path.dirname(__file__), "..", "tools", "db.sqlite3")
    conn = sqlite3.connect(sqlite3_path)
    cursor = conn.cursor()
    return conn,cursor

def insertConfig(cursor,cfgKey,cfgValue):
    sql = '''insert into configInter(cfgKey,cfgValue) values(?,?)'''
    cursor.execute(sql, (cfgKey,cfgValue))


def updateConfig(cfgKey,cfgValue):
    conn,cursor = getCursor()
    sql = '''update configInter set cfgValue = ? where cfgKey= ?'''
    cursor.execute(sql, (cfgValue,cfgKey))
    conn.commit()
    conn.close()
    logger.info("更新%s：%s" % (cfgKey,cfgValue))



def getConfig(cfgKey):
    conn,cursor = getCursor()
    sql = '''select cfgValue from configInter where cfgKey=?'''
    cursor.execute(sql,(cfgKey,))
    res = cursor.fetchone()
    # logger.info(res)
    # logger.info("getConfig获取%s：%s" % (cfgKey,res[0]))
    conn.close()
    return res[0]


def insertSession(conn,cursor,mobile,neoid,neoses):
    sql = '''insert into userSession(mobile,neoid,neoses) values(?,?,?)'''
    cursor.execute(sql, (mobile,neoid,neoses))
    conn.commit()
    logger.info("插入新数据：%s：%s" % (mobile,neoses))

def updateSession(conn,cursor,mobile,neoid,neoses):
    if getSession(cursor,mobile):
        sql = '''update userSession set neoses = ?,neoid= ? where mobile= ?'''
        cursor.execute(sql, (neoses,neoid,mobile))
        conn.commit()
        logger.info("更新%s：%s" % (mobile,neoses))
    else:
        insertSession(conn,cursor,mobile,neoid,neoses)

def getSession(cursor,mobile):
    sql = '''select neoses from userSession where mobile=?'''
    cursor.execute(sql,(mobile,))
    res = cursor.fetchone()

    if res:
        return res[0]
    else:
        return None

def getNeoid(cursor,mobile):
    sql = '''select neoid from userSession where mobile=?'''
    cursor.execute(sql,(mobile,))
    res = cursor.fetchone()

    if res:
        return res[0]
    else:
        return None

def getMobileNeoidNeoses(cursor,mobile):
    sql = '''select mobile,neoid,neoses from userSession where mobile=?'''
    cursor.execute(sql,(mobile,))
    res = cursor.fetchone()
    if res:
        return res
    else:
        return None

if __name__ == "__main__":
    pass
    createConfig()
    # conn,cursor = getCursor()
    # insertConfig(cursor,"ipv4","000")
    # insertConfig(cursor, "neo_id", "000")
    # insertConfig(cursor,"neo_ses","000")
    # conn.commit()
    # conn.close()
    # insertConfig(cursor, "skip_login", "000")
    # updateConfig("ipv4","000999")
    # print(getConfig('neo_ses'))


