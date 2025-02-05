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

    chrome.runtime.onMessageExternal.addListener(async (message, sender, sendResponse) => {
        let res = await fetch(
            await endp(':8832/tasks/acquire/h10/' + message.header_id + '/' + message.task_id),
            { method: 'post' },
        );
        if (res.status === 200) {
            sendResponse('OK');
            try {
                await startH10(message);
            } catch (e) {
                fetch(await endp(':8832/tasks/report/' + message.task_id), {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    method: 'PATCH',
                    body: JSON.stringify({
                        confirm: true,
                        errors: [(new Date().toUTCString()) + ' [h10] can\'t send the data'],
                        stop: true,
                    }),
                });
            }
        } else if (res.status === 409) {
            sendResponse('busy');
        } else {
            sendResponse('fail');
        }
    });
    chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
        let need_run = true;
        if (message.length) {
            for (let i in message) {
                if (i === 'fetch') {
                    need_run = false;
                    fetch(await endp(message[i][0]), message[i][1]).then((response) => {
                        sendResponse(response);
                    });
                }
            }
        }
        if (need_run) {
            let res = await fetch(
                await endp(':8832/tasks/acquire/h10/' + message.header_id + '/' + message.task_id),
                { method: 'post' },
            );
            if (res.status === 200) {
                sendResponse('OK');
                try {
                    await startH10(message);
                } catch (e) {
                    fetch(await endp(':8832/tasks/report/' + message.task_id), {
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        method: 'PATCH',
                        body: JSON.stringify({
                            confirm: true,
                            errors: [(new Date().toUTCString()) + ' [h10] can\'t send the data'],
                            stop: true,
                        }),
                    });
                }
            } else if (res.status === 409) {
                sendResponse('busy');
            } else {
                sendResponse('fail');
            }
        }
    });
});

async function startH10(task) {
    chrome.tabs.create({
        url: 'https://members.helium10.com/cerebro/?accountId=1545531519',
        windowId: task.windowId,
    }, async (tab) => {
        chrome.tabs.update(tab.id, { autoDiscardable: false });
        await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            files: ['helper.js', 'tasks/h10task.js'],
        });

        await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            args: [task],
            func: (task) => {
                runH10Task(task);
            },
        });
    });
    chrome.tabs.create({
        url: 'https://www.amazon.com/dp/' + task.asins[1],
        windowId: task.windowId,
    }, async (tab) => {
        chrome.tabs.update(tab.id, { autoDiscardable: false });
        await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            files: ['helper.js', 'tasks/h10product-task.js'],
        });

        await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            args: [task.task_id],
            func: (task_id) => {
                runProductTask(task_id);
            },
        });
    });
    chrome.tabs.create({
        url: 'https://www.amazon.com/dp/' + task.asins[0],
        windowId: task.windowId,
    }, async (tab) => {
        chrome.tabs.update(tab.id, { autoDiscardable: false });
        await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            files: ['helper.js', 'tasks/h10target-product-task.js'],
        });

        await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            args: [task.task_id],
            func: task_id => {
                runTargetProductTask(task_id);
            },
        });
    });
}
