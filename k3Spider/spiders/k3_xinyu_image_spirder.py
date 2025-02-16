from typing import Any, Iterable

import scrapy
from scrapy import Request
from scrapy.http import Response

from k3Spider.items import K3XinyuImageItem


class K3XinyuImageSpider(scrapy.Spider):
    name = 'k3_xinyu_spider'
    allowed_domains = ['xinyu.k3.cn', 'www.k3.cn']
    start_urls = ['http://xinyu.k3.cn/']

    # def start_requests(self) -> Iterable[Request]:
    # def start_requests(self):
    #     cookies = {
    #         'daily_login': '1',
    #         'user_user_id': '3852585',
    #         'user_username': '17279821841%40k3.cn',
    #         'user_phash': 'e2b6dcc1558670683e61308ae439af6b',
    #         'user_hash': '4d2d87d763cf78b9258942e6b0a06f88',
    #         'k3cn': 'dXNlcl9pZD0zODUyNTg1JnR5cGU9MCZ1c2VybmFtZT0xNzI3OTgyMTg0MUBrMy5jbiZ0PTE3Mzk2ODkyNzMmaGFzaD1jNGZmMTczMzVhNzFjNzYwMzBiNzI4Mzc3ODVmOTBmMA%3D%3D',
    #     }
    #
    #     for url in self.start_urls:
    #         yield scrapy.Request(url, cookies=cookies, callback=self.parse)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        # 不使用get_all()
        li_lists = response.css('body div.container ul.content li')

        temp_lists = li_lists[:1]

        for item in temp_lists:
            # 详情页面链接,需要进去爬取相关数据
            detail_page = item.css('a.pictureTags::attr(href)').get()

            if detail_page:
                headers = {
                    'Host': 'www.k3.cn',
                    'Origin': 'https://www.k3.cn',
                    'Referer': 'https://www.k3.cn/p/ooboump.html?_page=1&_cat=xinyu&_pos=1&_type=img',
                    'X-Requested-With': 'XMLHttpRequest',
                }

                cookies = {
                    'user_phash': 'e2b6dcc1558670683e61308ae439af6b',
                    'k3cn': 'dXNlcl9pZD0zODUyNTg1JnR5cGU9MCZ1c2VybmFtZT0xNzI3OTgyMTg0MUBrMy5jbiZ0PTE3Mzk2ODkyNzMmaGFzaD1jNGZmMTczMzVhNzFjNzYwMzBiNzI4Mzc3ODVmOTBmMA%3D%3D',
                    'user_hash': '4d2d87d763cf78b9258942e6b0a06f88',
                    'acw_tc': '1a0c399c17397125993264060e0033c66cea119fc18062f3ad9dbf525e4f24',
                }
                print(f'Found detail page: {detail_page}')  # 调试输出
                yield response.follow(detail_page, cookies=cookies, callback=self.parse_detail)

            image_url = item.css('a.pictureTags img.indexImage::attr(data-url)').get()
            print(image_url)

    # 爬取详情页的数据
    def parse_detail(self, response: Response, **kwargs: Any) -> Any:
        print('获取详情页面数据')

        contact_div = response.css('div.business div.site_right')
        address = contact_div.css('div:nth-of-type(2)').get()
        qq_number = contact_div.css('div:nth-of-type(3)').get()
        print(address)
        print(qq_number)
        print('获取详情页面数据 ----- 结束')

