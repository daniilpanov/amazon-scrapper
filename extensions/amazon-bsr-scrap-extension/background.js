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
    chrome.runtime.onMessage.addListener(run);
});

async function run(task, sender, sendResponse) {
    let acq = await fetch(
        'http://195.201.194.213:8832/tasks/acquire/bsr/' + task.header_id + '/' + task.task_id,
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
    if (task.bsr.startsWith('http://')) {
        task.bsr = task.bsr.slice(7);
    } else if (task.bsr.startsWith('https://')) {
        task.bsr = task.bsr.slice(8);
    }
    if (task.bsr.startsWith(task.domain)) {
        task.bsr = task.bsr.slice(task.domain.length + 1);
    } else if (task.bsr.startsWith('www.' + task.domain)) {
        task.bsr = task.bsr.slice(task.domain.length + 5);
    }
    let needle_tab = await chrome.tabs.create({
        url: 'https://www.' + task.domain + '/' + task.bsr,
        active: false,
        windowId: task.windowId,
    });
    chrome.tabs.update(needle_tab.id, { autoDiscardable: false });

    const date = new Date();
    try {
        // BSR lib
        await chrome.scripting.executeScript({
            target: { tabId: needle_tab.id },
            files: ['./includesInTab/parser.js', './includesInTab/bsrchildren.js'],
        });
        console.log('bsr imported');
        // BSR result
        let result = await chrome.scripting.executeScript({
            target: { tabId: needle_tab.id },
            args: [task.target],
            func: async target => {
                const bsr_collector = new BSRChildrenParser();
                await bsr_collector.waitLoading();
                bsr_collector.appendFunctions([bsr_collector.getASINsList, bsr_collector.getTree, bsr_collector.getCurrent]);
                let res = bsr_collector.applyFunctions();
                delete res.tree;
                let found = false;
                for (const asin of res.asins) {
                    if (asin === target) {
                        found = true;
                        break;
                    }
                }
                if (!found) {
                    res.asins = [...res.asins, { asin: target }];
                }
                return res;
            },
        });
        result = result[0]?.result;
        result.with_continue = Boolean(task.stage > 0);
        result.task_id = task.task_id;
        // load data
        if (Object.keys(result || {}).length) {
            fetch(await endp(':8832/cmd/alias/bsr/finish/'), {
                headers: {
                    'Content-Type': 'application/json',
                },
                method: 'POST',
                body: JSON.stringify(result),
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
                    date.toISOString() + ' [bsr] Error: ' + e.message,
                ],
                stop: true,
            }),
        });
    } finally {
        await chrome.tabs.remove(needle_tab.id);
    }
}
