# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class K3XinyuShoeMetaData(scrapy.Item):
    image_url = scrapy.Field()
    title = scrapy.Field()  # 货号
    address = scrapy.Field()  # 拿货地址
    qq_number = scrapy.Field()  # QQ号码
    mobile = scrapy.Field()  # 手机号
    wx = scrapy.Field()  # 微信号
