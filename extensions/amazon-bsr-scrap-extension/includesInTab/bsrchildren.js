class BSRChildrenParser extends Parser {
    // elementsQuerySelector = 'div[role=group] > div[role=treeitem] > a, div[role=group] > div[role=treeitem] > span';
    waitElementQuerySelector = 'div.a-cardui';
    allFunctions = [this.getASINsList, this.getTree, this.getCurrent, this.getParent, this.getChildren];

    tree = {};
    flatTree = [];
    ASINsList = [];

    getCategoryName(el) {
        return { bsrName: el.textContent.trim() || null };
    }

    getCategoryLink(el) {
        return { bsrLink: el.href || el.getAttribute('href') || null };
    }

    getASINsList() {
        if (this.ASINsList && this.ASINsList.length) {
            return { asins: this.ASINsList };
        }
        const element = this.root.querySelector('[data-client-recs-list]');
        if (!element) {
            return { asins: (this.ASINsList = []) };
        }
        try {
            const data = JSON.parse(element.getAttribute('data-client-recs-list'));
            for (const item of data) {
                this.ASINsList.push({ asin: item.id, rank: Number.parseInt(item.metadataMap['render.zg.rank']) });
            }
        } catch (e) {
        }
        return { asins: this.ASINsList };
    }

    getParent() {

    }

    getCurrent() {

    }

    // mode: 1 - tree, -1 - flat, 0 - both
    getTree(treegroup = null, mode = 0, parent_obj = null, level = 0) {
        treegroup ??= this.root.querySelector('div[role=tree]');
        parent_obj ??= this.tree;

        for (const treeGroupElement in treegroup) {

        }
    }

    getChildren() {

    }

    clickNextPage() {
        const newPage = document.querySelector('.a-pagination .a-last:not(.a-disabled) > a');
        if (newPage) {
            newPage.click();
            return true;
        }
        return false;
    }
}