// SORRY FOR THIS LEGACY CODE, I TRIED BE AS FAST AS I CAN :)

// Initialize varialbe
chrome.runtime.onInstalled.addListener(function(details) {
    chrome.storage.local.set({ tasks: 0 });
});


// Connection for transferring the data
chrome.runtime.onConnect.addListener(function(port) {
    // Add Event Listener to the port
    port.onMessage.addListener(async function(msg) {
        // Collection end
        if (msg.action === 'end') {
            port.disconnect();
            const count = await chrome.storage.local.get();
            await chrome.storage.local.set({ tasks: count.tasks - 1 });
            return;
        }
        // Get the tab
        let tab = (await chrome.tabs.query({ currentWindow: true, active: true }))[0];
        // If the current tab is not TikTok, wait for 100000 ms until tab switching
        for (let i = 0; i < 100 && (tab.status !== 'complete' || tab.title !== 'TikTok Shop Affiliate'); ++i) {
            await new Promise((r) => setTimeout(r, 100));
            tab = (await chrome.tabs.query({ currentWindow: true, active: true }))[0];
        }
        // Final check
        if (tab.title === 'TikTok Shop Affiliate') {
            const tabId = tab?.id;
            // Run scraping
            const res = await runProfileScrap(tabId);
            // Return the result
            port.postMessage(res);
        } else {
            port.postMessage(null);
        }
    });
});

// This is the function-router
async function scrap(request, send = null) {
    // Sorry for switch-case. it's just the fastest variant
    switch (request.action) {
        // Simple list scrap
        case 'L1':
            if (typeof request.tabId !== 'undefined' && request.tabId !== null) {
                const data = await runScrap(request.tabId, request.count || 100);
                if (data && data.length) {
                    const filedata = convertToCSV(data);
                    await chrome.scripting.executeScript({
                        target: { tabId: request.tabId },
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
        // Detailed profiles scrap
        case 'L2':
            if (typeof request.tabId !== 'undefined' && request.tabId !== null) {
                const data = await runFullScrap(request.tabId, request.count || 100);
                if (data && data.length === 2 && data[0].length) {
                    const filedata = convertToCSV(data[0], data[1]);
                    await chrome.scripting.executeScript({
                        target: { tabId: request.tabId },
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

// Simple list scrap
async function runScrap(tabId, count) {
    // Include needle 'in-tab' scripts
    await chrome.scripting.executeScript({
        target: { tabId: tabId },
        files: ['./utils.js', './tiktoksellerparser.js'],
    });
    // Scrape the list
    let data = [];
    for (let i = 0; i < count;) {
        let result = await chrome.scripting.executeScript({
            target: { tabId: tabId },
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
        i += result.length;  // increment is here
        data = [...data, ...result];
    }
    if (data && data.length) {
        return data;
    }
    return false;
}


// Detailed profile scrap (in this function opens only list tab)
async function runFullScrap(tabId, count) {
    // 'in-tab' includes
    await chrome.scripting.executeScript({
        target: { tabId: tabId },
        files: ['./utils.js', './tiktokgetlinks.js'],
    });
    // Initialize very long 'in-tab' function that connects to the background runtime, OPENS profiles tab, GETS result from the port and returns the result
    let result = await chrome.scripting.executeScript({
        target: { tabId: tabId },
        args: [count],
        func: async (count) => {
            let rows = [];
            // Gets the elements links
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
            let headers = new Set();
            const res = await new Promise(async r => {
                port = chrome.runtime.connect();
                const data = [];
                let row;
                // Send data to the port
                port.onMessage.addListener(async (msg) => {
                    if (msg) {
                        headers = headers.union(new Set(msg.headers));
                        delete msg.headers;
                        data.push(msg);
                    }
                    if (data.length >= count || !rows.length) {
                        return r(data);
                    }
                    row = rows.shift();
                    row.scrollIntoView();
                    row.click();
                    // Open a new profile signal
                    port.postMessage({});
                });
                row = rows.shift();
                row.scrollIntoView();
                row.click();
                // Open a new profile signal
                port.postMessage({});
            });
            if (port) {
                port.postMessage({ action: 'end' });
                try {
                    port.disconnect();
                } catch (e) {
                }
            }
            // All result
            return [res, headers.values().toArray()];
        },
    });
    // All result
    result = result[0]?.result || null;
    if (result && result.length) {
        return result;
    }
    return null;
}

// This function do the detailed scraping: goto each profile and scrap it
async function runProfileScrap(tabId) {
    await chrome.scripting.executeScript({
        target: { tabId: tabId },
        files: ['./tiktokprofile.js'],
    });
    let result = await chrome.scripting.executeScript({
        target: { tabId: tabId },
        args: [],
        // DON'T OPTIMIZE IT TO func: parsePage!!! In This script this function is undefined
        // This function exists only in the tab!
        func: () => {
            return parsePage();
        },
    });
    result = result[0]?.result || null;
    chrome.tabs.remove(tabId);  // close redundant tab
    return result;
}

// Wrapper for async call
function scrapWrapper(request, sender, sendResponse) {
    sendResponse('OK');
    scrap(request);
}

chrome.runtime.onMessage.addListener(scrapWrapper);
chrome.runtime.onMessageExternal.addListener(scrapWrapper);


function convertToCSV(arr, headers) {
    const csvRows = [];
    let values = [];
    // Take the headers from the first object keys if not exists
    if (!headers) {
        headers = Object.keys({ ...arr[0] });
    }
    for (const header of headers) {
        values.push('"' + header + '"');
    }
    csvRows.push(values.join(','));
    // Translate each object to the CSV-row
    for (let row of arr) {
        row = { ...row };
        console.log(row);
        // ...to the string
        values = headers.map(header => {
            let item = row[header];
            if (typeof item === 'object' && item) {
                item = JSON.stringify(item);
            } else {
                item = (item ?? '') + '';
            }
            if (item.includes(',')) {
                item = '"' + item.replaceAll('"', '\\"') + '"';
            }
            return item;
        });
        csvRows.push(values.join(','));
    }

    return csvRows.join('\n');
}
