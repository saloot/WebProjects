#=================================FUNCTION DESCRITION================================
# This code is responsible for displaying a particular meal. It reads the meal ID
# from the url, retrieves the meal from the dataset and if found, displays its
# detaiLs.
#====================================================================================


#=================INCLUDING THE NECESSARY LIBRARIES AND OTHER FILES==================
import webapp2
from google.appengine.api import memcache
from google.appengine.ext import db
import time

from dbs.databases import *
from utils import *
from google.appengine.ext.webapp import template
from datetime import date
from datetime import datetime
import logging
import traceback
#====================================================================================

#===================================THE MAIN CODE====================================
class DisplayPaperHandler(webapp2.RequestHandler):

    def get(self):
        params_html = {}
        user_author = ''
        paper_key = self.request.get('i')
        key = 'paper_%s' %paper_key
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
                    user_author = user.author_id
        
        temp_flag = 1
        try:
            paper = db.get(paper_key)
        except:
            logging.error("%s", 'There is no paper with such a key')
            temp_flag = 0
        
        if temp_flag:    
            paper_desc = []                    
            paper_desc.append(unescape_html(paper.title))
            if (paper.publication_date):
                paper_desc.append((paper.publication_date))
            else:
                paper_desc.append(int(paper.publication_year))
            paper_desc.append(paper.publisher)
            paper_desc.append(paper.authors_str)
            paper_desc.append(paper.keywords)
            paper_desc.append(unescape_html(paper.abstract))
            paper_desc.append(paper.pdf_link)
            paper_desc.append(paper.data_link)
            paper_desc.append(paper.code_link)
            paper_desc.append(paper.demo_link)
            paper_desc.append(paper.biblio_str)
            paper_desc.append(paper.web_link)
        
            authors_links = []
            for item in paper.authors:
                authorID = item.replace(" ", "")
                authorID = authorID.replace(",","")
                authors_links.append(authorID)
        
        
        
            params_html['key'] = paper_key
            params_html['admin_flag'] = admin_flag
            params_html['paper'] = paper_desc
            params_html['author_list'] = zip(paper.authors,authors_links)
            params_html['paper_abstract'] = unescape_html(paper.abstract)
            params_html['no_views'] = paper.no_views
            params_html['no_pdf_downloads'] = paper.no_pdf_downloads
            params_html['no_code_downloads'] = paper.no_code_downloads
            params_html['no_demo_downloads'] = paper.no_demo_downloads
            params_html['no_data_downloads'] = paper.no_data_downloads
            
            if paper.demo_link:
                if 'youtube' in paper.demo_link:
                    ind = paper.demo_link.find('watch?v=')            
                    if ind:
                        youtube_key = paper.demo_link[ind+8:len(paper.demo_link)]
                        params_html['youtube_demo'] = youtube_key
            if admin_flag:
                params_html['editpaper_link'] = "/_editpaper?i="+paper_key
            elif user_author in authors_links:
                params_html['editpaper_link'] = "/_editpaper?i="+paper_key
            else:
                params_html['editpaper_link'] = ''
         
        
            
            #----------------Increase the Click Counter in the Database--------------
            #pp = db.GqlQuery("SELECT * FROM Paper_Clicks_DB WHERE paperkey = '%s'" %paper_key)
            #pp = pp.get()
            pp = db.get(paper_key)
            if pp:
                pp.no_views = pp.no_views + 1
                pp.put()
            #------------------------------------------------------------------------
            
            self.response.out.write(template.render('./html/display_paper.html',params_html))
        else:
            self.redirect('/404?u=author')
        #last_chached = memcache.get(key_time)
        #if last_chached:
        #    self.response.write('Queried %f seconds ago' %(time.time()-last_chached))

#===============================THE JASON HANDLER====================================
# The JSON handler is responsible for producing proper JSON values, necessary for RSS
# feeds, APIs and so on.

class DisplayPostHandler_JSON(webapp2.RequestHandler):
    def get(self,paper_key):             
        q = db.GqlQuery("SELECT * FROM FoodList ORDER BY created_date DESC")
        meal = q.get()
        self.response.headers['Content-Type'] = 'application/json'
        
        post_dictionary = print_json(self,meal)
        self.response.out.write(json.dumps(post_dictionary))
#====================================================================================

