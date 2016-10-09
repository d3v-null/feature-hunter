# -*- coding: utf-8 -*-

from context import feature_hunter
from feature_hunter.db import DBWrapper
from feature_hunter.crawler import get_crawler_items
from feature_hunter.diff import ResultDiff

import unittest
# from tinydb import TinyDB
import json

target_name = 'triplej'
target_url = 'http://www.abc.net.au/triplej/music/featurealbums/'
target_record_spec = {"css": "div.podlist_item"}
target_field_specs = {
    "album": {"regex": r" - \s*(\S[\s\S]+\S)\s*$", "css": "div.text div.title::text"},
    "artist": {"regex": r"^\s*(\S[\s\S]+\S)\s* - ", "css": "div.text div.title::text"}
}

test_new_result = [ {"album": "Westway (The Glitter & The Slums)", "artist": "Sticky Fingers"}, {"album": "Smoke Fire Hope Desire", "artist": "Harts"}, {"album": "Divas & Demons", "artist": "Remi"}, {"album": "Internal", "artist": "SAFIA"}, {"album": "Animal", "artist": "Big Scary"}, {"album": "Prolapse", "artist": "Knife Party"}]
test_old_result = [ {"album": "Smoke Fire Hope Desire", "artist": "Harts"}, {"album": "Divas & Demons", "artist": "Remi"}, {"album": "Internal", "artist": "SAFIA"}, {"album": "Animal", "artist": "Big Scary"}, {"album": "Prolapse", "artist": "Knife Party"}, {"album": "Some Album", "artist":"Some Artist"}]
test_difference = [ {"album": "Westway (The Glitter & The Slums)", "artist": "Sticky Fingers"} ]

class DBTestsBasic(unittest.TestCase):
    """Basic DB Test cases."""

    def setUp(self):
        self.dbwrapper = DBWrapper("feature_albums_db_test.json")
        self.dbwrapper.purge()
        self.dbwrapper.insert_target(
            name=target_name,
            url=target_url,
            record_spec=target_record_spec,
            field_specs=target_field_specs
        )

        self.dbwrapper.insert_result(
            target_name='triplej',
            stamp='2016-10-09_15-25-00',
            result=test_new_result
        )
        self.dbwrapper.insert_result(
            target_name='triplej',
            stamp='2016-10-08_15-25-00',
            result=test_old_result
        )

    def testLatestResult(self):
        self.assertListEqual(
            self.dbwrapper.latest_result_json('triplej'),
            test_new_result
        )

    def testTargets(self):
        targets = list(self.dbwrapper.targets())
        self.assertTrue(len(targets) == 1)
        target = dict(targets[0])
        self.assertEqual(target['name'], target_name)
        self.assertEqual(target['url'], target_url)
        self.assertEqual(target['record_spec'], target_record_spec)
        self.assertEqual(target['field_specs'], target_field_specs)


# @unittest.skip("don't want to test on live server too often. uncomment to enable test")
class CrawlerTestsBasic(unittest.TestCase):
    def testCrawl(self):
        items = get_crawler_items(
            record_spec={
                'css':'div.podlist_item'
            },
            field_specs={
                'album':{
                    # 'xpath':"//div[contains(concat(' ', normalize-space(@class), ' '), ' podlist_item ')]//div[contains(concat(' ', normalize-space(@class), ' '), ' title ')]"
                    'css':'div.text div.title::text',
                    'regex':r' - \s*(\S[\s\S]+\S)\s*$'
                },
                'artist':{
                    'css':'div.text div.title::text',
                    'regex':r'^\s*(\S[\s\S]+\S)\s* - '
                }
            },
            start_urls=[
                'http://www.abc.net.au/triplej/music/featurealbums/'
            ]
        )
        self.assertEqual(len(items), 6)
        for item in items:
            self.assertTrue(item['album'])
            self.assertTrue(item['artist'])

class DiffTestBasic(unittest.TestCase):

    def testSimilarResults(self):
        "tests if resultsdiff doesn't false positive when results are reordered"
        diff = ResultDiff(
            old_result=test_old_result,
            new_result=[test_old_result[-1]]+test_old_result[:-1]
        )
        self.assertEqual(diff.difference(), [])

    def testNewRecord(self):
        diff = ResultDiff(
            old_result=test_old_result,
            new_result=test_new_result
        )
        self.assertEqual(diff.difference(), test_difference)

if __name__ == '__main__':
    unittest.main()
