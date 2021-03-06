# -*- coding: utf-8 -*-


import os

import scrapy
from scrapy.loader import ItemLoader

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from plos_spider.items import MetricsItem


class MetricsSpider(scrapy.Spider):
    """
    Retrieves metrics information and tags on articles about artificial gravity
    """
    name = "metrics_crawler"
    allowed_domains = ['journals.plos.org']
    start_urls = [
        "https://journals.plos.org/plosone/browse/artificial_gravity?page=1",
    ]

    def __init__(self, **kwargs):
        """
        Initializes the selenium driver when the spider is initialized
        """
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome(os.environ["WEBDRIVERS_PATH"] + "chromedriver")
        self.articles_scraped = 0
        self.articles_skipped = []

    def parse(self, response):
        """
        Method called by scrapy when parsing a page
        :param response: http response object
        :return: next page if not None
        """
        self.logger.info("Crawling page: {}".format(response.url))
        search_results = response.xpath('//*[@class="article-block"]/div')

        if len(search_results) == 0:
            return self.logger.error("No article block found")

        for article in search_results:
            article_link = article.xpath('./h2/a/@href').extract_first()
            self.logger.debug("Article link: {}".format(article_link))

            # parse each article page for metrics information
            self.articles_scraped += 1
            yield response.follow(article_link, callback=self.parse_article)

        # extract the url for the next page
        next_page_url = response.xpath('//*[@id="nextPageLink"]/@href').extract_first()
        self.logger.debug("Next page link: {}".format(next_page_url))

        if next_page_url is not None:
            yield response.follow(next_page_url, callback=self.parse)

        # retry skipped articles
        if self.settings.getbool("RETRY_SKIPPED"):
            if self.articles_skipped:

                while len(self.articles_skipped) > 0:
                    article = self.articles_skipped.pop()
                    self.parse_article(article)

    def parse_article(self, response):
        """
        Parses an article page for metrics and tags
        :param response: http response object
        :return: new metrics item
        """
        try:
            # the view count is generated with javascript so we need to use selenium
            self.driver.get(response.url)

            # wait for the dynamic element to be present
            views = WebDriverWait(
                driver=self.driver,
                timeout=10,
                # poll_frequency=500,
            ).until(
                EC.presence_of_element_located((By.ID, "almViews"))
            )
            self.logger.debug("View Count: {}".format(views.text))

        # skip the article if the page times out
        except TimeoutException as e:
            self.logger.warning(
                "Article skipped: {url}\n{error}".format(
                    url=response.url,
                    error=e
                )
            )
            self.articles_skipped.append(response)
            yield None

        else:
            # skip the article if the dynamic element has not been found
            if views is None:
                self.logger.warning("Article skipped: {url}".format(url=response.url))
                self.articles_skipped.append(response.url)
                yield None

            else:
                # we can use scrapy to gather the rest of the data
                tags_container = response.xpath('//*[@id="subjectList"]')
                tags = tags_container.xpath('.//@data-categoryname').extract()
                self.logger.debug("Tags: {}".format(tags))

                publish_string = response.xpath('//*[@id="artPubDate"]/text()').extract_first()
                self.logger.debug("Publish Date: {}".format(publish_string))

                # create item instance
                metrics_loader = ItemLoader(item=MetricsItem(), selector=tags_container)

                # populate item
                metrics_loader.add_value('views', views.text)
                metrics_loader.add_value('tags', tags)
                metrics_loader.add_value('publish_date', publish_string)

                # commit item
                yield metrics_loader.load_item()
