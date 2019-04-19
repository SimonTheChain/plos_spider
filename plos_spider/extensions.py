# -*- coding: utf-8 -*-


import os

from scrapy.mail import MailSender
from scrapy import signals
from scrapy.exceptions import NotConfigured


class ClosingActions(object):

    @classmethod
    def from_crawler(cls, crawler):
        """
        Connects the spider signals
        """
        if not crawler.settings.getbool('MYEXT_ENABLED'):
            raise NotConfigured

        # instantiate the extension object
        ext = cls()
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)

        return ext

    @staticmethod
    def spider_closed(spider):
        """
        Sends an email and closes the selenium driver when the spider is closed
        """
        spider.logger.debug("Sending email...")
        mailer = MailSender(
            smtphost="smtp.gmail.com",
            mailfrom=os.environ["EMAIL_SENDER"],
            smtpuser=os.environ["EMAIL_SENDER"],
            smtppass=os.environ["SMTPPASS"],
            smtptls=True,
            smtpssl=True,
            smtpport=587,
        )

        msg_body = "Web crawling job completed: {} articles scraped.".format(
            spider.articles_scraped
        )

        mailer.send(
            to=os.environ["EMAIL_RECEIVER"],
            subject="Web Crawling Results",
            body=msg_body,
            # cc=[""]
        )

        # close the selenium driver
        spider.logger.debug("Closing driver...")
        spider.driver.close()
