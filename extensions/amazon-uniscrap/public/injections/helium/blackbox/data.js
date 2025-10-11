function getBearerToken(userId) {
    return JSON.parse(localStorage.getItem('CORE_BEARER_TOKEN'))[String(userId)];
}

function getPacvueToken(userId) {
    return JSON.parse(localStorage.getItem('PACVUE_TOKENS'))[String(userId)].pacvueToken;
}

function getMarketplaces() {
    return {
        'amazon.com': 1,
        'amazon.ca': 2,
        'amazon.com.mx': 3,
        'amazon.de': 4,
        'amazon.es': 5,
        'amazon.fr': 6,
        'amazon.it': 7,
        'amazon.co.uk': 8,
        'amazon.in': 9,
        'amazon.co.jp': 10,
        'amazon.com.br': 12,
        'amazon.com.au': 14,
        'amazon.nl': 15,
        'amazon.ae': 17,
    }
}

function getMarketplaceId(marketplaceDomain) {
    return getMarketplaces()[marketplaceDomain];
}

async function getRootCategories({ userId, bearerToken, pacvueToken }, marketplaceId = 1) {
    const result = await fetch(`https://h10api.pacvue.com/rta/blackbox/v1/categories?accountId=${userId}&marketplaceId=${marketplaceId}`, {
        'headers': {
            'accept': 'application/json',
            'authorization': `Bearer ${bearerToken}`,
            'content-type': 'application/json',
            'x-pacvue-token': `Bearer ${pacvueToken}`,
        },
        'referrer': 'https://members.helium10.com/',
        'method': 'GET',
    });

    if (result.status !== 200)
        return null;

    const { data } = await result.json();

    return data.map(item => {
        return { [item.id]: item.nodeName };
    });
}

async function getChildrenCategories({ userId, bearerToken, pacvueToken }, parentId) {
    const result = await fetch(`https://h10api.pacvue.com/rta/blackbox/v1/categories/${parentId}/children?accountId=${userId}`, {
        'headers': {
            'accept': 'application/json',
            'content-type': 'application/json',
            'authorization': `Bearer ${bearerToken}`,
            'x-pacvue-token': `Bearer ${pacvueToken}`,
        },
        'referrer': 'https://members.helium10.com/',
        'method': 'GET',
    });

    if (result.status !== 200)
        return null;

    const { data } = await result.json();

    return data.map(item => {
        return { [item.id]: item.nodeName };
    });
}

async function startSearch({ userId, bearerToken, pacvueToken }, categoryIds, marketplaceId = 1) {
    const result = await fetchWithRetry(`https://h10api.pacvue.com/rta/blackbox/v1/search/products?accountId=${userId}`, {
        'headers': {
            'accept': 'application/json',
            'authorization': `Bearer ${bearerToken}`,
            'content-type': 'application/json',
            'x-pacvue-token': `Bearer ${pacvueToken}`,
        },
        'referrer': 'https://members.helium10.com/',
        'body': JSON.stringify({
            'productCodes': [],
            'filters': { 'category': categoryIds.map(item => String(item)) },
            'marketplaceId': marketplaceId,
            'filtersType': 'advanced',
        }),
        'method': 'POST',
    });

    if (result.status !== 200)
        return null;

    const { data } = await result.json();

    return data.id;
}

async function getPaginatedResult({ userId, bearerToken, pacvueToken }, searchId) {
    const result = await fetchWithRetry(`https://h10api.pacvue.com/rta/blackbox/v1/search/products/${searchId}/results?accountId=${userId}&page=1&per_page=100`, {
        'headers': {
            'accept': 'application/json',
            'authorization': `Bearer ${bearerToken}`,
            'content-type': 'application/json',
            'x-pacvue-token': `Bearer ${pacvueToken}`,
        },
        'referrer': 'https://members.helium10.com/',
        'method': 'GET',
    });

    if (result.status !== 200)
        return null;

    const { data } = await result.json();

    return data;
}

async function getResult({ userId, bearerToken, pacvueToken }, searchId) {
    const result = await fetchWithRetry(`https://h10api.pacvue.com/rta/blackbox/v1/search/products/${searchId}/export?accountId=${userId}`, {
        'headers': {
            'accept': 'application/json',
            'authorization': `Bearer ${bearerToken}`,
            'content-type': 'application/json',
            'x-pacvue-token': `Bearer ${pacvueToken}`,
        },
        'referrer': 'https://members.helium10.com/',
        'method': 'GET',
    });

    if (result.status !== 200)
        return null;

    const { data } = await result.json();

    return data;
}

async function getCategoryDetails({ userId, bearerToken, pacvueToken }, categoryId) {
    const result = await fetch(`https://h10api.pacvue.com/rta/blackbox/v1/categories/${categoryId}?accountId=${userId}`, {
        'headers': {
            'accept': 'application/json',
            'authorization': `Bearer ${bearerToken}`,
            'content-type': 'application/json',
            'x-pacvue-token': `Bearer ${pacvueToken}`,
        },
        'referrer': 'https://members.helium10.com/',
        'method': 'GET',
    });

    if (result.status !== 200) {
        return null;
    }

    const { data } = await result.json();
    return data;
}
