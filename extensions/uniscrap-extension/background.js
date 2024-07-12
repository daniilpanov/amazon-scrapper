import pako from './pako.esm.mjs';

chrome.tabs.query({
    url: 'chrome-extension://' + chrome.runtime.id + '/control_panel.html',
}, (tabs) => {
    if (!tabs || !tabs.length) {
        chrome.tabs.create({
            url: 'control_panel.html',
            // autoDiscardable: false,
        });
    }
});
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
