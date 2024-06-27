chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    for (let i in request) {
        if (i === 'fetch') {
            fetch(request[i][0], request[i][1]).then((response) => {
                sendResponse(response);
            });
        } else if (i === 'gzip') {
            sendResponse(pako.gzip(JSON.stringify(request[i])));
        }
    }
});

async function run({root, task}, sender, sendResponse) {
    console.log(task);
    let acq = await fetch(
        'http://195.201.194.213:8832/tasks/acquire/products/' + task.taskHeader._id + '/' + task._id,
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
            url: 'https://www.' + (task.data.domain || 'amazon.com') + '/' + (task.result.prefix ? task.result.prefix + '/' : '') + '/dp/' + asin + '?th=1',
            active: false,
        });
        created = true;
    }

    try {
        /*// Products lib
        await chrome.scripting.executeScript({
            target: {tabId: needle_tab.id},
            files: ['./products.js'],
        });
        // Product card
        let result = await chrome.scripting.executeScript({
            target: {tabId: needle_tab.id},
            args: [task],
            func: (task) => {

            },
        });
        let {data, errors} = result.result;
        // load data
        await fetch('http://195.201.194.213:8832/products/set_result/card/', {
            headers: {
                'Content-Type': 'application/json',
            },
            method: 'POST',
            body: JSON.stringify(data),
        })
        // Aspects
        if (task.data.collect_aspects) {
            result = await chrome.scripting.executeScript({
                target: {tabId: needle_tab.id},
                args: [task],
                func: (task) => {

                },
            });
            data = result.result.data;
            errors = result.result.errors;
        }*/
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
            const result = await chrome.scripting.executeScript({
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
            const errors = result.result.errors;
            if (errors) {
                await fetch('http://195.201.194.213:8832/tasks/report/' + task._id, {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    method: 'PATCH',
                    body: JSON.stringify({
                        confirm: true,
                        errors: errors,
                        stop: true,
                    }),
                });
            }
            // else release and finish
            else {
                await fetch('http://195.201.194.213:8832/tasks/finish/' + task._id, {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    method: 'PATCH',
                });
                await fetch('http://195.201.194.213:8832/tasks/release/' + task._id, {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    method: 'POST',
                });
            }
            const date = new Date();
            await fetch('http://45.14.245.223:1802/new_collection/', {
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
        await fetch('http://195.201.194.213:8832/tasks/report/' + task._id, {
            headers: {
                'Content-Type': 'application/json',
            },
            method: 'PATCH',
            body: JSON.stringify({
                confirm: true,
                errors: [
                    'Error when parsing data from page: ' + e.message,
                ],
                stop: true,
            }),
        });
    } finally {
        if (created) {
            chrome.scripting.executeScript({
                target: {tabId: needle_tab.id},
                func: () => {
                    // window.close();
                    console.log('window.close();');
                },
            });
        }
    }
}

chrome.runtime.onMessageExternal.addListener(run)
chrome.runtime.onMessage.addListener(run)
