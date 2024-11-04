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

function report(msg, task_id, stop, confirm = true) {
    console.log(msg);
    console.error(msg);
    fetch('http://195.201.194.213:8832/tasks/report/' + task_id, {
        headers: {
            'Content-Type': 'application/json',
        },
        method: 'PATCH',
        body: JSON.stringify({
            confirm: confirm,
            errors: [
                (new Date()).toISOString() + ' ' + msg,
            ],
            stop: stop,
        }),
    });
}

async function makeQueryByASIN(asin, window_id) {
    const tab = await chrome.tabs.create({
        url: 'https://www.amazon.com/dp/' + asin + '?th=1',
        active: false,
        windowId: window_id,
    });
    let exc = null;
    let result = null;
    try {
        chrome.tabs.update(tab.id, {autoDiscardable: false});

        await chrome.scripting.executeScript({
            target: {tabId: tab.id},
            files: ['./products.js'],
        });

        // Breadcrumbs
        result = await chrome.scripting.executeScript({
            target: {tabId: tab.id},
            func: () => {
                const products_collector = new CollectProductInfo();
                try {
                    return products_collector.getBreadcrumbs();
                } catch (e) {
                    return {'error': e.message};
                }
            },
        });
        result = result[0]?.result;
    } catch (e) {
        exc = e;
    } finally {
        console.log('Remove tab [' + asin + ']');
        try {
            await chrome.tabs.remove(tab.id);
            console.log('Tab removed! [' + asin + ']');
        } catch (e) {
            report('[PT] Error: can\'t close tab! ' + e.message, task_id, true);
        }
    }

    if (!result || exc) {
        throw exc || new Error('No breadcrumbs found!');
    }
    return result;
}

async function collect100ASINs(query, limit, window_id) {
    limit = limit || 100;
    let asinList = [];
    let counter = 1;
    let tab;

    while (asinList.length < limit) {
        tab = await chrome.tabs.create({
            url: encodeURI(`https://amazon.com/s?k=${query}&page=${counter}`),
            active: false,
            windowId: window_id,
        });
        chrome.tabs.update(tab.id, {autoDiscardable: false});
        const result = await chrome.scripting.executeScript({
            target: {tabId: tab.id},
            args: [asinList, limit],
            func: (asinList, limit) => {
                function scrap(document) {
                    const productCards = document.querySelectorAll('div[data-asin]');
                    for (const card of productCards) {
                        if (asinList.length >= limit) {
                            console.log(asinList);
                            return asinList;
                        }
                        const asin = card.getAttribute('data-asin')?.trim();
                        if (asin) {
                            asinList.push(asin);
                        }
                    }
                    return asinList;
                }

                return new Promise((resolve) => {
                    const appElement = document.querySelector('.s-result-item');
                    if (appElement) {
                        return resolve(scrap(document));
                    }

                    const observer = new MutationObserver((mutationsList, observer) => {
                        for (let mutation of mutationsList) {
                            if (mutation.type === 'childList' || mutation.type === 'subtree') {
                                const appElement = document.querySelector('.s-result-item');
                                if (appElement) {
                                    observer.disconnect();
                                    return resolve(scrap(document));
                                }
                            }
                        }
                    });

                    observer.observe(document.body, {
                        childList: true,
                        subtree: true,
                    });
                });
            }
        });
        console.log(result);
        asinList = result[0]?.result || asinList;
        await chrome.tabs.remove(tab.id);
        ++counter;
        if (!asinList || !asinList.length || counter > limit) {
            break;
        }
    }
    asinList = new Set(asinList);
    console.log(Array.from(asinList));
    return Array.from(asinList);
}

async function getNewAsins(asins_list, reference, query) {
    return await fetch('http://195.201.194.213:8832/product-targeting/filter-asins', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            asins: asins_list,
            reference: reference,
            query: query,
        }),
    });
}

