# -*- coding:utf-8 -*-
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy import log
from scrapy.http import Request
from article.items import ArticleItem
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class ArticleSpider(Spider):
    name = "single"
    allowed_domains = ["mimito.com.cn"]
    # 抓取的第一篇文章
    start_urls = [
        "http://www.mimito.com.cn/dapei/m2016041433.html"
    ]

    # 设置下载延时
    download_delay = 1

    contentList = []
    items = []
    articleCount = 0
    articleMaxCount = 75
    imageQianZhui = 'http://www.mimito.com.cn'
    currentUrl = ''
    currentMainImage = ''

    def parse(self, response):
        if len(self.currentUrl) == 0:
            self.currentUrl = str(response.url)
        sel = Selector(response)
        title = sel.xpath('//div[@class="content"]/h1/text()').extract()
        nextArticleUrlList = sel.xpath('//div[@class="content"]/div[@class="pre_art"]/a').extract()
        nextArticleUrl = ''
        if len(nextArticleUrlList) > 1:
            nextArticleUrl = sel.xpath('//div[@class="content"]/div[@class="pre_art"]/a[last()]/@href').extract()[0]
        contents = sel.xpath('//div[@class="content"]/div[@class="content_01"]/p')
        nextPage = sel.xpath('//div[@class="page2"]/a[last()]')
        nextPageStr = nextPage.xpath('./text()').extract()[0].encode('utf-8')
        nextPageUrl = nextPage.xpath('./@href').extract()[0]
        # log.msg("Append done." + nextPageStr + nextPageUrl)
        for content in contents:
            # 过滤一些特殊的情况
            # 判断是不是图片
            imgs = content.xpath('./img')
            if imgs:  # 是图片
                for img in imgs:
                    if str(img.xpath('@src').extract()[0]).startswith('data:image/'):
                        log.msg('diu qi image')
                    else:
                        imgpath = self.imageQianZhui + img.xpath('@src').extract()[0]
                        if len(self.currentMainImage) == 0:
                            self.currentMainImage = imgpath
                        self.contentList.append(imgpath)
            else:  # 不是图片
                # 如果是加粗过的文字
                if content.xpath('./strong'):
                    strongStr = content.xpath('./strong/text()').extract()[0]
                    self.contentList.append(strongStr)
                else:
                    textStr = content.xpath('./text()').extract()[0]
                    self.contentList.append(textStr)

        nextStr = '下一页'
        nextStr.encode('utf-8')
        if nextPageStr == nextStr:  # 说明是下一页
            # log.msg("Append done.----equal")
            # log.msg("Append done.----nextPageUrl:" + nextPageUrl)
            yield Request(nextPageUrl, callback=self.parse)
        else:  # 没有下一页了
            item = ArticleItem()
            item['title'] = [t.encode('utf-8') for t in title]
            item['title'] = item['title'][0]
            contentStr = ""
            for index in range(len(self.contentList)):
                contentStr += self.contentList[index].encode('utf-8')
                if index <> len(self.contentList) - 1:
                    contentStr += '$'

            item['content'] = contentStr
            item['url'] = self.currentUrl.encode('utf-8')
            item['mainImage'] = self.currentMainImage.encode('utf-8')
            print self.contentList
            self.contentList = []
            self.articleCount += 1
            self.currentUrl = ''
            self.currentMainImage = ''
            yield item
            # 尝试抓取下一篇文章
            if nextArticleUrl and self.articleCount < self.articleMaxCount:
                log.msg("Append done.----nextArticleUrl:" + nextArticleUrl)
                yield Request(nextArticleUrl, callback=self.parse)
