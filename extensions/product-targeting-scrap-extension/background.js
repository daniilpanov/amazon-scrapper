chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    for (let i in request) {
        if (i === 'fetch') {
            fetch(request[i][0], request[i][1]).then((response) => {
                sendResponse(response);
            });
        } else if (i === 'log') {
            console.log(request[i]);
        }
    }
});

async function run(task, sender, sendResponse) {
    if (!task || !task.header_id || !task.task_id) {
        return sendResponse('bad request');
    }
    let acq = await fetch(
        'http://localhost:8832/tasks/acquire/' + task.script + '/' + task.header_id + '/' + task.task_id,
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
    let needle_tab = null;
    const asin = task.reference_asin || task.asin;
    // check if needle tab is already opened
    for (const tab of await chrome.tabs.query({windowId: task.windowId})) {
        if (tab.url.startsWith('https://www.amazon.') && tab.url.includes('/dp/' + asin)) {
            needle_tab = tab;
            break;
        }
    }
    if (!needle_tab) {
        needle_tab = await chrome.tabs.create({
            url: 'https://www.' + (task.domain || 'amazon.com') + '/dp/' + asin + '?th=1',
            active: false,
            windowId: task.windowId,
        });
        chrome.tabs.update(needle_tab.id, {autoDiscardable: false});
    }

    const date = new Date();
    try {
        let result, data;
        // Products lib
        try {
            await chrome.scripting.executeScript({
                target: {tabId: needle_tab.id},
                files: ['./products.js'],
            });
        } catch (e) {
            console.log('Error when importing products.js:', e);
            console.error('Error when importing products.js:', e);
        }
        // Product card
        result = await chrome.scripting.executeScript({
            target: {tabId: needle_tab.id},
            args: [task],
            func: (task) => {
                window.finish_collecting = false;
                const products_collector = new CollectProducts(task.reference_asin || task.asin);
                try {
                    if (task.script.endsWith('-Ref')) {
                        return products_collector.getBreadcrumbs();
                    } else if (task.script.endsWith('-Item')) {
                        return products_collector.getProductCard();
                    }
                } catch (e) {
                    return {'error': e.message};
                }
            },
        });
        data = result[0].result;
        // load data
        if (task.script.endsWith('-Ref') || Object.keys(data || {}).length) {
            let script, d;
            if (task.script.endsWith('-Ref')) {
                script = 'asin';
                d = {
                    reference_asin: asin,
                    query: data,
                };
            } else {
                script = 'item';
                d = {
                    reference: task.reference,
                    query: task.query,
                    asin: asin,
                    title: data.title,
                    description: data.description,
                    root_task_id: task.root_task_id,
                };
            }
            fetch('http://localhost:8832/product-targeting/result/set/' + script + '/' + task.task_id, {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'POST',
                body: JSON.stringify(d).replaceAll('\n', '\\n'),
            }).then((res) => {
                if (res.status > 204) {
                    console.log('card write error:', res.statusText, '\ndata:', JSON.stringify(d));
                    console.error('card write error:', res.statusText, '\ndata:', JSON.stringify(d));
                    throw new Error('card write error:', res.statusText, '\ndata:', JSON.stringify(d));
                }
            });
        }
    } catch (e) {
        console.log(e);
        fetch('http://localhost:8832/tasks/report/' + task.task_id, {
            headers: {
                'Content-Type': 'application/json',
            },
            method: 'PATCH',
            body: JSON.stringify({
                confirm: true,
                errors: [
                    date.toISOString() + ' [' + task.script + '] Error: ' + e.message,
                ],
                stop: true,
            }),
        });
    } finally {
        chrome.scripting.executeScript({
            target: {tabId: needle_tab.id},
            func: () => {
                window.finish_collecting = true;
            },
        });
        console.log('Data sent! Remove tab [' + asin + ']');
        try {
            await chrome.tabs.remove(needle_tab.id);
            console.log('Tab removed! [' + asin + ']');
        } catch (e) {
            console.log(e);
            console.error(e);
        }
    }
}

chrome.runtime.onMessageExternal.addListener(run);
chrome.runtime.onMessage.addListener(run);
