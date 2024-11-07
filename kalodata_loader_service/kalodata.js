function randomnum(min, max) {
    return Math.floor(Math.random() * (max - min) + min);
}

async function getJsonData(req) {
    req = await req;
    if (req.status > 299) {
        throw new LimitReached();
    }
    let data = await req.json();
    if (!data || !data.success) {
        throw new LimitReached();
    }
    return data.data;
}

function convertNum(num) {
    num = num.trim();
    let numberRange = num.split('-');
    if (numberRange.length > 2) {
        let parts = [];
        let symbol = null;
        for (let numPart of numberRange) {
            let res = convertNum(numPart);
            symbol = res[0] || symbol;
            parts.push(String(res[1]));
        }
        return [symbol, ...parts];
    }
    num = num.replace(',', '');
    // Config
    let k = 1;
    let symbolsMap = {
        'k': 1000,
        'm': 1000000,
        'b': 1000000000,
    };
    for (let sym in symbolsMap) {
        if (num.slice(num.length - 1).toLowerCase() === sym) {
            k = symbolsMap[sym];
            num = num.slice(0, num.length - 1);
            break;
        }
    }
    let symbol = null;
    if (!/[0-9]/.test(num[0])) {
        symbol = num[0];
        num = num.slice(1);
    } else if (!/[0-9]/.test(num.slice(num.length - 1))) {
        symbol = num.slice(num.length - 1);
        num = num.slice(0, num.length - 1);
    }
    try {
        num = parseFloat(num);
        return [symbol, num * k];
    } catch (e) {
        return [null, null];
    }
}

class CheckEmailScene {
    static SIGNUP = 'signup';
    static LOGIN = 'login';
}

class Items {
    static VIDEO = 'video';
    static PRODUCT = 'product';
    static CREATOR = 'creator';
    static SHOP = 'shop';
}

class LimitReached extends Error {
    constructor(message) {
        super(message);
        this.name = 'LimitReached';
    }
}

class EmailChecker {
    constructor(scene, captchaType = 'cloudflare', response = 'token') {
        this.tempMailInst = new TempMail();
        this.scene = scene;
        this.captchaType = captchaType;
        this.response = response;
        this.code = null;
    }

    async genEmail() {
        await this.tempMailInst.genEmail();
        this.email = this.tempMailInst.email;
    }

    async getCode() {
        let msgs = await this.tempMailInst.fetchEmails('noreply@email.kalodata.com');
        for (let msg of (msgs || [])) {
            let bodyParts = msg.fetchData().body.split(' ');
            for (let part of bodyParts) {
                part = part.trim();
                if (!part) continue;
                if (part.match(/^\d{6}$/)) {
                    this.code = part;
                    return part;
                }
            }
        }
        return null;
    }
}

class Request {
    static host = 'www.kalodata.com';
    static baseUrl = 'https://' + Request.host + '/';
    static defaultHeaders = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-GB,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,en-US;q=0.6',
        'country': 'US',
        'currency': 'USD',
        'dnt': '1',
        'language': 'en-US',
        'host': Request.host,
        'origin': Request.baseUrl,
        'priority': 'u=1, i',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    };

    constructor(req = null) {
        if (req) {
            this.startDate = req.startDate;
            this.endDate = req.endDate;
        } else {
            this.startDate = null;
            this.endDate = null;
        }
        this.currentPage = '';
    }

    req(method, url, body) {
        let conf = {
            method: method || 'POST',
        };
        if (body) {
            conf.headers = {
                'Content-Type': 'application/json',
            };
            conf.body = JSON.stringify(body || {});
        }
        return fetch(Request.baseUrl + (url || ''), conf);
    }
}

class Kalodata extends Request {
    queryProfile() {
        return this.req('POST', 'user/queryProfile');
    }

    getFirstDay() {
        return this.req('POST', 'api/firstDay0', { body: { country: 'US' } });
    }

    getAllLastDays() {
        return this.req('GET', 'api/allLastDay');
    }

