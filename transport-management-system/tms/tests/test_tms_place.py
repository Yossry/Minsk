# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import urllib

from mock import MagicMock

import simplejson as json

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestTmsPlace(TransactionCase):

    def setUp(self):
        super(TestTmsPlace, self).setUp()
        self.place = self.env.ref('tms.tms_place_01')
        self.result = {
            'status': 'OK',
            'results': [
                {'geometry': {
                    'location_type': 'APPROXIMATE',
                    'bounds': {
                        'northeast': {'lat': 29.73872,
                                      'lng': -98.22295799999999},
                        'southwest': {'lat': 29.2241411, 'lng': -98.8058509}},
                    'viewport': {
                        'northeast': {'lat': 29.73872,
                                      'lng': -98.22295799999999},
                        'southwest': {'lat': 29.2241411, 'lng': -98.8058509}},
                    'location': {'lat': 29.4241219,
                                 'lng': -98.49362819999999}},
                    'address_components': [{
                        'long_name': 'San Antonio',
                        'types': ['locality', 'political'],
                        'short_name': 'San Antonio'}, {
                        'long_name': 'Bexar County',
                        'types': ['administrative_area_level_2', 'political'],
                        'short_name': 'Bexar County'}, {
                        'long_name': 'Texas',
                        'types': ['administrative_area_level_1', 'political'],
                        'short_name': 'TX'}, {
                        'long_name': 'United States',
                        'types': ['country', 'political'],
                        'short_name': 'US'}],
                    'place_id': 'ChIJrw7QBK9YXIYRvBagEDvhVgg',
                    'formatted_address': 'San Antonio, TX, USA',
                    'types': ['locality', 'political']}]}
        self.geo_point = {
            'coordinates': [1234567.0123456789, 2273030.926987689],
            'type': 'Point'}

    def test_10_tms_place_get_coordinates(self):
        urllib.urlopen = MagicMock()
        urllib.urlopen.return_value = False
        with self.assertRaisesRegexp(
                ValidationError,
                'Google Maps is not available.'):
            self.place.get_coordinates()
        self.place.state_id = False
        with self.assertRaisesRegexp(
                ValidationError,
                'You need to set a Place and a State Name'):
            self.place.get_coordinates()

    def test_11_tms_place_get_coordinates(self):
        json.load = MagicMock()
        json.load.return_value = self.result
        self.place.get_coordinates()
        self.assertEqual(self.place.latitude, 29.4241219,
                         msg='Latitude is not correct')
        self.assertEqual(self.place.longitude, -98.4936282,
                         msg='Longitude is not correct')

    def test_20_tms_place_open_in_google(self):
        self.place.open_in_google()

    def test_30_tms_place_compute_complete_name(self):
        self.place._compute_complete_name()
        self.assertEqual(self.place.complete_name, 'San Antonio, Texas',
                         'Full Complete Name')

    def test_40_tms_place_compute_complete_name(self):
        self.place.write({'name': 'San Francisco'})
        self.place._compute_complete_name()
        self.assertEqual(
            self.place.complete_name,
            'San Francisco, Texas',
            'On change works')
        self.place.write({'state_id': False})
        self.place._compute_complete_name()
        self.assertEqual(
            self.place.complete_name,
            'San Francisco',
            'On change works')

    def test_50_tms_place_get_country_id(self):
        self.place.get_country_id()
        self.assertEqual(self.place.country_id, self.place.state_id.country_id)
        self.place.state_id = False
        self.place.get_country_id()
        self.assertEqual(self.place.country_id.id, False)
