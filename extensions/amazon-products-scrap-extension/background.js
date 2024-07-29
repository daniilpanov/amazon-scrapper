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

async function run({root, task}, sender, sendResponse) {
    if (!task || !root || !task.header_id) {
        return sendResponse('bad request');
    }
    let acq = await fetch(
        'http://195.201.194.213:8832/tasks/acquire/products/' + task.header_id + '/' + task._id,
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
    const {asin} = task.data;
    // check if needle tab is already opened
    for (const tab of await chrome.tabs.query({})) {
        if (tab.url.startsWith('https://www.amazon.') && tab.url.includes('/dp/' + asin)) {
            needle_tab = tab;
            break;
        }
    }
    if (!needle_tab) {
        needle_tab = await chrome.tabs.create({
            url: 'https://www.' + (task.data.domain || 'amazon.com') + '/' + (task.result?.prefix ? task.result.prefix + '/' : '') + 'dp/' + asin + '?th=1',
            active: false,
        });
        chrome.tabs.update(needle_tab.id, {autoDiscardable: false});
    }

    const date = new Date();
    try {
        let result, data, errors;
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
                const products_collector = new CollectProducts(task.data.asin);
                try {
                    const product_card = products_collector.getProductCard(task.data.collect_media_config);
                    const aspects = (task.data.collect_aspects) ? products_collector.getAspects() : null;
                    return {product_card, aspects};
                } catch (e) {
                    return {'error': e};
                }
            },
        });
        data = result[0].result;
        // handle errors
        if (data.error) {
            console.log(data.error);
            fetch('http://195.201.194.213:8832/tasks/report/' + task._id, {
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
        if (Object.keys(data.product_card || {}).length) {
            fetch('http://195.201.194.213:8832/products/set_result/card/' + task.data.asin, {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'POST',
                body: JSON.stringify(data.product_card),
            }).then((res) => {
                if (res.status > 204) {
                    console.log('card write error:', res.statusText, '\ndata:', data.product_card);
                    console.error('card write error:', res.statusText, '\ndata:', data.product_card);
                }
            });
        }
        if (data.aspects && data.aspects.length) {
            fetch('http://195.201.194.213:8832/products/set_result/aspects/' + task.data.asin, {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'POST',
                body: JSON.stringify(data.aspects),
            }).then((res) => {
                if (res.status > 201) {
                    console.log('aspects write error:', res.statusText, '\ndata:', data.aspects);
                    console.error('aspects write error:', res.statusText, '\ndata:', data.aspects);
                }
            });
        }
        // If it is target - run target collecting
        if (task.data.collect_media_config && task.data.target) {
            console.log('collect product media: ' + task.data.asin);
            fetch('http://localhost:8832/products/target/collect/' + task.data.asin, {method: 'POST'}).then((res) => {
                if (res.status > 201) {
                    console.log('product ' + task.data.asin + ' target collecting start error:', res.statusText);
                    console.error('product ' + task.data.asin + ' target collecting start error:', res.statusText);
                }
            });
        }
        // Reviews
        if (task.stage) {
            // Goto reviews page
            await chrome.scripting.executeScript({
                target: {tabId: needle_tab.id},
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
            // Reviews lib
            try {
                await chrome.scripting.executeScript({
                    target: {tabId: needle_tab.id},
                    files: ['./reviews.js'],
                });
            } catch (e) {
                console.log('Error when importing reviews.js:', e);
                console.error('Error when importing reviews.js:', e);
            }
            result = await chrome.scripting.executeScript({
                target: {tabId: needle_tab.id},
                args: [task],
                func: (task) => {
                    return new Promise(async (resolve, reject) => {
                        // create parser
                        const collector = new CollectReviews(
                            task.data.asin,
                            task.result?.prefix || null,
                            task.data.current_format,
                            task.data.keywords || '',
                            task.data.domain || 'amazon.com',
                        );
                        // setup callbacks
                        // send res
                        collector.per_index_callback = (data) => {
                            chrome.runtime.sendMessage(
                                {
                                    fetch: [
                                        'http://195.201.194.213:8832/products/set_result/reviews',
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
                        };
                        // reject on a lot of errors
                        let fails_counter = 0;
                        collector.serviceunavailableerror_callback = () => {
                            if (fails_counter > 20) {
                                reject({errors: ['unknown error']});
                                return false;
                            }
                            return ++fails_counter;
                        };
                        // resolve on finish
                        collector.finish_callback = () => {
                            resolve();
                        };
                        // startup
                        collector.index = task.data.index || 0;
                        collector.page = task.data.page || 1;
                        await collector.collect();
                    });
                },
            });
            // report errors of reviews collecting if exist
            errors = result[0].result?.errors;
            if (errors) {
                fetch('http://195.201.194.213:8832/tasks/report/' + task._id, {
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
                fetch('http://195.201.194.213:8832/tasks/finish/' + task._id, {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    method: 'PATCH',
                });
                fetch('http://195.201.194.213:8832/tasks/release/' + task._id, {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    method: 'POST',
                });
            }
        } else {
            fetch('http://195.201.194.213:8832/tasks/finish/' + task._id, {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'PATCH',
            });
            fetch('http://195.201.194.213:8832/tasks/release/' + task._id, {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'POST',
            });
        }
    } catch (e) {
        console.log(e);
        fetch('http://195.201.194.213:8832/tasks/report/' + task._id, {
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
            target: {tabId: needle_tab.id},
            func: () => {
                window.finish_collecting = true;
            },
        })
        console.log(await fetch('http://45.14.245.223:1802/new_collection/', {
            headers: {
                'accept': 'application/json',
                'Content-Type': 'application/json',
            },
            method: 'POST',
            body: JSON.stringify({
                'name': task.taskHeader.alias || asin,
                'date': (new Date(date.getTime() + date.getTimezoneOffset() * 60000)).toISOString().split('T')[0],
                'asins': [asin],
            }),
        }));
        try {
            await chrome.tabs.remove(needle_tab.id);
        } catch (e) {
            console.log(e);
            console.error(e);
        }
    }
}

chrome.runtime.onMessageExternal.addListener(run);
chrome.runtime.onMessage.addListener(run);
