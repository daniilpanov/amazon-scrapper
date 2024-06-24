from QtWebView import Scraper


class ReviewsScene(Scraper):
    asin: str | None = None
    url: str | None = None
    keywords: str = ''
    current_format: bool = True
    need_proxy = True
    scripts = {'reviews.js': './reviews_service/reviews.js'}
    prefix: str | None = None
    index = 0
    page_number = 1

    def beginScene(self, task):
        super().beginScene(task)
        self.task = task
        data = task.get('data', {})
        self.asin = data['asin']
        self.prefix = task.get('result', {}).get('canonical_prefix')
        self.url = ('https://www.' + data.get('domain', 'amazon.com') + (
            self.prefix + '/' if self.prefix else '') + '/product-service/' + data['asin']
                    + '/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews&pageNumber=1')
        self.index = task.get('index', 0)
        self.page_number = task.get('page', 1)

    def __next__(self):
        super().__iter__()
        self.setUrl(self.url)
        print('setReviewsUrl')

    def actionHtmlLoaded(self, html):
        if not super().actionHtmlLoaded(html):
            return False
        if self.setAmazonLocation():
            return False
        self.runJs('''new QWebChannel(qt.webChannelTransport, async (channel) => {
            const RLC = channel.objects.ReviewsLoader;
            const collector = new CollectReviews("%s", %s, %s, "%s", "%s");
            collector.per_index_callback = (data) => {
                RLC.loadPage(data);
            };
            let fails_counter = 0;
            collector.serviceunavailableerror_callback = () => {
                if (fails_counter > 20) {
                    return false;
                }
                return ++fails_counter;
            };
            collector.index = %s;
            collector.page = %s;
            console.log(await collector.collect());
        });
        ''' % (self.asin, f'"{self.prefix}"' if self.prefix else 'null', 'true' if self.current_format else 'false',
               self.keywords, self.domain, str(self.index), str(self.page_number)))
