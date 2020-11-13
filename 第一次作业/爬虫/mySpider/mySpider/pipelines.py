# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from .dataManage import DataManager

class MyspiderPipeline(object):

    def __init__(self):
        self.db = DataManager()

    def process_item(self, item, spider):
        data = tuple(dict(item).values())
        self.db.save_data(data)
        return item
