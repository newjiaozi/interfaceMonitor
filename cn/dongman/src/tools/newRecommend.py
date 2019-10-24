from cn.dm.src.interface import *
import random

def getRandomData():
    ## random.randint(0,1)
    ancientchinese=random.randint(0,1)
    boy=random.randint(0,1)
    campus=random.randint(0,1)
    comedy=random.randint(0,1)
    fantasy=random.randint(0,1)
    filmadaptation=random.randint(0,1)
    healing=random.randint(0,1)
    inspirational=random.randint(0,1)
    love=random.randint(0,1)
    metropolis=random.randint(0,1)
    suspense=random.randint(0,1)
    termination=random.randint(0,1)
    isNewUser = random.choice([True,False])
    age = random.choice(["0","1","2","3","4","5","6",""])
    # age = random.randint(0,6)
    gender = random.choice(["B","G"])
    return ancientchinese,boy,campus,comedy,fantasy,filmadaptation,healing,inspirational,love,metropolis,suspense,termination,isNewUser,age,gender


def checkRecommendData(cursor,ancientchinese,boy,campus,comedy,fantasy,filmadaptation,healing,inspirational,love,metropolis,suspense,termination,isNewUser,age,gender):
    sql = makeSql(ancientchinese,boy,campus,comedy,fantasy,filmadaptation,healing,inspirational,love,metropolis,suspense,termination,age,gender)
    cursor.execute(sql)
    titleNos = cursor.fetchall()
    title_list = []
    for titleno in titleNos:
        title_list.append(titleno[0])
    ##  423，1268看脸时代和女神降临
    r = checkTermination(cursor,title_list,ancientchinese, boy, campus, comedy, fantasy, filmadaptation, healing, inspirational,love, metropolis, suspense, termination)
    r_list = list(r)
    r_list.sort(key=lambda x: (x[0],x[4]), reverse=True)

    if isNewUser:
        if gender == "B":
            if 423 not in title_list:
                sql = 'select a.ranking_mana,a.title,a.thumbnail_app_big_image,a.short_synopsis,a.title_no,b.gn_seo_code,a.picture_author_name,a.writing_author_name from title a left join genre_new b on a.represent_genre_new_code = b.gn_id where a.title_no = "423"'
                title = getTitles(cursor, sql)
                # print("#"*20,title)
                r_list.insert(0, title[0])
            else:
                r_tmp = ""
                for r in r_list:
                    if r[4] == 423:
                        r_tmp = r
                        r_list.remove(r)
                        break
                r_list.insert(0,r_tmp)

        elif gender == "G":
            if 1268 not in title_list:
                sql = 'select a.ranking_mana,a.title,a.thumbnail_app_big_image,a.short_synopsis,a.title_no,b.gn_seo_code,a.picture_author_name,a.writing_author_name from title a left join genre_new b on a.represent_genre_new_code = b.gn_id where a.title_no = "1268"'
                title = getTitles(cursor, sql)
                # print("#"*20,title)
                r_list.insert(0, title[0])
            else:
                r_tmp = ""
                for r in r_list:
                    if r[4] == 1268:
                        r_tmp = r
                        r_list.remove(r)
                        break
                r_list.insert(0, r_tmp)
    return r_list[:5]

    # return r[:5]


def getTitles(cursor,titlesql):
    print(titlesql)
    cursor.execute(titlesql)
    titles = cursor.fetchall()
    return titles

def checkTermination(cursor,title_list,ancientchinese,boy,campus,comedy,fantasy,filmadaptation,healing,inspirational,love,metropolis,suspense,termination):
    ##只选了完结：返回1；选择了完结和至少一个分类返回2；没选完结，只有其他分类，返回3
    # titlesql = "select a.rest_termination_status_code,a.ranking_mana,a.likeit_count,a.title,a.thumbnail_app_big_image,a.short_synopsis,a.title_no,b.gn_seo_code,a.picture_author_name,a.writing_author_name from title a left join genre_new b on a.represent_genre_new_code = b.gn_id where a.title_no in %s" % str(tuple(title_list))
    if len(title_list) == 1:
        title_list = "("+str(title_list[0])+")"
    else:
        title_list = str(tuple(title_list))
    if termination == 1:
        if ancientchinese or boy or campus or comedy or fantasy or filmadaptation or healing or inspirational or love or metropolis or suspense:
            ##2
            print("#####:2"*5)
            sql = "select a.ranking_mana,a.title,a.thumbnail_app_big_image,a.short_synopsis,a.title_no,b.gn_seo_code,a.picture_author_name,a.writing_author_name from title a left join genre_new b on a.represent_genre_new_code = b.gn_id where a.title_no in %s" % title_list
            return getTitles(cursor,sql)
        else:
            ###1
            print("#####:1"*5)
            sql = 'select a.likeit_count,a.title,a.thumbnail_app_big_image,a.short_synopsis,a.title_no,b.gn_seo_code,a.picture_author_name,a.writing_author_name from title a left join genre_new b on a.represent_genre_new_code = b.gn_id where a.rest_termination_status_code = "TERMINATION" and  a.title_no in %s' % title_list
            return getTitles(cursor, sql)
    else:
        ##3
        print("#####:3"*5)
        sql = "select a.ranking_mana,a.title,a.thumbnail_app_big_image,a.short_synopsis,a.title_no,b.gn_seo_code,a.picture_author_name,a.writing_author_name from title a left join genre_new b on a.represent_genre_new_code = b.gn_id where a.title_no in %s" % title_list
        return getTitles(cursor, sql)


