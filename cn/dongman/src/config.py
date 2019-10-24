#coding=utf-8

config={
    "qamysql":{"host":"rm-2ze984p4ljnijqtg1.mysql.rds.aliyuncs.com",
               "port":3306,
               "user":"rmtroot",
               "passwd":"dmdb2050mCn",
               "db":"webtoon",
               },
    "realmysql":{"host":"rm-2ze984p4ljnijqtg1.mysql.rds.aliyuncs.com",
               "port":3306,
               "user":"rmtroot",
               "passwd":"dmdb2050mCn",
               "db":"webtoon",
               },
    "qamweb":"http://qam.dongmanmanhua.cn",
    "qamheaders":{"User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
                  "Host":"qam.dongmanmanhua.cn",
                  # "Upgrade-Insecure-Requests":"1",
                  # "Accept-Language":"zh-CN,zh;q=0.9",
                  # "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
                  },
    "qapcweb":"https://qa.dongmanmanhua.cn",
    "qapcheaders":{"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
                   "Host":"qa.dongmanmanhua.cn",
                   },
        }


def getCfgDict(key):
    return config[key]

def getCfgValue(key1,key2):
    return config[key1][key2]