    getConfigurations(...configKeys) {
        let data = configKeys.map(key => ({ key }));
        return this.req('POST', 'api/configurations', data);
    }

    getCategoriesTree() {
        return this.getConfigurations('global.category.tree');
    }

    homepageDialogQueryList() {
        return this.req('POST', 'homepage/dialog/queryList');
    }

    userQueryMembership() {
        return this.req('POST', 'user/queryMembership', { body: { country: 'US' } });
    }

    getCountryContacts() {
        return this.req('POST', 'v1/countryV1/contacts', { params: { type: 'pc' }, headers: { origin: null, 'content-type': null } });
    }

    getUserFeatures(lst) {
        return this.req('POST', 'user/features', { body: { country: 'US', list: lst } });
    }

    livestreamQueryUnwatch() {
        return this.req('POST', 'livestream/queryUnWatch', { headers: { 'content-type': null } });
    }

    logout() {
        return this.req('POST', 'user/logout', { headers: { 'content-type': null } });
    }

    sendEmailMessage(emailChecker) {
        return this.req('POST', 'email/emailSendMessage', { response: emailChecker.response, scene: emailChecker.scene, email: emailChecker.email, captchaType: emailChecker.captchaType });
    }

    verifyEmailMessage(emailChecker) {
        return this.req('POST', 'email/check' + emailChecker.scene.charAt(0).toUpperCase() + emailChecker.scene.slice(1) + 'Verification', { body: { email: emailChecker.email, loginMethod: 'EMAIL', emailCode: emailChecker.code, scene: emailChecker.scene } });
    }

    singupOrLogin(emailChecker, sceneKey = null) {
        let keyScene = sceneKey || (emailChecker.scene === CheckEmailScene.LOGIN ? 'scene' : 'scence');
        console.log({
            [keyScene]: emailChecker.scene,
            "tcCode": "",
            "email": emailChecker.email,
            "emailCode": emailChecker.code,
            "loginMethod": "EMAIL",
        });
        return this.req('POST', 'user/' + emailChecker.scene, { body: { [keyScene]: emailChecker.scene, "tcCode": "", "email": emailChecker.email, "emailCode": emailChecker.code, "loginMethod": "EMAIL" } });
    }

    searchUserTCCode(emailChecker) {
        return this.req('POST', 'user/searchUserTCCode', { body: { email: emailChecker.email } });
    }

    homepageBannersQueryList() {
        return this.req('POST', 'homepage/banner/queryList', { headers: { 'content-type': null } });
    }

    homepageSolutionQueryList() {
        return this.req('POST', 'homepage/solution/queryList', { headers: { 'content-type': null } });
    }

    modifyProfile(data) {
        return this.req('POST', 'user/modifyProfile', data)
    }

    modifyProfileInitially(data) {
        const names = [
            'Oliver',
            'Stephen',
            'Joe',
            'Joy',
            'Vanessa',
            'Candys',
            'Nick',
            'Bob',
            'Amanda',
            'Agata',
        ];
        const last_names = [
            'Stone',
            'Smith',
            'Jevirson',
            'Black',
            'White',
        ];
        let defaults = {
            'businessOnTiktok': 'No',
            'identity': 'None of the above',
            'companySize': '1-5',
            'firstName': names[randomnum(0, names.length)],
            'lastName': (Math.random() < 0.5 ? last_names[randomnum(0, last_names.length)] : ''),
        };
        return this.modifyProfile({ ...defaults, ...data });
    }

    modifyProfileSource(source = 'Others') {
        return this.modifyProfile({ source });
    }

    modifyProfilePassword(passwd = 'OsdKey0909') {
        return this.modifyProfile({ password });
    }

    overviewRankQueryProductsTops(pageNum, pageSize = 10) {
        return this.req('POST', 'overview/rank/queryProductTops', { body: { startDate: this.startDate, endDate: this.endDate, pageNo: pageNum, pageSize } });
    }