async function getInfoAboutOneASIN(asin, task_id, window_id) {
    const tab = await chrome.tabs.create({
        url: 'https://www.amazon.com/dp/' + asin + '?th=1',
        active: false,
        windowId: window_id,
    });
    chrome.tabs.update(tab.id, {autoDiscardable: false});

    try {
        let result;
        // Products lib
        try {
            await chrome.scripting.executeScript({
                target: {tabId: tab.id},
                files: ['./products.js'],
            });
        } catch (e) {
            report('Error when importing products.js: ' + e.message, task_id, true);
        }
        // Product card
        result = await chrome.scripting.executeScript({
            target: {tabId: tab.id},
            func: () => {
                window.finish_collecting = false;
                const products_collector = new CollectProductInfo();
                try {
                    return products_collector.getProductCard();
                } catch (e) {
                    return {'error': e.message};
                }
            },
        });
        const data = result[0]?.result
        if (!data || data.error) {
            report('[PT] Error: ' + (data ? data.error : 'no data'), task_id, true);
            return null;
        }
        return data || null;
    } catch (e) {
        report('[PT] Error: ' + e.message, task_id, true);
    } finally {
        chrome.scripting.executeScript({
            target: {tabId: tab.id},
            func: () => {
                window.finish_collecting = true;
            },
        });
        console.log('Remove tab [' + asin + ']');
        try {
            await chrome.tabs.remove(tab.id);
            console.log('Tab removed! [' + asin + ']');
        } catch (e) {
            report('[PT] Error: can\'t close tab! ' + e.message, task_id, true);
        }
    }
}

function sendInfoAboutOneASIN(reference, query, asin, title, description) {
    fetch('http://195.201.194.213:8832/product-targeting/result/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({reference, query, asin, title, description}).replaceAll('\n', '\\n'),
    });
}

async function finishTask(task_id) {
    await fetch(
        'http://195.201.194.213:8832/tasks/finish/' + task_id,
        {method: 'PATCH'},
    );
    await fetch(
        'http://195.201.194.213:8832/tasks/release/' + task_id,
        {method: 'POST'},
    );
}

async function run(task, sender, sendResponse) {
    if (!task || !task.header_id || !task.task_id) {
        return sendResponse('bad request');
    }
    let acq = await fetch(
        'http://195.201.194.213:8832/tasks/acquire/' + task.script + '/' + task.header_id + '/' + task.task_id,
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
    // Getting query
    if (!task.query) {
        try {
            task.query = await makeQueryByASIN(task.reference, task.windowId);
        } catch (e) {
            report(e.message, task.task_id, true);
            return;
        }
    }
    // Collecting all asins
    let all_asins;
    try {
        all_asins = await collect100ASINs(task.query, task.limit, task.windowId);
    } catch (e) {
        report(e.message, task.task_id, true);
        return;
    }
    // Getting new asins
    let new_asins;
    try {
        const res = await getNewAsins(all_asins, task.reference, task.query);
        if (res.status !== 200) {
            new_asins = all_asins;
        } else {
            new_asins = await res.json()
        }
    } catch (e) {
        report(e.message, task.task_id, false, false);
        new_asins = all_asins;
    }

    console.log(new_asins);

    for (const asin of new_asins) {
        const res = await getInfoAboutOneASIN(asin, task.task_id, task.windowId);
        if (res && res.title) {
            if (!res.description) {
                res.description = null;
            }
            sendInfoAboutOneASIN(task.reference, task.query, asin, res.title, res.description);
        }
    }
    await finishTask(task.task_id);
}

chrome.runtime.onMessageExternal.addListener(run);
chrome.runtime.onMessage.addListener(run);


// Control panel
chrome.tabs.query({
    url: 'chrome-extension://' + chrome.runtime.id + '/control_panel.html',
    currentWindow: true,
}, (tabs) => {
    if (!tabs || !tabs.length) {
        chrome.tabs.create({
            url: 'control_panel.html',
        }, (tab) => {
            chrome.tabs.update(tab.id, {autoDiscardable: false});
        });
    }
});
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    for (let i in request) {
        if (i === 'fetch') {
            fetch(request[i][0], request[i][1]).then((response) => {
                sendResponse(response);
            });
        }
    }
});