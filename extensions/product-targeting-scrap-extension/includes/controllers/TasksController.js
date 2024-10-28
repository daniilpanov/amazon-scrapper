import { Queue } from '../Queue';

class TasksController {
    tasksQueue = new Queue();
    limit = 1;

    constructor(limit) {
        if (limit) {
            this.limit = limit;
        }
    }
}