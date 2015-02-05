# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

import logging


def index():
    """
    This is the main page of the wiki.  
    You will find the title of the requested page in request.args(0).
    If this is None, then just serve the latest revision of something titled "Main page" or something 
    like that. 
    """
    title = request.args(0) or 'main page'
    # You have to serve to the user the most recent revision of the 
    # page with title equal to title.
    
    # Let's uppernice the title.  The last 'title()' below
    # is actually a Python function, if you are wondering.
    display_title = title.title()

    
    # Here, I am faking it.  
    # Produce the content from real database data. 
    #content = represent_wiki("I like <<Panda>>s")
    q = db.pagetable

    def generate_view_button(row):
        b = A('View', _class='btn', _href=URL('default', 'view', args=[row.id]))
        return b

    def generate_edit_button(row):
        b = A('Edit', _class='btn', _href=URL('default', 'edit', args=[row.id]))
        return b

    def generate_del_button(row):
        b = A('Delete', _class='btn', _href=URL('default', 'delete', args=[row.id]))
        return b

    links = [
        dict(header = '', body = generate_view_button),
        dict(header = '', body = generate_edit_button),
        dict(header = '', body = generate_del_button)
    ]

    form = SQLFORM.grid(q, editable = False, deletable = False, details = False, links=links)
    return dict(display_title=display_title, form=form)

def view():
    p = db.pagetable(request.args(0)) or redirect(URL('default', 'index'))
    form = SQLFORM(db.pagetable, record = p, readonly = True)
    return dict(form=form)

@auth.requires_login()
def add():
    """form = SQLFORM(db.pagetable)
    if form.process().accepted:
        session.flash = T('Page added')
        redirect(URL('default', 'index'))"""
    form = FORM('Page title: ', INPUT(_name='input_title'), 'Body: ', INPUT(_name='input_body'), '', INPUT(_type='submit'))
    if form.process().accepted:
        #page_id = db.executesql('SELECT max(id) from pagetable')
        """q = db((db.pagetable).select(db.pagetable.id.max()))
        print 'the time is now'
        print q
        if q == '9':
            print 'equal'
        else:
            print 'not equal'
        for thing in q:
            print thing.id"""
        #insert new page with title
        db.pagetable.insert(title = request.vars['input_title'])

        #get id of page that was just inserted
        q = db().select(db.pagetable.id)
        page_id = q[len(q) - 1].id

        #insert new revision tied to new page
        db.revision.insert(pageid = page_id, body = request.vars['input_body'])
        redirect(URL('default', 'view', args = page_id))
    return dict(form=form)

@auth.requires_login()
def edit():
    p = db.pagetable(request.args(0)) or direct(URL('default', 'index'))
    form = SQLFORM(db.pagetable, record = p)
    if form.process().accepted:
        session.flash = T('Updated')
        redirect(URL('default', 'view', args = [p.id]))
    return dict(form=form)

@auth.requires_login()
def delete():
    p = db.pagetable(request.args(0)) or redirect(URL('default', 'index'))
    db(db.pagetable.id == p.id).delete()
    redirect(URL('default', 'index'))


def test():
    """This controller is here for testing purposes only.
    Feel free to leave it in, but don't make it part of your wiki.
    """
    title = "This is the wiki's test page"
    form = None
    content = None
    
    # Let's uppernice the title.  The last 'title()' below
    # is actually a Python function, if you are wondering.
    display_title = title.title()
    
    # Gets the body s of the page.
    r = db.testpage(1)
    s = r.body if r is not None else ''
    # Are we editing?
    editing = request.vars.edit == 'true'
    # This is how you can use logging, very useful.
    logger.info("This is a request for page %r, with editing %r" %
                 (title, editing))
    if editing:
        # We are editing.  Gets the body s of the page.
        # Creates a form to edit the content s, with s as default.
        form = SQLFORM.factory(Field('body', 'text',
                                     label='Content',
                                     default=s
                                     ))
        # You can easily add extra buttons to forms.
        form.add_button('Cancel', URL('default', 'test'))
        # Processes the form.
        if form.process().accepted:
            # Writes the new content.
            if r is None:
                # First time: we need to insert it.
                db.testpage.insert(id=1, body=form.vars.body)
            else:
                # We update it.
                r.update_record(body=form.vars.body)
            # We redirect here, so we get this page with GET rather than POST,
            # and we go out of edit mode.
            redirect(URL('default', 'test'))
        content = form
    else:
        # We are just displaying the page
        content = s
    return dict(display_title=display_title, content=content, editing=editing)


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
