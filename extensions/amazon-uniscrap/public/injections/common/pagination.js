function paginationCheck() {
    const pagination = document.querySelector('.s-pagination-strip > ul, ul.a-pagination');
    if (!pagination || !pagination.children.length) {
        return false;
    }

    return pagination.children[pagination.children.length - 1].tagName !== 'SPAN';
}

function paginationClick() {
    const pagination = document.querySelector('.s-pagination-strip > ul, ul.a-pagination');
    pagination.children[pagination.children.length - 1].querySelector('a').click();
}

function paginationCheckAndClick(withDelay = null) {
    const pagination = document.querySelector('.s-pagination-strip > ul, ul.a-pagination');
    if (!pagination || !pagination.children.length) {
        return false;
    }

    if (pagination.children[pagination.children.length - 1].tagName === 'SPAN') {
        return false;
    }
    return withDelay ? new Promise((resolve) => {
        pagination.children[pagination.children.length - 1].querySelector('a').click();
        setTimeout((r) => { r(true); }, withDelay, resolve);
    }) : (pagination.children[pagination.children.length - 1].querySelector('a').click() || true);
}