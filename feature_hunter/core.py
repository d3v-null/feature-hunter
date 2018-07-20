""" Provide core functions for feature_hunter. """

import argparse

from alerts import Alerter
from crawler import get_html_crawler_records
from db import DBWrapper
from diff import ResultDiff
from helpers import get_safe_timestamp


def refresh_db(database_path, scrapy_settings=None):
    dbwrapper = DBWrapper(database_path)
    alerts = {}
    for target in list(dbwrapper.targets()):
        target_name = target.get('name')
        assert target_name, "target_name must be valid"
        last_result = dbwrapper.latest_result_json(target_name)
        print "OLD RESULT: %s" % str(last_result)

        this_result = get_html_crawler_records(
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
            alerts[target_name] = delta
    return alerts

def get_parser():
    parser = argparse.ArgumentParser(description="refresh a feature_hunter database")
    # for parser_args, parse_kwargs in [
    #     (['db'], {'help': })
    # ]
    parser.add_argument('--db', help='The path of the database. e.g. feature_db.json')
    parser.add_argument('--user-agent', help="The user agent string",
                        default= 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)')
    parser.add_argument('--scrapy-log-level', help="The log level to use for Scrapy: DEBUG|INFO",
                        default= 'INFO')
    parser.add_argument('--scrapy-log-enable', help="Enable Scrapy logging: TRUE|FALSE",
                        default= 'TRUE')
    parser.add_argument('--enable-alerts', default=False, action='store_true')
    parser.add_argument('--smtp-host')
    parser.add_argument('--smtp-port')
    parser.add_argument('--smtp-sender')
    parser.add_argument('--smtp-pass')
    parser.add_argument('--smtp-receipiant')
    parser.add_argument('--smtp-domain')
    parser.add_argument('--smtp-debug', default=False, action='store_true')
    return parser

def get_settings(args):
    if not args:
        return
    db_path = args.db
    scrapy_settings = {}
    for key, attr in [
        ('USER_AGENT', 'user_agent'),
        ('LOG_LEVEL', 'scrapy_log_level')
    ]:
        if getattr(args, attr, None) is not None:
            scrapy_settings[key] = getattr(args, attr)

    smtp_settings = {}
    for key, attr in [
        ('host', 'smtp_host'),
        ('port', 'smtp_port'),
        ('sender', 'smtp_sender'),
        ('pass', 'smtp_pass'),
        ('host', 'smtp_host'),
        ('domain', 'smtp_domain'),
        ('debug', 'smtp_debug')
    ]:
        if getattr(args, attr, None) is not None:
            smtp_settings[key] = getattr(args, attr)

    return db_path, scrapy_settings, smtp_settings


def main():
    parser = get_parser()
    args = parser.parse_args()
    db_path, scrapy_settings, smtp_settings = get_settings()
    alerts = refresh_db(db_path, scrapy_settings)
    if alerts:
        print "alerts!" + str(alerts)
        if args.enable_alerts:
            Alerter.create_alert(alerts, smtp_settings)

if __name__ == '__main__':
    main()
