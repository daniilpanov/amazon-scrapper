async function getElementLinks(shift = 0) {
    const rootEl = document.getElementsByClassName('arco-table-body');
    if (!rootEl || !rootEl.length) {
        return false;
    }

    const all_rows = rootEl[0].getElementsByTagName('tr');
    if (!all_rows || !all_rows.length) {
        return false;
    }

    return [...all_rows].slice(shift);
}

async function scrapeNewPage() {
    try {
        const res = await chrome.runtime.sendMessage({
            action: 'L2P',
        });
        return JSON.parse(res);
    } catch (e) {
        console.log(e);
        return null;
    }
}

