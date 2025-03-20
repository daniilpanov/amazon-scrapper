function convertNum(num) {
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

class Entity {
    detailPath = 'detail';
    historyPath = 'detail/history';
    metricsPath = 'detail/total';

    entityName;
    collectDate = null;
    additionalFilters;
    additionalSelfFilters;
    additionalHistoryFilters;
    additionalHeaders;
    details;
    history;
    metrics;
    relationships;
    other;
    dtc;
    relationshipsOptions;
    otherOptions;

    constructor(_id, entityName, dtc, {
        filters,
        selfFilters,
        historyFilters,
        headers,
    } = {}, relationships = null, items = null, customPaths = null) {
        this.id = _id;
        this.details = {};
        this.history = {};
        this.metrics = {};
        this.additionalFilters = filters ?? this.additionalFilters ?? { authority: true };
        this.additionalSelfFilters = selfFilters ?? this.additionalSelfFilters ?? { ...this.additionalFilters };
        this.additionalHistoryFilters = historyFilters ?? this.additionalHistoryFilters ?? { ...this.additionalFilters };
        this.additionalHeaders = headers ?? this.additionalHeaders ?? { country: 'US', currency: 'USD' };
        this.entityName = entityName;
        this.dtc = dtc;
        this.relationships = {};
        this.other = {};
        this.relationshipsOptions = this.relationshipsOptions ?? {};
        this.otherOptions = this.otherOptions ?? {};

        for (const item in (items || [])) {
            this.other[item] = {};
            this.otherOptions[item] = items[item];
        }
        for (const relationship in (relationships || [])) {
            this.relationships[relationship] = [];
            this.relationshipsOptions[relationship] = relationships[relationship];
        }

        for (const key in (customPaths || {})) {
            this[key] = customPaths[key];
        }
    }

    async getMetrics() {
        try {
            let res = (await (await fetch('https://www.kalodata.com/' + this.entityName + '/' + this.metricsPath, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.additionalHeaders,
                },
                body: JSON.stringify({
                    id: this.id,
                    startDate: getDateShift(this.dtc.endDate, 29),
                    endDate: this.dtc.endDateStr,
                    ...this.additionalFilters,
                    ...this.additionalSelfFilters,
                }),
            })).json())?.data || {};
            for (let key in res) {
                if (res[key] && typeof res[key] === 'string') {
                    this.metrics[key] = convertNum(res[key])[1];
                } else {
                    this.metrics[key] = res[key];
                }
            }
        } catch (err) {
        }
    }

    async getDetails() {
        const res = (await (await fetch('https://www.kalodata.com/' + this.entityName + '/' + this.detailPath, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...this.additionalHeaders,
            },
            body: JSON.stringify({
                id: this.id,
                startDate: getDateShift(this.dtc.endDate, 29),
                endDate: this.dtc.endDateStr,
                ...this.additionalFilters,
                ...this.additionalSelfFilters,
            }),
        })).json())?.data || {};

        for (let key in res) {
            this.details[key] = res[key];
            if (res[key] && typeof res[key] === 'string') {
                this.details[key] = res[key].trim() || null;
                if (this.details[key][0] === '$' || ['%', 'k', 'm', 'b'].includes(this.details[key][this.details[key].length - 1].toLowerCase())) {
                    const converted = convertNum(res[key]);
                    if (converted[1]) {
                        this.details[key + (converted[0] || '')] = converted[1];
                        delete this.details[key];
                    }
                } else if (/^[0-9.]+$/.test(this.details[key])) {
                    this.details[key] = Number(this.details[key]);
                }
            }
        }
    }

    async getHistory() {
        this.history = (await (await fetch('https://www.kalodata.com/' + this.entityName + '/' + this.historyPath, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...this.additionalHeaders,
            },
            body: JSON.stringify({
                id: this.id,
                startDate: getDateShift(this.dtc.endDate, 29),
                endDate: this.dtc.endDateStr,
                ...this.additionalFilters,
                ...this.additionalSelfFilters,
                ...this.additionalHistoryFilters,
            }),
        })).json()).data || [];
    }

    async getRelationshipsSpecial(relationName, path) {
        const { headers = {}, filters = {} } = this.relationshipsOptions[relationName] || {};
        const res = (await (await fetch('https://www.kalodata.com/' + this.entityName + '/' + path, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...this.additionalHeaders,
                ...headers,
            },
            body: JSON.stringify({
                id: this.id,
                startDate: getDateShift(this.dtc.endDate, 29),
                endDate: this.dtc.endDateStr,
                ...this.additionalFilters,
                ...filters,
            }),
        })).json()).data || {};

        if (!Object.keys(res).length) return false;

        if (!this.relationships[relationName]) {
            this.relationships[relationName] = [];
        }
        let colsMapping = {};
        for (let row of res) {
            row = this.convertAll(row);
            this.relationships[relationName].push(row[0]);
            colsMapping = { ...colsMapping, ...row[1] };
        }
        this.replaceKeys(this.relationships, relationName, colsMapping);
        return true;
    }

    convertAll(row) {
        const excludedCols = new Set(['duration', 'title']);
        const colsMapping = {};

        for (let key in row) {
            if (!row[key]) continue;
            if (typeof row[key] === 'string') {
                row[key] = row[key].trim() || null;
                if (!excludedCols.has(key) && /^\$?[0-9.]+[%kmb]?$/.test(row[key].toLowerCase()) && (row[key][0] === '$' || ['%', 'k', 'm', 'b'].includes(row[key][row[key].length - 1].toLowerCase()))) {
                    const converted = convertNum(row[key]);
                    if (converted[1] !== null) {
                        if (converted[0]) {
                            row[key + converted[0]] = converted[1];
                            delete row[key];
                            colsMapping[key] = key + converted[0];
                        } else {
                            row[key] = converted[1];
                        }
                    }
                } else if (/^[0-9.]+$/.test(row[key])) {
                    row[key] = Number(row[key]);
                }
            } else if (row[key].length) {
                const r = [];
                for (let i of row[key]) {
                    if (typeof i === 'object') r.push(this.convertAll(i)[0]);
                    else r.push(i)
                }
                row[key] = r;
            } else if (typeof row[key] === 'object') {
                row[key] = this.convertAll(row[key])[0];
            }
        }

        return [row, colsMapping];
    }

    replaceKeys(arr, key, colsMapping) {
        const newData = [];
        for (let row of arr[key]) {
            for (const key in row) {
                if (key in colsMapping) {
                    row[colsMapping[key]] = row[key];
                    delete row[key];
                }
            }
            newData.push(row);
        }
        arr[key] = newData;
    }

    async getRelationships({ relationName, postfix = 'queryList' }, { page = 1, pgsize = 10 } = {}, count = false) {
        const { headers = {}, filters = {} } = this.relationshipsOptions[relationName] || {};
        const res = (await (await fetch('https://www.kalodata.com/' + this.entityName + '/detail/' + relationName + '/' + (count ? 'count' : postfix), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...this.additionalHeaders,
                ...headers,
            },
            body: JSON.stringify({
                id: this.id,
                startDate: getDateShift(this.dtc.endDate, 29),
                endDate: this.dtc.endDateStr,
                sort: [{ field: 'revenue', type: 'DESC' }],
                pageNo: page,
                pageSize: pgsize,
                ...this.additionalFilters,
                ...filters,
            }),
        })).json()).data || {};

        if (count) {
            return res;
        }

        if (!Object.keys(res).length) return false;

        if (!this.relationships[relationName]) {
            this.relationships[relationName] = [];
        }
        let colsMapping = {};
        for (let row of res) {
            row = this.convertAll(row);
            this.relationships[relationName].push(row[0]);
            colsMapping = { ...colsMapping, ...row[1] };
        }
        this.replaceKeys(this.relationships, relationName, colsMapping);
        return true;
    }

    async getOther({ otherPath, otherKey = otherPath }, params) {
        params = { ...(this.otherOptions[otherKey] || {}), ...(params || {}) };
        if (!params.body) {
            params.body = {};
        }
        const keys = Object.keys(params.body);
        if (!keys.includes('id')) {
            params.body.id = this.id;
        }
        if (!keys.includes('endDate')) {
            params.body.endDate = this.dtc.endDateStr;
        }
        if (!keys.includes('startDate')) {
            params.body.startDate = getDateShift(this.dtc.endDate, 29);
        }
        const res = (await (await fetch('https://www.kalodata.com/' + this.entityName + '/' + otherPath, {
            method: params.method || 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...this.additionalHeaders,
                ...(params.headers || {}),
            },
            body: JSON.stringify(params.body),
        })).json()).data || {};

        if (!Object.keys(res).length) return false;

        this.other[otherKey] = this.convertAll(res)[0];
    }

    async paginate(func, args, pageData, pagesLimit = null) {
        pageData.pgsize = pageData.pgsize ?? 10;
        const count = await func(...args, true);
        for (let i = 0; i < count && (!pagesLimit || pageData.page < pagesLimit); i += pageData.pgsize, ++pageData.page) {
            const res = await func(...args);
            if (!res) break;
            await new Promise(resolve => setTimeout(resolve, 100));
        }
    }

    async getAllRelationships() {
        for (const relationship in this.relationshipsOptions) {
            if (this.relationshipsOptions[relationship].special) {
                await this.getRelationshipsSpecial(relationship, this.relationshipsOptions[relationship].path);
            } else {
                const args = [{
                    relationName: relationship,
                    postfix: this.relationshipsOptions[relationship].postfix ?? 'queryList',
                }, { page: 1, pgsize: 10 }];
                const pageArgs = args[1];
                await this.paginate(this.getRelationships.bind(this), args, pageArgs, 10);
            }
        }
    }

    async getAllOther() {
        for (const other in this.otherOptions) {
            await this.getOther({
                otherPath: this.otherOptions[other].path ?? other,
                otherKey: other,
            }, this.otherOptions[other]);
        }
    }
}

