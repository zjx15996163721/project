# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.conf import settings
import pymongo


class QianchengPipeline(object):
    def process_item(self, item, spider):
        return item


class MongoPipeline(object):
    def __init__(self):
        self.connection = pymongo.MongoClient(host=settings['MONGODB_HOST'], port=settings['MONGODB_PORT'])
        self.connection.admin.authenticate(settings['USERNAME'], settings['PASSWORD'])
        self.db = self.connection[settings['MONGODB_DBNAME']]
        self.collection = self.db[settings['COLLECTION']]

    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item