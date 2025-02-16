import re
from typing import Any, Iterable

import scrapy
from scrapy import Request
from scrapy.http import Response

from k3Spider.items import K3XinyuImageItem, K3XinyuShoeMetaData


class K3XinyuImageSpider(scrapy.Spider):
    name = 'k3_xinyu_spider'
    allowed_domains = ['xinyu.k3.cn', 'www.k3.cn']
    start_urls = ['http://xinyu.k3.cn/']


    def parse(self, response: Response, **kwargs: Any) -> Any:
        # 不使用get_all()
        li_lists = response.css('body div.container ul.content li')
        temp_lists = li_lists[:1]



        for item in temp_lists:
            shoe_meta_data = K3XinyuShoeMetaData()
            image_url = item.css('a.pictureTags img.indexImage::attr(data-url)').get()

            shoe_meta_data['image_url'] = image_url

            # 详情页面链接,需要进去爬取相关数据
            detail_page = item.css('a.pictureTags::attr(href)').get()
            if detail_page:
                headers = {
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding': 'gzip, deflate, br, zstd',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Pragma': 'no-cache',
                    'Referer': 'https://www.k3.cn/p/ooboump.html?_page=1&_cat=xinyu&_pos=1&_type=img',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
                    'X-Requested-With': 'XMLHttpRequest',
                    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
                }
                cookies = {
                    'daily_login': '1',
                    'user_user_id': '3852585',
                    'user_login_ip': '183.239.141.21',
                    'user_username': '17279821841%40k3.cn',
                    'user_type': '0',
                    'user_is_user_login': '1',
                    'user_login_type': 'web',
                    'user_phash': 'e2b6dcc1558670683e61308ae439af6b',
                    'k3cn': 'dXNlcl9pZD0zODUyNTg1JnR5cGU9MCZ1c2VybmFtZT0xNzI3OTgyMTg0MUBrMy5jbiZ0PTE3Mzk2ODkyNzMmaGFzaD1jNGZmMTczMzVhNzFjNzYwMzBiNzI4Mzc3ODVmOTBmMA%3D%3D',
                    'user_hash': '4d2d87d763cf78b9258942e6b0a06f88',
                    'acw_tc': '0a472f8217397185774694971e0039c06895fbcb6812bb06d5f8136316a6a4',
                }

                yield response.follow(detail_page, cookies=cookies, callback=self.parse_detail, meta={'meta_data': shoe_meta_data})


    # 爬取详情页的数据
    def parse_detail(self, response: Response, **kwargs: Any) -> Any:
        print('获取详情页面数据')

        contact_div = response.css('div.business div.site_right')
        # 提取地址（排除 <b> 标签）
        address = contact_div.xpath('.//div[contains(., "拿货点")]//text()[not(parent::b)]').getall()
        address = ''.join(address).strip()  # 合并文本并去除空白字符
        address = re.sub(r'^[：\s ]+', '', address)  # 剔除开头的 `：`、空格和 ` `


        # 提取 QQ 号码（排除 <b> 标签）
        qq_number = contact_div.xpath('.//div[contains(., "Q Q")]//text()[not(parent::b)]').getall()
        qq_number = ''.join(qq_number).strip()  # 合并文本并去除空白字符
        qq_number = re.sub(r'^[：\s ]+', '', qq_number)  # 剔除开头的 `：`、空格和 ` `

        # # 提取地址（排除 <b> 标签）
        # address_div = contact_div.css('div:contains("拿货点")')
        # address = ''.join(address_div.css('*:not(b)::text').getall()).strip()
        #
        # # 提取 QQ 号码（排除 <b> 标签）
        # qq_div = contact_div.css('div:contains("Q Q")')
        # qq_number = ''.join(qq_div.css('*:not(b)::text').getall()).strip()
        shoe_meta_data = response.meta['meta_data']
        shoe_meta_data['address'] = address
        shoe_meta_data['qq_number'] = qq_number
        # print('地址:', address)
        # print('QQ号码:', qq_number)
        print('获取详情页面数据 ----- 结束')

        yield  shoe_meta_data

