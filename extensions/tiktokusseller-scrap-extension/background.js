chrome.runtime.onConnect.addListener(function (port) {
    port.onMessage.addListener(async function (msg) {
        if (msg.action === 'end') {
            port.disconnect();
            return;
        }
        let tab = (await chrome.tabs.query({ active: true }))[0];
        for (let i = 0; i < 100 && (tab.status !== 'complete' || tab.title !== 'TikTok Shop Affiliate'); ++i) {
            await new Promise((r) => setTimeout(r, 100));
            tab = (await chrome.tabs.query({ active: true }))[0];
        }
        if (tab.title === 'TikTok Shop Affiliate') {
            const tabId = tab?.id;
            const res = await runProfileScrap(tabId);
            port.postMessage(res);
        } else {
            port.postMessage(null);
        }
    });
});


async function scrap(request, send = null) {
    console.log(request);
    switch (request.action) {
        case 'L1':
            if (typeof request.tabId !== 'undefined' && request.tabId !== null) {
                const data = await runScrap(request.tabId, request.count || 100)
                if (data && data.length) {
                    const filedata = convertToCSV(data);
                    await chrome.scripting.executeScript({
                        target: {tabId: request.tabId},
                        args: [filedata],
                        func: (filedata) => {
                            downloadCSV(filedata, 'result.csv');
                        },
                    });
                    return 'OK';
                } else {
                    return 'invalid tab';
                }
            }
            break;
        case 'L2':
            if (typeof request.tabId !== 'undefined' && request.tabId !== null) {
                const data = await runFullScrap(request.tabId, request.count || 100)
                if (data && data.length) {
                    const filedata = convertToCSV(data);
                    await chrome.scripting.executeScript({
                        target: {tabId: request.tabId},
                        args: [filedata],
                        func: (filedata) => {
                            downloadCSV(filedata, 'result-full.csv');
                        },
                    });
                    return 'OK';
                } else {
                    return 'invalid tab';
                }
            }
            break;
        default:
            return 'bad request';
    }

}

async function runScrap(tabId, count) {
    await chrome.scripting.executeScript({
        target: {tabId: tabId},
        files: ['./utils.js', './tiktoksellerparser.js'],
    });
    let data = [];
    for (let i = 0; i < count;) {
        let result = await chrome.scripting.executeScript({
            target: {tabId: tabId},
            args: [i],
            func: async (i) => {
                try {
                    await scrollToTheEnd();
                    return parsePage(i);
                } catch (e) {
                    console.log(e);
                    return null;
                }
            },
        });
        console.log(result);
        result = result[0]?.result;
        if (!result || !result.length) {
            break;
        }
        i += result.length;
        data = [...data, ...result];
    }
    if (data && data.length) {
        return data;
    }
    return false;
}

async function runFullScrap(tabId, count) {
    await chrome.scripting.executeScript({
        target: {tabId: tabId},
        files: ['./utils.js', './tiktokgetlinks.js'],
    });
    let result = await chrome.scripting.executeScript({
        target: {tabId: tabId},
        args: [count],
        func: async (count) => {
            let rows = [];
            while (rows.length < count) {
                try {
                    await scrollToTheEnd();
                    rows = [...rows, ...await getElementLinks(rows.length)];
                } catch (e) {
                    console.log(e);
                    break;
                }
            }
            let port = null;
            const res = await new Promise(async (r) => {
                port = chrome.runtime.connect();
                const data = [];
                let row;
                port.onMessage.addListener(async (msg) => {
                    if (msg) {
                        data.push(msg);
                    }
                    if (data.length >= count || !rows.length) {
                        return r(data);
                    }
                    row = rows.shift();
                    row.scrollIntoView();
                    row.click();
                    port.postMessage({});
                });
                row = rows.shift();
                row.scrollIntoView();
                row.click();
                port.postMessage({});
            });
            if (port) {
                port.disconnect();
            }
            return res;
        },
    });
    console.log(result);
    result = result[0]?.result || null;
    if (result && result.length) {
        return result;
    }
    return null;
}

async function runProfileScrap(tabId) {
    await chrome.scripting.executeScript({
        target: {tabId: tabId},
        files: ['./tiktokprofile.js'],
    });
    let result = await chrome.scripting.executeScript({
        target: {tabId: tabId},
        args: [],
        func: () => {
            return parsePage();
        },
    });
    result = result[0]?.result || null;
    console.log(result);
    chrome.tabs.remove(tabId);
    return result;
}

function scrapWrapper(request, sender, sendResponse) {
    sendResponse('OK');
    scrap(request);
}

chrome.runtime.onMessage.addListener(scrapWrapper);
chrome.runtime.onMessageExternal.addListener(scrapWrapper);


function convertToCSV(arr) {
    // Взять заголовки из ключей первого объекта
    const csvRows = [];
    const headers = Object.keys({...arr[0]});
    let values = [];
    for (const header of headers) {
        values.push('"' + header + '"');
    }
    csvRows.push(values.join(','));
    // Преобразовать каждый объект в строку CSV
    for (let row of arr) {
        row = {...row};
        console.log(row);
        // Приводим к строке
        values = headers.map(header => {
            let item = row[header];
            if (typeof item === 'object' && item) {
                item = JSON.stringify(item);
            } else {
                item = (item ?? '') + '';
            }
            if (item.includes(',')) {
                item = '"' + item.replaceAll('"', '\"') + '"';
            }
            return item;
        });
        csvRows.push(values.join(','));
    }

    return csvRows.join('\n');
}
