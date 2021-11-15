# -*- coding: utf-8 -*-
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import uuid

from itemadapter import ItemAdapter

import json

import pymysql

class NbaPipeline(object):

    def __init__(self):
        self.file_json = open('news_json.json','w')

    def get_uuid(self):
        r_uuid = uuid.uuid1()
        return str(r_uuid).replace('-', '')

    def process_item(self, item, spider):
        item = dict(item)

        for aaa in item:
            print(aaa + '值:' + str(item[aaa]).strip())

        MYSQL_CONNECT = pymysql.connect(host='192.168.2.104', port=3306, user='root', passwd='123456', db='NBA', charset='utf8')
        cursor = MYSQL_CONNECT.cursor()
        id = self.get_uuid()
        sql = f"INSERT INTO NBA_NEWS(ID,NEWS_URL,NEWS_TITLE) VALUES('{id}','{str(item['url']).strip()}','{str(item['new_title']).strip()}')"
        print(sql)
        try:
            cursor.execute(sql)
        except Exception as e:
            print("保存新闻: %s 时出错：%s" % (sql, e))

        print('执行完成')

        cursor.close()
        MYSQL_CONNECT.commit()
        MYSQL_CONNECT.close()

        json_data = json.dumps(item) + ',\n'
        self.file_json.write(json_data)

        return item

    def __del__(self):
        self.file_json.close()