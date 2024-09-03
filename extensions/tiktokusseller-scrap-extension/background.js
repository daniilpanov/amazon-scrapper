
async function scrap(request) {
    console.log(request);
    switch (request.action) {
        case 'NEWTAB':
            // TODO: add new method
            return 'unavailable';
        case 'CURRTAB':
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
        default:
            return 'bad request';
    }

}

async function runScrap(tabId, count) {
    await chrome.scripting.executeScript({
        target: {tabId: tabId},
        files: ['./tiktoksellerparser.js'],
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

function scrapWrapper(request, sender, sendResponse) {
    sendResponse('OK');
    scrap(request);
}

chrome.runtime.onMessage.addListener(scrap);
chrome.runtime.onMessageExternal.addListener(scrap);


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
        // Приводим к строке
        values = headers.map(header => {
            let item = (row[header] ?? '') + '';
            if (item.includes(',')) {
                item = '"' + item.replaceAll('"', '\\"') + '"';
            }
            return item;
        });
        csvRows.push(values.join(','));
    }

    return csvRows.join('\n');
}
