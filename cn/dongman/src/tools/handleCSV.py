import pandas
import csv,codecs
import os



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


# 以map的方式读csv
def read_dict_csv(csv_file):
    with open(csv_file) as f:
        # 定义key
        field_names = ['id', 'name']
        # 写入数据
        reader = csv.DictReader(f, fieldnames=field_names)
        for row in reader:
            # print(row)
            print(row['name'])


def read_csv(csv_file):
    with open(csv_file) as f:
        reader = csv.reader(f)
        row_list = []
        for row in reader:
            row_list.append(row)
        return row_list


def write_csv(data,csv_file):
    with open(csv_file,"w") as f:
        writer = csv.writer(f)
        for row in data:
            writer.writerow(row)


if __name__ == "__main__":
    pass
    # client,dbname = getConnect()
    # residParent = getAllReply(dbname)
    # print("开始写入评论数据到csv")
    # writeCsvByCsv(residParent,csvParpath)
    # print("评论ID和parentid写入csv完成")
    # res = getAllIDByNeoId(dbname)
    # writeCsvByCsvStr(res,csvpath)





