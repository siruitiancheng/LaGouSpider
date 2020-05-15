# coding=utf8
import requests
import urllib.parse as UP
import time
import random
import pandas as pd
from lxml import etree


class LaGou():

    data_list = []

    def __init__(self,job,education,city):
        self.job = job
        self.education = education
        self.city = city


    def diff_url(self):
        search = {
            'job': self.job,
            'education': self.education,
            'city': self.city
        }
        # 针对只选择求职范围的处理情况
        if self.education == '' and self.city != '':
            del search['education']
            searchs = UP.urlencode(search)  # 参数为dict，然后用parse.urlencode()进行编码
            diff_url = 'https://www.lagou.com/jobs/list_' + searchs[4:10] + '?px=default&' + searchs[-23:]
            print(diff_url)

            return diff_url

        # 针对只选择了学历的情况
        elif self.city == '' and self.education != '':
            del search['city']
            searchs = UP.urlencode(search)
            diff_url = 'https://www.lagou.com/jobs/list_' + searchs[4:10] + '?px=default&xl=' + searchs[-18:] + '&city=%E5%85%A8%E5%9B%BD'
            return diff_url
        # 针对学历和城市都不选择的情况
        elif self.education == '' and self.city == '':
            del search['education']
            del search['city']
            searchs = UP.urlencode(search)
            diff_url = 'https://www.lagou.com/jobs/list_' + searchs[4:10] + '?px=default&city=%E5%85%A8%E5%9B%BD'
            return diff_url
        # 针对学历和城市都选择的情况
        else:
            searchs = UP.urlencode(search)
            diff_url = 'https://www.lagou.com/jobs/list_' + searchs[4:10] + '?px=default&xl=' + searchs[21:39] + '&city=' + searchs[45:]
            return diff_url

    def choice_url(self):
        # 当一开始选择不同时，所对应的请求json文件不同
        test = {}
        # 针对只选择求职范围的情况
        if self.city != '' and self.education == '':
            test['city'] = self.city
            test = UP.urlencode(test)
            choice_url = 'https://www.lagou.com/jobs/positionAjax.json?px=default&' + test + '&needAddtionalResult=false'

        # 针对选择求职范围和学历的情况
        elif self.education != '' and self.city != '':
            test['education'] = self.education
            test['city'] = self.city
            test = UP.urlencode(test)
            choice_url = 'https://www.lagou.com/jobs/positionAjax.json?xl=' + test[10:28] + '&px=default' + '&city=' + test[-18:] + '&needAddtionalResult=false'

        # 针对选择求职学历的情况
        elif self.education != '' and self.city == '':
            test['x1'] = education
            test = UP.urlencode(test)
            choice_url = 'https://www.lagou.com/jobs/positionAjax.json?' + test + '&px=default&needAddtionalResult=false'

        # 针对求职学历和城市都不选择的情况
        else:
            choice_url = 'https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false'
        return choice_url

    def get_api_json(self,url, url_1, page):
        headers = {
            'Host': 'www.lagou.com',
            'Connection': 'keep-alive',
            'Origin': 'https://www.lagou.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3100.0 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': str(url),
            'Accept-Language': 'zh-CN,zh;q=0.9'}
        # 抓包得到必须要传递的data参数
        data = {
            'first': 'false',
            'pn': page,
            'kd': self.job
        }
        sess = requests.session()  # 创建一个session对象
        sess.headers.update(headers)
        html1 = sess.get(url, headers=headers)  # 先get
        if html1.status_code == 200:  # 判断请求后的状态码是否请求成功
            try:
                html = sess.post(url=url_1, headers=headers, data=data)
                html.raise_for_status()  # post请求不成功，则引发HTTPError异常
                return html.json()
            except:
                print('这一页的采集有问题')

    def GetCookie(self):
        url = 'https://www.lagou.com/jobs/list_%E8%BF%90%E8%90%A5/p-city_213?&cl=false&fromSearch=true&labelWords=&suginput='
        # 注意如果url中有中文，需要把中文字符编码后才可以正常运行
        headers = {
            'User-Agent': 'ozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3704.400 QQBrowser/10.4.3587.400'
        }
        response = requests.get(url=url, headers=headers, allow_redirects=False)
        # cookies = requests.utils.dict_from_cookiejar(response.cookies)
        # print(response.cookies)
        return response.cookies

    def detail_parse(self,positionid, showid, s):
        # 解析详情页数据
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'www.lagou.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3704.400 QQBrowser/10.4.3587.400'
        }
        url = 'https://www.lagou.com/jobs/{}.html?show={}'.format(positionid, showid)
        response = s.get(url, headers=headers, cookies=self.GetCookie())
        tree = etree.HTML(response.content)
        job_detail = tree.xpath('//div[@class="job-detail"]/p/text()')
        job_detail = ''.join(job_detail)
        return job_detail


    def save(self,data_json, job):

        table_Lables = ['数据来源网站', 'jd的地址', '岗位行业', '公司名称', '公司轮次', '公司人数', '公司行业', '热门城市', '岗位', '学历', '工作年限', '岗位薪资',
                        '发布时间', '关键内容']
        showid = data_json['content']['showId']
        for i in data_json['content']['positionResult']['result']:
            position_id = i['positionId']
            positionId = 'https://www.lagou.com/jobs/{}.html'.format(i['positionId'])
            s = requests.Session()
            keyContent = self.detail_parse(position_id, showid, s)
            self.data_list.append(
                ['拉勾网', positionId, i['firstType'], i['companyFullName'], i['financeStage'],
                 i['companySize'], i['industryField'], i['city'], i['positionName'], i['education'], i['workYear'],
                 i['salary'], i['createTime'], keyContent])
        data_write = pd.DataFrame(columns=table_Lables, data=self.data_list)
        if job == '':
            job = '所有职位'
        data_write.to_excel('拉钩_%s.xlsx' % job, index=False, encoding='utf_8_sig')

    def main(self):
        diff_url = self.diff_url()
        choice_url = self.choice_url()
        for page in range(1, pages + 1):
            data_json = self.get_api_json(diff_url, choice_url, page)
            print('正在采集第%d页' % page)
            self.save(data_json, job)


if __name__ == '__main__':
    job= input('请输入你要查询的职位，不输入则不限职位：').strip()
    education = input('请输入你的学历【专科/本科/硕士/博士】，不输入则不限学历：').strip()
    city = input('请输入你想要的工作地点，不输入则代表全国范围：').strip()
    pages = int(input('请输入你要爬取的页数：'))
    la_gou =  LaGou(job,education,city)
    la_gou.main()