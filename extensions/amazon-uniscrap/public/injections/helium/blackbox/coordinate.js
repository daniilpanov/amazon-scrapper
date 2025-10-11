function extractTokens(userId) {
    return {
        bearerToken: getBearerToken(userId),
        pacvueToken: getPacvueToken(userId),
    };
}

async function getCategories(level, marketplaceId, userConfig) {
    const root = categoriesToObject(await getRootCategories(userConfig, marketplaceId));
    --level;
    let currCats = root;
    for (let i = 0; i < level; ++i) {
        let currRes = {};
        for (const currCatId in currCats) {
            const part = categoriesToObject(await getChildrenCategories(userConfig, currCatId));
            currRes = { ...currRes, ...part };
        }
        currCats = currRes;
    }
    return currCats;
}

async function getCategoriesRecursive(userConfig, parentId = null, level = 0) {
    let categoriesData;
    if (parentId === null) {
        categoriesData = await getRootCategories(userConfig);
    } else {
        categoriesData = await getChildrenCategories(userConfig, parentId);
    }

    if (!categoriesData) {
        return {};
    }

    const categories = categoriesToObject(categoriesData);
    let result = { ...categories };

    for (const categoryId in categories) {
        const categoryDetails = await getCategoryDetails(userConfig, categoryId);

        if (categoryDetails && categoryDetails.hasChildren) {
            const childCategories = await getCategoriesRecursive(
                userConfig,
                categoryId,
                level + 1,
            );
            result = { ...result, ...childCategories };
        }
    }

    return result;
}

async function waitForResponse(userConfig, searchId, duration = 1000, retries = 5) {
    let data = null;
    while (!data && (--retries) >= 0) {
        await new Promise(r => setTimeout(r, duration));
        data = await getPaginatedResult(userConfig, searchId);
    }
    return data;
}

async function exportCategoriesData(catIds, userConfig, domain, marketplaceId) {
    const searchId = await startSearch(userConfig, catIds, marketplaceId);

    if (!await waitForResponse(userConfig, searchId))
        return [];

    await new Promise(r => setTimeout(r, 500));
    const data = await getResult(userConfig, searchId);

    return data.map(el => mapProductData(el, domain));
}

function executeParallelQueries(catIdsChunk, userConfig, domain, marketplaceId, chunkCallback) {
    const coroutines = [];

    for (const catId of catIdsChunk)
        coroutines.push(exportCategoriesData(
            [catId],
            userConfig,
            domain,
            marketplaceId,
        ).then(chunkCallback));

    return Promise.all(coroutines);
}

function chunkCatIds(catIds, parallelQueries) {
    const chunks = [];
    for (let i = 0; i < catIds.length; i += parallelQueries)
        chunks.push(catIds.slice(i, i + parallelQueries));
    return chunks;
}

async function processAll(domain, userId, level, chunkCallback, parallelQueries = 3) {
    const marketplaceId = getMarketplaceId(domain) ?? 1;

    const userConfig = {
        userId, ...extractTokens(userId),
    };

    const catIds = await getCategories(level, marketplaceId, userConfig);
    const chunkedCatIds = chunkCatIds(Object.keys(catIds), parallelQueries);

    for (const catIdChunk of chunkedCatIds) {
        await executeParallelQueries(catIdChunk, userConfig, domain, marketplaceId, chunkCallback);
        await new Promise(r => setTimeout(r, 500));
    }
}
