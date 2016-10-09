"""Core functions for feature_hunter"""

import argparse

from db import DBWrapper
from crawler import get_crawler_items
from diff import ResultDiff
from helpers import get_safe_timestamp

def refresh_db(database_path, scrapy_settings=None):
    dbwrapper = DBWrapper(database_path)
    for target in list(dbwrapper.targets()):
        target_name = target.get('name')
        assert target_name, "target_name must be valid"
        last_result = dbwrapper.latest_result_json(target_name)
        print "OLD RESULT: %s" % str(last_result)

        this_result = get_crawler_items(
            record_spec=target['record_spec'],
            field_specs=target['field_specs'],
            start_urls=[target['url']],
            settings=scrapy_settings
        )
        print "NEW RESULT: %s" % str(this_result)

        delta = ResultDiff(last_result, this_result).difference()

        print "DELTA: %s" % delta

        if delta:
            dbwrapper.insert_result(
                target_name=target_name,
                result=this_result,
                stamp=get_safe_timestamp()
            )

def main():
    parser = argparse.ArgumentParser(description="refresh a feature_hunter database")
    parser.add_argument('--db', help='The path of the database. e.g. feature_db.json')
    parser.add_argument('--user-agent', help="The user agent string",
                        default= 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)')
    parser.add_argument('--scrapy-log-level', help="The log level to use for Scrapy",
                        default= 'INFO')
    args = parser.parse_args()

    if args:
        db_path = args.db
        scrapy_settings = {}
        if args.user_agent:
            scrapy_settings['USER_AGENT'] = args.user_agent
        if args.scrapy_log_level:
            scrapy_settings['LOG_LEVEL'] = args.scrapy_log_level
        refresh_db(db_path, scrapy_settings)

if __name__ == '__main__':
    main()
