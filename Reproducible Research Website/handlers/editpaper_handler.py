import webapp2
from google.appengine.ext.webapp import template
from google.appengine.api import images
from utils import *
from google.appengine.ext import db
#from dbs.databases import FoodList
#from dbs.databases import UserPass_Chef
from dbs.databases import *
from google.appengine.api import memcache
from datetime import datetime
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images
from google.appengine.api import search

class EditPaperHandler(webapp2.RequestHandler):
    
    def get(self):
        
        #---------------------Check if the User is Admin---------------------
        admin_flag = 0
        temp = self.request.cookies.get('user_id')
        if temp:
            userid = valid_hash_cookie(temp)
            user = db.GqlQuery("SELECT * FROM UserPass_User WHERE user_id = '%s'" %userid)
            user = user.get()
            if user:
                admin_flag = user.isadmin
                user_author = user.author_id
        #---------------------------------------------------------------------
        
        #----------------Retrieve the Paper from the Database-----------------
        paper_key = self.request.get('i')
        paper = db.get(paper_key)
        #---------------------------------------------------------------------
        
        #-------------------Assign HTML Template Parameters-------------------        
        paper_type_list = ['Conference','Journal','Thesis','Poster','Patent','Report','Poster','Book','Book Chapter','Presentation']
        publication_status_list = ['Accepted','Submitted','Published']
        
        params_html = {}
        params_html['paper_type_list'] = paper_type_list
        params_html['initial_paper_type'] = paper.publication_type
        params_html['paper_title_val'] = paper.title
        if paper.publication_date:
            params_html['publication_date_val'] = paper.publication_date
        else:
            params_html['publication_date_val'] = str(paper.publication_year) + "-01-01"
        params_html['paper_abstract'] = paper.abstract
        params_html['pdf_link_val'] = paper.pdf_link        
        params_html['web_link_val'] = paper.web_link
        if paper.data_link is not None:
            params_html['data_link_val'] = paper.data_link
        
        if paper.code_link is not None:
            params_html['code_link_val'] = paper.code_link
        
        if paper.demo_link is not None:
            params_html['demo_link_val'] = paper.demo_link
        
        params_html['authors_list_val'] = zip(paper.authors,paper.email_authors)
        params_html['biblio_str'] = paper.biblio_str
        params_html['initial_status'] = paper.publication_status
        params_html['publication_status_list'] = publication_status_list
        params_html['keywords'] = '; '.join(paper.keywords)
        params_html['admin_flag'] = admin_flag
        #---------------------------------------------------------------------
        
        
        paper_authors = []
        for item in paper.authors:
            authorID = item.replace(" ", "")
            authorID = authorID.replace(",","")
            paper_authors.append(authorID)
                
        if user_author in paper_authors:
            params_html['admin_flag'] = 1
        
        self.response.out.write(template.render('./html/edit_paper.html',params_html))
        
    def post(self): 
        params_html = {}  
        paper_type_list = ['Conference','Journal','Thesis','Poster','Patent','Report','Poster','Book','Book Chapter','Presentation']
        publication_status_list = ['Accepted','Submitted','Published']
        
        params_html['paper_type_list'] = paper_type_list
        params_html['publication_status_list'] = publication_status_list
        
        #----------------Retrieve the Paper from the Database-----------------
        paper_key = self.request.get('i')
        paper = db.get(paper_key)
        paper_publisher = paper.publisher
        #---------------------------------------------------------------------
        
        #---------------------Check if the User is Admin---------------------
        admin_flag = 0
        temp = self.request.cookies.get('user_id')
        if temp:
            userid = valid_hash_cookie(temp)
            user = db.GqlQuery("SELECT * FROM UserPass_User WHERE user_id = '%s'" %userid)
            user = user.get()
            admin_flag = user.isadmin
            user_author = user.author_id
        
        params_html['admin_flag'] = admin_flag
        #---------------------------------------------------------------------
        
        #----------------------Get the Details from the Form-------------------
        paper_title = (self.request.get('paper_title'))        
        publication_type = self.request.get('publication_type')
        publication_date = self.request.get('publication_date')
        paper_abstract = (self.request.get('abstract_of_paper'))
        paper_keywords = self.request.get('pub_keywords')
        biblio_str = self.request.get('how_to_cite')
        web_link = self.request.get('web_link')
        pdf_link = self.request.get('pdf_link')        
        code_link = self.request.get('code_link')
        demo_link = self.request.get('demo_link')
        data_link = self.request.get('data_link')
        publication_status = self.request.get('publication_status')
        
        #..........................Retrive the Authors........................
        paper_authors = []
        author_count = 0
        for i in range(1,len(paper.authors)+1):
            field_name = str(i) + "_author"
            temp = self.request.get(field_name)
            paper_authors.append(temp)
            if temp != '':
                author_count = author_count + 1
        #.....................................................................
        
        #.......................Retrive the Author Emails.....................
        author_emails = []
        email_success_flag = 1
        for i in range(1,len(paper.authors)+1):
            field_name = str(i) + "_email"
            temp = self.request.get(field_name)
            if (temp):
                if (valid_email(temp)):
                    author_emails.append(temp)
                else:
                    email_success_flag = 0
                    author_emails.append('')
            else:
                author_emails.append('')    
        #.....................................................................
        
        #---------------------------------------------------------------------
        
        #-----------------------Check for Input Errors------------------------
        success_flag = 1
         
        if not paper_title:
            success_flag = 0
            params_html['error_title'] = 'Paper title is necessary!'
        else:
            params_html['paper_title_val'] = (paper_title)
            
        if author_count == 0:
            success_flag = 0
            params_html['error_author'] = 'At least one author is required!'
            params_html['authors_list_val'] = []
        
        if not email_success_flag:
            success_flag = 0
            params_html['error_email'] = 'The entered email is invalid'
            
        if author_count:
            params_html['authors_list_val'] = zip(paper_authors,author_emails)
        
        if not publication_date:
            success_flag = 0
            params_html['error_date'] = 'Date is ncessary!'
        else:
            params_html['publication_date_val'] = publication_date
            
        if not paper_abstract:
            success_flag = 0
            params_html['error_abstract'] = "Abstract shouldn't be empty!"
        else:
            params_html['paper_abstract'] = (paper_abstract)
        
        if not paper_keywords:
            success_flag = 0
            params_html['error_keywords'] = 'At least one keyword is necessary'
        else:
            params_html['keywords'] = paper_keywords
        
        if not biblio_str:
            success_flag = 0
            params_html['error_cite'] = 'This field is absolutely necessary'
        else:
            params_html['biblio_str'] = biblio_str
        
        if not web_link:
            success_flag = 0
            params_html['error_web_link'] = 'A URL for the full paper is necessary'
        else:
            params_html['web_link_val'] = web_link
        
        if not pdf_link:
            success_flag = 0
            params_html['error_pdf_link'] = 'A URL for the PDF is necessary'
        else:
            params_html['pdf_link_val'] = pdf_link
        
        if not demo_link:
            demo_link = None
            
        
        if not data_link:
            data_link = None
            
        params_html['initial_paper_type'] = publication_type
        params_html['initial_status'] = publication_status
        #---------------------------------------------------------------------
        
        
        
        if not success_flag:
            paper_authors = []
            for item in paper.authors:
                authorID = item.replace(" ", "")
                authorID = authorID.replace(",","")
                paper_authors.append(authorID)
                
            if user_author in paper_authors:
                params_html['admin_flag'] = 1
            self.response.out.write(template.render('./html/edit_paper.html',params_html))
        else:
            temp = self.request.cookies.get('user_id')
            if temp:
                chef_id = valid_hash_cookie(temp)
                if not chef_id:
                    self.redirect('/login')
            else:
                self.redirect('/login')        
            
            #------------------------------Update Paper Details-----------------------------
            paper.title = paper_title
            paper.publication_type = publication_type   
            paper.publication_date = publication_date
            paper.abstract = paper_abstract
            paper.keywords = paper_keywords.split(';')
            paper.biblio_str = biblio_str
            if web_link:
                paper.web_link = web_link
            if pdf_link:
                paper.pdf_link = pdf_link
            
            if code_link:
                paper.code_link = code_link
            else:
                paper.code_link = None
            if demo_link:
                paper.demo_link = demo_link
            else:
                paper.demo_link = None
            if data_link:    
                paper.data_link = data_link
            else:
                paper.data_link = None
                
            paper.publication_status = publication_status
            paper.authors = paper_authors
            paper.authors_str = '; '.join(paper_authors)
            paper.email_authors = author_emails
            paper.put()
            #---------------------------------------------------------------------
            
            #--------------------Index the Paper for Future Search Queries----------------------
            index = search.Index(name='PAPER_INDICES', namespace='PAPER_INDICES_NAMESPACE')
            key_val = paper.key()

            key_val = str(key_val).replace('-','_')
            fields = [search.TextField(name='abstract', value=paper_abstract),
                        search.TextField(name='doc_id', value=key_val),
                        #search.DateField(name='publication_date',value=datetime.datetime.now().date()),
                        search.TextField(name='title', value=paper_title),
                        search.TextField(name='authors', value='; '.join(paper_authors)),
                        search.TextField(name='keywords', value=paper_keywords),      
                        search.AtomField(name='pub_type', value=publication_type),
                        search.TextField(name='publisher', value=paper_publisher),
                        search.AtomField(name='pub_status', value=publication_status),
                        search.NumberField(name='pub_year', value=int(paper.publication_year)),
                        search.TextField(name='dockey', value=str(paper.key()))]
                
            d = search.Document(doc_id=key_val, fields=fields)
            try:
                add_result = search.Index(name='PAPER_INDICES').put(d)
                
            except search.Error:
                self.response.out.write("Sorry we weren't able to add this!")
                #-----------------------------------------------------------------------------------

            
            
            #-----------------Add or Update the Author to the Authors Database------------------
            itr = 0
            author_emails = paper.email_authors
            
            for author in paper.authors:
                authorID = str(author.replace(" ", ""))
                authorID = authorID.replace(",","")
                email = author_emails[itr]
                
                user = db.GqlQuery("SELECT * FROM Authors_DB WHERE author_id = '%s'" %authorID)
                user = user.get()
                
                if user:
                    
                    #............................Update the Author..............................
                    published_papers = user.paper_keys
                    if str(paper.key()) not in str(published_papers):
                        published_papers.append(str(paper.key()))
                        user.paper_keys = published_papers
                        
                        titles = user.paper_titles
                        titles.append(str((paper.title)))
                        user.paper_titles = titles
                        
                        dates = user.paper_dates
                        dates.append(str(paper.publication_year))
                        user.paper_dates = dates
                        
                        
                        authors_str = user.other_authors
                        authors_str.append(paper.authors_str)
                        user.other_authors = authors_str
                    user.email_add = email
                    user.put()
                    #...........................................................................
        
                else:
                    #.....................Add the Author to the Database........................
                    ind = author.find(",")
                    first_name = author[0:ind]
                    last_name = author[ind+2:len(author)]
                    
                    u = Authors_DB(author_id = authorID,firstname = first_name, lastname = last_name,email_add = email,
                                   paper_keys = list([str(paper.key())]),paper_titles = list([str(paper.title)]),
                                   paper_dates = list([str(paper.publication_year)]),other_authors = list([paper.authors_str]))
                    u.put()
                    #...........................................................................

                itr = itr + 1
                #-----------------------------------------------------------------------------------
            
            perma_link=('./_paper?i=%s' %str(paper.key()))
            
            self.redirect('/%s' %perma_link)
