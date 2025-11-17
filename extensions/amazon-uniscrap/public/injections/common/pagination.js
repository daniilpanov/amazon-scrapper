const paginationUlElementQuerySelector = '.s-pagination-strip > ul, ul.a-pagination';

function getLastPaginationLink() {
    const pagination = document.querySelector(paginationUlElementQuerySelector);
    if (!pagination || !pagination.children.length)
        return false;

    return pagination.children[pagination.children.length - 1].querySelector('& > span > a');
}

function clickToNextPage() {
    const lastElement = getLastPaginationLink();
    if (!lastElement)
        return false;

    lastElement.click();
    return true;
}

async function waitAndClickToNextPage(timeout = 1000) {
    if (await waitLoading(paginationUlElementQuerySelector, timeout))
        return clickToNextPage();
}
