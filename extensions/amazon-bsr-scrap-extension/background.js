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
        'http://195.201.194.213:8832/tasks/acquire/bsr/' + task.header_id + '/' + task._id,
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
    // check if needle tab is already opened
    for (const tab of await chrome.tabs.query({})) {
        if (tab.url === task.data.bsr) {
            needle_tab = tab;
            break;
        }
    }
    if (!needle_tab) {
        needle_tab = await chrome.tabs.create({
            url: task.data.bsr,
            active: false,
        });
        created = true;
    }
    console.log(needle_tab);

    const date = new Date();
    try {
        let result, data, errors, need_import = created;
        if (!created) {
            need_import = await chrome.scripting.executeScript({
                target: {tabId: needle_tab.id},
                func: () => {return typeof CollectBSR === 'undefined'},
            });
            need_import = need_import[0].result || false;
        }
        console.log(need_import);
        // BSR lib
        if (need_import) {
            await chrome.scripting.executeScript({
                target: {tabId: needle_tab.id},
                files: ['./bsr.js'],
            });
        }
        console.log('bsr imported');
        // BSR result
        result = await chrome.scripting.executeScript({
            target: {tabId: needle_tab.id},
            args: [task],
            func: (task) => {
                console.log('hello! :)');
                const bsr_collector = new CollectBSR(task.data.limit, task.data.count, task.data.target, task.data.unique_brands, task.data.domain);
                console.log('BSR Collector created!');
                if (!task?.data?.bsr) {
                    console.log('Fail!');
                    return {errors: ['Can not get BSR URL! Please enter full URL']};
                }
                let asins_links = {};
                console.log('Collect asins');
                for (const asin of bsr_collector.getASINsLInks(task.data.bsr)) {
                    asins_links[asin] = `https://${task.data.domain}/dp/${asin}`;
                }
                return {data: {bsr_url: task.data.bsr, asins_links: asins_links}};
            },
        });
        console.log('result!');
        data = result[0].result?.data;
        data.with_continue = Boolean(task.stage > 0);
        data.task_id = task._id;
        errors = result[0].result?.errors;
        console.log(data, errors);
        // handle errors
        if (errors) {
            fetch('http://195.201.194.213:8832/tasks/report/' + task._id, {
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
        fetch('http://195.201.194.213:8832/tasks/report/' + task._id, {
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
        if (created) {
            await chrome.tabs.remove(needle_tab.id);
        }
    }
}

chrome.runtime.onMessageExternal.addListener(run)
chrome.runtime.onMessage.addListener(run)
