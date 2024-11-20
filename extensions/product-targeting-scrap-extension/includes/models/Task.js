import { Queue } from '../Queue';

export class Task {
    res = {};  // { scenario_name: result, ... }
    orderedTasks = new Queue();  // tasks keys queue
    tasksMap = {};  // { scenario_name: function, ... }
    currentKey = null;
    resParts = {};
    startSignal = null;
    interruptSignal = null;

    constructor(tasksMap, order, { start, interrupt }) {
        if (tasksMap) {
            this.tasksMap = tasksMap;
        }
        if (order) {
            this.orderedTasks.elements = order;
        } else {
            this.orderedTasks.elements = [...Object.keys(tasksMap)];
        }
        if (start) {
            this.startSignal = start;
        }
        if (interrupt) {
            this.interruptSignal = interrupt;
        }
    }

    addInterrupt(interrupt) {
        this.interruptSignal = interrupt || null;
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

    start() {
        //  Call start signal if it set up
        return this.startSignal && (this.startSignal() || true) || false;
    }

    interrupt() {
        //  Call interrupt signal if it set up
        return this.interruptSignal && (this.interruptSignal() || true) || false;
    }
}