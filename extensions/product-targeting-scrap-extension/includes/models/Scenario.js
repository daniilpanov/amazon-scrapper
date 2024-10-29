export class Scenario {
    tabId = null;
    dependencies = [];
    functions = [];

    constructor(deps) {
        this.dependencies = deps || [];
    }


    addDependency(file) {
        this.dependencies.push(file);
    }

    createTab(url) {
        return chrome.tabs.create({
            url: url,
        }, (tab) => { this.tabId = tab.id; });
    }

    loadDependencies() {
        return chrome.scripting.executeScript({
            target: { tabId: this.tabId },
            files: this.dependencies,
        });
    }

    appendFunction(f, ...args) {
        this.functions.push([f, args]);
    }

    applyFunctionsAsync() {
        const res = [];
        for (const f of this.functions) {
            res.push(chrome.scripting.executeScript({
                target: { tabId: this.tabId },
                args: f[1],
                func: f[0],
            }));
        }
        return res;
    }

    async applyFunctionsSync() {
        const res = [];
        for (const f of this.functions) {
            try {
                const t = await chrome.scripting.executeScript({
                    target: { tabId: this.tabId },
                    args: f[1],
                    func: f[0],
                });
                res.push(t?.result[0]);
            } catch (e) {
                res.push(e);
            }
        }
        return res;
    }
}