    overviewRankQueryCreatorsTops(pageNum, pageSize = 10) {
        return this.req('POST', 'overview/rank/queryCreatorTops', { body: { startDate: this.startDate, endDate: this.endDate, pageNo: pageNum, pageSize } });
    }

    overviewRankQueryShopsTops(pageNum, pageSize = 10) {
        return this.req('POST', 'overview/rank/queryShopTops', { body: { startDate: this.startDate, endDate: this.endDate, pageNo: pageNum, pageSize } });
    }

    overviewRankQueryVideoTops(pageNum, pageSize = 10) {
        return this.req('POST', 'overview/rank/queryVideoTops', { body: { startDate: this.startDate, endDate: this.endDate, pageNo: pageNum, pageSize } });
    }

    overviewRankQueryLiveTops(pageNum, pageSize = 10) {
        return this.req('POST', 'overview/rank/queryLiveTops', { body: { startDate: this.startDate, endDate: this.endDate, pageNo: pageNum, pageSize } });
    }

    creatorEnrich(ids, cateIds = null) {
        return this.req('POST', 'creator/enrich', { body: { ids, country: 'US', startDate: this.startDate, endDate: this.endDate, cateIds: cateIds || [] } });
    }

    shopEnrich(ids, cateIds = null) {
        return this.req('POST', 'shop/enrich', { body: { ids, country: 'US', startDate: this.startDate, endDate: this.endDate, cateIds: cateIds || [] } });
    }

    videoEnrich(ids, cateIds = null) {
        return this.req('POST', 'video/enrich', { body: { ids, country: 'US', startDate: this.startDate, endDate: this.endDate, cateIds: cateIds || [] } });
    }

    livestreamEnrich(ids, cateIds = null) {
        return this.req('POST', 'livestream/enrich', { body: { ids, country: 'US', startDate: this.startDate, endDate: this.endDate, cateIds: cateIds || [] } });
    }
}

class KalodataController {
    constructor() {
        this.kalodataInst = new Kalodata();
    }

    initialize() {
        this.kalodataInst.init();
        this.kalodataInst.startDate = this.kalodataInst.getJsonData(this.kalodataInst.getFirstDay());
        let lastDays = this.kalodataInst.getJsonData(this.kalodataInst.getAllLastDays());
        for (let country in lastDays) {
            if (country === 'US') {
                this.kalodataInst.endDate = lastDays[country];
                break;
            }
        }
    }
}

class Creator extends Request {
    constructor(_id, req) {
        super(req);
        this.id = _id;
        this.nickname = null;
        this.revenue = null;
        this.liveRevenue = null;
        this.videoRevenue = null;
        this.sale = null;
        this.followers = null;
        this.countCoopShops = null;
        this.history = [];
        this.metrics = {};
        this.contacts = {};
        this.collectDate = null;
        this.creatorType = null;
        this.creatorDebut = null;
        this.sellerId = null;
        this.productsCount = null;
        this.region = null;
        this.mainCategories = {};
        this.categories = {};
    }

    searchShopList() {
        return this.getJsonData(this.req('POST', 'creator/detail/searchShopList', { body: { authority: true, id: this.id, startDate: this.startDate, endDate: this.endDate } }));
    }

    countCooperativeShops(page = 1, psize = 10) {
        this.countCoopShops = this.getJsonData(this.req('POST', 'creator/detail/searchCooperativeShops/count', { body: { id: this.id, startDate: this.startDate, endDate: this.endDate, authority: true, pageNo: page, pageSize: psize, sort: [{ field: 'revenue', type: 'DESC' }] } }));
    }

    searchCooperativeShops(page = 1, psize = 10) {
        return this.getJsonData(this.req('POST', 'creator/detail/searchCooperativeShops', { body: { id: this.id, startDate: this.startDate, endDate: this.endDate, authority: true, pageNo: page, pageSize: psize, sort: [{ field: 'revenue', type: 'DESC' }] } }));
    }

