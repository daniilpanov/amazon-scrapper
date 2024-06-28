chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    for (let i in request) {
        if (i === 'fetch') {
            fetch(request[i][0], request[i][1]).then((response) => {
                sendResponse(response);
            });
        }
    }
});

async function run({root, task}, sender, sendResponse) {
    console.log(task);
    let acq = await fetch(
        'http://195.201.194.213:8832/tasks/acquire/products/' + task.header_id + '/' + task._id,
        {method: 'post'},
    )
    if (acq.status !== 200) {
        if (acq.status === 409) {
            sendResponse('busy')
        } else {
            sendResponse('fail')
            console.error('Error when try to acquire task:', acq.statusText);
        }
        return;
    }
    sendResponse('OK');
    let needle_tab = null, created = false;
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
            url: 'https://www.' + (task.data.domain || 'amazon.com') + '/' + (task.result.prefix ? task.result.prefix + '/' : '') + 'dp/' + asin + '?th=1',
            active: false,
        });
        created = true;
    }

    const date = new Date();
    try {
        let result, data, errors;
        // Products lib
        await chrome.scripting.executeScript({
            target: {tabId: needle_tab.id},
            files: ['./products.js'],
        });
        // Product card
        result = await chrome.scripting.executeScript({
            target: {tabId: needle_tab.id},
            args: [task],
            func: (task) => {
                window.products_collector = CollectProducts(task.data.asin);
                return {data: window.products_collector.getProductCard(task.data.collect_media_config)};
            },
        });
        data = result[0].result?.data;
        errors = result[0].result?.errors;
        // handle errors
        if (errors) {
            fetch('http://195.201.194.213:8832/tasks/report/' + task._id, {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'PATCH',
                body: JSON.stringify({
                    confirm: false,
                    errors: [
                        [date.toISOString() + ' [products.card]', errors],
                    ],
                    stop: false,
                }),
            });
        }
        // load data
        if (Object.keys(data || {}).length) {
            fetch('http://195.201.194.213:8832/products/set_result/card/', {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'POST',
                body: JSON.stringify(data),
            });
        }
        // Aspects
        if (task.data.collect_aspects) {
            result = await chrome.scripting.executeScript({
                target: {tabId: needle_tab.id},
                args: [task],
                func: (task) => {
                    if (!window.products_collector) {
                        window.products_collector = CollectProducts(task.data.asin);
                    }
                    return {data: window.products_collector.getAspects()};
                },
            });
            data = result[0].result?.data;
            errors = result[0].result?.errors;
            // handle errors
            if (errors) {
                fetch('http://195.201.194.213:8832/tasks/report/' + task._id, {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    method: 'PATCH',
                    body: JSON.stringify({
                        confirm: false,
                        errors: [
                            [date.toISOString() + ' [products.aspects]', errors]
                        ],
                        stop: false,
                    }),
                });
            }
            // load data
            if (data?.length) {
                fetch('http://195.201.194.213:8832/products/set_result/aspects/', {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    method: 'POST',
                    body: JSON.stringify(data),
                });
            }
        }
        // If it is target - run target collecting
        if (task.data.collect_media_config && task.data.target) {
            fetch('http://localhost:8832/products/target/collect/' + task.data.asin, {method: 'POST'})
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
            await chrome.scripting.executeScript({
                target: {tabId: needle_tab.id},
                files: ['./reviews.js'],
            });
            result = await chrome.scripting.executeScript({
                target: {tabId: needle_tab.id},
                args: [task],
                func: (task) => {
                    return new Promise(async (resolve, reject) => {
                        // create parser
                        const collector = new CollectReviews(
                            task.data.asin,
                            task.result.prefix || null,
                            task.data.current_format,
                            task.data.keywords || '',
                            task.data.domain || 'amazon.com'
                        );
                        // setup callbacks
                        // send res
                        collector.per_index_callback = (data) => {
                            console.log(data);
                            console.log(JSON.stringify(data));
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
                                    ]
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
                        errors: [date.toISOString() + ' [products.aspects]', errors],
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
            fetch('http://45.14.245.223:1802/new_collection/', {
                    'accept': 'application/json',
                    'Content-Type': 'application/json',
                    body: JSON.stringify({
                        'name': 'Collected-' + asin,
                        'date': (new Date(date.getTime() + date.getTimezoneOffset() * 60000)).toISOString().split('T')[0],
                        'asins': [asin],
                    }),
                },
            );
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
        if (created) {
            chrome.tabs.remove(needle_tab.id);
        }
    }
}

chrome.runtime.onMessageExternal.addListener(run)
chrome.runtime.onMessage.addListener(run)
