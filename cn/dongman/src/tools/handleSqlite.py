import sqlite3
from cn.dongman.src.tools.logger import logger

def createConfig():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('''create table configInter(cfgKey varchar(20) primary key,cfgValue varchar(200)) ''')
    conn.commit()
    conn.close()


def getCursor():
    conn = sqlite3.connect('db.sqlite3')
    with conn:
        cursor = conn.cursor()
        return conn,cursor

def insertConfig(cursor,cfgKey,cfgValue):
    sql = '''insert into configInter(cfgKey,cfgValue) values(?,?)'''
    cursor.execute(sql, (cfgKey,cfgValue))


def updateConfig(cfgKey,cfgValue):
    conn,cursor = getCursor()
    with conn:
        sql = '''update configInter set cfgValue = ? where cfgKey= ?'''
        cursor.execute(sql, (cfgValue,cfgKey))
        conn.commit()
        logger.info("更新%s：%s" % (cfgKey,cfgValue))



def getConfig(cfgKey):
    conn,cursor = getCursor()
    with conn:
        sql = '''select cfgValue from config where cfgKey=?'''
        cursor.execute(sql,(cfgKey,))
        res = cursor.fetchone()
        logger.info("getConfig获取%s：%s" % (cfgKey,res[0]))
        return res[0]


if __name__ == "__main__":
    createConfig()
    conn,cursor = getCursor()
    # insertConfig(cursor,"ipv4","000")
    insertConfig(cursor, "neo_id", "000")
    insertConfig(cursor,"neo_ses","000")
    # insertConfig(cursor, "skip_login", "000")
    # updateConfig("ipv4","000999")
    # print(getConfig('ipv4'))


