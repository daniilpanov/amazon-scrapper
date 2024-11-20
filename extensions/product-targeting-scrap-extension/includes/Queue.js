export class Queue {
    elements;

    constructor(els = []) {
        this.elements = els;
    }

    enqueue(el) {
        this.elements.push(el);
    }

    dequeue() {
        return this.elements.shift();
    }

    front() {
        return this.elements[0];
    }

    isEmpty() {
        return this.size() === 0;
    }

    size() {
        return this.elements.length;
    }
}