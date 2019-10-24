import pandas
import csv,codecs
from cn.dm.src.tools.getMongodb import *
from cn.dm.src.interface import *


jmeterpath = "/Users/dongman/Documents/jmeters/data"
resultpath = "commentids.csv"
resultParpath = "commentidandparentid.csv"
csvpath = os.path.join(jmeterpath,resultpath)
csvParpath = os.path.join(jmeterpath,resultParpath)


def writeCsv(data,csvpath):
    df = pandas.DataFrame(data)
    df.to_csv(data,index=False,header=False)

def writeCsvByCsv(data,csvpath):
    csv_file = codecs.open(csvpath,"w+","utf-8")
    writer = csv.writer(csv_file)
    for i in data:
        writer.writerow(i)

def writeCsvByCsvStr(data,csvpath):
    csv_file = codecs.open(csvpath,"w+","utf-8")
    writer = csv.writer(csv_file)
    for i in data:
        writer.writerow([i])


if __name__ == "__main__":

    client,dbname = getConnect()
    # residParent = getAllReply(dbname)
    # print("开始写入评论数据到csv")
    # writeCsvByCsv(residParent,csvParpath)
    # print("评论ID和parentid写入csv完成")
    res = getAllIDByNeoId(dbname)
    writeCsvByCsvStr(res,csvpath)





