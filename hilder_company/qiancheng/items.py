# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class QianchengItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    company_source = scrapy.Field()
    company_id = scrapy.Field()
    company_name = scrapy.Field()
    url = scrapy.Field()
    company_size = scrapy.Field()
    business = scrapy.Field()
    company_info = scrapy.Field()
    address = scrapy.Field()
    crawler_time = scrapy.Field()

    city = scrapy.Field()
    region = scrapy.Field()
    company_short_info = scrapy.Field()
    development_stage = scrapy.Field()
    registration_time = scrapy.Field()
    registered_capital = scrapy.Field()
    operating_period = scrapy.Field()
