# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import codecs
from scrapy.exceptions import DropItem
from scrapy import log
import MySQLdb
import MySQLdb.cursors


class ArticlePipeline(object):
    def __init__(self):
        self.file = codecs.open('result.json', 'wb', encoding='utf-8')

    def process_item(self, item, spider):
        log.msg("process_item process_item.--process_item--process_item:")
        # log.msg("title title.--title--title:"+item['title'][0])
        if len(item['title']) > 0:
            log.msg("enter enter.--enter--enter:")
            line = json.dumps(dict(item)) + '\n'
            # print line
            self.file.write(line.decode("unicode_escape"))
            return item
        else:
            log.msg("DropItem DropItem.--DropItem--DropItem:")
            return DropItem('id is null')


class DBPipeline(object):
    def __init__(self):
        try:
            self.db = MySQLdb.connect(host="101.200.165.239", user="root", passwd="root", port=3306, db="xiaoyusuper",
                                      charset="utf8")
            self.cursor = self.db.cursor()
            print "Connect to db successfully!"
        except:
            print "Fail to connect to db!"

    # pipeline默认调用
    def process_item(self, item, spider):
        if len(item['url']) > 0:
            param = (item['title'], item['mainImage'], item['url'], item['content'])
            sql = "insert into article_info (title,main_image,url,content) values (%s, %s, %s, %s)"
            self.cursor.execute(sql, param)
            return item
        else:
            return DropItem(item)

