chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    for (let i in request) {
        if (i === 'fetch') {
            fetch(request[i][0], request[i][1]).then((response) => {
                sendResponse(response);
            });
        }
    }
});

async function run(task, sender, sendResponse) {
    let acq = await fetch(
        'http://195.201.194.213:8832/tasks/acquire/bsr/' + task.header_id + '/' + task.task_id,
        {method: 'post'},
    );
    if (acq.status !== 200) {
        if (acq.status === 409) {
            sendResponse('busy');
        } else {
            sendResponse('fail');
            console.error('Error when try to acquire task:', acq.statusText);
        }
        return;
    }
    sendResponse('OK');
    let needle_tab = null, created = false;
    // check if needle tab is already opened
    for (const tab of await chrome.tabs.query({windowId: task.windowId})) {
        if (tab.url === task.bsr) {
            needle_tab = tab;
            break;
        }
    }
    if (!needle_tab) {
        needle_tab = await chrome.tabs.create({
            url: 'https://www.amazon.com/' + task.bsr,
            active: false,
            windowId: task.windowId,
        });
        chrome.tabs.update(needle_tab.id, {autoDiscardable: false});
        created = true;
    }

    const date = new Date();
    try {
        let result = null, data, errors, need_import = created;
        if (!created) {
            need_import = await chrome.scripting.executeScript({
                target: {tabId: needle_tab.id},
                func: () => {
                    return typeof CollectBSR === 'undefined';
                },
            });
            need_import = need_import[0].result || false;
        }
        // BSR lib
        if (need_import) {
            await chrome.scripting.executeScript({
                target: {tabId: needle_tab.id},
                files: ['./bsr.js'],
            });
        }
        console.log('bsr imported');
        // BSR result
        for (let i = 0; i < 100; ++i) {
            result = await chrome.scripting.executeScript({
                target: {tabId: needle_tab.id},
                args: [task],
                func: async (task) => {
                    window.finish_collecting = false;
                    console.log('hello! :)');
                    const bsr_collector = new CollectBSR(task.limit, task.count, task.target, task.unique_brands, task.domain);
                    console.log('BSR Collector created!');
                    if (!task?.bsr) {
                        console.log('Fail!');
                        return {errors: ['Can not get BSR URL! Please enter full URL']};
                    }
                    let asins_links = {};
                    console.log('Collect asins');
                    for (const asin of await bsr_collector.getASINsLInks(task.bsr)) {
                        asins_links[asin] = `https://${task.domain}/dp/${asin}`;
                    }
                    window.finish_collecting = true;
                    return {data: {bsr_url: task.bsr, asins_links: asins_links}};
                },
            });
            if (result) {
                break;
            }
            await new Promise(r => setTimeout(r, 100));
        }
        console.log('result!', result);
        data = result[0].result?.data;
        data.with_continue = Boolean(task.stage > 0);
        data.task_id = task.task_id;
        errors = result[0].result?.errors;
        console.log(data, errors);
        // handle errors
        if (errors) {
            fetch('http://195.201.194.213:8832/tasks/report/' + task.task_id, {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'PATCH',
                body: JSON.stringify({
                    confirm: true,
                    errors: [
                        [date.toISOString() + ' [bsr]', errors],
                    ],
                    stop: true,
                }),
            });
        }
        // load data
        if (Object.keys(data || {}).length) {
            fetch('http://195.201.194.213:8832/cmd/alias/bsr/finish/', {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'POST',
                body: JSON.stringify(data),
            });
        }
    } catch (e) {
        console.log(e);
        fetch('http://195.201.194.213:8832/tasks/report/' + task.task_id, {
            headers: {
                'Content-Type': 'application/json',
            },
            method: 'PATCH',
            body: JSON.stringify({
                confirm: true,
                errors: [
                    date.toISOString() + ' [bsr] Error: ' + e.message,
                ],
                stop: true,
            }),
        });
    } finally {
        await chrome.tabs.remove(needle_tab.id);
    }
}

chrome.runtime.onMessageExternal.addListener(run);
chrome.runtime.onMessage.addListener(run);
