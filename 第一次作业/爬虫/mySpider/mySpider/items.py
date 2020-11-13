# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MyspiderItem(scrapy.Item):
    # define the fields for your item here like:
    #姓名
    name = scrapy.Field()
    #职位名
    work = scrapy.Field()
    #联系电话
    tellphone = scrapy.Field()
    #传真
    fax = scrapy.Field()
    #邮箱
    email = scrapy.Field()
    #研究方向
    researchDirection = scrapy.Field()
