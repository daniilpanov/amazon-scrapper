// const status = document.getElementById('status');
const scrapeButton = document.getElementById('toParseButton');
// const pagesCounter = document.getElementById('pagesCounter');
const totalPagesCount = document.getElementById('totalPagesCount');

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
            action: 'CURRTAB',
            tabId: (await chrome.tabs.query({ currentWindow: true, active: true }))[0].id,
            count: num,
        }, (res) => {
            console.log(res);
            // status.innerHTML = 'Status: end';
        });
    } catch (e) {
    }
});
