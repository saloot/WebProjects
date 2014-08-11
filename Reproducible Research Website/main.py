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


from handlers.login_handle import LoginHandler
from handlers.logout_handle import LogoutHandler
from handlers.newpost_handle import NewPostHandler
from handlers.displaypaper_handle import DisplayPaperHandler
from handlers.displaypaper_handle import DisplayPostHandler_JSON
from handlers.signup_handle import SignUpHandler
from handlers.dashboard_handle import DashboardHandler
from handlers.authorprofile_handle import AuthorProfileHandler
from handlers.displaymap_handle import DisplayMapHandler
from handlers.admin_handle import AdminHandler
from handlers.image_handle import ImageHandler
from handlers.review_handle import ReviewHandler
from handlers.import_papers_handle import ImportHandler
from handlers.not_found import NotFoundHandler
from handlers.how_handler import HowItWorksHandler
from handlers.about_handler import AboutUsHandler
from handlers.payment_handler import PaymentHandler
from handlers.checkout_handler import CheckOutHandler
from handlers.show_review_handler import ChefShowReview
from handlers.send_message_handler import SendMessageHandler
from handlers.inbox_handler import MessageInboxHandler
from handlers.show_message_handler import ShowMessageHandler
from handlers.outbox_handler import MessageSentHandler
from handlers.editpaper_handler import EditPaperHandler
from handlers.search_handle import SearchHandler
from handlers.publicationbyyear_handle import PublicationByYearHandler
from handlers.edit_profile_handle import EditProfileHandler
from handlers.display_profile_handle import DisplayProfileHandler
from handlers.pdf_counter_handler import PDFCounterHandler
from handlers.code_counter_handler import CodeCounterHandler
from handlers.demo_counter_handler import DemoCounterHandler
from handlers.data_counter_handler import DataCounterHandler
from handlers.change_pass_handler import ChangePasswordHandler
from google.appengine.api import search

from utils import *

from time import gmtime, strftime
from datetime import datetime
from collections import namedtuple

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from dbs.databases import *

import logging

inf = 100000

class MainHandler(webapp2.RequestHandler):
    def get(self):
        params_html = {}
        
        temp = self.request.cookies.get('user_id')
        admin_flag = 0
        if temp:
            userid = valid_hash_cookie(temp)
            if userid:
                params_html['userid'] = userid
                user = db.GqlQuery("SELECT * FROM UserPass_User WHERE user_id = '%s'" %userid)
                user = user.get()
                if user:
                    admin_flag = user.isadmin

        params_html['isactive'] = ['active','0']

        search_results = []
        
        
        papers_list = db.GqlQuery("SELECT * FROM Papers_DB ORDER BY created_date DESC")

        front_counter = 0
        
        if papers_list is not None:
            
            success_flag = 0
            for paper in papers_list:

                front_counter = front_counter + 1
                paper_specification = []                    
                paper_specification.append(unescape_html(paper.title))
                paper_specification.append(paper.publication_year)                
                paper_specification.append((paper.key()))
                paper_specification.append(paper.authors_str)
                search_results.append(paper_specification)
            
                if (front_counter>5):
                    break
            
            params_html['papers_list'] = search_results                
                
        params_html['admin_flag'] = admin_flag
        
        self.response.out.write(template.render('./html/front_page.html',params_html))
        
    def post(self):
        params_html = {}
        temp = self.request.cookies.get('user_id')
        
        admin_flag = 0
        if temp:
            userid = valid_hash_cookie(temp)
            if userid:
                params_html['userid'] = userid
                user = db.GqlQuery("SELECT * FROM UserPass_User WHERE user_id = '%s'" %userid)
                user = user.get()
                if user:
                    admin_flag = user.isadmin

        params_html['isactive'] = ['active','0']
        params_html['admin_flag'] = admin_flag

        search_results = []
        
        
        search_query = self.request.get('search_filed')
        success_flag = 1
        
        
        if not search_query:
            success_flag = 0
            params_html['error_search'] = 'The search criteria can not be empty!'
        else:
            params_html['search_filed_value'] = search_query
            
        if not success_flag:
            
            search_results = []
            
            papers_list = db.GqlQuery("SELECT * FROM Papers_DB ORDER BY created_date  ")

            front_counter = 0
        
            if papers_list is not None:
            
                success_flag = 0
                for paper in papers_list:

                    front_counter = front_counter + 1
                    paper_specification = []                    
                    paper_specification.append(unescape_html(paper.title))
                    paper_specification.append(paper.publication_year)                
                    paper_specification.append((paper.key()))
                    paper_specification.append(paper.authors_str)
                    search_results.append(paper_specification)
            
                    if (front_counter>5):
                        break
            
                params_html['papers_list'] = search_results
                            
                self.response.out.write(template.render('./html/front_page.html',params_html))
        else:
            
            self.redirect('/_search?q=%s' %search_query )
        

class MainHandler_JSON(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        posts = db.GqlQuery("SELECT * FROM Blogpost ORDER BY created_date DESC")        
        post_dictionary = []
        for blog_post in posts:
            post_dictionary.append(print_json(self,blog_post))
                    
        self.response.out.write(json.dumps(post_dictionary))
            
        key = 'front'
        front_page = memcache.get(key)
        if front_page is None:
            front_page = db.GqlQuery("SELECT * FROM Blogpost ORDER BY created_date DESC LIMIT 10")
            front_page = list(front_page)
            memcache.set(key,front_page)
            memcache.set('time',time.time())

        for blog_post in front_page:            
            self.response.write('<h1>%s</h1>'%blog_post.title)
            self.response.write('<br>')
            self.response.write(blog_post.content)
            self.response.write('<br>')
            self.response.write('<hr>')
        last_chached = memcache.get('time')
        if last_chached:
            self.response.write('Queried %f seconds ago' %(time.time()-last_chached))


def handle_404(request, response, exception):
    logging.exception(exception)
    response.out.write(template.render('./html/404.html',''))
    response.set_status(404)            

        
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/.json/?', MainHandler_JSON),    
    ('/_admin/?', AdminHandler),
    ('/_image', ImageHandler),
    ('/signup/?', SignUpHandler),    
    ('/_author', AuthorProfileHandler),
    ('/_publicationyear', PublicationByYearHandler),
    ('/newpost/?', NewPostHandler),
    ('/dashboard/?', DashboardHandler),
    ('/login/?', LoginHandler),
    ('/logout/?', LogoutHandler),
    ('/display_map/?', DisplayMapHandler),    
    ('/_paper', DisplayPaperHandler),    
    ('/_paymentstatus', PaymentHandler),
    ('/_checkout', CheckOutHandler),
    ('/message_send', SendMessageHandler),
    ('/message_inbox', MessageInboxHandler),
    ('/message_sent',MessageSentHandler),
    ('/_msg', ShowMessageHandler),
    ('/_review', ReviewHandler),
    ('/_import',ImportHandler),
    ('/_editprofile',EditProfileHandler),
    ('/_showprofile',DisplayProfileHandler),
    ('/_editpaper',EditPaperHandler),
    ('/_changepassword',ChangePasswordHandler),
    ('/how_it_works',HowItWorksHandler),
    ('/_reviews_chef',ChefShowReview),
    ('/_search',SearchHandler),
    ('/about',AboutUsHandler),
    ('/_pdf_counter',PDFCounterHandler),
    ('/_code_counter',CodeCounterHandler),
    ('/_demo_counter',DemoCounterHandler),
    ('/_data_counter',DataCounterHandler),    
    ('/([a-zA-Z0-9]+.json)/?', DisplayPostHandler_JSON)
], debug=True)

app.error_handlers[404] = handle_404