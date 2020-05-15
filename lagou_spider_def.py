#coding:utf-8

import requests
import time
from lxml import etree
import pandas as pd

def GetCookie():
    url = 'https://www.lagou.com/jobs/list_%E8%BF%90%E8%90%A5/p-city_213?&cl=false&fromSearch=true&labelWords=&suginput='
    # 注意如果url中有中文，需要把中文字符编码后才可以正常运行
    headers = {
        'User-Agent': 'ozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3704.400 QQBrowser/10.4.3587.400'
    }
    response = requests.get(url=url,headers=headers,allow_redirects=False)
    return response.cookies

def getdata(page,kw =''):
    url = 'https://www.lagou.com/jobs/positionAjax.json?px=new&needAddtionalResult=false'

    headers = {
        'Host': 'www.lagou.com',
        'Origin': 'https://www.lagou.com',
        'Referer': 'https://www.lagou.com/jobs/list_%E8%BF%90%E8%90%A5?labelWords=&fromSearch=true&suginput=',
        'User-Agent': 'ozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3704.400 QQBrowser/10.4.3587.400'
    }
    data = {
        'first': 'true',
        'pn': str(page),
        'kd': str(kw),
    }
    s = requests.Session()
    response = s.post(url = url,data=data,headers = headers,cookies = GetCookie())
    # 这里的请求是post且获取的内容是json格式，因此使用json=data的方式才能获取到数据
    response.encoding = response.apparent_encoding  # 根据网页内容分析出的编码方式。
    return response.json()

data_list = []
def savedata(data_json, job=None):
    table_Lables = ['数据来源网站', 'jd的地址', '岗位行业', '公司名称', '公司轮次', '公司人数', '公司行业', '热门城市', '岗位', '学历', '工作年限', '岗位薪资', '发布时间', '关键内容']
    showid = data_json['content']['showId']
    for i in data_json['content']['positionResult']['result']:
        position_id = i['positionId']
        positionId = 'https://www.lagou.com/jobs/{}.html'.format(i['positionId'])
        s = requests.Session()
        keyContent = detail_parse(position_id, showid, s)
        data_list.append(
            [
                '拉勾网', positionId, i['firstType'], i['companyFullName'], i['financeStage'],
             i['companySize'], i['industryField'], i['city'], i['positionName'], i['education'], i['workYear'],
             i['salary'], i['createTime'], keyContent
            ])
    data_write = pd.DataFrame(columns=table_Lables, data=data_list)
    if job == None:
        job = '所有职位'
    return data_write.to_excel('拉钩_%s.xlsx' % job, index=False, encoding='utf_8_sig')

def detail_parse(positionid,showid,s):
    # 解析详情页数据
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.lagou.com',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3704.400 QQBrowser/10.4.3587.400'
               }
    url = 'https://www.lagou.com/jobs/{}.html?show={}'.format(positionid,showid)
    print(url)
    response = s.get(url,headers = headers,cookies = GetCookie())
    tree = etree.HTML(response.content)
    job_detail = tree.xpath('//div[@class="job-detail"]/p/text()')
    job_detail = ''.join(job_detail)
    return job_detail

def main(page):
    for i in range(1,page+1):
        print('第%s页正在爬取' % (i))
        data = getdata(page,'产品经理')
        savedata(data)
        time.sleep(1)
    print('*' * 100)
    print('所有数据爬取完毕，可以关闭当前界面，前往查看爬取下来的数据了~')

if __name__ == '__main__':
    main(2)   # 参数是爬去多少页
