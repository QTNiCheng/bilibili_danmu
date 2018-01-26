from Unity import RandomHeader
import re, time, requests
from bs4 import BeautifulSoup
import pymongo
import collections
headers = RandomHeader.randHeader() #随机UA

# 获取弹幕ID和视频标题
def requests_get_danmu_id(url):
    print(url)
    response = requests.get(url=url, headers=headers).text
    Soup = BeautifulSoup(response, 'lxml')
    title = Soup.select('#viewbox_report > div.info > div.v-title > h1')
    for temp in title:
        title = temp.get_text()
    try:
        try:
            danmu_id = re.findall(r'cid=(\d+)&', response)[0]
        except:
            danmu_id = re.findall(r'"cid":(\d+),', response)[0]
        return danmu_id, title
    except Exception as e:
        print('视频不见啦', e)


# Unix转换为2018-1-1这种格式
def date_time(seconds):
    timeArray = time.localtime(int(seconds))
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime

#秒转换成时间
def sec2str(seconds):
    seconds = eval(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    time = "%02d:%02d:%02d" % (h, m, s)
    return time

# 获取弹幕数据
def get_danmu(danmu_id, title, sig):
    danmu_id_list = ['dmroll,{},{}'.format(_, danmu_id) for _ in range(1424275200, 1516464000, 86400)] #2015年拜年祭Unix时间戳
    danmu_id_list.append('{}.xml'.format(danmu_id))
    # all_list = []
    client = pymongo.MongoClient('localhost', 27017)
    comment_info = client['哔哩哔哩拜年祭']
    sheet_table = comment_info['{}'.format(title)]

    for temp in danmu_id_list:
        # print(temp)
        if temp[-4:] != '.xml':
            print('正在抓取{}的弹幕'.format(date_time(re.findall(r'dmroll,(\d+),', temp)[0])))  #dmroll,1516464000,3107762
        else:
            print('正在抓取今天的弹幕')
        danmu_url = 'https://comment.bilibili.com/{}'.format(temp)
        danmu_html = requests.get(url=danmu_url, headers=headers).content
        soup = BeautifulSoup(danmu_html, 'lxml')
        all_d = soup.select('d')
        if all_d:
            for d in all_d:
                # # 把d标签中P的各个属性分离开
                danmu_list = d['p'].split(',')
                # # d.get_text()是弹幕内容
                # danmu_list.append(d.get_text())
                # danmu_list[0] = sec2str(danmu_list[0])
                # danmu_list[4] = date_time(danmu_list[4])
                # all_list.append(danmu_list)
                # # print(danmu_list)
                data = collections.OrderedDict()
                # data = {
                #     '出现的时间': sec2str(danmu_list[0]),
                #     '弹幕模式': danmu_list[1],
                #     '字号': danmu_list[2],
                #     '颜色': danmu_list[3],
                #     '发送时间': danmu_list[4],
                #     '弹幕池': danmu_list[5],
                #     '发送者ID': danmu_list[6],
                #     'rowID': danmu_list[7],
                #     '弹幕内容': d.get_text()
                # }
                data['出现的时间'] = sec2str(danmu_list[0]),
                data['弹幕模式'] = danmu_list[1],
                data['字号'] = danmu_list[2],
                data['颜色'] = danmu_list[3],
                data['发送时间'] = danmu_list[4],
                data['弹幕池'] = danmu_list[5],
                data['发送者ID'] = danmu_list[6],
                data['rowID'] = danmu_list[7],
                data['弹幕内容'] = d.get_text()
                sheet_table.insert_one(data)


if __name__ == '__main__':
    url_list = ['https://www.bilibili.com/video/av1999286/?from=search&seid=16917212761754012495#page={}'.format(a) for a in range(1,5)]
    for url, sig in zip(url_list, ['1P', '2P', '3P', '4P']):
        danmu_id, title = requests_get_danmu_id(url)
        all_list = get_danmu(danmu_id, title, sig)






