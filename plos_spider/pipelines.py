# -*- coding: utf-8 -*-


import datetime


class ViewsPerDay(object):

    def process_item(self, item, spider):
        """
        Adds the number of views per day to the item
        :param item: MetricsItem
        :param spider: metrics_crawler
        :return: MetricsItem
        """
        right_now = datetime.datetime.now()
        delta = right_now - item["publish_date"]
        views_per_day = item["views"] / delta.days
        item["views_per_day"] = round(views_per_day)

        return item
