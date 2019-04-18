# -*- coding: utf-8 -*-


import re
import datetime

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
        raise TypeError("The argument for 'extract_integer' should be a string")

    numbers = re.compile(r"(?P<count>\d+)")
    string_value = text.replace(",", "")
    count_match = numbers.match(string_value)

    if count_match:
        return int(count_match.group("count"))


def convert_to_datetime(publish_string):
    """
    Converts a date string into datetime
    :param publish_string: Date in the form of a string
    :return: Date in datetime
    """
    if not isinstance(publish_string, str):
        raise TypeError("The argument for 'convert_to_datetime' should be a string")

    publish_datetime = datetime.datetime.strptime(
        publish_string,
        "Published: %B %d, %Y"
    )

    return publish_datetime


class MetricsItem(scrapy.Item):
    views = scrapy.Field(
        input_processor=MapCompose(extract_integer),
        output_processor=TakeFirst(),
    )
    publish_date = scrapy.Field(
        input_processor=MapCompose(convert_to_datetime),
        output_processor=TakeFirst(),
    )
    views_per_day = scrapy.Field()
    tags = scrapy.Field()
