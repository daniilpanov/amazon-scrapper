from PyQt5.QtNetwork import QNetworkProxy, QNetworkCookie
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineScript, QWebEngineProfile
from PyQt5.QtCore import QUrl, QFile, QTextStream, pyqtSlot, QTimer, pyqtSignal
from bs4 import BeautifulSoup

import helpers


class WebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, msg, line, sourceID):
        if sourceID:
            return
        print(f'JS console message [{line},{sourceID}]:', level, msg)

    def javaScriptAlert(self, url, msg):
        print(f'JS alert [{url}]:', msg)
        # QMessageBox.information(self.view(), "Alert", msg)


class Scraper(QWebEngineView):
    default_web_page = WebEnginePage
    actions: list
    soup: BeautifulSoup | None = None
    need_proxy: bool = False
    domain: str = 'amazon.com'
    task: dict
    # signals
    # [task_id]
    success_signal = pyqtSignal(str)
    # [task_id, stage]
    set_stage_signal = pyqtSignal(str, int)
    # [task_id, error, play, reload]
    report_signal = pyqtSignal(str, str, bool, bool)
    # [task_id]
    reload_signal = pyqtSignal(str)
    # [task_id]
    proxy_change_signal = pyqtSignal(str)

    def __init__(self):
        super(Scraper, self).__init__()
        self.profile = QWebEngineProfile.defaultProfile()
        self.setPage(self.default_web_page(self.profile, self))
        # empty actions list
        self.actions = []

        # Load qwebchannel.js
        file = QFile('./qwebchannel.js')
        if not file.open(QFile.ReadOnly):
            print('Failed to load qwebchannel.js')
            return
        script = QTextStream(file).readAll()
        file.close()

        # Create QWebEngineScript
        qwebchannel_script = QWebEngineScript()
        qwebchannel_script.setName('qwebchannel.js')
        qwebchannel_script.setSourceCode(script)
        qwebchannel_script.setInjectionPoint(QWebEngineScript.DocumentCreation)
        qwebchannel_script.setWorldId(QWebEngineScript.MainWorld)
        qwebchannel_script.setRunsOnSubFrames(False)

        # Insert script into profile
        self.profile.scripts().insert(qwebchannel_script)

        # Create a QWebChannel and register a QObject to communicate with JavaScript
        self.channel = QWebChannel(self.page())
        self.page().setWebChannel(self.channel)

        self.channel.registerObject('mainCh', self)
        self.loadFinished.connect(self._onLoadFinished)

    def getURL(self):
        return self.page().url()

    def setUrl(self, url: QUrl | str):
        if isinstance(url, str):
            url = QUrl(url)
        if self.page().url().url() == url.url():
            self.reload()
        else:
            self.load(url)
        print('url changed')

    def getAmazonLocation(self):
        if not self.soup:
            raise ValueError
        popover_line_2 = self.soup.find(attrs={'id': 'glow-ingress-line2'})
        if not popover_line_2:
            return None
        return popover_line_2.text.strip()

    def setAmazonLocation(self, zip_code: int = 90005):
        curr_loc = self.getAmazonLocation()
        if not curr_loc or str(zip_code) in curr_loc:
            return False
        print('setLoc')
        self.runJs('''
        new QWebChannel(qt.webChannelTransport, (channel) => {
            const mainCh = channel.objects.mainCh;
            (async () => {
                async function waitEl(q) {
                    let el = document.querySelector(q);
                    while (!el) {
                        await new Promise(resolve => setTimeout(resolve, 500));
                        el = document.querySelector(q);
                    }
                    return el;
                }
                const loc_popover = await waitEl('#nav-global-location-popover-link');
                loc_popover.click();
                const input = await waitEl('#GLUXZipUpdateInput');
                input.value = ''' + str(zip_code) + ''';
                const submit_button = await waitEl('[data-action=GLUXPostalUpdateAction] > input');
                submit_button.click();
                mainCh._action
            })();
        });
        ''')
        return True

    def getActionObjects(self):
        return self.actions

    def setActionObjects(self, actions):
        if isinstance(actions, (list, tuple)):
            self.actions = actions
            for action in actions:
                self.channel.registerObject(action.__class__.__name__, action)
        else:
            if self.actions:
                self.actions.append(actions)
            else:
                self.actions = [actions]
            self.channel.registerObject(actions.__class__.__name__, actions)

    def actionHtmlLoaded(self, html):
        # 0) parse page html
        self.soup = BeautifulSoup(html, 'lxml')
        print('bs')
        # 1) connection
        if self.soup.find('body', {'class': 'neterror'}):
            pass
        print('connection successful')
        # 2) captcha
        if self.soup.select('body > div > div[style*="width: 350px"]'):
            print('solving captcha!')
            img = self.soup.select_one('img[src]')
            solve = helpers.captcha_solve(img['src'])
            if not solve:
                return self.reload()
            self.runJs('''
            const input = document.querySelector('#captchacharacters');
            input.value = "''' + solve + '''";
            const submit = document.querySelector('button[type=submit]');
            submit.click();
            ''')
        return True

    @pyqtSlot(str)
    def receiveHtml(self, html):
        print('html loaded!')
        return self.actionHtmlLoaded(html)

    def getHtml(self):
        print('wait for html')
        self.page().runJavaScript('''
            new QWebChannel(qt.webChannelTransport, (channel) => {
                const mainCh = channel.objects.mainCh;
                mainCh.receiveHtml(document.documentElement.outerHTML);
            });
        ''')

    def runJs(self, script):
        self.page().runJavaScript(script)

    def configure(self, proxy_setup=None, domain='amazon.com'):
        self.domain = domain
        if not proxy_setup:
            return
        if (addr := proxy_setup.get('addr')) and (port := proxy_setup.get('port')):
            self.setProxy(addr, port, proxy_setup.get('username'), proxy_setup.get('password'))
        if cookies := proxy_setup.get('cookies'):
            for name, value in cookies.items():
                self.setCookie(name, value, domain)
                self.setCookie(name, value, 'www.' + domain)
        if ua := proxy_setup.get('useragent'):
            self.setUserAgent(ua)

    def beginScene(self, task):
        pass

    def __iter__(self):
        pass

    def endScene(self):
        pass

    @staticmethod
    def setGlobalProxy(addr, port, username=None, password=None, *, _type=QNetworkProxy.HttpProxy):
        proxy = QNetworkProxy()
        proxy.setType(_type)
        proxy.setHostName(addr)
        proxy.setPort(port)
        if username:
            proxy.setUser(username)
            if password:
                proxy.setPassword(password)
        QNetworkProxy.setApplicationProxy(proxy)

    def setProxy(self, addr, port, username=None, password=None, *, _type=QNetworkProxy.HttpProxy):
        return self.setGlobalProxy(addr, port, username, password, _type=_type)

    def setUserAgent(self, ua):
        self.profile.setHttpUserAgent(ua)

    def setCookie(self, name, value, domain=None):
        cookie = QNetworkCookie(name.encode(), value.encode())
        cookie.setDomain(domain)
        self.profile.cookieStore().setCookie(cookie)

    def _onLoadFinished(self):
        print('loaded')
        self.getHtml()
        self.runJs('console.log("Hello, world!");')
