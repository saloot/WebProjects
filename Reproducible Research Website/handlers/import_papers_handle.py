# TO DO: 1) Check if already exists
#        2) Swap the first and the last name of the authors
#        3) Write the piece of code for name conventions and etc.

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
import logging
import traceback

from time import gmtime, strftime
from datetime import datetime
from collections import namedtuple

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from dbs.databases import *
from google.appengine.api import search
from difflib import SequenceMatcher

import xml.etree.ElementTree as ET
inf = 100000


publication_type_match = {}
publication_type_match['CONF'] = 'Conference'
publication_type_match['ARTICLE'] = 'Journal'
publication_type_match['PATENT'] = 'Patent'
publication_type_match['THESIS'] = 'Thesis'
publication_type_match['STUDENT'] = 'Report'
publication_type_match['REPORT'] = 'Report'
publication_type_match['CHAPTER'] = 'Book Chapter'
publication_type_match['POSTER'] = 'Poster'
publication_type_match['TALK'] = 'Presentation'
publication_type_match['BOOK'] = 'Book'
publication_type_match['REVIEW'] = 'Report'
publication_type_match['WORKING'] = 'Draft'

publication_status_match = {}
publication_status_match['SUBMITTED'] = 'Submitted'
publication_status_match['PUBLISHED'] = 'Published'
publication_status_match['ACCEPTED'] = 'Accepted'

