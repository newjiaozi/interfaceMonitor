
import redis
from cn.dongman.src.tools.logger import logger


def connectRedis():
    r = redis.Redis(host='r-2ze7889e17a315d4.redis.rds.aliyuncs.com', port=6379, password='dmred2017qUsa', db="0",decode_responses=True)
    return r

def setString(r,key,value):
    try:
        res = r.set(key,value)
        logger.info("setString成功 %s：%s" % (key,value))
        return res
    except Exception:
        logger.exception("setString发生异常 %s:%s" % (key,value))

def getString(r,key):
    try:
        res = r.get(key)
        logger.info("getString成功 %s" % key)
        return res
    except Exception:
        logger.exception("getString发生异常 %s" % key)

def setHash(r,name,key,value):
    try:
        res = r.hset(name,key,value)
        logger.info("setHash成功 %s：%s：%s" % (name,key,value))
        return res
    except Exception:
        logger.exception("setHash发生异常 %s：%s：%s" % (name,key,value))

def getHash(r,name,key):
    try:
        res = r.hget(name,key)
        logger.info("getHash成功 %s：%s" % (name,key))
        return res
    except Exception:
        logger.exception("getHash发生异常 %s：%s" % (name,key))

def setListL(r,name,*values):
    try:
        res = r.lpush(name,*values)
        logger.info("setList成功 %s" % name)
        return res
    except Exception:
        logger.exception("setList发生异常 %s" % name)

def setListR(r,name,*values):
    try:
        res = r.rpush(name,*values)
        logger.info("setList成功 %s" % name)
        return res
    except Exception:
        logger.exception("setList发生异常 %s" % name)


def getList(r,name,key):
    try:
        res = r.hget(name,key)
        logger.info("getHash成功 %s：%s" % (name,key))
        return res
    except Exception:
        logger.exception("getHash发生异常 %s：%s" % (name,key))

def deleteCommentRedis(r):
    r = redis.Redis(host='r-2ze7889e17a315d4.redis.rds.aliyuncs.com', port=6379, password='dmred2017qUsa', db="0",decode_responses=True)
    pattern = "comment_frequency_*_*"
    k = r.keys(pattern=pattern)
    if k:
        r.delete(*k)
        logger.info("redis删除成功 %s" % k)
    else:
        logger.info("没有匹配到需要删除的redis")