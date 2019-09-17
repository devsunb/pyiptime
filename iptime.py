import logging
import re

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger('IPTIME')


class IPTime:
    def __init__(self, url):
        """
        ipTIME router
        :param url: URL to access ipTIME router
        """
        self.url = url

        self.url_login_page = self.url + 'sess-bin/login_session.cgi'
        self.url_login_handler = self.url + 'sess-bin/login_handler.cgi'
        self.url_timepro = self.url + 'sess-bin/timepro.cgi'
        self.url_list_wol = self.url_timepro + '?tmenu=iframe&smenu=expertconfwollist'
        self.regex_sess = re.compile('setCookie\\(\'(.*)\'\\);')
        self.session = {}

        # check if connections are stable
        r = requests.get(self.url_login_page).text
        bs = BeautifulSoup(r, 'html.parser')
        title = bs.find('title').text
        if 'ipTIME' not in title:
            logger.error('Wrong URL : [{}] {}'.format(title, url))
            raise RuntimeError('Wrong URL : [{}] {}'.format(title, url))
        logger.info('Target ipTIME : {}'.format(title))

    def login(self, user, pw):
        """
        Login method
        :param user: Username
        :param pw: Password
        """
        d = {'init_status': 1, 'captcha_on': 0, 'captcha_file': '', 'username': user, 'passwd': pw,
             'default_passwd': '', 'captcha_code': ''}
        h = {'Referer': self.url_login_page, 'User-Agent': 'Mozilla/5.0'}
        logger.debug('Login to ipTIME (USER : {})'.format(user))
        r = requests.post(self.url_login_handler, d, h).text
        regex_search = self.regex_sess.search(r)
        if regex_search is None or not regex_search.groups():
            logger.error('Login failed (USER : {})'.format(user))
            raise RuntimeError('Login failed (USER : {})'.format(user))
        self.session['efm_session_id'] = regex_search.groups()[0]
        logger.info('Login success (USER : {})'.format(user))

    def list_wol(self):
        """
        List WOL
        :return: WOL List [[no, mac, id], ...]
        """
        logger.debug('List WOL')
        if not self.session['efm_session_id']:
            logger.error('Not Authenticated')
            raise RuntimeError('Not Authenticated')
        r = requests.get(self.url_list_wol, cookies=self.session).text
        bs = BeautifulSoup(r, 'html.parser')
        result = []
        for tr in bs.find_all('tr', {'class': 'wol_main_tr'})[1:]:
            tds = tr.find_all('td')
            if len(tds) > 3:
                result.append([tds[0].text, tds[1].text, tds[2].text])
        logger.debug('WOL List : {}'.format(result))
        return result

    def wake(self, mac):
        """
        Run WOL
        :param mac: Target MAC address
        """
        logger.debug('Run WOL to [{}]'.format(mac))
        if not self.session['efm_session_id']:
            logger.error('Not Authenticated')
            raise RuntimeError('Not Authenticated')
        d = {'tmenu': 'iframe', 'smenu': 'expertconfwollist', 'nomore': '0', 'wakeupchk': mac, 'act': 'wake'}
        r = requests.post(self.url_timepro, d, cookies=self.session).text
        if mac not in r:
            logger.error('WOL failed : [{}]'.format(mac))
            raise RuntimeError('WOL failed : [{}]'.format(mac))
        logger.info('WOL success : {}'.format(mac))
