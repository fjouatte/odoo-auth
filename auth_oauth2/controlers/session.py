# coding: utf-8

import httplib2
import logging
from openerp.addons.web import http
from openerp.addons.web.controllers.main import Session as session
from openerp.tools import config
from openerp.osv import osv

openerpweb = http


class Session(session):

    _cp_path = "/web/session"

    @openerpweb.jsonrequest
    def destroy(self, req):
        uid = req.session._uid
        id_token = req.session.model('res.users').read(
            uid, ['oauth_id_token']
        )['oauth_id_token']
        exceptions = False
        if not id_token:
            req.session._suicide = True
            return
        conn = httplib2.Http()
        uri = config.get('auth_oauth2.end_session_endpoint')
        try:
            conn.request(uri, 'GET', body="{'id_token': %s}" % (id_token))
        except Exception as e:
            logging.error("Oauth2 end session : %s" % (e.strerror))
            exceptions = e
        req.session._suicide = True
        if exceptions:
            raise osv.except_osv(
                u"Attention, une erreur s'est produite lors de la déconnexion",
                u"Il est possible que vous ne soyez pas déconnecté du SSO"
            )
