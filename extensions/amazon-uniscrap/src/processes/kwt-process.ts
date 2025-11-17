import browser from 'webextension-polyfill';

type Result = {
    empty: boolean,
    result: ResultItem[],
};

type ResultItem = {
    asin: string,
    title?: string,
    score?: number,
    image?: string,
    bestSellerIn?: string,
    isSponsored?: boolean,
    price?: number,
    itemPrice?: number,
    oldPrice?: number,
    subscriptionDiscount?: number,
    subscriptionDiscountPercents?: number,
};

type TaskConfig = {
    searchQuery: string;
    pagesLimit?: number;
    itemsLimit?: number;
    timeLimit?: number;
    asins?: string[];
    destination: 'local' | 'remote';
};

export async function KWTProcess(task: TaskConfig): Promise<void> {
    const result: Result = await kwtProcess(task);

    if (task.destination === 'local') {
        const binString = Array.from(new TextEncoder().encode(JSON.stringify(result.result)), (byte) =>
            String.fromCodePoint(byte),
        ).join("");

        await browser.downloads.download({
            url: 'data:application/json;base64,' + btoa(binString),
            filename: 'resultKWT.json',
            saveAs: true,
        });
    }
}

async function kwtProcess(task: TaskConfig): Promise<Result> {
    const tab = await browser.tabs.create({
        url: encodeURI('https://www.amazon.com/s?k=' + task.searchQuery).replaceAll('#', '%23'),
        active: false,
    });
    if (!tab || !tab.id) throw new Error(`Unable to process task: no tab found (${JSON.stringify(task)})`);
    await browser.tabs.update(tab.id, {
        autoDiscardable: false,
    });

    try {
        await browser.scripting.executeScript({
            target: { tabId: tab.id },
            files: [
                'injections/common/parseImageURL.js',
                'injections/common/parseCurrency.js',
                'injections/common/wait.js',
                'injections/common/pagination.js',
                'injections/kwt/callbackFactories.js',
                'injections/kwt/parsePage.js',
            ],
        });
    } catch (e) {
        await browser.tabs.remove(tab.id);
        throw new Error(`Unable to process task: can't inject files due to ${e} (${JSON.stringify(task)})`);
    }
    let result;
    for (let i = 0; !result && i < 10; ++i) {
        result = (await browser.scripting.executeScript({
            target: { tabId: tab.id },
            args: [task.searchQuery || null, task.pagesLimit || null, task.itemsLimit || null, task.timeLimit || null, task.destination === 'local', task.asins || null],
            func: async (sq, pagesLimit, itemsLimit, timeLimit, saveAll, asins) => {
                /** @ts-ignore */
                return await parseAll({ pagesLimit, itemsLimit, timeLimit, asins }, {}, saveAll ? {} : {
                    /** @ts-ignore */
                    perPageCallback: createPerPageCallback(sq),
                    /** @ts-ignore */
                    onErrorCallback: createErrorCallback(sq),
                }, 100, saveAll);
            },
        }))[0]?.result;
    }
    await browser.tabs.remove(tab.id);
    if (!result) throw new Error(`Error while processing task: too many errors (${JSON.stringify(task)})`);
    return result;
}
