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
import xml.etree.ElementTree as ET
inf = 100000

class ImportHandler(webapp2.RequestHandler):
    
    def get(self):
        
        params_front = {}        
        search_results = []
        search_results_sorted_price = []
        
        paper_title = unescape_html2(self.request.get('q'))
        query_criteria = "?p=title%3A" + escape_html(paper_title)
        query_criteria = query_criteria + "&of=xm&rg=200"
        
        url = "http://infoscience.epfl.ch/search" + query_criteria    
        confirmRequest = urllib.urlopen(url)
        response_str = confirmRequest.read()
        if (response_str):
                
            #------------------------------------Fetch Papers----------------------------------
                
            found_papers = re.finditer('<dc:format>(.*)</dc:format>', response_str)
                
            if found_papers:
                paper_indices_end = []
                for item in found_papers:
                    paper_indices_end.append(item.end())
                    
                paper_indices_start = []
                temp = re.finditer('<oai_dc:dc(.*)dc.xsd', response_str)
                for item in temp:
                    paper_indices_start.append(item.start())
                    
                if (len(paper_indices_start) != len(paper_indices_end)):
                    self.response.out.write('Error! The two lengths should be equal')
                else:
                    papers_list = []
                    for l in range(0,len(paper_indices_start)):
                        paper_raw = response_str[paper_indices_start[l]:paper_indices_end[l]]
                        
                        paper_title = re.finditer('<dc:title>(.*)</dc:title>', paper_raw)
                        if paper_title:
                            for item in paper_title:
                                title = paper_raw[item.start():item.end()]
                                title = title[10:len(title)-11]
                                #self.response.out.write(title)
                            
                            
                        paper_abstract = re.finditer('<dc:description>(.*)</dc:description>', paper_raw)
                        if paper_abstract:
                            for item in paper_abstract:
                                abstract = paper_raw[item.start():item.end()]
                                abstract = abstract[16:len(abstract)-17]
                                #self.response.out.write(abstract)
                            
                        paper_authors = re.finditer('<dc:creator>(.*)</dc:creator>', paper_raw)
                        if paper_authors:
                            authors = ''
                            for item in paper_authors:
                                temp = paper_raw[item.start():item.end()]
                                temp = temp[12:len(temp)-13]
                                authors = authors + temp + ' & '
                                
                            authors = authors[0:len(authors)-3]
                            #self.response.out.write(authors)
                            
                        paper_link = re.finditer('<dc:identifier>(.*)</dc:identifier>', paper_raw)
                        if paper_link:
                            for item in paper_link:
                                link = paper_raw[item.start():item.end()]
                                link = link[15:len(link)-16]
                                #self.response.out.write(link)
                                    
                        paper_date = re.finditer('<dc:date>(.*)</dc:date>', paper_raw)
                        if paper_date:
                            for item in paper_date:
                                date_p = paper_raw[item.start():item.end()]
                                date_p = date_p[9:len(date_p)-10]
                                #self.response.out.write(date_p)
                            
                        paper_publisher = re.finditer('<dc:publisher>(.*)</dc:publisher>', paper_raw)
                        publisher = 'none'
                        if paper_publisher:
                            for item in paper_publisher:
                                publisher = paper_raw[item.start():item.end()]
                                publisher = publisher[15:len(publisher)-16]
                                #self.response.out.write(publisher)
                        else:
                            publisher = ''
                            
                        paper_keywords = re.finditer('<dc:subject>(.*)</dc:subject>', paper_raw)
                        if paper_keywords:
                            keywords = ''
                            for item in paper_keywords:
                                temp = paper_raw[item.start():item.end()]
                                temp = temp[12:len(temp)-13]
                                keywords = keywords + temp + ';'
                                
                            authors = authors[0:len(keywords)-1]
                            #self.response.out.write(keywords)
                        
                        
                        papers_list.append(list([title,authors,abstract,link,date_p,publisher,keywords]))
                
                params_front['paper_list'] = papers_list                     
                self.response.out.write(template.render('./html/display_newpapers.html',params_front))
            else:
                self.response.out.write('Sorry your search did not lead to any results :(')
                #----------------------------------------------------------------------------------
                
    def post(self):
        
        checkbox_vals = self.request.get_all("selected_papers")
        
        itr = 0 
        params_front = {}        
        search_results = []
        search_results_sorted_price = []
        
        paper_title = unescape_html2(self.request.get('q'))
        query_criteria = "?p=title%3A" + escape_html(paper_title)
        query_criteria = query_criteria + "&of=xd"
        
        url = "http://infoscience.epfl.ch/search" + query_criteria    
        confirmRequest = urllib.urlopen(url)
        response_str = confirmRequest.read()
        
        if (response_str):
                
            #------------------------------------Fetch Papers----------------------------------
                
            found_papers = re.finditer('<dc:format>(.*)</dc:format>', response_str)
                
            if found_papers:
                paper_indices_end = []
                for item in found_papers:
                    paper_indices_end.append(item.end())
                    
                paper_indices_start = []
                temp = re.finditer('<oai_dc:dc(.*)dc.xsd', response_str)
                for item in temp:
                    paper_indices_start.append(item.start())
                    
                if (len(paper_indices_start) != len(paper_indices_end)):
                    self.response.out.write('Error! The two lengths should be equal')
                else:
                    papers_list = []
                    for l in range(0,len(paper_indices_start)):
                        paper_raw = response_str[paper_indices_start[l]:paper_indices_end[l]]
                        
                        paper_title = re.finditer('<dc:title>(.*)</dc:title>', paper_raw)
                        if paper_title:
                            for item in paper_title:
                                title = paper_raw[item.start():item.end()]
                                title = title[10:len(title)-11]
                                #self.response.out.write(title)
                            
                            
                        paper_abstract = re.finditer('<dc:description>(.*)</dc:description>', paper_raw)
                        if paper_abstract:
                            for item in paper_abstract:
                                abstract = paper_raw[item.start():item.end()]
                                abstract = abstract[16:len(abstract)-17]
                                #self.response.out.write(abstract)
                            
                        paper_authors = re.finditer('<dc:creator>(.*)</dc:creator>', paper_raw)
                        authors_list = []
                        if paper_authors:
                            authors = ''
                            for item in paper_authors:
                                temp = paper_raw[item.start():item.end()]
                                temp = temp[12:len(temp)-13]
                                authors = authors + temp + ' & '
                                authors_list.append(temp)
                                
                            authors = authors[0:len(authors)-3]
                            #self.response.out.write(authors)
                            
                        paper_link = re.finditer('<dc:identifier>(.*)</dc:identifier>', paper_raw)
                        if paper_link:
                            for item in paper_link:
                                link = paper_raw[item.start():item.end()]
                                link = link[15:len(link)-16]
                                #self.response.out.write(link)
                                    
                        paper_date = re.finditer('<dc:date>(.*)</dc:date>', paper_raw)
                        if paper_date:
                            for item in paper_date:
                                date_p = paper_raw[item.start():item.end()]
                                date_p = date_p[9:len(date_p)-10]
                                #self.response.out.write(date_p)
                            
                        paper_publisher = re.finditer('<dc:publisher>(.*)</dc:publisher>', paper_raw)
                        publisher = 'none'
                        if paper_publisher:
                            for item in paper_publisher:
                                publisher = paper_raw[item.start():item.end()]
                                publisher = publisher[14:len(publisher)-15]
                                #self.response.out.write(publisher)
                        
                        
                        paper_keywords = re.finditer('<dc:subject>(.*)</dc:subject>', paper_raw)
                        if paper_keywords:
                            keywords = ''
                            for item in paper_keywords:
                                temp = paper_raw[item.start():item.end()]
                                temp = temp[12:len(temp)-13]
                                keywords = keywords + temp + ';'
                                
                            authors = authors[0:len(keywords)-1]
                            #self.response.out.write(keywords)
                        
                        itr = itr + 1
                        if (str(itr) in (checkbox_vals)):
                            papers_list.append(list([title,authors,abstract,link,date_p,publisher,keywords,authors_list,link]))
                            self.response.out.write(itr)
                        
                
                params_front['paper_list'] = papers_list
                paper_added_flag = 0
                
                for paper in papers_list:
                    
                    #---------------Check if the paper does not already exists----------------
                    already_exists = 0
                    #-------------------------------------------------------------------------
                    if not already_exists:
                        p = Papers_DB(title = paper[0],publication_date = int(paper[4]), publication_venue = paper[5],keywords = paper[6],
                             authors = paper[7],abstract = paper[2],authors_str = paper[1],web_link = link)
                        p.put()
                    
                        paper_added_flag = 1
                        perma_link=('./_paper?i=%s' %str(p.key()))

                    else:
                        self.response.out.write('Sorry the paper already exists in the database. Replace?')

                if paper_added_flag:
                    self.redirect('/%s' %perma_link)
                else:
                    self.response.out.write(template.render('./html/display_newpapers.html',params_front))
                