"""Database intefaces for feature_hunter"""

import tinydb
from tinydb import where
from tinydb import TinyDB
import json

from helpers import get_safe_timestamp

class DBWrapper(object):
    def __init__(self, db_path):
        self.db = TinyDB(db_path)

    def insert_target(self, name, url, record_spec, field_specs):
        targets = self.db.table('targets')
        matching_target = targets.get(where('name') == name)
        if matching_target:
            targets.remove(where('name') == name)
        record_spec_str, field_specs_str = [
            json.dumps(spec) for spec in [record_spec, field_specs]
        ]
        targets.insert({
            'name':name,
            'url':url,
            'record_spec':record_spec_str,
            'field_specs':field_specs_str
        })

    def insert_result(self, target_name, result, stamp=None):
        if not target_name or not result:
            return
        if not stamp:
            stamp = get_safe_timestamp()
        result_str = json.dumps(result)
        results = self.db.table('results')
        results.insert({
            'target':target_name,
            'result':result_str,
            'stamp':stamp
        })

    def latest_result_json(self, target_name):
        if not target_name:
            return None

        results = self.db.table('results')
        target_results = results.search(where('target') == target_name)
        if not target_results:
            return None
        target_results = sorted(target_results, key=lambda r: r['stamp'])
        latest_result_raw = target_results[-1].get('result')
        if not latest_result_raw:
            return None
        return json.loads(latest_result_raw)

    def targets(self):
        targets = self.db.table('targets')
        for target in targets.all():
            yield {
                'name':target['name'],
                'url':target['url'],
                'record_spec':json.loads(target['record_spec']),
                'field_specs':json.loads(target['field_specs'])
            }

    def purge(self):
        self.db.purge_tables()
