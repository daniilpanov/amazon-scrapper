chrome.tabs.query({
    url: 'chrome-extension://' + chrome.runtime.id + '/html/control_panel.html',
}, tabs => {
    if (!tabs || !tabs.length) {
        chrome.tabs.create({
            url: 'html/control_panel.html',
        }, (tab) => {
            chrome.tabs.update(tab.id, { autoDiscardable: false });
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


chrome.runtime.onMessageExternal.addListener(async (message, sender, sendResponse) => {
    let res = await fetch(
        'http://195.201.194.213:8832/tasks/acquire/h10/' + message.header_id + '/' + message.task_id,
        { method: 'post' },
    );
    if (res.status === 200) {
        sendResponse('OK');
        try {
            await startH10(message);
        } catch (e) {
            fetch('http://195.201.194.213:8832/tasks/report/' + message.task_id, {
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
            func: (task_id) => {
                runTargetProductTask(task_id);
            },
        });
    });
}
