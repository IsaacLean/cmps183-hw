# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    """posts = db().select(db.forsalesite.ALL)
    return dict(posts = posts)"""

    q = db.forsalesite
    form = SQLFORM.grid(q,
        fields=[db.forsalesite.name, db.forsalesite.date_posted, db.forsalesite.title, db.forsalesite.category, db.forsalesite.price, db.forsalesite.available])
    return dict(form = form)

@auth.requires_login()
def add():
    form = SQLFORM(db.forsalesite)
    if form.process().accepted:
        session.flash = T('Listing added')
        redirect(URL('default', 'index'))
    return dict(form = form)

def view():
    #p = db(db.forsalesite.id == request.args(0)).select().first()
    p = db.forsalesite(request.args(0)) or redirect(URL('default', 'index'))
    form = SQLFORM(db.forsalesite, record = p, readonly = True)
    return dict(form = form)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login()
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
