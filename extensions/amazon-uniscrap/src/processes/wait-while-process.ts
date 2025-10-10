import browser from 'webextension-polyfill';

type Config = {
    url: string,
    fname: string,
    lname: string,
    email: string,
    phone: string,
};


export async function waitWhileProcess(task: Config) {
    const tab = await browser.tabs.create({
        // url: 'https://waitwhile.com/locations/spfdsunday/',
        // url: 'https://waitwhile.com/locations/bearpantry/',
        url: task.url,
    });
    if (!tab || !tab.id) throw new Error(`Unable to process task: can not create tab`);
    try {
        await browser.tabs.update(tab.id, {
            autoDiscardable: false,
        });

        let q = 0;  // TM stage
        for (let i = 0; i < 1000; ++i) {
            if (q === 1) {
                let res = 1;
                for (let i = 0; i < 5 && res === 1; ++i) {
                    res = await tryExecuteScript(tab.id, task);
                    await new Promise(resolve => setTimeout(resolve, 200));
                }
                if (res > 1) {
                    console.log('SUCCESS!');
                    break;
                } else {
                    console.log('FAILED!');
                    q = 0;
                }
            } else {
                if (await tryExecuteScript(tab.id, task)) q = 1;
                else {
                    console.log('???');
                    await browser.tabs.update(tab.id, { url: task.url });
                    await new Promise(resolve => setTimeout(resolve, 250));
                }
            }
        }
        await browser.runtime.sendMessage({
            queue: 'result.success.spfd',
            msg: { ...task, success: true },
        });
    } catch (e: any) {
        console.log('Error:', e);
        await browser.runtime.sendMessage({
            queue: 'result.error.spfd',
            msg: { ...task, success: false, error: e.message },
        });
    } finally {
        // await browser.tabs.remove(tab.id!);
    }
}


async function tryExecuteScript(tabId: number, task: Config) {
    try {
        await browser.scripting.executeScript({
            target: { tabId: tabId },
            files: [
                'injections/common/humanize.js',
                'injections/spfd/registration.js',
            ],
        });
    } catch (e) {
        throw new Error(`Unable to process task: can't inject files due to ${e}`);
    }

    try {
        const result = (await browser.scripting.executeScript({
            target: { tabId: tabId },
            args: [task.fname, task.fname, task.phone, task.email],
            func: async (fname, lname, phone, email) => {
                try {
                    /** @ts-ignore */
                    return await getRegistrationStatus(fname, lname, phone, email);
                } catch (e) {
                    return { success: false, error: e };
                }
            },
        }))[0]?.result || {};
        return result.success + (result.stage || 0);
    } catch (e) {
        throw new Error(`Error while processing task: ${e}`);
    }
}
