#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import random
import string
import hashlib
import datetime
import time
import Cookie
import json
import urllib2
import urllib
from utils import *

from time import gmtime, strftime
from datetime import datetime
from collections import namedtuple

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from dbs.databases import *
from google.appengine.api import search

inf = 100000

class SearchHandler(webapp2.RequestHandler):
    
    def get(self):
        
        params_html = {}
        #----------------------Check If a User Has Signed In-------------------------
        admin_flag = 0
        temp = self.request.cookies.get('user_id')
        if temp:
            userid = valid_hash_cookie(temp)
            if userid:
                params_html['userid'] = userid
                user = db.GqlQuery("SELECT * FROM UserPass_User WHERE user_id = '%s'" %userid)
                user = user.get()
                if user:
                    admin_flag = user.isadmin
                    
        params_html['admin_flag'] = admin_flag
        #----------------------------------------------------------------------------
        
        #-------------------------Perform a Search over the Database-----------------
        returned_results = []
        search_results_sorted_price = []
        search_query = unescape_html(self.request.get('q'))
        
        try:
            index = search.Index('PAPER_INDICES')
            query = search.Query(query_string=search_query,options=search.QueryOptions(limit=20))
            search_results = index.search(query)
            number_found = search_results.number_found
            
            
            for doc in search_results:
                paper_desc = []
                paper_desc.append(doc.field('title').value)
                paper_desc.append(doc.field('authors').value)
                paper_desc.append(int(doc.field('pub_year').value))
                paper_desc.append(doc.field('dockey').value)
                
                returned_results.append(paper_desc)
            
            
        except search.Error:
            self.response.out.write('Search Error!')                
        #----------------------------------------------------------------------------            
        
        #--------------------------Assign HTML Parameters----------------------------
        params_html['papers_list'] = returned_results
        #----------------------------------------------------------------------------
        
        self.response.out.write(template.render('./html/display_search_results.html',params_html))
              
                     
    