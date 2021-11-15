# -*- coding: utf-8 -*-
import scrapy

from NBA.items import NbaNewsItem


class NbatestSpider(scrapy.Spider): # 继承scrapy.spider
    # 爬虫名字
    name = 'NBATest'
    # 允许爬取的范围
    allowed_domains = ['tiyu.baidu.com/match/NBA']
    # 开始爬取的url地址
    start_urls = ['https://tiyu.baidu.com/match/NBA/tab/%E6%96%B0%E9%97%BB']

    # 数据提取的方法，接受下载中间件传过来的response
    def parse(self, response):
        news_list = response.xpath('//*/div[@class="c-container wa-match-news-list"]/div/*/a')
        for news in news_list:
            new_info = NbaNewsItem()
            new_info['url'] = news.xpath('./@data-click').extract_first()
            new_info['new_title'] = news.xpath('./div[1]/text()').extract_first()
            yield new_info

