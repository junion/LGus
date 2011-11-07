import os.path,string
import pickle
import cherrypy
import simplejson
from cherrypy.lib.cptools import accept
import cherrypy.lib.auth_basic
import cherrypy.lib.sessions
import LetsgoSimulator as ls

def load_user(login): 
    user_passwds = pickle.load(open('web/users/passwd','rb'))
    if login in user_passwds:
        return (login,user_passwds[login])

def check_passwd(login,password): 
    valid_user = load_user(login) 
    print valid_user
    if valid_user == None: 
        return u'Wrong login or no login was entered' 
    if valid_user[1] != password: 
        return u"<br />Wrong password"
    return False 

def login_screen(from_page='..', username='', error_msg=''): 
    login_page = open('web/login.html','r').read()
    login_page = string.replace(login_page,'{$error_msg}',error_msg)
    login_page = string.replace(login_page,'{$username}',username)
    return login_page

        
class LetsgoWebApp:
    def __init__(self):
        self.register_page = open('web/register.html','r').read()
        self.template = open('web/index.html','r').read() 
#        self.simulator = ls.UserSimulator()
#        self.simulator.dialog_init()
#        self.history = ''
#        self.params = {'{$bus}':self.simulator.goal['G_bn'],
#                       '{$from}':self.simulator.goal['G_dp'],
#                       '{$to}':self.simulator.goal['G_ap'],
#                       '{$time}':self.simulator.goal['G_tt'],
#                       '{$field}':'',
#                       '{$val}':'',
#                       '{$history}':'',
#                       '{$show_goal}':'Show'}

    def generate_html(self,params):
        html = self.template
        for k in params.keys():
            if params['{$show_goal}'] == 'Show' and\
            k in ['{$bus}','{$from}','{$to}','{$time}']:
                html = string.replace(html,k,'')
            else:
                html = string.replace(html,k,params[k])
        return html
       
    def get_usr_act(self,sys_act=None,conf_field=None,conf_val=None):
        simulator = cherrypy.session.get('simulator')
        history = cherrypy.session.get('history')
        params = cherrypy.session.get('params')
        print simulator
        
        if sys_act in ['I:bus','start_over']:
            return self.start_over()
        
        if conf_field and conf_val:
            sys_act = 'C:G_%s:%s'%(conf_field,conf_val)
            
        sys_act_template = {'R:open':'What can I do for you?',
                            'R:bn':'Which bus route do you want?',
                            'R:dp':'Where do you want to leave from?',
                            'R:ap':'Where do you want to go?',
                            'R:tt':'When do you want to travel?',
                            'I:bus':'Here is your bus information'}
        usr_act_template = {'bn':'blah',
                            'dp':'blah from',
                            'ap':'blah to',
                            'tt':'blah'}
        usr_acts,cs = simulator.get_usr_act(sys_act)
#        usr_acts,cs = self.simulator.get_usr_act(sys_act)
        params['{$confirms}'] = ''
#        self.params['{$confirms}'] = ''
        usr_utter = ''
        for usr_act in usr_acts:
            print usr_act
            try:
                act,field,val = usr_act.split(':')
                params['{$confirms}'] += '<option value="C:%s:%s">%s. Did I get that right?</option>\n'%('G_'+field,val,val)
#                self.params['{$confirms}'] += '<option value="C:%s:%s">%s. Did I get that right?</option>\n'%('G_'+field,val,val)
                usr_utter = ' '.join([usr_utter,usr_act_template[field],val])
            except:
                if usr_act == 'yes':
                    usr_utter = 'yes ' + usr_utter
                elif usr_act == 'no':
                    usr_utter = 'no ' + usr_utter
                elif usr_act == 'non-understanding':
                    usr_utter = 'blah blah blah' + usr_utter
        try:
            sys_act = sys_act_template[sys_act]
        except:
            act,field,val = sys_act.split(':')
            sys_act = val + ' Did I get that right?'
        history = '\n'.join([history,'SYSTEM: %s\nUSER: %s(%f)'%(sys_act,usr_utter,cs)])
        params['{$history}'] = history 
        
        cherrypy.session['simulator'] = simulator
        cherrypy.session['history'] = history
        cherrypy.session['params'] = params
        return self.generate_html(params)
