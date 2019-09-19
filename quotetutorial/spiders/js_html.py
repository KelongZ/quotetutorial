# -*- coding: utf-8 -*-
import scrapy
import json
import re
from urllib.parse import urlencode

class JsHtmlSpider(scrapy.Spider):
    name = 'js_html'
    allowed_domains = ['finance.china.com.cn']

    start_urls = []
    for i in range(1,5):
        data = {
            'callback': 'jQuery111109070254808521516_1568796896902',
            'cnl': 'stock',
            'index': '0',
            'page': i
        }
        params = urlencode(data)
        base_url = 'http://app.finance.china.com.cn/news/more_news.php'
        url = 'http://app.finance.china.com.cn/news/more_news.php' + '?' + params
        start_urls.append(url)



    def parse(self, response):
        rs = response.text.encode("utf-8").decode("unicode-escape")
        rs = re.sub(r'\\', '', rs)
        pattern = re.compile(r'<a href="(.*?)".*?target.*?"_blank">(.*?)</a>', re.S)
        result = re.findall(pattern, rs)
        for item in result:
            i = item[0]
            j = item[1]
            print(i+'\n'+j)