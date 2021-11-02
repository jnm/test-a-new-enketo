#!/usr/bin/env python3
# jnm 20210624

PORT = 8000
ENKETO_SERVER = 'https://ee.for-testing-only.kbtdev.org/'
ENKETO_SURVEY_ENDPOINT = 'api/v2/survey/all'
ENKETO_API_TOKEN = 'this is a testing instance of enketo express'

import http.server
import re
import requests
from http import HTTPStatus
from urllib.parse import urlparse, parse_qs

def enketo_survey_request(openrosa_server_url, form_id):
    data = {
        'server_url': openrosa_server_url,
        'form_id': form_id,
    }
    response = requests.post(
        '{}{}'.format(ENKETO_SERVER, ENKETO_SURVEY_ENDPOINT),
        # bare tuple implies basic auth
        auth=(ENKETO_API_TOKEN, ''),
        data=data
    )
    response.raise_for_status()
    return response

def get_enketo_survey_links_table(username, url):
    """
    username like 'jnm_demo'
    url like 'https://kf.kobotoolbox.org/#/forms/abcdefghijklmnopqrstuv/summary'
    """
    matches = re.match(
        r'https://(?:kf|kobo)\.(kobotoolbox\.org|humanitarianresponse\.info)/#/forms/([^/]+)',
        url,
    )
    if not matches:
        return
    domain = matches[1]
    asset_uid = matches[2]
    response = enketo_survey_request(
        f'https://kc.{domain}/{username}', asset_uid
    )
    response_json = response.json()
    output = '<table border="1">'
    for key, value in response_json.items():
        if isinstance(value, str) and value.startswith('https'):
            value = f'<a href="{value}">{value}</a>'
        output += f'<tr><td>{key}</td><td>{value}</td></tr>'
    output += '</table>'
    return output

class MyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def _write_str(self, s):
        self.wfile.write(s.encode('utf-8'))

    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        w = self._write_str
        w('<html><head><title>KoBoToolbox Enketo Testing</title></head><body>')
        get_data = parse_qs(urlparse(self.path).query)
        username = get_data.get('username', [None])[0]
        url = get_data.get('url', [None])[0]
        if username and url:
            w('<h2>Response from Enketo</h2>')
            w(
                '<p>Do <strong>NOT</strong> use these links for any data '
                'collection other than testing. They may stop working without '
                'notice, at any time!</p>'
            )
            w(get_enketo_survey_links_table(username, url))
        w('<h2>Test a form with a new version of Enketo</h2>')
        w(
            '<form><p><label>URL of a form, e.g. '
            'https://kf.kobotoolbox.org/#/forms/abcdefghijklmnopqrstuv/summary.<br>'
            'Forms must be hosted on kobotoolbox.org or humanitarianresponse.info.<br>'
            'Do not use a form that was uploaded directly to the legacy interface.<br>'
            '<input type="text" name="url" size="80"></label></p>'
            '<p><label>Username of an account with access to submit to this form: '
            '<input type="text" name="username"></label></p>'
            '<p><input type="submit"></p></form>'
        )
        w('<h3>Information about this version of Enketo</h3>')
        w(
            '<iframe src="https://ee.for-testing-only.kbtdev.org/" '
            'width="69%" height="555"></iframe>'
        )
        w('</body></html>')

if __name__ == '__main__':
    with http.server.ThreadingHTTPServer(
        ('', PORT), MyHTTPRequestHandler
    ) as httpd:
        print(f'Ready for service on port {PORT}.')
        httpd.serve_forever()
