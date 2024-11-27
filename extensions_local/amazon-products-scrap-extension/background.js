AbortSignal.timeout ??= function timeout(ms) {
    const ctrl = new AbortController();
    setTimeout(() => ctrl.abort(), ms);
    return ctrl.signal;
};

chrome.tabs.query({
    url: 'chrome-extension://' + chrome.runtime.id + '/html/control_panel.html',
    currentWindow: true,
}, (tabs) => {
    if (!tabs || !tabs.length) {
        chrome.tabs.create({
            url: 'html/control_panel.html',
        }, (tab) => {
            chrome.tabs.update(tab.id, { autoDiscardable: false });
        });
    }
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (!request.length)
        return;

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
        'http://localhost:8832/tasks/acquire/products/' + task.header_id + '/' + task.task_id,
        { method: 'post' },
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
    const asin = task.asin;
    // check if needle tab is already opened
    for (const tab of await chrome.tabs.query({ windowId: task.windowId })) {
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
        chrome.tabs.update(needle_tab.id, { autoDiscardable: false });
    }

    const date = new Date();
    try {
        let result, data, errors;
        // Products lib
        try {
            await chrome.scripting.executeScript({
                target: { tabId: needle_tab.id },
                files: ['./includesInTab/parser.js', './includesInTab/products.js'],
            });
        } catch (e) {
            console.log('Error when importing dependencies:', e);
            console.error('Error when importing dependencies:', e);
        }
        // Product card
        result = await chrome.scripting.executeScript({
            target: { tabId: needle_tab.id },
            args: [asin],
            func: (asin) => {
                window.finish_collecting = false;
                const products_collector = new ProductsParser({ asin });
                try {
                    products_collector.appendFunctions(products_collector.allFunctions);
                    return products_collector.applyAsyncFunctions();
                } catch (e) {
                    return { 'error': e };
                }
            },
        });
        data = result[0].result;
        // handle errors
        if (data.error) {
            console.log(data.error);
            fetch('http://localhost:8832/tasks/report/' + task.task_id, {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'PATCH',
                body: JSON.stringify({
                    confirm: false,
                    errors: [
                        [date.toISOString() + ' [products.card]' + data.error.message],
                    ],
                    stop: false,
                }),
            });
        }
        // load data
        if (Object.keys(data || {}).length) {
            data.collectMedia = task.collect_media_config && task.target;
            fetch('http://localhost:8832/products/set_result/card/' + task.asin, {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'POST',
                body: JSON.stringify(data).replaceAll('\n', '\\n'),
            }).then((res) => {
                if (res.status > 204) {
                    console.log('card write error:', res.statusText, '\ndata:', JSON.stringify(data.product_card));
                    console.error('card write error:', res.statusText, '\ndata:', JSON.stringify(data.product_card));
                }
            });
        }
        /*if (data.aspects && data.aspects.length) {
            fetch('http://localhost:8832/products/set_result/aspects/' + task.asin, {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'POST',
                body: JSON.stringify(data.aspects),
            }).then((res) => {
                if (res.status > 201) {
                    console.log('aspects write error:', res.statusText, '\ndata:', JSON.stringify(data.aspects));
                    console.error('aspects write error:', res.statusText, '\ndata:', JSON.stringify(data.aspects));
                }
            });
        }*/
        // If it is target - run target collecting
        /*if (task.collect_media_config && task.target) {
            console.log('collect product media: ' + task.asin);
            fetch('http://localhost:8832/products/target/collect/' + task.asin, { method: 'POST' }).then((res) => {
                if (res.status > 201) {
                    console.log('product ' + task.asin + ' target collecting start error:', res.statusText);
                    console.error('product ' + task.asin + ' target collecting start error:', res.statusText);
                }
            });
        }*/
        // Reviews
        if (task.stage) {
            // Goto reviews page
            await chrome.scripting.executeScript({
                target: { tabId: needle_tab.id },
                func: () => {
                    let see_rev = document.getElementById('acrCustomerReviewLink');
                    see_rev.scrollIntoView();
                    see_rev.click();
                    see_rev = document.querySelector('[data-hook=see-all-reviews-link-foot]');
                    see_rev.scrollIntoView();
                    see_rev.click();
                },
            });
            await new Promise(resolve => setTimeout(resolve, 500));
            // correct URL
            const tab = await chrome.tabs.get(needle_tab.id);
            let tabs_parts = tab.url.split('/');
            for (const i in tabs_parts) {
                if (/B0[0-9A-Z]{8}/.test(tabs_parts[i])) {
                    tabs_parts[i] = asin;
                }
            }
            await chrome.tabs.update(tab.id, { url: tabs_parts.join('/') });
            await new Promise(resolve => setTimeout(resolve, 1000));
            // get reviews
            await chrome.scripting.executeScript({
                target: { tabId: needle_tab.id },
                func: () => {
                    let see_rev = document.getElementById('acrCustomerReviewLink');
                    see_rev.scrollIntoView();
                    see_rev.click();
                    see_rev = document.querySelector('[data-hook=see-all-reviews-link-foot]');
                    see_rev.scrollIntoView();
                    see_rev.click();
                },
            });
            try {
                await chrome.scripting.executeScript({
                    target: { tabId: needle_tab.id },
                    files: ['./reviews.js'],
                });
            } catch (e) {
                console.log(e);
                console.error(e);
            }
            // Reviews
            const f = (task) => {
                return new Promise(async (resolve, reject) => {
                    // create parser
                    const collector = new CollectReviews(
                        task.asin,
                        null,
                        task.current_format,
                        task.keywords || '',
                        task.domain || 'amazon.com',
                    );
                    // setup callbacks
                    // send res
                    collector.per_index_callback = (data) => {
                        if (data && data.length) {
                            chrome.runtime.sendMessage(
                                {
                                    fetch: [
                                        'http://localhost:8832/products/set_result/reviews',
                                        {
                                            headers: {
                                                // 'Content-Encoding': 'gzip',
                                                'Content-Type': 'application/json',
                                            },
                                            method: 'POST',
                                            body: JSON.stringify(data),
                                        },
                                    ],
                                    log: data,
                                },
                                (response) => {
                                },
                            );
                        }
                    };
                    // reject on a lot of errors
                    let fails_counter = 0;
                    collector.serviceunavailableerror_callback = () => {
                        if (fails_counter > 20) {
                            reject({ errors: ['unknown error'] });
                            return false;
                        }
                        return ++fails_counter;
                    };
                    // resolve on finish
                    collector.finish_callback = () => {
                        resolve();
                    };
                    // startup
                    collector.index = task.index || 0;
                    collector.page = task.page || 1;
                    await collector.collect();
                });
            };
            try {
                result = await chrome.scripting.executeScript({
                    target: { tabId: needle_tab.id },
                    args: [task],
                    func: f,
                });
            } catch (e) {
                try {
                    await chrome.scripting.executeScript({
                        target: { tabId: needle_tab.id },
                        files: ['./reviews.js'],
                    });
                    await new Promise(resolve => setTimeout(resolve, 500));
                    result = await chrome.scripting.executeScript({
                        target: { tabId: needle_tab.id },
                        args: [task],
                        func: f,
                    });
                } catch (e) {
                    console.log('Error when importing reviews.js:', e);
                    console.error('Error when importing reviews.js:', e);
                }
            }
            // report errors of reviews collecting if exist
            errors = result[0].result?.errors;
            if (errors) {
                fetch('http://localhost:8832/tasks/report/' + task.task_id, {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    method: 'PATCH',
                    body: JSON.stringify({
                        confirm: false,
                        errors: [date.toISOString() + ' [products.reviews]', errors],
                        stop: false,
                    }),
                });
            }
            // else release and finish
            else {
                fetch('http://localhost:8832/tasks/finish/' + task.task_id, {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    method: 'PATCH',
                });
                fetch('http://localhost:8832/tasks/release/' + task.task_id, {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    method: 'POST',
                });
            }
        } else {
            fetch('http://localhost:8832/tasks/finish/' + task.task_id, {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'PATCH',
            });
            fetch('http://localhost:8832/tasks/release/' + task.task_id, {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'POST',
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
                    date.toISOString() + ' [products] Error: ' + e.message,
                ],
                stop: true,
            }),
        });
    } finally {
        chrome.scripting.executeScript({
            target: { tabId: needle_tab.id },
            func: () => {
                window.finish_collecting = true;
            },
        });
        console.log('End! wait for sending... [' + asin + ']');
        try {
            console.log(asin, await fetch('http://45.14.245.223:1802/new_collection/', {
                headers: {
                    'accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                method: 'POST',
                body: JSON.stringify({
                    'name': task.alias || asin,
                    'date': (new Date(date.getTime() + date.getTimezoneOffset() * 60000)).toISOString().split('T')[0],
                    'asins': [asin],
                }),
                signal: AbortSignal.timeout(15000),
            }));
        } catch (e) {
            fetch('http://localhost:8832/tasks/report/' + task.task_id, {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'PATCH',
                body: JSON.stringify({
                    confirm: false,
                    errors: [
                        [date.toISOString() + ' [products.next] Error on trying to send new asins: ' + e.message],
                    ],
                    stop: false,
                }),
            });
        }
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
