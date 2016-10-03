import httplib2
from openerp.addons.web import http
from openerp.addons.web.controllers.main import Session as session
from openerp.tools import config

openerpweb = http


class Session(session):

    _cp_path = "/web/session"

    @openerpweb.jsonrequest
    def destroy(self, req):
        uid = req.session._uid
        id_token = req.session.model('res.users').read(
            uid, ['oauth_id_token']
        )['oauth_id_token']
        if not id_token:
            req.session._suicide = True
        conn = httplib2.Http()
        uri = config.get('auth_oauth2.end_session_endpoint')
        conn.request(uri, 'GET', body="{'id_token': %s}" % (id_token))
        req.session._suicide = True
