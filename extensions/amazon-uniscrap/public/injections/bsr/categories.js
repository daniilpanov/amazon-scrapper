function getWaitTreeQuerySelector() { return 'div.a-cardui'; }

function _getCategoryName(el) {
    return { bsrName: el.textContent.trim() || null };
}

function _getCategoryLink(el) {
    return { bsrLink: el.href || el.getAttribute('href') || null };
}

function _getTreeRecursive(flatTree, treeGroup, group, level) {
    let currentBSR = null;
    let selectedBSR = null;
    let index = 0;

    for (const treeElement of treeGroup) {
        if (treeElement.getAttribute('role') === 'treeitem') {
            const el = treeElement.children[0];
            currentBSR = { index, ..._getCategoryName(el), ..._getCategoryLink(el), level };
            if (!currentBSR.bsrLink) {
                currentBSR.bsrLink = location.href;
                selectedBSR = currentBSR;
            }
            group.push(currentBSR);
            flatTree.push({
                bsrLink: currentBSR.bsrLink,
                bsrName: currentBSR.bsrName,
                index,
                level,
            });
            ++index;
        } else {
            currentBSR.group = [];
            selectedBSR = _getTreeRecursive(flatTree, treeElement.children || [], currentBSR.group, level + 1) ?? selectedBSR;
        }
    }
    if (selectedBSR?.group) delete selectedBSR.group;
    return selectedBSR;
}

function getTree() {
    const flatTree = [];
    const tree = [];
    const currentBSR = _getTreeRecursive(flatTree, document.querySelector('div[role=tree]')?.children || [], tree, 0);
    return { tree, flatTree, currentBSR };
}
