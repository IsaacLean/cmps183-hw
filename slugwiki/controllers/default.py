# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

import logging


def index():
    title = request.args(0) or 'All Wiki Pages'
    display_title = title.replace('_', ' ')
    form = ''
    btnAdd = ''
    page_body = ''
    last_modified = ''
    btnEdit = ''
    btnHistory = ''
    
    if request.args(0) != None:
        #get the page id
        q = db(db.pagetable.title == display_title).select().first()
        
        if(q == None):
            #if q is None then that means the page doesn't exist
            page_body = 'This page doesn\'t exist yet!'
        else:
            #otherwise the page exists and get the latest revision for the page id
            page_id = q.id
            q = db(db.revision.pageid == page_id).select().last()

            last_modified = 'Last modified: ' + str(q.date_created)
            btnEdit = A('Edit this page', _class='btn', _href=URL('default', 'edit', args = [display_title]))
            btnHistory = A('History', _class='btn', _href=URL('default', 'history', args = [display_title]))
            page_body = represent_wiki(q.body)
    else:
        q = db.pagetable

        def generate_view_button(row):
            b = A('View', _class='btn', _href=URL('default', 'index', args=[row.title]))
            return b

        def generate_edit_button(row):
            b = A('Edit', _class='btn', _href=URL('default', 'edit', args=[row.title]))
            return b

        def generate_history_button(row):
            b = A('History', _class='btn', _href=URL('default', 'history', args=[row.title]))
            return b

        def generate_del_button(row):
            b = A('Delete', _class='btn', _href=URL('default', 'delete', args=[row.id]))
            return b

        links = [
            dict(header = '', body = generate_view_button),
            dict(header = '', body = generate_edit_button),
            dict(header = '', body = generate_history_button),
            dict(header = '', body = generate_del_button)
        ]

        #display table of all pages in database with buttons
        form = SQLFORM.grid(q, create = False, editable = False, deletable = False, details = False, csv = False, links=links)

        #create add button
        btnAdd = A('Add a new page', _class='btn', _href=URL('default', 'add'))

    #return data to index.html
    return dict(display_title=display_title, form=form, page_body=page_body, btnAdd=btnAdd, last_modified=last_modified, btnEdit=btnEdit, btnHistory=btnHistory)

@auth.requires_login()
def add():
    #generate form for user to use
    form = SQLFORM.factory(
        Field('input_title', 'string', label = 'Page Title', requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, db.pagetable.title)]),
        Field('input_body', 'text', label = 'Content')
        )
    form.add_button('Cancel', URL('default', 'index'))

    #after receiving data from a submitted form...
    if form.process().accepted:
        #insert new page with title
        db.pagetable.insert(title = request.vars['input_title'])

        #get id of page that was just inserted
        q = db().select(db.pagetable.id)
        page_id = q[len(q) - 1].id

        #insert new revision tied to new page
        db.revision.insert(pageid = page_id, body = request.vars['input_body'])
        session.flash = T('Page added')
        redirect(URL('default', 'index', args = request.vars['input_title']))

    #return data to add.html
    return dict(form=form)

@auth.requires_login()
def edit():
    query_title = request.args(0).replace('_', ' ')
    q = db(db.pagetable.title == query_title).select().last()
    page_query = q
    latest_title = ""
    page_id = -1

    if(q):
        latest_title = q.title
        page_id = q.id
    else:
        redirect(URL('default', 'index'))

    #get the latest page/revision data
    q = db(db.revision.pageid == page_id).select().last()
    latest_body = q.body

    form = SQLFORM.factory(
        Field('input_title', 'string', label = 'Page Title', default = latest_title, requires = IS_NOT_EMPTY()),
        Field('input_body', 'text', label = 'Content', default = latest_body),
        Field('input_comment', 'string', label = 'Revision comment')
        )
    form.add_button('Cancel', URL('default', 'index', args = [latest_title]))

    #after receiving data from a submitted form...
    if form.process().accepted:
        page_query.update_record(title = request.vars['input_title'])
        db.revision.insert(pageid = page_id, body = request.vars['input_body'], rev_comment = request.vars['input_comment'])
        session.flash = T('Page edited')
        redirect(URL('default', 'index', args = request.vars['input_title']))

    #return data to edit.html
    return dict(form=form, page_title=latest_title)

@auth.requires_login()
def history():
    page_title = request.args(0).replace('_', ' ')
    q = db(db.pagetable.title == page_title).select().last()
    page_query = q
    latest_title = ""
    page_id = -1

    if(q):
        page_id = q.id
    else:
        redirect(URL('default', 'index'))

    def generate_revert_button(row):
        b = A('Revert', _class='btn', _href=URL('default', 'revert', args=[page_title, row.id]))
        return b

    links = [
        dict(header = '', body = generate_revert_button)
    ]

    fields = [db.revision.userid, db.revision.date_created, db.revision.body, db.revision.rev_comment]

    form = SQLFORM.grid(db.revision.pageid == page_id, fields=fields, create = False, editable = False, deletable = False, details = False, csv = False, sortable=False, orderby="revision.date_created DESC", user_signature=False, links=links)
    
    btnBack = A('Return to page', _class='btn', _href=URL('default', 'index', args = [page_title]))

    return dict(form=form, page_title=page_title, btnBack=btnBack)

@auth.requires_login()
def revert():
    page_title = request.args(0).replace('_', ' ')
    q = db(db.pagetable.title == page_title).select().last()
    latest_title = ""
    page_id = -1
    rev_id = request.args(1)

    if(q):
        page_id = q.id
        q = db(db.revision.id == rev_id).select().last()
        if(q):
            comment = "Revert to revision " + rev_id + " created on " + str(q.date_created)
            db.revision.insert(pageid = page_id, body = q.body, rev_comment = comment)
            session.flash = T('Page reverted')
            redirect(URL('default', 'index', args = [page_title]))
        else:
            redirect(URL('default', 'index'))
    else:
        redirect(URL('default', 'index'))

@auth.requires_login()
def delete():
    #get page_id from URI
    page_id= db.pagetable(request.args(0)) or redirect(URL('default', 'index'))
    
    form = FORM.confirm('Are you sure you want to delete this page?')
    if form.accepted:
        db(db.pagetable.id == page_id.id).delete()
        session.flash = T('Page deleted')
        redirect(URL('default', 'index'))

    return dict(form=form)


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
