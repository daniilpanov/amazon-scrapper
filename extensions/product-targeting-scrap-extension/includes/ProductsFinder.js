import { Queue } from './Queue';

class ProductsFinder {
    windowId;
    ASINsQueue;
    workers;
    activeTasks = 0;
    nextIndex = 0;
    dependencies = [];

    constructor(windowId, ASINsList, workers = 1) {
        this.windowId = windowId;
        this.ASINsQueue = new Queue(ASINsList);
        this.workers = workers;
    }

    createTabs(ASINs) {
        const resPromises = [];
        for (const ASIN of ASINs) {
            resPromises.push(chrome.tabs.create({
                windowId: this.windowId,
                url: 'https://www.amazon.com/dp/' + ASIN,
            }));
        }
        return resPromises;
    }

    next() {
        if (this.activeTasks >= this.workers) {
            return false;
        } else if (this.ASINsQueue.isEmpty()) {
            return true;
        }
        const newASINs = [];
        const limit = this.workers - this.activeTasks;
        for (let i = 0; i < limit; ++i, ++this.nextIndex, ++this.activeTasks) {
            const ASIN = this.ASINsQueue.dequeue();
            newASINs.push(ASIN);
        }
        const resPromises = this.createTabs(newASINs);
        for (const promise of resPromises) {
            // Tab created
            resPromises.then(((tab) => {
                // Libraries loaded
                this.loadLibraries(tab.id).then((() => {
                    // Execute script
                    this.executeScript(() => {

                    }, { tabId: tab.tabId }).then((() => {  // Script executed
                        // Tab closed
                        this.closeTab(tab.tabId).then((() => {
                            --this.activeTasks;
                        }));
                    }));
                }));
            }));
        }
    }

    loadLibraries(tabId) {
        return chrome.scripting.executeScript({
            target: {tabId: tabId},
            files: this.dependencies,
        });
    }

    executeScript(func, target, args = []) {
        return chrome.scripting.executeScript({
            target,
            args,
            func,
        });
    }

    closeTab(tabId) {
        return chrome.tabs.remove(tabId);
    }
}