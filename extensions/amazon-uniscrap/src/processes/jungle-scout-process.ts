import browser from 'webextension-polyfill';

type Result = {
    [key: string]: {
        rating?: number,
        reviewsCount?: number,
        moRevenue?: number,
    }
};

type TaskConfig = {
    startURL?: string;
    searchRequests?: string[];
    tabId?: number;
    pagination?: boolean;
    filters?: {
        [key: string]: string | number | boolean;
    };
    destination: 'local' | 'remote';
};

export async function jungleScoutProcess(task: TaskConfig): Promise<void> {
    let result: Result = {};
    if (!task.searchRequests) {
        result = await jungleScoutSingleProcess(task);
    } else {
        for (const request of task.searchRequests) {
            task.startURL = `https://amazon.com/s?k=${request.replaceAll(' ', '+')}`;
            result = { ...await jungleScoutSingleProcess(task), ...result };
        }
    }

    if (task.destination === 'remote') {
        return jungleScoutRemoteResultSending(result);
    }

    console.log(result);

    await browser.downloads.download({
        url: 'data:application/json;base64,' + btoa(JSON.stringify(result)),
        filename: 'resultJungleScout.json',
        saveAs: true,
    });
}

async function jungleScoutRemoteResultSending(result: Result): Promise<void> {

}

async function jungleScoutSingleProcess(task: TaskConfig): Promise<Result> {
    const [ tab, needClose ] = await (async task => {
        if (task.tabId) {
            return [await browser.tabs.get(task.tabId), false];
        } else if (task.startURL) {
            return [await browser.tabs.create({
                url: task.startURL,
            }), true];
        } else {
            return [(await browser.tabs.query({ active: true }))[0], false];
        }
    })(task);
    if (!tab || !tab.id) throw new Error(`Unable to process task: no tab found (${JSON.stringify(task)})`);
    await browser.tabs.update(tab.id, {
        autoDiscardable: false,
    });

    try {
        await browser.scripting.executeScript({
            target: { tabId: tab.id },
            files: [
                'injections/common/wait.js',
                'injections/common/parseCurrency.js',
                'injections/common/pagination.js',
                'injections/junglescout/SearchProcess.js',
            ],
        });
    } catch (e) {
        if (needClose) await browser.tabs.remove(tab.id);
        throw new Error(`Unable to process task: can't inject files due to ${e} (${JSON.stringify(task)})`);
    }
    try {
        const result: Result = (await browser.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => {
                /** @ts-ignore */
                return getTheDataWithPagination();
            },
        }))[0]?.result || {};

        let res: Result = {};
        for (const asin in result) {
            const item = result[asin];
            if (
                item.moRevenue && item.moRevenue >= 30000
                && item.rating && item.rating < 3.5
                && item.reviewsCount && item.reviewsCount >= 10
            ) res[asin] = result[asin];
        }

        return res;
    } catch (e) {
        throw new Error(`Error while processing task: ${e} (${JSON.stringify(task)})`);
    } finally {
        if (needClose) await browser.tabs.remove(tab.id);
    }
}
