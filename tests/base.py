"""Base class for Shotgun API tests."""
try:
    import simplejson as json
except ImportError:
    import json as json
import unittest

import mock
import shotgun_json as api

import config

class TestBase(unittest.TestCase):
    
    def setUp(self):
        
        self.is_mock = False
        self.sg = api.Shotgun(config.server_url, config.script_name, 
            config.api_key, http_proxy=config.http_proxy)
        if config.session_uuid:
            self.sg.set_session_uuid(config.session_uuid)
            
        if config.mock:
            self._setup_mock()
        return
        
    def tearDown(self):
        self.sg = None
        return
    
    def _setup_mock(self):
        """Setup mocking on the ShotgunClient to stop it calling a live server
        """
        #Replace the function used to make the final call to the server
        #eaiser than mocking the http connection + response
        self.sg._http_request = mock.Mock(spec=api.Shotgun._http_request,
            return_value=((200, "OK"), {}, None))
        
        #also replace the function that is called to get the http connection
        #to avoid calling the server. OK to return a mock as we will not use 
        #it
        self.mock_conn = mock.Mock(spec=api.Http)
        #The Http objects connection property is a dict of connections 
        #it is holding
        self.mock_conn.connections = dict()
        self.sg._connection = self.mock_conn
        self.sg._get_connection = mock.Mock(return_value=self.mock_conn)
        
        #create the server caps directly to say we have the correct version
        self.sg._server_caps = api.ServerCapabilities(self.sg.config.server, 
            {"version" : [2,4,0]})
        self.is_mock = True
        return
        
    def _mock_http(self, data, headers=None, status=None):
        """Setup a mock response from the SG server. 
        
        Only has an affect if the server has been mocked. 
        """
        #test for a mock object rather than config.mock as some tests 
        #force the mock to be created
        if not isinstance(self.sg._http_request, mock.Mock):
            return

        if not isinstance(data, basestring):
            data = json.dumps(data, ensure_ascii=False, encoding="utf-8")
            
        resp_headers = {
            'cache-control': 'no-cache',
            'connection': 'close',
            'content-length': (data and str(len(data))) or 0 ,
            'content-type': 'application/json; charset=utf-8',
            'date': 'Wed, 13 Apr 2011 04:18:58 GMT',
            'server': 'Apache/2.2.3 (CentOS)',
            'status': '200 OK'
        }
        if headers:
            resp_headers.update(headers)
        
        if not status:
            status = (200, "OK")
        #create a new mock to reset call list etc.
        self._setup_mock()
        self.sg._http_request.return_value = (status, resp_headers, data)
        
        self.is_mock = True
        return
    
    def _assert_http_method(self, method, params, check_auth=True):
        """Asserts _http_request is called with the method and params."""
        
        args, _ = self.sg._http_request.call_args
        arg_verb, arg_path, arg_body, arg_headers = args
        assert isinstance(arg_body, basestring)
        arg_body = json.loads(arg_body)
        
        arg_params = arg_body.get("params")
        
        self.assertEqual(method, arg_body["method_name"])
        if check_auth:
            auth = arg_params[0]
            self.assertEqual(config.script_name, auth["script_name"])
            self.assertEqual(config.api_key, auth["script_key"])
        
        if params:
            rpc_args = arg_params[len(arg_params)-1]
            self.assertEqual(params, rpc_args)
            
        return
        
