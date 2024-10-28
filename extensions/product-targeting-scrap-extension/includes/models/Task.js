import { Queue } from '../Queue';

class Task {
    res = {};  // { scenario_name: result, ... }
    orderedTasks = new Queue();  // tasks keys queue
    tasksMap = {};  // { scenario_name: function, ... }
    currentKey = null;
    resParts = {};

    constructor(tasksMap, order) {
        if (tasksMap) {
            this.tasksMap = tasksMap;
        }
        if (order) {
            this.orderedTasks.elements = order;
        } else {
            this.orderedTasks.elements = [...Object.keys(tasksMap)];
        }
    }

    writeRes(val) {
        this.res[this.currentKey] = val;
    }

    appendRes(r) {
        this.resParts = { ...this.resParts, ...r };
    }

    getRes(k) {
        return k ? this.res[k] : this.res;
    }

    _nextKey() {
        this.res = this.resParts;
        this.resParts = {};
        return (this.currentKey = (this.orderedTasks.dequeue() || null));
    }

    nextFunc() {
        const key = this._nextKey();
        return key ? this.tasksMap[key] : null;
    }
}