function createProduct(id, dtc) {
    return new Entity(id, 'product', dtc, {}, {
        creator: {},
        video: {},
        live: {},
    }, {
        conversionRatio: { path: 'detail/creator/getConversionRadio' },
    });
}

function createCreator(id, dtc) {
    return new Entity(id, 'creator', dtc, {
        filters: {
            cateIds: [],
            sellerId: '',
        },
    }, {
        searchShopList: { special: true, path: 'detail/searchShopList' },
        searchCooperativeShops: { postfix: '' },
        live: {},
        video: {
            body: {
                'videoType': '',
                'video.filter.ad.view_ratio': '',
                'video.filter.ad.revenue_ratio': '',
                'video.filter.ad.daily_cost': '',
                'video.filter.ad.daily_roas': '',
            },
        },
        searchProducts: { postfix: '' },
    });
}

function createVideo(id, dtc) {
    return new Entity(id, 'video', dtc, {
        historyFilters: { productId: '' },
    }, {
        products: { special: true, path: 'detail/stat/queryProductList' },
    }, {
        similarVideos: { path: 'detail/similar/revenue' },
    }, {
        metricsPath: 'a/detail/total',
        historyPath: 'detail/stat/queryProductStat',
    });
}

function createShop(id, dtc) {
    return new Entity(id, 'shop', dtc, {
        filters: {
            cateIds: [],
        },
    }, {
        searchCooperativeCreators: {
            postfix: '',
            filters: { creatorType: '' },
        },
        product: { filters: { productType: '' } },
        searchLives: {
            postfix: '',
            filters: { creatorType: '' },
        },
        searchVideos: {
            postfix: '',
            filters: { videoType: '', creatorNickName: '' },
        },
        searchNewProducts: {
            special: true,
            path: 'detail/searchNewProducts',
            filters: {
                pageNo: 1,
                pageSize: 5,
                sort: [{ 'field': 'revenue', 'type': 'DESC' }],
            },
        },
    }, {
        selfPromotion: { path: 'detail/salesStrategy/selfPromotion' },
        affiliate: { path: 'detail/salesStrategy/affiliate' },
        extraTotal: {
            path: 'detail/extraTotal',
            body: {
                cateIds: [],
                historyEndDate: dtc.endDateStr,
                historyStartDate: getDateShift(dtc.endDate, 29),
            },
        },
    });
}
