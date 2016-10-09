"""Crawler functions for feature_hunter"""

import scrapy
import re
from scrapy.crawler import CrawlerProcess
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals

class ArbitraryRecordSpider(scrapy.Spider):
    name = "feature_albums"

    def __init__(self, record_spec, field_specs, start_urls, *args, **kwargs):
        super(ArbitraryRecordSpider, self).__init__(*args, **kwargs)
        self.start_urls = start_urls
        self.field_specs = field_specs
        self.record_spec = record_spec

    def parse(self, response):
        if self.record_spec.get('css'):
            response_records = response.css(self.record_spec['css'])
        elif self.record_spec.get('xpath'):
            response_records = response.xpath(self.record_spec['xpath'])
        else:
            response_records = []
        for response_record in response_records:
            record_fields = {}
            for field_name, field_spec in self.field_specs.items():
                # print "processing field %s with fieldspec %s" % (field_name, str(field_spec))
                # print "respons being parsed: %s" % (response_record.extract())
                record_fields[field_name] = None
                if field_spec.get('css'):
                    field_raw = response_record.css(field_spec['css']).extract_first()
                elif field_spec.get('xpath'):
                    field_raw = response_record.xpath(field_spec['xpath']).extract_first()
                else:
                    field_raw = response_record.extract()
                # print "field_raw: %s" % (repr(field_raw))
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
            yield record_fields

def get_crawler_items(record_spec, field_specs, start_urls, settings=None):
    if not settings:
        settings = {
            'USER_AGENT':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
            'LOG_LEVEL':'INFO'
        }
    process = CrawlerProcess(settings)
    process.crawl(
        ArbitraryRecordSpider,
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
