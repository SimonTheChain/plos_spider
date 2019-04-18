# -*- coding: utf-8 -*-


import re

import scrapy
from scrapy.loader.processors import MapCompose
from scrapy.loader.processors import TakeFirst


def extract_integer(text):
    """
    Extracts an integer from a string
    :param text: Source string
    :return: Integer
    """
    if not isinstance(text, str):
        return

    numbers = re.compile(r"(?P<count>\d+)")
    string_value = text.replace(",", "")
    count_match = numbers.match(string_value)

    if count_match:
        return int(count_match.group("count"))


class MetricsItem(scrapy.Item):
    views = scrapy.Field(
        input_processor=MapCompose(extract_integer),
        output_processor=TakeFirst(),
    )
    publish_date = scrapy.Field(
        output_processor=TakeFirst(),
    )
    views_per_day = scrapy.Field()
    tags = scrapy.Field()
