# coding: utf-8
import ast
import httplib2
import logging
from openerp.addons.web import http
from openerp.addons.web.controllers.main import Session as session
from openerp.tools import config
from openerp.osv import osv
from oauth2client.client import AccessTokenCredentials as ATC

openerpweb = http


class Session(session):

    _cp_path = "/web/session"

    @openerpweb.jsonrequest
    def destroy(self, req):
        uid = req.session._uid
        user_values = req.session.model('res.users').read(
            uid, ['oauth_id_token', 'oauth_token']
        )
        id_token = user_values['oauth_id_token']
        token = user_values['oauth_token']
        exceptions = False
        if not id_token:
            req.session._suicide = True
            return
        id_token = ast.literal_eval(id_token)
        cred = ATC(token, None)
        http_credentials = cred.authorize(httplib2.Http())
        user_id = id_token['sub']
        uri = config.get('auth_oauth2.end_session_endpoint')
        client_id = config.get('auth_oauth2.client_id')
        client_secret = config.get('auth_oauth2.client_secret')
        req_body = {
            'user_id': int(user_id),
            'client_id': client_id,
            'client_secret': client_secret,
        }
        try:
            response = http_credentials.request(uri, 'GET', body=str(req_body))
            if response[0].status != 200:
                exceptions = True
        except Exception as e:
            logging.error("oauth2 end session : %s" % (e))
            exceptions = e
        req.session._suicide = True
        if exceptions:
            raise osv.except_osv(
                u"Attention, une erreur s'est produite lors de la déconnexion",
                u"Il est possible que vous ne soyez pas déconnecté du SSO"
            )
