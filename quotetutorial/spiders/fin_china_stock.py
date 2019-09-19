# -*- coding: utf-8 -*-
import scrapy
import re
from urllib.parse import urlencode

from quotetutorial.items import NewsItem
from quotetutorial.items import ImageItem

class FinChinaStockSpider(scrapy.Spider):
    name = 'fin_china_stock'
    allowed_domains = ['finance.china.com.cn/stock']
    # 这里去掉了start_urls，因为它会在start_requests自动执行一遍。
    # start_urls = ['http://finance.china.com.cn/stock/']

    first_url = 'http://finance.china.com.cn/stock/'
    more_urls = []
    for i in range(1,3):
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
        # TODO 加一个ImageItem进来获取原始图片地址，并转换，保存新旧数据

        item = response.meta['item']
        # 正则提取css选择的日期内容
        pub_time = response.css('.fl.time2::text').re_first('(\d{4}.*?:\d{2})')
        origin = response.css('.fl.time2 a::text').extract_first()
        contents = response.css('.navp.c p').extract()

        '''# TODO 添加image获取，下载上传oss，转换并储存
        ori_image_urls = response.css('.navp.c p').re('<img src="(.*?)">')
        oss_image_urls = []
        for j in len(ori_image_urls):
            ImageItems = ImageItem()
            ImageItems['ori_image_url'] = ori_image_urls[j]
            # TODO 这里有个下载储存并上传到oss，最终返回oss地址的动作
            ImageItems['oss_image_url'] = None
            oss_image_urls.append()'''

        contents = ''.join(contents)
        # TODO 写个替换老网址的for loop (replace函数，考虑一次替换)

        item['pub_time'] = pub_time
        item['origin'] = origin
        item['contents'] = contents
        yield item


