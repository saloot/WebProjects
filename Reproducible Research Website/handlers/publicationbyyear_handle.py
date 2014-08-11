#=================================FUNCTION DESCRITION================================
# This code is responsible for displaying the chefs' profiles, namely, all the food
# they offer, their favourite recipes, their rating, etc.
#====================================================================================


#=================INCLUDING THE NECESSARY LIBRARIES AND OTHER FILES==================
import webapp2
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from dbs.databases import *
import collections
from utils import *
import time
#====================================================================================


#===================================THE MAIN CODE====================================
class PublicationByYearHandler(webapp2.RequestHandler):
    
    #---------------------Display the HTML Template Upon Loading---------------------    
    def get(self):
        
        params_html = {}                         # The list of parametersthat will be passed to the html template
        
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
        #----------------------------------------------------------------------------
        
        #-------------------Retrieve the Papers from the Database--------------------
        papers = db.GqlQuery("SELECT * FROM Papers_DB ORDER BY publication_year DESC")
        year_index = []
        papers_list = {}
        for paper in papers:
            paper_desc = []
            paper_desc.append(paper.title)
            #paper_desc.append(paper.publication_date)
            paper_desc.append(paper.publication_year)
            paper_desc.append(str(paper.key()))
            paper_desc.append(paper.authors_str)
            
            pub_year = paper.publication_year
            if str(pub_year) in year_index:                
                papers_list[(pub_year)].append(paper_desc)
            else:
                papers_list[(pub_year)] = list([paper_desc])

                year_index.append(str(pub_year))
        #----------------------------------------------------------------------------
        

        #--------------------------Assign HTML Parameters----------------------------
        #papers_list = sorted(papers_list.items(), key=lambda s: s[0])
        papers_list = collections.OrderedDict(sorted(papers_list.items(),reverse=True))
        params_html['year_index'] = year_index
        params_html['papers_list'] = papers_list
        params_html['admin_flag'] = admin_flag
        #----------------------------------------------------------------------------
            
        
        #------------------------Display the Final HTML File-------------------------
        self.response.out.write(template.render('./html/display_papers_by_year.html',params_html))
        #----------------------------------------------------------------------------
            
        #----------------------------------------------------------------------------        
            
        
    #--------------------------------------------------------------------------------

#====================================================================================