# -*- coding: utf-8 -*-

import codecs
import json

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi
import MySQLdb
from MySQLdb.cursors import DictCursor

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ArticleSpiderPipeline(object):
    def process_item(self, item, spider):
        return item


# 自定义写入json文件的pipeline
class JsonWithEncodingPipeline(object):
    # 自定义json文件的导出
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


# 调用scrapy提供的json exporter导出json文件
class JsonExporterPipeline(object):

    def __init__(self):
        self.file = open('article.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()


# 自定义插入MySQL数据库pipline
class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1', 'root', '123456', 'article_spider', charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            INSERT INTO jobbole_article (`title`, `url`, `create_date`, `url_object_id`, `front_image_url`, `front_image_path`, `comment_nums`, `fav_nums`, `praise_nums`, `tags`, `content`) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(insert_sql,
                            (item['title'], item['url'], item['create_date'], item['url_object_id'],
                             item['front_image_url'], ['front_image_path'], item['comment_nums'],
                             item['fav_nums'], item['praise_nums'], item['tags'], item['content']))
        self.conn.commit()
        return item


# 采用同步的机制写入MySQL
class MysqlTwistedPipeline(object):
    def __init__(self, db_pool):
        self.db_pool = db_pool

    @classmethod
    def from_settings(cls, settings):
        db_params = dict(host=settings['MYSQL_HOST'],
                         db=settings['MYSQL_DBNAME'],
                         user=settings['MYSQL_USER'],
                         passwd=settings['MYSQL_PASSWORD'],
                         charset='utf8',
                         cursorclass=DictCursor,
                         use_unicode=True)
        db_pool = adbapi.ConnectionPool('MySQLdb', **db_params)
        return cls(db_pool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入编程异步执行
        query = self.db_pool.runInteraction(self.do_insert, item)
        # 处理异常
        query.addErrback(self.handle_error, item, spider)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        insert_sql = """
                    INSERT INTO jobbole_article (`title`, `url`, `create_date`, `url_object_id`, `front_image_url`, `comment_nums`, `fav_nums`, `praise_nums`, `tags`, `content`) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
        cursor.execute(insert_sql,
                       (item['title'], item['url'], item['create_date'], item['url_object_id'],
                        item['front_image_url'], item['comment_nums'], item['fav_nums'],
                        item['praise_nums'], item['tags'], item['content']))

    def handle_error(self, failure, item, spider):
        # 处理异步插入异常
       print(failure)


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if 'front_image_url' in item:
            for ok, value in results:
                image_file_path = value['path']
            item['front_image_path'] = image_file_path
        return item
