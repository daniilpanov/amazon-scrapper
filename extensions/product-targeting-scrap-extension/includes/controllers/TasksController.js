import { Queue } from '../Queue';
import { Task } from '../models/Task';

export class TasksController {
    tasksQueue = new Queue();
    limit = 1;
    free = this.limit;

    constructor(limit) {
        if (limit) {
            this.free = this.limit = limit;
        }
    }

    _startIfFree() {
        if (!this.tasksQueue.size()) {
            return null;
        }
        if (!this.free) {
            return false;
        }
        --this.free;
        return this.tasksQueue.dequeue();  // start task
    }

    buildTask(funcsMap, funcsOrder) {
        const task = new Task(funcsMap, funcsOrder);
        this.tasksQueue.enqueue(task);
        return this._startIfFree();
    }

    addResult(res) {

    }
}