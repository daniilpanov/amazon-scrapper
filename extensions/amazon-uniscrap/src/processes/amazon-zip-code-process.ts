import browser from 'webextension-polyfill';

type TaskConfig = {
    zipCode: number;
};

export async function AmazonZipCodeProcess(task: TaskConfig): Promise<void> {
    const tab = await browser.tabs.create({
        url: encodeURI('https://www.amazon.com'),
        active: false,
    });

    if (!tab?.id)
        throw new Error(`Unable to create a tab: unknown error (${JSON.stringify(task)})`);

    try {
        for (let i = 0; i < 5; ++i) {
            if (await executeMainScript(task.zipCode, tab.id))
                break;

            await browser.tabs.reload(tab.id);
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
    } finally {
        await browser.tabs.remove(tab.id);
    }
}

async function executeMainScript(zipCode: number, tabId: number): Promise<boolean> {
    await browser.scripting.executeScript({
        target: { tabId },
        files: ['injections/amazon-zip-code/changeZip.js'],
    });

    return (await browser.scripting.executeScript({
        target: { tabId },
        args: [zipCode],
        func: async zipCode => {
            /** @ts-ignore */
            return await changeZipCode(zipCode);
        },
    }))[0]?.result;
}