#        self.history = '\n'.join([self.history,'SYSTEM: %s\nUSER: %s(%f)'%(sys_act,usr_utter,cs)])
#        self.params['{$history}'] = self.history 
#        return self.generate_html(self.params)
    get_usr_act.exposed = True

    def start_over(self):
        simulator = cherrypy.session['simulator']
        simulator.dialog_init()
        cherrypy.session['history'] = ''
        cherrypy.session['params'] = {'{$bus}':simulator.goal['G_bn'],
                       '{$from}':simulator.goal['G_dp'],
                       '{$to}':simulator.goal['G_ap'],
                       '{$time}':simulator.goal['G_tt'],
                       '{$field}':'',
                       '{$val}':'',
                       '{$history}':'',
                       '{$show_goal}':'Show'}

#        self.simulator.dialog_init()
#        self.history = ''
#        self.params = {'{$bus}':self.simulator.goal['G_bn'],
#                       '{$from}':self.simulator.goal['G_dp'],
#                       '{$to}':self.simulator.goal['G_ap'],
#                       '{$time}':self.simulator.goal['G_tt'],
#                       '{$field}':'',
#                       '{$val}':'',
#                       '{$history}':'',
#                       '{$show_goal}':'Show'}
#        return self.generate_html(self.params)
        return self.generate_html(cherrypy.session.get('params'))
    start_over.exposed = True

    def show_goal(self):
        params = cherrypy.session.get('params')
        if params['{$show_goal}'] == 'Show':
            params['{$show_goal}'] = 'Hide'
        else:
            params['{$show_goal}'] = 'Show' 
        cherrypy.session['params'] = params
        return self.generate_html(params)
#        if self.params['{$show_goal}'] == 'Show':
#            self.params['{$show_goal}'] = 'Hide'
#        else:
#            self.params['{$show_goal}'] = 'Show' 
#        return self.generate_html(self.params)
    show_goal.exposed = True

    def register(self):
        return self.register_page
    register.exposed = True

    def index(self):
        return self.start_over()
#        return self.loginpage
    index.exposed = True

class Service(object):
    @cherrypy.expose
    def default(self,*args,**kwargs):
        return

class REST(object):
    exposed = True
    
#    def GET(self):
#        cherrypy.response.status = '404 Not Found'
#        cherrypy.response.body = 'Not Found'
    
class UsrSim(object):
    exposed = True

    @cherrypy.tools.json_in(on = True)
    @cherrypy.tools.json_out(on = True)            
    def POST(self):
        def web2int(s):
            import string
            trans = {'Request(Open)':'R:open',\
                     'Request(Bus number)':'R:bn',\
                     'Request(Departure place)':'R:dp',\
                     'Request(Arrival place)':'R:ap',\
                     'Request(Travel time)':'R:tt',\
                     'Confirm(Bus number':'C:G_bn',\
                     'Confirm(Departure place':'C:G_dp',\
                     'Confirm(Arrival place':'C:G_ap',\
                     'Confirm(Travel time':'C:G_tt'
                     }
            old = s.split(':')[0]
            s = string.replace(s,old,trans[old])
            return s.split(')')[0]
        
        simulator = cherrypy.session.get('simulator')
        params = cherrypy.request.json
        print params
        if 'Command' in params:
            if params['Command'] == 'Start over':
                simulator.dialog_init()
                return {}
            elif params['Command'] == 'Get user goal':
                return {'Bus number':simulator.goal['G_bn'],\
                       'Departure place':simulator.goal['G_dp'],\
                       'Arrival place':simulator.goal['G_ap'],\
                       'Travel time':simulator.goal['G_tt']}
        elif 'System action' in params:
            usr_acts,cs = simulator.get_usr_act(web2int(params['System action']))
            web_ua = []
            for usr_act in usr_acts:
                try:
                    act,field,val = usr_act.split(':')
                    if act == 'I':
                        web_act = 'Inform('
                    if field == 'bn':
                        web_act += 'Bus number' 
                    elif field == 'dp':
                        web_act += 'Departure place'
                    elif field == 'ap':
                        web_act += 'Arrival place'
                    elif field == 'tt':
                        web_act += 'Travel time'
                    web_ua.append(web_act+':'+val+')')
                except:
                    if usr_act == 'yes':
                        web_ua.append('Affirm')
                    elif usr_act == 'no':
                        web_ua.append('Deny')
                    elif usr_act == 'non-understanding':
                        web_ua.append('Non-understanding')
            return {'User action':web_ua,'Confidence score':cs}
        
