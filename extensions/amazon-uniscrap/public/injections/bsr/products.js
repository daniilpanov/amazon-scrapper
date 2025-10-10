function getWaitProductsQuerySelector() { return 'div.a-cardui [data-asin]'; }

function findASINsList(rankShift = 0) {
    const element = document.querySelector('[data-client-recs-list]');
    if (!element) return [];
    const ASINsList = [];
    try {
        const data = JSON.parse(element.getAttribute('data-client-recs-list'));
        for (const item of data)
            ASINsList.push({ asin: item.id, rank: Number.parseInt(item.metadataMap['render.zg.rank']) + rankShift });
    } catch (e) { }
    return ASINsList;
}
