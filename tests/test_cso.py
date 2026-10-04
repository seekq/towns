import copy
import unittest
from unittest.mock import patch
import cso


class ParsingTests(unittest.TestCase):
    def setUp(self):
        self.cube = {
            'id': ['town', 'sex'], 'size': [2, 2],
            'dimension': {
                'town': {'category': {'index': {'b': 1, 'a': 0},
                                     'label': {'a': 'Alpha', 'b': 'Beta'}}},
                'sex': {'category': {'index': ['m', 'f']}}},
            'value': {'0': 0, '3': 9}, 'status': {'3': 'p'}}

    def test_sparse_order_missing_zero_and_status(self):
        rows = list(cso.iter_rows(*cso.normalize_dataset(self.cube)))
        self.assertEqual(rows, [['Alpha', 'm', '0', ''], ['Alpha', 'f', '', ''],
                                ['Beta', 'm', '', ''], ['Beta', 'f', '9', 'p']])

    def test_classic_wrapper_and_dimension_order(self):
        classic = copy.deepcopy(self.cube)
        classic['dimension']['id'] = classic.pop('id')
        classic['dimension']['size'] = classic.pop('size')
        self.assertEqual(list(cso.iter_rows(*cso.normalize_dataset({'dataset': classic}))),
                         list(cso.iter_rows(*cso.normalize_dataset(self.cube))))

    def test_reject_wrong_value_count(self):
        self.cube['value'] = [1]
        with self.assertRaises(ValueError):
            cso.normalize_dataset(self.cube)

    def test_reject_invalid_category_positions(self):
        self.cube['dimension']['town']['category']['index'] = {'a': 1, 'b': 1}
        with self.assertRaises(ValueError):
            cso.normalize_dataset(self.cube)

    def test_label_resolution_and_ambiguity(self):
        meta = {'variables': [{'code': 'T', 'text': 'Town', 'values': ['a', 'b'],
                              'valueTexts': ['Alpha, County One', 'Alpha Two']}]}
        self.assertEqual(cso.resolve_select(['Town=County One'], meta)[0]['selection']['values'], ['a'])
        with self.assertRaises(SystemExit):
            cso.resolve_select(['Town=Alpha'], meta)
        with self.assertRaises(SystemExit):
            cso.resolve_select(['T=a', 'T=*'], meta)

    def test_retry_exhaustion_reports_http_status(self):
        response = unittest.mock.Mock(status_code=503, text='Unavailable', headers={})
        with patch('cso.requests.Session') as session, patch('cso.time.sleep') as sleep:
            session.return_value.__enter__.return_value.request.return_value = response
            with self.assertRaisesRegex(SystemExit, 'HTTP 503'):
                cso.request_response('GET', 'https://example.invalid', max_retries=2)
            self.assertEqual(sleep.call_count, 1)


if __name__ == '__main__':
    unittest.main()
