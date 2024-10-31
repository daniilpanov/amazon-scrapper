class BSRChildDepsParser extends MultiParser {
    elementsQuerySelector = 'div[role=group] > div[role=treeitem]';
    MP = null;

    getCategoryName(el) {
        return { bsrLink: el.href || el.getAttribute('href') || null };
    }

    getLink(el) {
        return { bsrLink: el.href || el.getAttribute('href') || null };
    }

    getASINsList() {
        return (this.MP || (this.MP = new BSRMultiParser())).findASINsList();
    }
}