class ImportHandler(webapp2.RequestHandler):
    
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
        
        search_results = []
        search_results_sorted_price = []
        query_criteria = ''
        paper_title = self.request.get('q')
        if paper_title:
            query_criteria = "?p=title%3A" + paper_title.replace('_','%20')
        
        paper_authors = self.request.get('a')
        if paper_authors:
            if query_criteria:
                query_criteria = query_criteria + "+and+author%3A" + paper_authors.replace('_','&nbsp')
            else:
                query_criteria = "?p=author%3A" + paper_authors.replace('_','&nbsp')
            
        query_criteria = query_criteria + "&of=xm&rg=200"
        #self.response.out.write(query_criteria)
        url = ("http://infoscience.epfl.ch/search" + query_criteria)
        
        
        confirmRequest = urllib.urlopen(url)
        response_str = confirmRequest.read()
        
        #self.response.out.write(url)
        root = ET.fromstring(response_str)
        papers_list = []
        sucess_flags_list = []
        paper_addition_errors = []
        for record in root:
            
            #--------------------------------Initialize Variables------------------------------
            paper_authors = []
            publishing_labs = []
            pdf_link = ''
            pdf_public = 0
            publication_status = ''
            github_link = ''
            data_link = ''
            publication_type = ''
            publication_venue = ''
            publisher = ''
            publication_pages = ''
            publication_vol = ''
            publication_no = ''
            publication_details = ''
            paper_title = ''
            publication_year = ''
            paper_abstract = ''
            paper_keywords = []
            paper_sucess_flag = 0
            
            #----------------------------------------------------------------------------------
            for child in record:
                att = child.attrib
                
                #--------------------------Get the Authors of the Paper------------------------
                if (att['tag'] == '909'):
                    for codings in child:
                        d = codings.attrib
                        if (d['code'] == 'p'):
                            publishing_labs.append(codings.attrib)
                #------------------------------------------------------------------------------
                
                #---------------------------Get the Publication Title--------------------------
                if (att['tag'] == '245'):
                    for codings in child:
                        d = codings.attrib
                        if (d['code'] == 'a'):
                            paper_title = codings.text
                #------------------------------------------------------------------------------                
                
                #----------------------------Get the Publication Date--------------------------
                if (att['tag'] == '260'):
                    for codings in child:
                        d = codings.attrib
                        if (d['code'] == 'c'):
                            publication_year = codings.text
                #------------------------------------------------------------------------------
                
                #--------------------------Get the Authors of the Paper------------------------
                if (att['tag'] == '700'):
                    for codings in child:
                        d = codings.attrib
                        if (d['code'] == 'a'):
                            if isinstance(codings.text, str):
                                paper_authors.append(unicode(swap_first_last_name(codings.text),'utf-8'))
                            else:
                                paper_authors.append(unicode(swap_first_last_name(codings.text)))
                #------------------------------------------------------------------------------
                
                #--------------Get the Link to the Paper on Infoscience Website----------------                
                if (att['tag'] == '024'):
                    for codings in child:
                        d = codings.attrib
                        if (d['code'] == 'a'):
                            link_val = codings.text
                            temp = re.finditer('oai:infoscience.epfl.ch:(.*)', link_val)                                
                            if temp:
                                for item in temp:
                                    web_link = link_val[item.start():item.end()]
                                    web_link = "http://infoscience.epfl.ch/record/" + web_link[24:len(web_link)]
                #self.response.out.write(web_link)                        
                #------------------------------------------------------------------------------
                
                #-------Get the Link to the PDF File, The Simulation Code and Data Files-------                
                if (att['tag'] == '856'):
                    for codings in child:
                        d = codings.attrib
                        if (d['code'] == 'u'):
                            link_val = codings.text
                            if ('github' in link_val):
                                github_link = link_val
                            elif ('.pdf' in link_val):
                                pdf_link = link_val
                                
                                if (d['code'] == 'x'):
                                    if (codings.text == 'PUBLIC'):
                                        pdf_public = 1                            
                            elif ('.zip' in link_val):
                                data_link = link_val
                        
                        #........For Final Version of the Website and Naming Conventions........
                        # if (d['code'] == 'z'):
                        #     val = codings.text
                        #     if (val == '')
                        #.......................................................................    
                #------------------------------------------------------------------------------
                
                #---------------------------Get the Publication Status-------------------------
                if (att['tag'] == '973'):
                    for codings in child:
                        d = codings.attrib
                        if (d['code'] == 's'):
                            publication_status = codings.text
                        
                        if (d['code'] == 'x'):
                            if (codings.text == 'PUBLIC'):
                                pdf_public = 1                            
                #------------------------------------------------------------------------------
                
                #---------------------------Get the Publication Type---------------------------
                if (att['tag'] == '980'):
                    for codings in child:
                        d = codings.attrib
                        if (d['code'] == 'a'):
                            publication_type = codings.text
                #------------------------------------------------------------------------------                
                            
                #----------------------Get the Publication Venue Details-----------------------
                if (publication_type == 'CONF'):
                    if (att['tag'] == '711'):
                        for codings in child:
                            d = codings.attrib
                            if (d['code'] == 'a'):
                                publication_venue = codings.text
                            if (d['code'] == 'c'):
                                publication_venue = publication_venue + '; ' + codings.text
                            if (d['code'] == 'd'):
                                publication_venue = publication_venue + '; ' + codings.text
                #------------------------------------------------------------------------------                
                
                #---------------------------Get Publisher's Details----------------------------                
                if (att['tag'] == '773'):
                    for codings in child:
                        d = codings.attrib
                        if (d['code'] == 'c'):
                            publication_pages = codings.text
                        if (d['code'] == 'n'):
                            publication_no = codings.text
                        if (d['code'] == 'v'):
                            publication_vol = codings.text
                        if (d['code'] == 'p'):
                            publisher = codings.text
                #------------------------------------------------------------------------------
            
                #----------------------------Get the Paper's Abstract--------------------------
                if (att['tag'] == '520'):
                    for codings in child:
                        d = codings.attrib
                        if (d['code'] == 'a'):
                            paper_abstract = codings.text
                #------------------------------------------------------------------------------
                
                #----------------------------Get the Paper's Keywords--------------------------
                if (att['tag'] == '653'):
                    for codings in child:
                        d = codings.attrib
                        if (d['code'] == 'a'):
                            paper_keywords.append(codings.text)
                #------------------------------------------------------------------------------
                
            
            #------------------------------Some Post Processing--------------------------------
            if publication_vol:
                publication_details = 'Vol. ' + publication_vol + ', '
            if publication_no:
                publication_details = publication_details + 'No. ' + publication_no + ', '
            if publication_pages:
                publication_details = publication_details + 'pp. ' + publication_pages + ', '
            
            publication_details = publication_details[0:len(publication_details)-2]
            
            paper_authors_str = '; '.join(paper_authors)
            paper_keywords_str = ', '.join(paper_keywords)
            #----------------------------------------------------------------------------------
            
            
            papers_list.append(list([paper_title,paper_authors_str,paper_abstract,web_link,publication_year,publisher,paper_keywords_str,data_link,github_link,publication_details]))
            sucess_flags_list.append(paper_sucess_flag)
            paper_addition_errors.append('')
        #----------------------------Feed the List to the HTML Template------------------------
        params_html['paper_list'] = zip(papers_list,sucess_flags_list,paper_addition_errors)
        
        self.response.out.write(template.render('./html/display_newpapers.html',params_html))
        #--------------------------------------------------------------------------------------
        
        
    def post(self):
        
        checkbox_vals = self.request.get_all("selected_papers")
        
        itr = 0 
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
                    adding_user = user
                    
        params_html['admin_flag'] = admin_flag
        #----------------------------------------------------------------------------

        search_results = []
        search_results_sorted_price = []
        match_author_id = 0
        query_criteria = ''
        paper_title = self.request.get('q')
        if paper_title:
            query_criteria = "?p=title%3A" + paper_title.replace('_','%20')
        
        paper_authors = self.request.get('a')
        if paper_authors:
            match_author_id = 1            
            if query_criteria:
                query_criteria = query_criteria + "+and+author%3A" + paper_authors.replace('_','&nbsp')
            else:
                query_criteria = "?p=author%3A" + paper_authors.replace('_','&nbsp')
            
        query_criteria = query_criteria + "&of=xm&rg=200"
        
        url = "http://infoscience.epfl.ch/search" + query_criteria    
        confirmRequest = urllib.urlopen(url)
        response_str = confirmRequest.read()
        
        
        root = ET.fromstring(response_str)
        papers_list = []
        #self.response.out.write(response_str)
        for record in root:
            
            #--------------------------------Initialize Variables------------------------------
            paper_authors = []
            publishing_labs = []
            pdf_link = ''
            web_link = ''
            data_link = ''
            code_link = ''
            demo_link = ''
            pdf_public = 0
            publication_status = ''
            github_link = ''
            
            publication_type = ''
            publication_venue = ''
            publisher = ''
            publication_pages = ''
            publication_vol = ''
            publication_no = ''
            publication_details = ''
            paper_title = ''
            publication_year = ''
            paper_abstract = ''
            paper_keywords = []
            authors_emails = []
            #----------------------------------------------------------------------------------
            for child in record:
                att = child.attrib
                
                #--------------------------Get the Authors of the Paper------------------------
                if (att['tag'] == '909'):
                    for codings in child:
                        d = codings.attrib
                        if (d['code'] == 'p'):
                            publishing_labs.append(codings.attrib)
                #------------------------------------------------------------------------------
                
                #---------------------------Get the Publication Title--------------------------
                if (att['tag'] == '245'):
                    for codings in child:
                        d = codings.attrib
                        if (d['code'] == 'a'):
                            if isinstance(codings.text, str):
                                paper_title = unicode(codings.text,'utf-8')
                            else:
                                paper_title = unicode(codings.text)
                #------------------------------------------------------------------------------                
                
                #----------------------------Get the Publication Date--------------------------
                if (att['tag'] == '260'):
                    for codings in child:
                        d = codings.attrib
                        if (d['code'] == 'c'):
                            publication_year = codings.text
                #------------------------------------------------------------------------------
                
                #--------------------------Get the Authors of the Paper------------------------
                if (att['tag'] == '700'):
                    for codings in child:
                        d = codings.attrib
                        if (d['code'] == 'a'):
                            if isinstance(codings.text, str):
                                paper_authors.append(unicode(swap_first_last_name(codings.text),'utf-8'))
                            else:
                                paper_authors.append(unicode(swap_first_last_name(codings.text)))
                            authors_emails.append('')
                #------------------------------------------------------------------------------
                #--------------Get the Link to the Paper on Infoscience Website----------------                
                if (att['tag'] == '024'):
                    for codings in child:
                        d = codings.attrib
                        if (d['code'] == 'a'):
                            link_val = codings.text
                            temp = re.finditer('oai:infoscience.epfl.ch:(.*)', link_val)                                
                            if temp:
                                for item in temp:
                                    web_link = link_val[item.start():item.end()]
                                    web_link = "http://infoscience.epfl.ch/record/" + web_link[24:len(web_link)]
                #self.response.out.write(web_link)                        
                #------------------------------------------------------------------------------
                
                #-------Get the Link to the PDF File, The Simulation Code and Data Files-------
                if (att['tag'] == '856'):
                    for codings in child:
                        d = codings.attrib
                        if (d['code'] == 'u'):
                            link_val = codings.text
                            if ('github' in link_val):
                                github_link = link_val
                            elif ('.pdf' in link_val):
                                pdf_link = link_val
                                
                                if (d['code'] == 'x'):
                                    if (codings.text == 'PUBLIC'):
                                        pdf_public = 1                            
                            elif ('.zip' in link_val):
                                data_link = link_val
                        
                        #........For Final Version of the Website and Naming Conventions........
                        # if (d['code'] == 'z'):
                        #     val = codings.text
                        #     if (val == '')
                        #.......................................................................    
                #------------------------------------------------------------------------------
                
                #---------------------------Get the Publication Status-------------------------
                if (att['tag'] == '973'):
                    for codings in child:
                        d = codings.attrib
                        if (d['code'] == 's'):                             
                            ky = codings.text
                            publication_status = publication_status_match[ky]
                        
                        if (d['code'] == 'x'):
                            if (codings.text == 'PUBLIC'):
                                pdf_public = 1                            
                #------------------------------------------------------------------------------
                
                #---------------------------Get the Publication Type---------------------------
                if (att['tag'] == '980'):
                    for codings in child:
                        d = codings.attrib
                        if (d['code'] == 'a'):
                            ky = codings.text
                            publication_type = publication_type_match[ky]
                #------------------------------------------------------------------------------                
                            
                #----------------------Get the Publication Venue Details-----------------------
                if (publication_type == 'CONF'):
                    if (att['tag'] == '711'):
                        for codings in child:
                            d = codings.attrib
                            if (d['code'] == 'a'):
                                publication_venue = codings.text
                            if (d['code'] == 'c'):
                                publication_venue = publication_venue + '; ' + codings.text
                            if (d['code'] == 'd'):
                                publication_venue = publication_venue + '; ' + codings.text
                #------------------------------------------------------------------------------                
                
                #---------------------------Get Publisher's Details----------------------------                
                if (att['tag'] == '773'):
                    for codings in child:
                        d = codings.attrib
                        if (d['code'] == 'c'):
                            publication_pages = codings.text
                        if (d['code'] == 'n'):
                            publication_no = codings.text
                        if (d['code'] == 'v'):
                            publication_vol = codings.text
                        if (d['code'] == 'p'):
                            publisher = codings.text
                #------------------------------------------------------------------------------
            
                #----------------------------Get the Paper's Abstract--------------------------
                if (att['tag'] == '520'):
                    for codings in child:
                        d = codings.attrib
                        if (d['code'] == 'a'):
                            paper_abstract = codings.text
                #------------------------------------------------------------------------------
                
                #----------------------------Get the Paper's Keywords--------------------------
                if (att['tag'] == '653'):
                    for codings in child:
                        d = codings.attrib
                        if (d['code'] == 'a'):
                            if isinstance(codings.text, str):
                                paper_keywords.append(unicode(codings.text,'utf-8'))
                            else:
                                paper_keywords.append(unicode(codings.text))
                                
                            
                #------------------------------------------------------------------------------
                
            
            #------------------------------Some Post Processing--------------------------------
            paper_authors_str = '; '.join(paper_authors)
            paper_keywords_str = ', '.join(paper_keywords)
            
            
            publication_details = paper_authors_str.replace(',','') + ', "' +paper_title + '", '
            if publisher:
                publication_details = publication_details + publisher + ', '
            
            if publication_vol:
                publication_details = publication_details + 'Vol. ' + publication_vol + ', '
            if publication_no:
                publication_details = publication_details + 'No. ' + publication_no + ', '
            if publication_pages:
                publication_details = publication_details + 'pp. ' + publication_pages + ', '
            
            publication_details = publication_details[0:len(publication_details)-2]
            
            
            #----------------------------------------------------------------------------------
            
            itr = itr + 1
            if (str(itr) in (checkbox_vals)):
                papers_list.append(list([paper_title,paper_authors_str,paper_abstract,pdf_link,publication_year,
                                         publisher,paper_keywords,paper_authors,data_link,github_link,
                                         publication_details,publication_status,publication_type,
                                         publication_details,demo_link,web_link,authors_emails]))
            
                #papers_list.append(list([paper_title,paper_authors_str,paper_abstract,web_link,publication_year,publisher,paper_keywords_str,data_link,github_link,publication_details]))
        
        #------------------------Add the Selected Papers to the Database------------------------
        params_html['paper_list'] = papers_list
        paper_added_flag = 0
        sucess_flags_list = []
        paper_addition_errors = []
        for paper in papers_list:
                    
            #--------------------Check if the paper does not already exists---------------------
            paper_sucess_flag = ''
            addition_error = ''
            already_exists = 0
            query = db.GqlQuery("SELECT * FROM Papers_DB WHERE title = '%s'" %paper[0])
            query = query.get()
            if query:
                already_exists = 1
                paper_key = query.key()
            #-----------------------------------------------------------------------------------                        
            temp_flag = 1
            if not already_exists:
                try:
                    p = Papers_DB(title = paper[0],publication_year = int(paper[4]), publisher = paper[5],keywords = paper[6],
                             authors = paper[7],abstract = paper[2],authors_str = paper[1],
                             publication_status=paper[11],publication_type = paper[12],biblio_str = paper[13],
                             email_authors = paper[16])                    
                except:
                    #self.response.out.write('salam')
                    temp_flag = 0
                    stacktrace = traceback.format_exc()
                    logging.error("%s", stacktrace)
                    addition_error = str(stacktrace)
                    temp = re.finditer('BadValueError: Property (.*) is required', str(stacktrace))
                    paper_sucess_flag = ''
                    if temp:
                        for item in temp:
                            addition_error = addition_error[item.start():item.end()]
                            addition_error = addition_error[23:len(addition_error)]
            else:
                p = query
                if paper[0]:
                    p.title = paper[0]
                else:
                    temp_flag = 0
                    
                p.publication_year = int(paper[4])
                p.publisher = paper[5]
                p.keywords = paper[6]
                if paper[7]:
                    p.authors = paper[7]
                else:
                    temp_flag = 0
                
                p.abstract = paper[2]
                p.authors_str = paper[1]
                p.publication_status=paper[11]
                p.publication_type = paper[12]
                p.biblio_str = paper[13]
                p.abstractemail_authors = paper[16]
            
            if temp_flag:
                if (paper[14]):
                    p.demo_link = paper[13]
                if (paper[3]):
                    p.pdf_link = paper[3]
                if (paper[9]):
                    p.code_link = paper[9]
                if (paper[8]):
                    p.data_link = paper[8]
                if (paper[15]):
                    p.web_link = paper[15]
                
            temp_flag = 1
            if 'p' in locals():
                try:
                    p.put()                        
                except:
                    temp_flag = 0
                    #logging.error('Error adding the paper')
                    stacktrace = traceback.format_exc()
                        
                    logging.error("%s", stacktrace)
                    addition_error = str(stacktrace)
                    paper_sucess_flag = ''
                        
                    temp = re.finditer('BadValueError: Property(.*)is required', str(stacktrace))
                    if temp:
                        for item in temp:
                            addition_error = addition_error[item.start():item.end()]
                            addition_error = addition_error[23:len(addition_error)]
                                    
        
                if temp_flag:
                    paper_sucess_flag = p.key()
                    
            #--------------------Index the Paper for Future Search Queries----------------------
            if paper_sucess_flag:
                index = search.Index(name='PAPERS_INDEXES', namespace='PAPER_INDICES_NAMESPACE')
                key_val = p.key()

                key_val = str(key_val).replace('-','_')
                fields = [search.TextField(name='abstract', value=paper[2]),
                            search.TextField(name='doc_id', value=key_val),
                            #search.DateField(name='publication_date',value=datetime.datetime.now().date()),
                            search.TextField(name='title', value=paper[0]),
                            search.TextField(name='authors', value=paper[1]),
                            search.TextField(name='keywords', value=paper_keywords_str),      
                            search.AtomField(name='pub_type', value=paper[11]),
                            search.TextField(name='publisher', value=paper[5]),
                            search.AtomField(name='pub_status', value=paper[10]),
                            search.NumberField(name='pub_year', value=int(paper[4])),
                            search.TextField(name='dockey', value=str(p.key()))]
                
                d = search.Document(doc_id=key_val, fields=fields)
                try:
                    add_result = search.Index(name='PAPERS_INDEXES').put(d)
                    #self.response.out.write('salam')
                except search.Error:
                    self.response.out.write("Sorry we weren't able to add this!")
            #-----------------------------------------------------------------------------------
                
            #-------------------Check if the USerID Matches any of the Authors------------------
            if match_author_id:
                if adding_user:
                    authors_links = []
                    for item in p.authors:
                        authorID = item.replace(" ", "")
                        authorID = authorID.replace(",","")
                        authors_links.append(authorID)
                    
                    if adding_user.author_id not in authors_links:
                        max_sim = 0
                        itr = 0
                        
                        for item in authors_links:
                            if (SequenceMatcher(None, adding_user.author_id.lower(), item.lower()).ratio()>max_sim):
                                ind = itr
                                max_sim = SequenceMatcher(None, adding_user.author_id.lower(), item.lower()).ratio()
                                #self.response.out.write(str(max_sim))
                            itr = itr + 1
                        if max_sim > 0.85:
                            adding_user.author_id = authors_links[ind]
                            adding_user.put()
                            
                            
            #-----------------------------------------------------------------------------------
            #-----------------Add or Update the Author to the Authors Database------------------
            if paper_sucess_flag:
                authors_list = paper[7]
                for author in authors_list:
                    authorID = author.replace(" ", "")
                    authorID = authorID.replace(",","")
                    user = db.GqlQuery("SELECT * FROM Authors_DB WHERE author_id = '%s'" %authorID)
                    user = user.get()
                    if user:
                        #............................Update the Author..............................
                        keys = user.paper_keys
                        if (str(p.key()) not in keys):
                            keys.append(str(p.key()))
                            user.paper_keys = keys
                            
                            titles = user.paper_titles
                            titles.append(p.title)
                            user.paper_titles = titles
                            
                            dates = user.paper_dates
                            dates.append(str(p.publication_year))
                            user.paper_dates = dates
                            
                            authors_str = user.other_authors
                            authors_str.append(p.authors_str)
                            user.other_authors = authors_str
                        
                            user.put()
                            #...........................................................................
                    else:
                        #.....................Add the Author to the Database........................
                        ind = author.find(",")
                        first_name = author[0:ind]
                        last_name = author[ind+2:len(author)]
                        u = Authors_DB(author_id = authorID,firstname = first_name, lastname = last_name,email_add = '',
                                       paper_keys = list([str(p.key())]),paper_titles = list([p.title]),
                                       paper_dates = list([str(p.publication_year)]),other_authors = list([p.authors_str]))
                        u.put()
                        #...........................................................................

                #-----------------------------------------------------------------------------------
                    
            paper_added_flag = 1
            
            sucess_flags_list.append(paper_sucess_flag)
            paper_addition_errors.append(addition_error)
                
        params_html['added_flag'] = paper_added_flag
        params_html['added_paper_flag'] = sucess_flags_list
        params_html['paper_list'] = zip(papers_list,sucess_flags_list,paper_addition_errors)
        
        self.response.out.write(template.render('./html/display_newpapers.html',params_html))
        #--------------------------------------------------------------------------------------
    
            