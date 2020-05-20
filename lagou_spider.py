#coding:utf-8
'''
拉钩网爬虫脚本
@author :  pli
datetime:  2020-05-16 11:52
'''
import requests
from lxml import etree
import pandas as pd
from retrying import retry
import openpyxl

class LaGou():
    def __init__(self,job,pages):
        self.job = job
        self.pages = pages
        self.headers = {
            'Host': 'www.lagou.com',
            'Origin': 'https://www.lagou.com',
            'User-Agent': 'ozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3704.400 QQBrowser/10.4.3587.400'
        }

    def GetCookie(self):
        url = 'https://www.lagou.com/jobs/list_%E8%BF%90%E8%90%A5/p-city_213?&cl=false&fromSearch=true&labelWords=&suginput='
        # 注意如果url中有中文，需要把中文字符编码后才可以正常运行
        response = requests.get(url=url,headers=self.headers,allow_redirects=False)
        return response.cookies

    def getdata(self):
        url = 'https://www.lagou.com/jobs/positionAjax.json?px=new&needAddtionalResult=false'
        self.headers['Referer'] = 'https://www.lagou.com/jobs/list_%E8%BF%90%E8%90%A5?labelWords=&fromSearch=true&suginput='
        data = {
            'first': 'true',
            'pn': str(self.pages),
            'kd': str(self.job),
        }
        response = requests.post(url = url,data=data,headers = self.headers,cookies = self.GetCookie())
        # 这里的请求是post且获取的内容是json格式，因此使用json=data的方式才能获取到数据
        response.encoding = response.apparent_encoding  # 根据网页内容分析出的编码方式。
        return response.json()

    data_list = []
    def savedata(self):
        data_json = self.getdata()
        table_Lables = ['数据来源网站', 'jd的地址', '岗位行业', '公司名称', '公司轮次', '公司人数', '公司行业', '热门城市', '岗位', '学历', '工作年限', '岗位薪资', '发布时间', '关键内容']
        showid = data_json['content']['showId']
        for i in data_json['content']['positionResult']['result']:
            position_id = i['positionId']
            positionId = 'https://www.lagou.com/jobs/{}.html'.format(i['positionId'])
            keyContent = self.detail_parse(position_id, showid)
            self.data_list.append(
                ['拉勾网', positionId, i['firstType'], i['companyFullName'], i['financeStage'],
                 i['companySize'], i['industryField'], i['city'], i['positionName'], i['education'], i['workYear'],
                 i['salary'], i['createTime'], keyContent
                ])
        data_write = pd.DataFrame(columns=table_Lables, data=self.data_list)
        if self.job == None:
            self.job = '所有职位'
        return data_write.to_excel('拉钩_%s.xlsx' % self.job, index=False, encoding='utf_8_sig')

    @retry(stop_max_attempt_number=10)
    def detail_parse(self,positionid,showid):
        # 解析详情页数据
        url = 'https://www.lagou.com/jobs/{}.html?show={}'.format(positionid,showid)
        print(url)
        response = requests.get(url,headers = self.headers,cookies = self.GetCookie())
        tree = etree.HTML(response.content)
        job_detail = tree.xpath('//div[@class="job-detail"]/p/text()')
        job_detail = ''.join(job_detail)
        return job_detail

    def main(self):
        for i in range(1,self.pages+1):
            print('第%s页正在爬取' % (i))
            self.savedata()
        print('*' * 100)
        print('所有数据爬取完毕，可以关闭当前界面，前往查看爬取下来的数据了~')

if __name__ == '__main__':
    job_input = input('请输入你要查询的职位，不输入则不限职位：').strip()   #strip()去除头尾空格
    page_input = int(input('请输入你要爬取的页数：'))
    lagou = LaGou(job_input,page_input)
    lagou.main()
