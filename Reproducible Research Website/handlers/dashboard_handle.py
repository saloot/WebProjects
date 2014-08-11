import webapp2

from utils import valid_hash_cookie
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from utils import *
from time import gmtime, strftime
from datetime import datetime

class DashboardHandler(webapp2.RequestHandler):
    def get(self):
        params_html = {}
        sort_param = self.request.get('v')
        temp = self.request.cookies.get('user_id')
        admin_flag = 0
        author_flag = 0
        if temp:
            userid = valid_hash_cookie(temp)
            if userid:
                params_html['userid'] = userid
                d = db.GqlQuery("SELECT * FROM UserPass_User WHERE user_id = '%s' " % userid)
                l = d.get()
                if l:
                    admin_flag = l.isadmin
                    author_flag = l.author_id
                else:
                    self.redirect('/login')
                    
                #----------------------------------------------------------------------------
        
                #-------------------------Add the Recently Added Papers----------------------
                papers_list = db.GqlQuery("SELECT * FROM Papers_DB ORDER BY created_date DESC")
                front_counter = 0
                search_results_recent_papers = []
                if papers_list is not None:
            
                    success_flag = 0
                    for paper in papers_list:

                        front_counter = front_counter + 1
                        paper_specification = []                    
                        paper_specification.append(unescape_html(paper.title))
                        paper_specification.append(paper.publication_year)                
                        paper_specification.append((paper.key()))
                        paper_specification.append(paper.authors_str)
                        search_results_recent_papers.append(paper_specification)
            
                        if (front_counter>4):
                            break
                #----------------------------------------------------------------------------
                
                #-----------------Add the Recently Added Papers by the Author----------------
                recently_authored_papers = []
                popular_papers_no_view = []
                
                if author_flag:                    
                    author_papers = db.GqlQuery("SELECT * FROM Authors_DB WHERE author_id = '%s' " %author_flag)
                    author_papers = author_papers.get()
                    papers_list = author_papers.paper_keys
                    #papers_list = papers_list[max(0,len(papers_list)-5):len(papers_list)]
                    recently_authored_papers = []
                    if papers_list is not None:
            
                        front_counter = 0 
                        for paper_key in papers_list[::-1]:                            
                            paper = db.get(paper_key)
                            if paper:
                                paper_specification = []                    
                                paper_specification.append(unescape_html(paper.title))
                                paper_specification.append(paper.publication_year)                
                                paper_specification.append((paper.key()))
                                paper_specification.append(paper.authors_str)
                                if (sort_param == 'code'):
                                    paper_specification.append(paper.no_code_downloads)
                                elif (sort_param == 'data'):
                                    paper_specification.append(paper.no_data_downloads)
                                elif (sort_param == 'pdf'):
                                    paper_specification.append(paper.no_pdf_downloads)
                                elif (sort_param == 'demo'):
                                    paper_specification.append(paper.no_demo_downloads)
                                else:
                                    paper_specification.append(paper.no_views)
                                
                                paper_specification.append(paper.no_views)
                                paper_specification.append(paper.no_pdf_downloads)
                                paper_specification.append(paper.no_code_downloads)
                                paper_specification.append(paper.no_data_downloads)
                                paper_specification.append(paper.no_demo_downloads)
                                recently_authored_papers.append(paper_specification)
                                front_counter = front_counter + 1
                            #if (front_counter>4):
                            #    break
                    
                    popular_papers_no_view = sorted(recently_authored_papers,key=lambda student: student[4],reverse=True)                    
                    recently_authored_papers = recently_authored_papers[0:min(5,len(popular_papers_no_view))]
                    popular_papers_no_view = popular_papers_no_view[0:min(5,len(popular_papers_no_view))]
                #----------------------------------------------------------------------------
                
                #----------------------Assign HTML Template Parameters-----------------------
                if (sort_param == 'code'):
                    params_html['no_code_flag'] = 1
                elif (sort_param == 'data'):
                    params_html['no_data_flag'] = 1
                elif (sort_param == 'pdf'):
                    params_html['no_pdf_flag'] = 1
                elif (sort_param == 'demo'):
                    params_html['no_demo_flag'] = 1
                else:
                    params_html['no_views_flag'] = 1
                params_html['admin_flag'] = admin_flag                
                params_html['recently_added_papers'] = search_results_recent_papers                
                params_html['is_author'] = author_flag
                params_html['recently_authored_papers'] = recently_authored_papers
                params_html['popular_papers_no_view'] = popular_papers_no_view
                self.response.out.write(template.render('./html/user_dashboard.html',params_html))
                
            else:
                self.response.out.write('Cheater!')
        else:
            self.redirect('/login')
