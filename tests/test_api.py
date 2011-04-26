"""Test calling the Shotgun API functions.

Includes short run tests, like simple crud and single finds. See 
test_api_long for other tests.
"""

import datetime
import sys
import time
import unittest

import mock
import shotgun_json as api

import base, config, dummy_data

class TestShotgunApi(base.TestBase):
    

    def setUp(self):
        super(TestShotgunApi, self).setUp()
        return
        
    def test_info(self):
        """Called info"""
        
        self._mock_http({
            'version': [2, 4, 0, u'Dev']
        })
        
        self.sg.info()
        return
    
    def test_server_dates(self):
        """Pass datetimes to the server"""
        t = {
            'project': { 'type': 'Project', 'id': config.PROJECT_ID },
            'start_date': datetime.date.today(),
        }
        newtask = self.sg.create('Task', t, ['content', 'sg_status_list'])

        t = {
            'project': { 'type': 'Project', 'id': config.PROJECT_ID },
            'sg_test_time': datetime.datetime.now(),
        }

        newtask = self.sg.create('Task', t, ['content', 'sg_status_list'])
        
        return

    def test_create_update_delete(self):
        """Called create, update, delete, revive"""
        
        #Create
        self._mock_http(
            {'results': {'code': 'JohnnyApple_Design01_FaceFinal',
             'description': 'fixed rig per director final notes',
             'entity': {'id': config.ASSET_ID, 'name': 'Asset 1', 'type': 'Asset'},
             'id': config.VERSION_ID,
             'project': {'id': config.PROJECT_ID, 'name': 'Demo Project', 'type': 'Project'},
             'sg_status_list': 'rev',
             'type': 'Version',
             'user': {'id': config.HUMAN_ID, 'name': 'Aaron Morton', 'type': 'HumanUser'}}}
        )
        
        data = {
            'project': {'type':'Project','id':config.PROJECT_ID},
            'code':'JohnnyApple_Design01_FaceFinal',
            'description': 'fixed rig per director final notes',
            'sg_status_list':'rev',
            'entity': {'type':'Asset','id':config.ASSET_ID},
            'user': {'type':'HumanUser','id':config.HUMAN_ID},
        }
        
        version = self.sg.create("Version", data, return_fields = ["id"])
        self.assertTrue(isinstance(version, dict))
        self.assertTrue("id" in version)
        #TODO: test returned fields are requested fields
        
        #Update
        self._mock_http(
            {'results': {'description': 'updated test', 
                'id': version["id"], 'type': 'Version'}}
        )
        
        data = data = {
            "description" : "updated test"
        }
        version = self.sg.update("Version", version["id"], data)
        self.assertTrue(isinstance(version, dict))
        self.assertTrue("id" in version)
        
        #Delete
        self._mock_http(
            {'results': True}
        )
        rv = self.sg.delete("Version", version["id"])
        self.assertEqual(True, rv)
        self._mock_http(
            {'results': False}
        )
        rv = self.sg.delete("Version", version["id"])
        self.assertEqual(False, rv)

        #Revive
        self._mock_http(
            {'results': True}
        )
        rv = self.sg.revive("Version", version["id"])
        self.assertEqual(True, rv)
        self._mock_http(
            {'results': False}
        )
        rv = self.sg.revive("Version", version["id"])
        self.assertEqual(False, rv)
        
    def test_find(self):
        """Called find, find_one for known entities"""
        
        self._mock_http(
            {'results': {'entities': [{'id': config.VERSION_ID, 'type': 'Version'}],
                 'paging_info': {'current_page': 1,
                                 'entities_per_page': 500,
                                 'entity_count': 1,
                                 'page_count': 1}}}
        )
        
        filters = [
            ['project','is',{'type':'Project','id': config.PROJECT_ID}],
            ['id','is', config.VERSION_ID]
        ]
        
        fields = ['id']
        
        versions = self.sg.find("Version", filters, fields=fields)
        
        self.assertTrue(isinstance(versions, list))
        version = versions[0]
        self.assertEqual("Version", version["type"])
        self.assertEqual(config.VERSION_ID, version["id"])
        
        version = self.sg.find_one("Version", filters, fields=fields)
        self.assertEqual("Version", version["type"])
        self.assertEqual(config.VERSION_ID, version["id"])
        
    def test_deprecated_functions(self):
        """Deprecated functions raise errors"""
        self.assertRaises(api.ShotgunError, self.sg.schema, "foo")
        self.assertRaises(api.ShotgunError, self.sg.entity_types)