chrome.storage.onChanged.addListener((changes, area) => {
    console.log(changes);
});

const status = document.getElementById('status');
const scrapeButton = document.getElementById('toParseButton');
const fullScrapeButton = document.getElementById('toFullParseButton');
// const pagesCounter = document.getElementById('pagesCounter');
const totalPagesCount = document.getElementById('totalPagesCount');

const localData = await chrome.storage.local.get();
status.innerHTML = localData?.tasks ? localData.tasks + ' tasks active' : 'No tasks';

scrapeButton.addEventListener('click', async () => {
    let num;
    try {
        num = Number.parseInt(totalPagesCount.value) || 100;
    } catch (e) {
        totalPagesCount.value = num = 100;
    }
    // status.innerHTML = 'Status: in process';
    try {
        await chrome.runtime.sendMessage({
            action: 'L1',
            tabId: (await chrome.tabs.query({ currentWindow: true, active: true }))[0].id,
            count: num,
        }, async (res) => {
            const count = await chrome.storage.local.get();
            await chrome.storage.local.set({tasks: count + 1});
            console.log(res, count);
        });
    } catch (e) {
    }
});

fullScrapeButton.addEventListener('click', async () => {
    let num;
    try {
        num = Number.parseInt(totalPagesCount.value) || 100;
    } catch (e) {
        totalPagesCount.value = num = 100;
    }
    // status.innerHTML = 'Status: in process';
    try {
        await chrome.runtime.sendMessage({
            action: 'L2',
            tabId: (await chrome.tabs.query({ currentWindow: true, active: true }))[0].id,
            count: num,
        }, async (res) => {
            console.log(res);
            const count = await chrome.storage.local.get();
            await chrome.storage.local.set({tasks: count.tasks + 1});
            console.log(res, count);
        });
    } catch (e) {
    }
});
