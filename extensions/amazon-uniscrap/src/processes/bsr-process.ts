import browser from 'webextension-polyfill';

type BSR = {
    bsrLink: string;
    bsrName: string;
    index: number;
    level: number;
};

type GroupedBSR = BSR | {
    group?: Array<BSR>;
};

type Product = {
    asin: string;
    rank?: number;
}

type ResultTree = {
    flatTree: Array<BSR>;
    tree: Array<GroupedBSR>;
    currentBSR: BSR;
};

type TaskConfig = {
    BSR_URL: string;
    startNewTreeTasks?: boolean;
    startNewProdTasks?: boolean;
    startNewProdTasksWithReview?: boolean;
    targetAsins?: string[];
};

export async function BSRProcess(task: TaskConfig): Promise<void> {
    if (!task.startNewTreeTasks) task.startNewTreeTasks = false;
    if (!task.startNewProdTasks) task.startNewProdTasks = false;
    if (!task.startNewProdTasksWithReview) task.startNewProdTasksWithReview = false;
    if (!task.targetAsins) task.targetAsins = [];
    const tab = await browser.tabs.create({
        url: task.BSR_URL,
    });
    if (!tab || !tab.id) throw new Error(`Unable to process task: no tab found (${JSON.stringify(task)})`);
    await browser.tabs.update(tab.id, {
        autoDiscardable: false,
    });

    let checkThrottled: boolean = (await browser.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
            return !document.getElementById('a-page');
        },
    }))[0]?.result;

    for (let i = 1; checkThrottled && i < 5; ++i) {
        await browser.tabs.reload(tab.id, { bypassCache: true });
        await new Promise(r => setTimeout(r, 500));
        checkThrottled = (await browser.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => {
                return !document.getElementById('a-page');
            },
        }))[0]?.result;
    }

    try {
        await browser.scripting.executeScript({
            target: { tabId: tab.id },
            files: [
                'injections/common/wait.js',
                'injections/common/pagination.js',
                'injections/bsr/categories.js',
                'injections/bsr/products.js',
            ],
        });
    } catch (e) {
        await browser.tabs.remove(tab.id);
        throw new Error(`Unable to process task: can't inject files due to ${e} (${JSON.stringify(task)})`);
    }

    let tree: ResultTree;

    try {
        tree = (await browser.scripting.executeScript({
            target: { tabId: tab.id },
            func: async () => {
                /** @ts-ignore */
                await waitLoading(getWaitTreeQuerySelector());
                /** @ts-ignore */
                return getTree();
            },
        }))[0]?.result;
        if (!tree) throw new Error('No BSR tree found!');
    } catch (e) {
        await browser.tabs.remove(tab.id);
        throw new Error(`Error while processing task: ${e} (${JSON.stringify(task)})`);
    }

    let ASINs: Array<Product> = [];

    try {
        for (let i = 0; i < 2; ++i) {
            ASINs = [...ASINs, ...((await browser.scripting.executeScript({
                target: { tabId: tab.id },
                args: [ASINs.length],
                func: async shift => {
                    /** @ts-ignore */
                    await waitLoading(getWaitProductsQuerySelector());
                    /** @ts-ignore */
                    return findASINsList(shift);
                },
            }))[0].result || [])];
            const switchPage = (await browser.scripting.executeScript({
                target: { tabId: tab.id },
                func: async () => {
                    /** @ts-ignore */
                    return waitAndClickToNextPage();
                },
            }))[0]?.result;
            if (!switchPage) break;
        }
    } catch (e) {
        await browser.tabs.remove(tab.id);
        throw new Error(`Error while processing task: ${e} (${JSON.stringify(task)})`);
    }
    try {
        await browser.scripting.executeScript({
            target: { tabId: tab.id },
            args: [tree.flatTree, tree.currentBSR, ASINs, task.startNewTreeTasks, task.startNewProdTasks, task.startNewProdTasksWithReview, task.targetAsins],
            func: async (tree, currentBSR, ASINs, startNewTreeTasks, startNewProdTasks, startNewProdTasksWithReview, targetAsins) => {
                /** @ts-ignore */
                chrome.runtime.sendMessage({
                    action: 'sendMessage',
                    data: {
                        queue: 'result.success.bsr',
                        msg: { tree, currentBSR, ASINs, startNewTreeTasks, startNewProdTasks, startNewProdTasksWithReview, targetAsins },
                    },
                });
            },
        });
    } catch (e) {
        throw new Error(`Error while processing task: ${e} (${JSON.stringify(task)})`);
    } finally {
        await browser.tabs.remove(tab.id);
    }
}