class Register(object):
    exposed = True
            
    @cherrypy.tools.json_in(on = True)
    @cherrypy.tools.json_out(on = True)
    def POST(self):
        params = cherrypy.request.json
        print params
        try:
            user_info = pickle.load(open('web/users/info','rb'))
            user_passwds = pickle.load(open('web/users/passwd','rb'))
        except IOError:
            user_info = {}
            user_passwds = {}
#        if params['action'] == 'register':
        if params['username'] == '':
            return {'err_id':1}
        if len(params['password']) < 5:
            return {'err_id':2}
        if not params['password'] == params['retype']:
            return {'err_id':3}
        if params['firstname'] == '':
            return {'err_id':4}
        if params['lastname'] == '':
            return {'err_id':5}
        import re
        email_re = re.compile(r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
                              r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
                              r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)  # domain
        if len(params['email']) < 5 and re.match('\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b', params['email']) == None:
            return {'err_id':6}
        if not params['username'] in user_info:
#                user_accounts[params['username']] = {'password':hashlib.md5(params['password']).hexdigest(),\
            user_info[params['username']] = {'firstname':params['firstname'],\
                                             'lastname':params['lastname'],'email':params['email']}
            user_passwds[params['username']] = params['password']
            pickle.dump(user_info,open('web/users/info','wb'))
            pickle.dump(user_passwds,open('web/users/passwd','wb'))
#                raise cherrypy.InternalRedirect("do_login?username=%s&password=%s&from_page=start_over"%(params['username'],params['password']))
            return {'err_id':0}
        else:
            return {'err_id':7}
#        elif params['action'] == 'login':
#            if not params['username'] in user_info:
#                return {'err_id':8}
#            else:
##                if not user_accounts[params['username']]['password'] == hashlib.md5(params['password']).hexdigest():
#                if not user_passwds[params['username']] == params['password']:
#                    return {'err_id':9}
        return {'err_id':-1}


    
letsgo_web = LetsgoWebApp()

def on_login(username):
    simulator = ls.UserSimulator()
    cherrypy.session['simulator'] = simulator
    print cherrypy.session['simulator']
#    cherrypy.session['history'] = ''
#    cherrypy.session['params'] = {'{$bus}':simulator.goal['G_bn'],
#                   '{$from}':simulator.goal['G_dp'],
#                   '{$to}':simulator.goal['G_ap'],
#                   '{$time}':simulator.goal['G_tt'],
#                   '{$field}':'',
#                   '{$val}':'',
#                   '{$history}':'',
#                   '{$show_goal}':'Show'}
    return letsgo_web.index()
    
services = Service()
services.rest = REST()
services.rest.usr_sim = UsrSim()
services.rest.register = Register()

current_dir = os.path.dirname(os.path.abspath(__file__))

http_conf_path = os.path.join(current_dir,'web/conf','http.conf')
cherrypy.config.update(http_conf_path)
cherrypy.config.update({ 
    'tools.session_auth.on': True, 
    'tools.session_auth.check_username_and_password':check_passwd, 
    'tools.session_auth.login_screen':login_screen, 
    'tools.session_auth.on_login':on_login
}) 

engine_conf_path = os.path.join(current_dir,'web/conf','engine.conf')
letsgo_web_app = cherrypy.tree.mount(letsgo_web,'/',config=engine_conf_path)

letsgo_web_app.merge(config={'/register':{'tools.session_auth.on':False}})

services_app = cherrypy.tree.mount(services,'/services',config=engine_conf_path)
_http_method_dispatcher = cherrypy.dispatch.MethodDispatcher()
service_conf = {'/rest':{'request.dispatch': _http_method_dispatcher},\
                '/rest/register':{'tools.session_auth.on':False}}
services_app.merge(service_conf)    

cherrypy.server.start()
cherrypy.engine.start()    