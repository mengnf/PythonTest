#coding:utf-8
import hashlib
import requests

import time

import datetime


class YouDaoFanyi(object):

    def __init__(self,word):
        self.word = word
        self.url = 'http://nmt.youdao.com/translate_o?smartresult=dict&smartresult=rule'
        self.headers = {
            'Cookie': 'OUTFOX_SEARCH_USER_ID=1173384304@10.169.0.82; OUTFOX_SEARCH_USER_ID_NCOO=363588297.24575675; JSESSIONID=aaagao_8czpTP_DYMJd0x; ___rl__test__cookies=1636445635995',
            'Referer': 'http://nmt.youdao.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
        }
        self.formdata = None

    def generate_formdata(self):
        '''
        salt: 16364447516133
        sign: c19c676a7ee838d40a7c4130357b08b5
        lts: 1636444751613
        bv: c795a332c678d5063a1ee5eb15253848
        '''
        salt = str(int(time.time()*1000))
        md5 = hashlib.md5()
        temp_str = "new-fanyiweb" + salt + "ydsecret://newfanyiweb.doctran/sign/0j9n2{3mLSN-$Lg]K4o0N2}"
        md5.update(temp_str.encode())
        sign = md5.hexdigest()

        self.formdata = {
            'i': self.word ,
            'from': 'AUTO',
            'to': 'AUTO',
            'smartresult': 'dict',
            'client': 'fanyideskweb',
            'salt': salt,
            'sign': sign,
            'lts': salt[0:len(salt)-1],
            'bv': 'c795a332c678d5063a1ee5eb15253848',
            'doctype': 'json',
            'version': '2.1',
            'keyfrom': 'fanyi.web',
            'action': 'FY_BY_REALTlME'
        }

    def get_data(self):
        response = requests.post(self.url, data=self.formdata, headers=self.headers)
        return response.content

    def run(self):
        self.generate_formdata()
        print(self.formdata)
        data = self.get_data()
        print(data)
        # url
        # headers
        # formdata
        # 获取请求，获取响应
        # 解析数据

if __name__ == '__main__':
    you_dao_fan_yi = YouDaoFanyi('我是谁')
    you_dao_fan_yi.run()

