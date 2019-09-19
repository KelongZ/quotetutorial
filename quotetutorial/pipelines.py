# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
import pymysql
from scrapy.exceptions import DropItem

from quotetutorial.items import QuoteItem
from quotetutorial.items import NewsItem
from quotetutorial.items import ImageItem
# todo 两种items如何区分引用(以下为解决办法) or 直接修改item变量名改为你需要的class变量
'''
from 项目.items import ItemsAA
from 项目.items import ItemsBB
def process_item(self, item, spider):
    if isinstance(item, ItemAA):
        # 你的处理方法
        pass

    elif isinstance(item, ItemBB):
        # 处理方法
        pass
'''

class TextPipeline(object):

    def __init__(self):
        self.limit = 50

    def process_item(self, item, spider):
        if item['text']:
            if len(item['text']) > self.limit:
                item['text'] = item['text'][0:self.limit].rstrip() + '...'
            return item
        else:
            return DropItem('Missing Text')

# Mongo上传item储存封装类
class MongoPipeline(object):

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db = crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        name = item.__class__.__name__
        self.db[name].insert(dict(item))
        return item

    def close_spider(self, spider):
        self.client.close()

# Mysql上传item储存封装类
class MysqlPipeline(object):

    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            database=crawler.settings.get('MYSQL_DATABASE'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            port=crawler.settings.get('MYSQL_PORT')
        )

    def open_spider(self, spider):
        self.db = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            charset='utf8',
            port=self.port
        )
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        data = dict(item)
        text = data['text']
        author = data['author']
        sql = "INSERT INTO quoteitem (text,author) VALUES(%s, %s)"
        values = (text, author)
        self.cursor.execute(sql, values)
        self.db.commit()
        return item

    def close_spider(self, spider):
        self.db.close()

class NewsMysqlPipeline(object):

    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            database=crawler.settings.get('MYSQL_DATABASE'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            port=crawler.settings.get('MYSQL_PORT')
        )

    def open_spider(self, spider):
        self.db = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            charset='utf8',
            port=self.port
        )
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        data = dict(item)
        title = data['title']
        url = data['url']
        pub_time = data['pub_time']
        origin = data['origin']
        contents = data['contents']
        ## 建议把表名替换为spider文件名，好自动对应上传数据库表位置
        sql_main = "INSERT INTO fin_china_stock (title,url,pub_time,origin,contents) VALUES(%s, %s, %s, %s, %s)"
        values_main = (title,url,pub_time,origin,contents)
        self.cursor.execute(sql_main, values_main)
        self.db.commit()
        return item

    def close_spider(self, spider):
        self.db.close()

class ImageMapPipeline(object):

    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            database=crawler.settings.get('MYSQL_DATABASE'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            port=crawler.settings.get('MYSQL_PORT')
        )

    def open_spider(self, spider):
        self.db = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            charset='utf8',
            port=self.port
        )
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        data = dict(item)
        ori_image_url = data['ori_image_url']
        oss_image_url = data['oss_image_url']
        sql_rela = "INSERT INTO inamge_map (ori_image_url,oss_image_url) VALUES(%s, %s)"
        values_rela = (ori_image_url,oss_image_url)
        self.cursor.execute(sql_rela, values_rela)
        self.db.commit()
        return item

    def close_spider(self, spider):
        self.db.close()