    searchProducts(page = 1, psize = 10) {
        return this.getJsonData(this.req('POST', 'creator/detail/searchProducts', { body: { id: this.id, startDate: this.startDate, endDate: this.endDate, authority: true, pageNo: page, pageSize: psize, sort: [{ field: 'revenue', type: 'DESC' }] } }));
    }

    getHistory() {
        return this.getJsonData(this.req('POST', 'creator/detail/history/total', { body: { id: this.id, startDate: this.startDate, endDate: this.endDate, authority: true, cateIds: [], sellerId: '' } }));
    }

    getMetrics() {
        let res = this.getJsonData(this.req('POST', 'creator/detail/total', { body: { id: this.id, startDate: this.startDate, endDate: this.endDate, authority: true, cateIds: [], sellerId: '' } }));
        for (let key in res) {
            this.metrics[key] = convertNum(res[key])[1];
        }
    }

    getDetails() {
        let details = this.getJsonData(this.req('POST', 'creator/detail', { body: { id: this.id, startDate: this.startDate, endDate: this.endDate, authority: true, cateIds: [], sellerId: '' } })) || {};
        this.contacts = Object.fromEntries(Object.entries(details.creatorContent || {}).map(([key, val]) => [key, val || null]));
        this.collectDate = details.collect_day;
        this.creatorType = details.creator_type;
        this.creatorDebut = details.creatorDebut;
        this.sellerId = details.seller_id;
        this.nickname = details.nickname;
        this.productsCount = parseInt(details.products_count, 10) || 0;
        this.region = details.region;
        this.mainCategories = details.main_category;
        this.categories = {
            'pri': details.pri_cate_ids,
            'sec': details.sec_cate_ids,
            'ter': details.ter_cate_ids,
        };
    }
}

class Product extends Request {
    constructor(_id, req) {
        super(req);
        this.id = _id;
        this.conversionRatio = null;
        this.creatorsCount = null;
        this.relatedCreators = [];
        this.metrics = {};
        this.history = [];
        this.sellerId = null;
        this.title = null;
        this.prices = {};
        this.isAffiliate = null;
        this.isFullService = null;
        this.collectDate = null;
        this.commissionRate = null;
        this.creatorGmvConcentration = null;
        this.brandName = null;
    }

    getMetrics() {
        let res = this.getJsonData(this.req('POST', 'product/detail/total', { body: { authority: true, id: this.id, startDate: this.startDate, endDate: this.endDate } }));
        for (let key in res) {
            this.metrics[key] = convertNum(res[key])[1];
        }
    }

    getHistory() {
        this.history = this.getJsonData(this.req('POST', 'product/detail/history', { body: { authority: true, id: this.id, startDate: this.startDate, endDate: this.endDate } }));
    }

    getDetails() {
        let details = this.getJsonData(this.req('POST', 'product/detail', { body: { authority: true, id: this.id, startDate: this.startDate, endDate: this.endDate } }));
        this.sellerId = details.seller_id || null;
        this.title = details.product_title || null;
        this.prices = {
            'max_original_price': details.max_original_price || null,
            'max_real_price': details.max_real_price || null,
            'min_in_30_price': details.min_in_30_price || null,
            'min_original_price': details.min_original_price || null,
            'min_real_price': details.min_real_price || null,
            'unit_price': details.unit_price || null,
        };
        this.isAffiliate = details.is_affiliate !== undefined ? Boolean(details.is_affiliate) : null;
        this.isFullService = details.is_full_service !== undefined ? Boolean(details.is_full_service) : null;
        this.collectDate = details.collect_day || null;
        this.commissionRate = details.commission_rate === '-' ? null : details.commission_rate;
        this.creatorGmvConcentration = details.creator_gmv_concentration || null;
        this.brandName = details.brand_name || null;
    }

    getConversionRatio() {
        let res = this.getJsonData(this.req('POST', 'product/detail/creator/g', { body: { authority: true, id: this.id, startDate: this.startDate, endDate: this.endDate } }));
        this.conversionRatio = res.conversion_ratio;
    }
}