def makeSql(ancientchinese,boy,campus,comedy,fantasy,filmadaptation,healing,inspirational,love,metropolis,suspense,termination,age,gender):
    wheresql = ""
    ##性别
    if gender == "B":
        wheresql += 'gender_b = "1"'
    elif gender == "G":
        wheresql += 'gender_g = "1"'
    ##年龄
    if age == '0':
        wheresql += ' and age_0 = "1"'
    elif age == '1':
        wheresql += ' and age_1 = "1"'
    elif age == '2':
        wheresql += ' and age_2 = "1"'
    elif age == '3':
        wheresql += ' and age_3 = "1"'
    elif age == '4':
        wheresql += ' and age_4 = "1"'
    elif age == '5':
        wheresql += ' and age_5 = "1"'
    elif age == '6':
        wheresql += ' and age_6 = "1"'
    ##分类
    genresqllist = []
    if ancientchinese == 1:
        genresqllist.append('ancient_chinese = "1"')
    if boy == 1:
        genresqllist.append('boy = "1"')
    if campus == 1:
        genresqllist.append('campus = "1"')
    if comedy == 1:
        genresqllist.append('comedy = "1"')
    if fantasy == 1:
        genresqllist.append('fantasy = "1"')
    if filmadaptation == 1:
        genresqllist.append('film_adptation = "1"')
    if healing == 1:
        genresqllist.append('healing = "1"')
    if inspirational == 1:
        genresqllist.append('inspirational = "1"')
    if love == 1:
        genresqllist.append('love = "1"')
    if metropolis == 1:
        genresqllist.append('metropolis = "1"')
    if suspense == 1:
        genresqllist.append('suspense = "1"')
    if termination == 1:
        genresqllist.append('termination = "1"')
    andwheresqlstr = ""
    if genresqllist:
        if len(genresqllist) == 1:
            andwheresql = ' and %s'
        else:
            andwheresql = ' and (%s)'
        genresql = " or ".join(genresqllist)
        andwheresqlstr = andwheresql % genresql
    if andwheresqlstr:
        querySql = 'select title_no from title_recommend_config where %s' % wheresql+andwheresqlstr
    else:
        querySql = 'select title_no from title_recommend_config where %s' % wheresql
    print(querySql)
    return querySql


def actionRecommend():
    conn,cursor = initDataFromDB()
    time_str = time.strftime("%Y%m%d %H:%M:%S", time.struct_time(time.localtime()))
    trys = []

    with open("trys%s.txt" % time_str,"w+") as t:
        while True:
        # for i in range(0,100000):
            res = getRandomData()
            # res = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, True, '1', 'B')
            if res not in trys:
                rs = appUserpreferenceNewadd(*res)
                sqlrs = checkRecommendData(cursor, *res)
                t.write(str(res)+" ###%s" % len(rs))
                t.write(os.linesep)
                trys.append(res)
                print(res)
                print("#" * 20, len(trys))
                assert len(rs) == len(sqlrs)
                for i in range(0,len(sqlrs)):
                    # print(sqlrs[i],rs[i])
                    print(sqlrs[i][1], sqlrs[i][4], rs[i]["title"], rs[i]["titleNo"])
                    assert sqlrs[i][1] == rs[i]["title"]
                    assert sqlrs[i][2] == rs[i]["thumbnail"]
                    assert sqlrs[i][3] == rs[i]["shortSynopsis"]
                    assert sqlrs[i][4] == rs[i]["titleNo"]
                    assert sqlrs[i][5] == rs[i]["representGenre"]
                    assert sqlrs[i][6] == rs[i]["pictureAuthorName"]



        cursor.close()


if __name__ == "__main__":
    actionRecommend()

