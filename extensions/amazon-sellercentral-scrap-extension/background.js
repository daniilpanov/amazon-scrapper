import pako from "./pako.esm.mjs";

// Я смог только так запустить фоновый скрипт - открыл новую вкладку и запустил всё что нужно там))
// Это взято из других проектов, так что здесь это скорее всего не так необходимо. Если обойдёшься без этого - будет очень круто
chrome.tabs.query({
    // ищем страницу расширения среди уже открытых
    url: 'chrome-extension://' + chrome.runtime.id + '/control_panel.html',
}, (tabs) => {
    // если такой нет, то открываем новую
    if (!tabs || !tabs.length) {
        chrome.tabs.create({
            url: 'control_panel.html',
        });
    }
});

// т.к. sellercentral находится на сервере с HTTPS, а endpoint на сервере с HTTP, запрос блочится, поэтому все запросы выполняются через background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    for (let i in request) {
        // делаем fetch запрос
        if (i === 'fetch') {
            fetch(request[i][0], request[i][1]).then((response) => {
                sendResponse(response);
            });
        }
        // сжимаем данные через gzip
        else if (i === 'gzip') {
            sendResponse(pako.gzip(JSON.stringify(request[i])));
        }
    }
});
