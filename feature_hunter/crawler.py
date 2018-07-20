""" Provide crawler functions for feature_hunter. """

import json
import re

import scrapy
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.selector import SelectorList
from scrapy.xlib.pydispatch import dispatcher


class GeneralizedRecordSpider(scrapy.Spider):
    name="records"

    def __init__(self, record_spec, field_specs, start_urls, *args, **kwargs):
        super(GeneralizedRecordSpider, self).__init__(*args, **kwargs)
        self.start_urls = start_urls
        self.field_specs = field_specs
        self.record_spec = record_spec

    # def query_response(self, response, query_type, query):
    #
    #
    # def query_selector(self, selector, query_type, query):
    #     if query_type == 'css':
    #         return selector.css(query)
    #     elif query_type == 'xpath':
    #         return selector.xpath(query)
    #     elif query_type == 'jsonpath':


    def get_field_raw(self, record_selector, field_spec):
        if field_spec.get('css'):
            return record_selector.css(field_spec['css']).extract_first()
        elif field_spec.get('xpath'):
            return record_selector.xpath(field_spec['xpath']).extract_first()
        # elif field_spec.get('jsonpath'):
        #     json_record = json.loads(response.body_as_unicode())
        #     jsonpath_expr = parse(field_spec['jsonpath'])
        #
        #     return

        return record_selector.extract()
        # print "field_raw: %s" % (repr(field_raw))

    def get_record_fields(self, record_selector):
        record_fields = {}
        for field_name, field_spec in self.field_specs.items():
            # print "processing field %s with fieldspec %s" % (field_name, str(field_spec))
            # print "respons being parsed: %s" % (record_selector.extract())
            record_fields[field_name] = None
            field_raw = self.get_field_raw(record_selector, field_spec)
            if not field_raw:
                continue
            if field_spec.get('regex'):
                # print "matching %s on %s" % (repr(field_spec.get('regex')), repr(field_raw))
                field_match = re.search(field_spec.get('regex'), field_raw)
                if not field_match:
                    continue
                record_fields[field_name] = field_match.group(1)
            else:
                record_fields[field_name] = field_raw
        return record_fields


    def parse(self, response):
        if self.record_spec.get('css'):
            record_selectors = response.css(self.record_spec['css'])
        elif self.record_spec.get('xpath'):
            record_selectors = response.xpath(self.record_spec['xpath'])
        # elif self.record_spec.get('jsonpath'):
        #     json_response = json.loads(response.body_as_unicode())
        #     jsonpath_expr = parse(self.record_spec['jsonpath'])
        #     records_raw = [json.dumps(match.value) for match in jsonpath_expr.find(json_response)]
        #     record_selectors = SelectorList([Selector(text=record_raw) for record_raw in records_raw])
        else:
            record_selectors = SelectorList()
        for record_selector in record_selectors:
            yield self.get_record_fields(record_selector)

class GeneralizedHtmlRecordSpider(GeneralizedRecordSpider):
    name = "html_records"


class GeneralizedJsonSpider(GeneralizedRecordSpider):
    name = "json_records"


    def parse(self, response):
        json_response = json.loads(response.body_as_unicode())

def get_html_crawler_records(record_spec, field_specs, start_urls, settings=None):
    if not settings:
        settings = {
            'USER_AGENT':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
            'LOG_LEVEL':'INFO'
        }
    process = CrawlerProcess(settings)
    process.crawl(
        GeneralizedHtmlRecordSpider,
        record_spec=record_spec,
        field_specs=field_specs,
        start_urls=start_urls
    )

    items = []
    def add_item(item):
        items.append(item)
    dispatcher.connect(add_item, signal=signals.item_passed)
    process.start()
    return items
