/**
 * Depends on pagination and parseCurrency commons
*/

function waitForInjectAndGetTheData(elem = null) {
    if (!elem) elem = document.getElementsByClassName('s-result-list')[0];
    const items = elem.querySelectorAll('[role="listitem"]');

    return new Promise((resolve, reject) => {
        const timeout = setTimeout(reject, 15000);

        // Resolve function
        function finish() {
            clearTimeout(timeout);
            setTimeout(resolve, 100, data);
        }

        let data = {};

        let left = items.length;
        for (const item of items) {
            const data_asin = item.getAttribute('data-asin');
            if (!data_asin) {
                // Bad element
                --left;
                continue;
            }

            const mo = new MutationObserver((records, observer) => {
                if (!observer.stage) {
                    // waiting injection
                    if (!item.querySelector('[id*="jsSearchEmbed"]')) return console.log('noJS');
                    observer.stage = 1;
                } else if (observer.stage === 1) {
                    // waiting loading
                    if (item.querySelector('[class*="LoadingPlaceholder"]')) {
                        return;  // Loading...
                    }
                    // Element finished
                    --left;
                    mo.disconnect();
                    data[data_asin] = { asin: data_asin, ...getProductBaseData(item) };
                    // setTimeout((i) => console.log(i.cloneNode(true)), 100, item);
                    if (left <= 0) finish();
                }
            });
            if (item.querySelector('[id*="jsSearchEmbed"]')) {
                if (item.querySelector('[class*="LoadingPlaceholder"]')) {
                    mo.stage = 1;  // Observing only loading
                } else {
                    // Element already loaded
                    --left;
                    data[data_asin] = { asin: data_asin, ...getProductBaseData(item) };
                    continue;
                }
            }
            // Observe
            mo.observe(item, { childList: true, subtree: true });
        }
        if (left <= 0) finish();
    });
}

function getProductBaseData(item) {
    let q = 0;  // Turing Machine condition
    let result = {
        reviewsCount: 0,
        rating: null,
        moRevenue: null,
    };
    const reviewsInfo = item.querySelector('[data-cy="reviews-block"] > div')?.textContent.split(' ') || [];
    let endFor = false;

    for (let i = 0, nod = reviewsInfo[i]; i < reviewsInfo.length; ++i, nod = reviewsInfo[i]) {
        if (!nod || !/^[0-9,. ]+$/.test(nod)) continue;
        switch (q) {
            case 0:
                result.rating = Number(nod.replaceAll(' ', ''));
                q = 1;
                break;
            case 1:
                q = 2;
                break;
            case 2:
                result.reviewsCount = Number(nod.replaceAll(/[, ]/g, ''));
                endFor = true;
                break;
        }
        if (endFor) break;
    }

    const jsDataSection = item.querySelectorAll('[id*="jsSearchEmbed"] > [class*="EmbedBase"] > [class*="DataSection"] > [class^="Flex"]');
    let moRevenue = null;
    for (const jsDataSectionElement of jsDataSection) {
        if (jsDataSectionElement.children[0]?.textContent.trim().startsWith('Mo. Revenue')) {
            moRevenue = jsDataSectionElement.children[1]?.textContent.trim();
            if (moRevenue) {
                result.moRevenue = moRevenue.includes('--') ? null : parseNumber(jsDataSectionElement.children[1]?.textContent.trim())[1];
            }
            break;
        }
    }

    return result;
}

async function getTheDataWithPagination() {
    let data = {};
    do {
        await new Promise((resolve, reject) => {
            let i = 0;
            const interval = setInterval(() => {
                if (document.querySelector('.s-result-list-placeholder.sg-row.aok-hidden')) {
                    clearInterval(interval);
                    return resolve();
                }
                ++i;
                if (i > 20) return reject();
            }, 500);
        });
        data = {...await waitForInjectAndGetTheData(), ...data};
    } while (Object.keys(data).length < 10000 && await waitAndClickToNextPage(1000));
    return data;
}
