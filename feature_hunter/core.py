"""Core functions for feature_hunter"""

import argparse

from db import DBWrapper
from crawler import get_html_crawler_records
from diff import ResultDiff
from helpers import get_safe_timestamp
from alerts import Alerter

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

def main():
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
    args = parser.parse_args()

    if args:
        db_path = args.db
        scrapy_settings = {}
        if args.user_agent is not None:
            scrapy_settings['USER_AGENT'] = args.user_agent
        if args.scrapy_log_level is not None:
            scrapy_settings['LOG_LEVEL'] = args.scrapy_log_level
        smtp_settings = {}
        if args.smtp_host is not None:
            smtp_settings['host'] = args.smtp_host
        if args.smtp_port is not None:
            smtp_settings['port'] = args.smtp_port
        if args.smtp_sender is not None:
            smtp_settings['sender'] = args.smtp_sender
        if args.smtp_pass is not None:
            smtp_settings['pass'] = args.smtp_pass
        if args.smtp_host is not None:
            smtp_settings['host'] = args.smtp_host
        if args.smtp_domain is not None:
            smtp_settings['domain'] = args.smtp_domain
        if args.smtp_debug is not None:
            smtp_settings['debug'] = args.smtp_debug

        alerts = refresh_db(db_path, scrapy_settings)
        if alerts:
            print "alerts!" + str(alerts)
            if args.enable_alerts:
                Alerter.create_alert(alerts, smtp_settings)

if __name__ == '__main__':
    main()
