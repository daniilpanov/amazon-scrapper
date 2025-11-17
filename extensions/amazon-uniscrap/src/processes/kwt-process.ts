import browser, { Tabs } from 'webextension-polyfill';
import Tab = Tabs.Tab;

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
    if (task.asins && !task.asins.length)
        task.asins = undefined;

    const tab = await browser.tabs.create({
        url: encodeURI('https://www.amazon.com/s?k=' + task.searchQuery).replaceAll('#', '%23'),
        active: false,
    });

    if (!tab?.id)
        throw new Error(`Unable to create a tab: unknown error (${JSON.stringify(task)})`);

    let timeout;

    try {
        // timeLimit + 1000 because the same timeout will be inside a tab
        if (task.timeLimit)
            timeout = setTimeout(browser.tabs.remove, task.timeLimit + 1000, tab.id);

        const result: Result = await kwtProcess(task, tab);

        if (task.destination === 'local') {
            const binString = Array.from(new TextEncoder().encode(JSON.stringify(result.result)), byte =>
                String.fromCodePoint(byte),
            ).join("");

            await browser.downloads.download({
                url: 'data:application/json;base64,' + btoa(binString),
                filename: 'resultKWT.json',
                saveAs: true,
            });
        }
    } finally {
        if (timeout)
            clearTimeout(timeout);

        await browser.tabs.remove(tab.id);
    }
}

async function kwtProcess(task: TaskConfig, tab: Tab): Promise<Result> {
    if (!tab.id)
        throw new Error(`Unable to process task: no tab found (${JSON.stringify(task)})`);

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
        throw new Error(`Unable to process task: can't inject files due to ${e} (${JSON.stringify(task)})`);
    }

    tab = await browser.tabs.get(tab.id);
    if (!tab || !tab.id)
        throw new Error(`Unable to process task: no tab found (${JSON.stringify(task)})`);

    if (!tab.url?.includes('/s?k='))
        throw new Error(`Unable to process task: redirect occurred to ${tab.url} (${JSON.stringify(task)})`);

    const result = (await browser.scripting.executeScript({
        target: { tabId: tab.id },
        args: [
            task.searchQuery,
            task.pagesLimit || null,
            task.itemsLimit || null,
            task.timeLimit || null,
            task.destination === 'local',
            task.asins || null,
        ],
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

    if (!result)
        throw new Error(`Error while processing task: an unknown error occurred (${JSON.stringify(task)})`);

    return result;
}
