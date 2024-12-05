class BSRChildrenParser extends Parser {
    // elementsQuerySelector = 'div[role=group] > div[role=treeitem] > a, div[role=group] > div[role=treeitem] > span';
    waitElementQuerySelector = 'div.a-cardui';
    allFunctions = [this.getASINsList, this.getTree, this.getCurrent, this.getParent, this.getChildren];

    tree = [];
    flatTree = [];
    ASINsList = [];

    currentBSR = null;

    _getCategoryName(el) {
        return { bsrName: el.textContent.trim() || null };
    }

    _getCategoryLink(el) {
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
                if (item.id) {
                    this.ASINsList.push({ asin: item.id, rank: Number.parseInt(item.metadataMap['render.zg.rank']) });
                }
            }
        } catch (e) {
        }
        return { asins: this.ASINsList };
    }

    _findCurrent(elem) {
        for (const groupElement of (elem.group || [])) {
            if (groupElement.bsrLink === this.currentBSR.bsrLink && groupElement.bsrName === this.currentBSR.bsrName) {
                return elem;
            }
            const res = this._findCurrent(groupElement);
            if (res) {
                return res;
            }
        }
        return null;
    }

    getParent() {
        let parentBSR = { ...this._findCurrent({ group: this.tree }) };
        delete parentBSR.group;
        return { parentBSR };
    }

    getCurrent() {
        let currentBSR = { ...this.currentBSR };
        delete currentBSR.group;
        return { currentBSR };
    }

    _getTreeRecursive(treeGroup, group, level) {
        let lastObj = null;
        let index = 0;

        for (const treeElement of treeGroup) {
            if (treeElement.getAttribute('role') === 'treeitem') {
                const el = treeElement.children[0];
                lastObj = { index, ...this._getCategoryName(el), ...this._getCategoryLink(el), level };
                if (!lastObj.bsrLink) {
                    lastObj.bsrLink = location.href;
                    this.currentBSR = lastObj;
                }
                group.push(lastObj);
                this.flatTree.push(lastObj);
                ++index;
            } else {
                lastObj.group = [];
                this._getTreeRecursive(treeElement.children || [], lastObj.group, level + 1);
            }
        }
    }

    getTree() {
        this._getTreeRecursive(this.root.querySelector('div[role=tree]')?.children || [], this.tree, 0);
        return { tree: this.tree };
    }

    getChildren() {
        return { childrenBSR: this.currentBSR.group || [] };
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