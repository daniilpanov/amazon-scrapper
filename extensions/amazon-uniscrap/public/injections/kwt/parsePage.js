async function wait(repeats, delay, func) {
    let res = func();
    for (let i = 0; i <= repeats && !res; ++i, res = func())
        await new Promise(resolve => setTimeout(resolve, delay));

    return res;
}

function checkIsLoaded(maxRetriesFallback, maxRetriesLoading) {
    const x = function () {
        const count = document.querySelectorAll('[data-asin]').length;

        if (count) {
            if (count > x.current) {
                x.retries = 0;
                x.current = count;
            } else if (x.retries > x.maxRetriesLoading)
                return true;
            else
                ++x.retries;
        } else if (++x.retries > maxRetriesFallback)
            throw new Error('Error: limit of maxRetriesFallback reached!');
    };
    x.current = 0;
    x.retries = 0;
    x.maxRetriesFallback = maxRetriesFallback;
    x.maxRetriesLoading = maxRetriesLoading;
    return x;
}

function parseItem(card) {
    const asin = card.getAttribute('data-asin');
    if (!asin)
        return null;

    const title = card.querySelector('h2 > span')?.textContent || card.querySelector('[data-type="productTitle"]')?.textContent || card.querySelector('div > a > span > .a-offscreen')?.textContent || null;
    const score = Number(card.querySelector('a i span')?.textContent.trim().split(' ')[0] || 0) || Number(card.querySelector('[data-type="productReviews"]')?.getAttribute('aria-label')?.trim().split(' ')[1] || 0);
    let image = card.getElementsByTagName('img')[0]?.getAttribute('src');
    if (image) image = unifyImageURL(image);

    const bought_count = parseNumber(card.querySelector('[data-cy="reviews-block"] span.a-color-secondary:last-child')?.textContent?.split(' ', 1)?.[0]?.trim())[1];

    const bestSellerIn = card.querySelector('[id="' + asin + '-best-seller-supplementary"]')?.textContent.trim().split(' ').slice(1).join(' ');

    let isSponsored = Boolean(card.querySelector('[aria-label="View Sponsored information or leave ad feedback"]'));
    if (!isSponsored) {
        const parentBlock = card.parentElement.closest('[data-asin]');
        if (!parentBlock?.getAttribute('data-asin'))
            isSponsored = !!parentBlock?.querySelector('[data-form-header-text="Leave feedback"]')
                || !!parentBlock?.querySelector('[data-action="multi-ad-feedback-form-trigger"]');
    }

    const [price, itemPrice, oldPrice] = [
        ...card.querySelectorAll('[data-cy="price-recipe"] a > *')
    ].map(item =>
        parseNumber(item.querySelector('.a-offscreen')?.textContent)[1]
    );

    const [subscrDEl, subscrDPEl] = card.querySelector('[data-cy="price-recipe"]')
        ?.children[1]
        ?.querySelectorAll('.a-row > span')
    || [];

    const subscriptionDiscount = parseNumber(
        subscrDEl?.textContent.match(/\$[0-9.]+/)?.[0]
        || null,
    )[1];

    const subscriptionDiscountPercents = parseNumber(
        subscrDPEl?.textContent.match(/[0-9.]+%/)?.[0]
        || null,
    )[1];

    return {
        asin,
        title,
        score,
        image,
        bought_count,
        bestSellerIn,
        isSponsored,
        price,
        itemPrice,
        oldPrice,
        subscriptionDiscount,
        subscriptionDiscountPercents,
    };
}

async function parsePage(
    productsPage,
    { perItemCallback, itemFilterCallback } = {},
    { countSponsored, countOrganic } = { countSponsored: 0, countOrganic: 0 },
    asins = undefined,
) {
    const date = new Date();
    const elements = productsPage.querySelectorAll('& > [data-asin]');
    const parsedData = [];

    for (const element of elements) {
        element.scrollIntoView();

        const item = parseItem(element);
        if (!item)
            continue;

        if (asins && asins.has(item.asin))
            asins.delete(item.asin);

        item.date = date.toISOString();

        if (item.isSponsored)
            ++countSponsored;
        else
            ++countOrganic;

        if (itemFilterCallback && !itemFilterCallback(item))
            continue;

        if (perItemCallback)
            await perItemCallback(item);

        parsedData.push(item);
    }

    return { co: countOrganic, cs: countSponsored, res: parsedData, remainingAsins: asins };
}

async function parseAll(
    { pagesLimit, itemsLimit, timeLimit, asins } = {},
    { itemFilterCallback } = {},
    { perItemCallback, perPageCallback, onErrorCallback } = {},
    clickDelay = null,
    saveAll = false,
) {
    let stop = false;
    let countItems = 0;
    let countPages = 0;
    // time limit
    const timerTimeLimit = timeLimit ? setTimeout(() => stop = true, timeLimit) : null;
    // for correct chunking
    let countSponsored = 0;
    let countOrganic = 0;
    if (asins)
        asins = new Set(asins);

    const result = { empty: !saveAll, result: [] };

    try {
        while (
            !stop &&
            (!itemsLimit || countItems < itemsLimit) &&
            (!pagesLimit || countPages < pagesLimit)
        ) {
            await wait(40, 200, checkIsLoaded(20, 3));

            const { cs, co, res, remainingAsins } = await parsePage(
                document.querySelector('.s-main-slot'),
                { perItemCallback, itemFilterCallback },
                { countSponsored, countOrganic },
                asins,
            );

            if (perPageCallback)
                await perPageCallback({ countSponsored, countOrganic, res });

            countSponsored += cs;
            countOrganic += co;
            countItems += res.length;
            ++countPages;

            if (saveAll)
                for (const item of res)
                    result.result.push(item);

            if (remainingAsins && !remainingAsins.size)
                break;

            asins = remainingAsins;

            if (!await waitAndClickToNextPage())
                break;

            await new Promise(resolve => setTimeout(resolve, clickDelay));
        }
    } catch (e) {
        if (onErrorCallback)
            await onErrorCallback(e);
    }

    if (timerTimeLimit)
        clearTimeout(timerTimeLimit);

    return result;
}
