# -*- coding: utf-8 -*-
import scrapy
import re
from urllib.parse import urlencode

from quotetutorial.items import NewsItem

class FinChinaStockSpider(scrapy.Spider):
    name = 'fin_china_stock'
    allowed_domains = ['finance.china.com.cn/stock']
    # 这里去掉了start_urls，因为它会在start_requests自动执行一遍。
    # start_urls = ['http://finance.china.com.cn/stock/']

    first_url = 'http://finance.china.com.cn/stock/'
    more_urls = []
    for i in range(1,2):
        data = {
            'callback': 'jQuery111109070254808521516_1568796896902',
            'cnl': 'stock',
            'index': '0',
            'page': i
        }
        params = urlencode(data)
        base_url = 'http://app.finance.china.com.cn/news/more_news.php'
        more_url = 'http://app.finance.china.com.cn/news/more_news.php' + '?' + params
        more_urls.append(more_url)


    def start_requests(self):
        # 先跑首页，再跑json载入的更多页面数据
        yield scrapy.Request(self.first_url, self.parse)
        for more_url in self.more_urls:
            yield scrapy.Request(url=more_url, callback=self.parse_more, dont_filter=True)


    def parse(self, response):
        # 获取title和url并返回url到回调函数中继续提取url中的详细内容
        articles = response.css('.hsTit3')
        for article in articles:
            item = NewsItem()
            title = article.css('a::text').extract_first()
            url = article.css('a::attr(href)').extract_first()
            item['title'] = title
            item['url'] = url
            # meta是response的一个成员变量，加入meta以后可以通过meta把额外一些内容添加到response中
            # dont_filter防止二次解析的域名被过滤掉
            yield scrapy.Request(url=url, callback=self.parse_article, meta={'item':item}, dont_filter=True)

    def parse_more(self, response):
        # 中国网的点击更多是json载入，但返回的是str形式，所以这里进行正则提取
        rs = response.text.encode("utf-8").decode("unicode-escape")
        rs = re.sub(r'\\', '', rs)
        pattern = re.compile(r'<a href="(.*?)".*?target.*?"_blank">(.*?)</a>', re.S)
        result = re.findall(pattern, rs)
        for data in result:
            item = NewsItem()
            item['title'] = data[1]
            item['url'] = data[0]
            yield scrapy.Request(url=data[0], callback=self.parse_article, meta={'item':item}, dont_filter=True)

    def parse_article(self, response):
        item = response.meta['item']
        # 正则提取css选择的日期内容
        pub_time = response.css('.fl.time2::text').re_first('(\d{4}.*?:\d{2})')
        origin = response.css('.fl.time2 a::text').extract_first()
        contents = response.css('.navp.c p').extract()

        # TODO 在pipeline里面处理list格式image_url并存入数据库
        item['ori_image_url'] = response.css('.navp.c p img::attr(src)').extract()

        contents = ''.join(contents)
        item['pub_time'] = pub_time
        item['origin'] = origin
        item['contents'] = contents
        yield item


