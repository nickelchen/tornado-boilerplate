# coding: utf-8
import sys
import tornado.web
import tornado.auth

from jinja2 import Template, Environment, FileSystemLoader
from bson.objectid import ObjectId

import filter, utils, session
from forms import *
from models import *

class BaseHandler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        tornado.web.RequestHandler.__init__(self, application, request, **kwargs)
        self.session = session.TornadoSession(application.session_manager, self)
        self._title = self.settings['app_name']

    def render_string(self,template,**args):
        env = Environment(loader=FileSystemLoader(self.settings['template_path']))
        env.filters['tags_name_tag'] = filter.tags_name_tag
        env.filters['user_name_tag'] = filter.user_name_tag
        env.filters['strftime'] = filter.strftime
        env.filters['strfdate'] = filter.strfdate
        env.filters['avatar'] = filter.avatar
        env.filters['truncate_lines'] = utils.truncate_lines
        template = env.get_template(template)
        return template.render(settings=self.settings,
                               title=self._title,
                               notice_message=self.notice_message,
                               current_user=self.current_user,
                               static_url=self.static_url,
                               modules=self.ui['modules'],
                               xsrf_form_html=self.xsrf_form_html,
                               **args)

    def render(self, template, **args):
        self.finish(self.render_string(template, **args))

    def get_current_user(self):
        user_id = self.get_secure_cookie("user_id")
        if not user_id: return None
        try:
          return User.objects(id = user_id).first()
        except:
          return None

    def notice(self,msg,type = "success"):
        type = type.lower()
        if ['error','success','warring'].count(type) == 0:
            type = "success"
        self.session["notice_%s" % type] = msg 
        self.session.save()

    @property
    def notice_message(self):
        try:
          msg = self.session['notice_error']
          self.session['notice_error'] = None
          self.session['notice_success'] = None
          self.session['notice_warring'] = None
          self.session.save()
          if not msg:
            return ""
          else:
            return msg
        except:
          return ""

    def render_404(self):
        raise tornado.web.HTTPError(404)

    def set_title(self, str):
        self._title = u"%s - %s" % (str,self.settings['app_name'])

class HomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("home.html", asks=[])

class LogoutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.set_secure_cookie("user_id","")
        self.redirect("/login")

class LoginHandler(BaseHandler):
    def get(self):
        self.set_title(u"登陆")
        self.render("login.html")

    def post(self):
        self.set_title(u"登陆")
        frm = LoginForm(self)
        if not frm.validate():
            frm.render("login.html")
            return

        password = utils.md5(frm.password)
        user = User.objects(login=frm.login,
                            password=password).first()
        if not user:
            frm.add_error("password", "不正确")
            frm.render("login.html")

        self.set_secure_cookie("user_id", str(user.id))
        self.redirect("/")

class RegisterHandler(BaseHandler):
    def get(self):
        self.set_title(u"注册")
        user = User()
        self.render("register.html", user=user)

    def post(self):
        self.set_title(u"注册")
        frm = RegisterForm(self)
        if not frm.validate():
            frm.render("register.html")
            return
        
        user = User(name=frm.name,
                    login=frm.login,
                    email=frm.email,
                    password=utils.md5(frm.password))
        try:
          user.save()
          self.set_secure_cookie("user_id",str(user.id))
          self.redirect("/")
        except Exception,exc:
          self.notice(exc,"error")
          frm.render("register.html")

