"""Test calling the Shotgun API functions."""

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
        
    def test_automated_find(self):
        """Called find for each entity type and read all fields"""
        
        #we just ned to get some response in the mock
        self._mock_http(
            {'results': {'entities': [{'id': -1, 'type': 'Mystery'}],
                 'paging_info': {'current_page': 1,
                                 'entities_per_page': 500,
                                 'entity_count': 1,
                                 'page_count': 1}}}
        )
        
        all_entities = self.sg.schema_entity_read().keys()
        direction = "asc"
        filter_operator = "all"
        limit = 1
        page = 1
        for entity_type in all_entities:
            if entity_type in ("Asset", "Task", "Shot", "Attachment"):
                continue
            print "Finding entity type", entity_type

            fields = self.sg.schema_field_read(entity_type)
            if not fields:
                print "No fields for %s skipping" % (entity_type,)
                continue
                 
            #trying to use some different code paths to the other find test
            order = [{'field_name': fields.keys()[0],'direction': direction},]
            if "project" in fields:
                filters = [
                    ['project','is', {
                        'type':'Project','id': config.PROJECT_ID}],
                ]
            else:
                filters = []

            records = self.sg.find(entity_type, filters, fields=fields.keys(), 
                order=order, filter_operator=filter_operator, limit=limit, 
                page=page)
            
            self.assertTrue(isinstance(records, list))
            
            if filter_operator == "all":
                filter_operator = "any"
            else: 
                filter_operator = "all"
            if direction == "desc":
                direction = "asc"
            else: 
                direction = "desc"
            limit = (limit % 5) + 1
            page = (page % 3) + 1
        return
        
    def test_schema(self):
        """Called schema functions"""
        
        self._mock_http(dummy_data.schema_entity_read)
        schema = self.sg.schema_entity_read()
        self.assertTrue(schema, dict)
        self.assertTrue(len(schema) > 0)

        self._mock_http(dummy_data.schema_read)
        schema = self.sg.schema_read()
        self.assertTrue(schema, dict)
        self.assertTrue(len(schema) > 0)
        
        self._mock_http(dummy_data.schema_field_read_version)
        schema = self.sg.schema_field_read("Version")
        self.assertTrue(schema, dict)
        self.assertTrue(len(schema) > 0)
        
        self._mock_http(dummy_data.schema_field_read_version_user)
        schema = self.sg.schema_field_read("Version", field_name="user")
        self.assertTrue(schema, dict)
        self.assertTrue(len(schema) > 0)
        self.assertTrue("user" in schema)
                
        self._mock_http({"results":"sg_monkeys"})
        properties = {
            "description" : "How many monkeys were needed"
        }
        new_field_name = self.sg.schema_field_create("Version", "number", 
            "Monkey Count", properties=properties)
            
        self._mock_http({"results":True})
        properties = {
            "description" : "How many monkeys turned up"
        }
        rv = self.sg.schema_field_update("Version", new_field_name, 
            properties)
        self.assertTrue(rv)
        
        self._mock_http({"results":True})
        rv = self.sg.schema_field_delete("Version", new_field_name)
        self.assertTrue(rv)
        
        
    def test_deprecated_functions(self):
        """Deprecated functions raise errors"""
        self.assertRaises(api.ShotgunError, self.sg.schema, "foo")
        self.assertRaises(api.ShotgunError, self.sg.entity_types)