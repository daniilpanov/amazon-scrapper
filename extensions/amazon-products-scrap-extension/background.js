AbortSignal.timeout ??= function timeout(ms) {
    const ctrl = new AbortController();
    setTimeout(() => ctrl.abort(), ms);
    return ctrl.signal;
};

let lastUpdate = Date.now();
const urlList = [
    'https://localhost',
    'http://localhost',
    'https://cp.nyle.ai',
    'http://cp.nyle.ai',
    'https://195.201.194.213',
    'http://195.201.194.213',
];
let currentUrl = urlList[0];

const URL_EXPIRATION_TIME = 5 * 60 * 1000;

async function endp(uri, force = false) {
    if (!force && Date.now() - lastUpdate < URL_EXPIRATION_TIME) {
        return currentUrl + uri;
    }

    for (const url of urlList) {
        try {
            const response = await fetch(url + ':8832/ping', { method: 'GET', signal: AbortSignal.timeout(5000) });
            console.log(response.ok);
            if (response.ok) {
                currentUrl = new URL(url).origin;
                lastUpdate = Date.now();
                return currentUrl + uri;
            }
        } catch (error) {
            console.log(error);
        }
    }

    return null;
}


endp(':8832/ping', true).then(res => {
    console.log('URL:', res);
    if (!res) {
        console.log('Error! No endpoints found!');
        return;
    }
    chrome.tabs.query({
        url: 'chrome-extension://' + chrome.runtime.id + '/html/control_panel.html',
    }, tabs => {
        if (!tabs || !tabs.length) {
            chrome.tabs.create({
                url: 'html/control_panel.html',
            }, tab => {
                chrome.tabs.update(tab.id, { autoDiscardable: false });
            });
        }
    });

    chrome.runtime.onMessageExternal.addListener(run);
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        let need_run = true;
        for (let i in request) {
            if (i === 'fetch') {
                need_run = false;
                fetch(request[i][0], request[i][1]).then((response) => {
                    sendResponse(response);
                });
            } else if (i === 'log') {
                need_run = false;
                console.log(request[i]);
            }
        }

        if (need_run)
            return run(request, sender, sendResponse);
    });
});

async function run(task, sender, sendResponse) {
    if (!task || !task.header_id || !task.task_id) {
        return sendResponse('bad request');
    }
    let acq = await fetch(
        'http://195.201.194.213:8832/tasks/acquire/products/' + task.header_id + '/' + task.task_id,
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
    const numberInBSR = task.rank;
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
            func: () => {
                window.finish_collecting = false;
                const products_collector = new ProductsParser();
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
            fetch(await endp(':8832/tasks/report/' + task.task_id), {
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
            data.bsr_link = task.bsr_link;
            data.number_in_BSR = numberInBSR;
            fetch(await endp(':8832/products/set_result/card/' + asin), {
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
            const f = task => {
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
                    collector.per_index_callback = data => {
                        if (data && data.length) {
                            chrome.runtime.sendMessage(
                                {
                                    fetch: [
                                        ':8832/products/set_result/reviews',
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
                                response => {
                                    if (response === 'bad request') {
                                        console.log('BAD REQUEST!', data);
                                    }
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
                fetch(await endp(':8832/tasks/report/' + task.task_id), {
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
                fetch(await endp(':8832/tasks/finish/' + task.task_id), {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    method: 'PATCH',
                });
                fetch(await endp(':8832/tasks/release/' + task.task_id), {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    method: 'POST',
                });
            }
        } else {
            fetch(await endp(':8832/tasks/finish/' + task.task_id), {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'PATCH',
            });
            fetch(await endp(':8832/tasks/release/' + task.task_id), {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'POST',
            });
        }
    } catch (e) {
        console.log(e);
        fetch(await endp(':8832/tasks/report/' + task.task_id), {
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
            fetch(await endp(':8832/tasks/report/' + task.task_id), {
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
