import { CompatClient, IMessage, Stomp, StompSubscription } from '@stomp/stompjs';

type TaskResult = void | boolean | Promise<void> | Promise<boolean>;
type TaskHandler = (task: any) => TaskResult;
type TaskConfig = {
    params: { [key: string]: string },
    active: boolean,
    func: TaskHandler,
    subscription?: StompSubscription,
};

export default class StompConnection {
    private stompClient?: CompatClient;
    private readonly sockURL: string;
    private readonly maxConcurrentTasks: number;

    private subscriptions: Map<string, TaskConfig> = new Map();

    public onTaskStarted?: TaskHandler;
    public onTaskFinished?: TaskHandler;

    private maxReconnectionCount: number = 10;
    private reconnectionCount: number = 0;
    public needReconnect: boolean = true;
    public resetNeedReconnect: boolean = true;


    constructor(url: string, maxConcurrentTasks: number) {
        this.maxConcurrentTasks = maxConcurrentTasks;
        this.sockURL = url;
    }

    get connected(): boolean { return this.stompClient?.connected as boolean; }

    public connect(err?: any): void | Promise<void> {
        if (!this.needReconnect || this.reconnectionCount >= this.maxReconnectionCount) {
            if (this.resetNeedReconnect)
                this.needReconnect = true;

            this.reconnectionCount = 0;
            return;
        }

        ++this.reconnectionCount;

        if (this.connected) {
            try {
                this.stompClient!.disconnect();
            } catch (e) {}
        }

        this.stompClient = Stomp.over(() => new WebSocket(this.sockURL));
        this.stompClient.onStompError = this.connect.bind(this);

        return new Promise(async (resolve, reject): Promise<void> => {
            if (err)
                console.log('Reconnecting due to the error:', err);

            if (!this.stompClient) {
                console.error('Connection error: no STOMP');
                return reject();
            }

            this.stompClient.connect(
                { login: 'guest', passcode: 'guest' },
                (frame: any) => {
                    console.log('Connected: ' + frame);
                    this.reconnectionCount = 0;
                    this.stompClient?.activate();

                    this.subscriptions.forEach((config: TaskConfig, queue: string) => {
                        if (config.active)
                            this.subscribe(queue, config.func, undefined, config.params);
                    });

                    return resolve(frame);
                },
                (error: any) => {
                    console.error('Connection error: ' + error);
                    return reject(error);
                },
            );
        });
    }

    public subscribe(queue: string, callback: TaskHandler, prefetch_count?: number, params?: {[key: string]: string}) {
        if (!params)
            params = {};

        if (!prefetch_count)
            prefetch_count = this.maxConcurrentTasks;

        params['durable'] = params['durable'] ?? 'true';
        params['ack'] = params['ack'] ?? 'client-individual';
        params['prefetch-count'] = params['prefetch-count'] ?? prefetch_count;

        // If a subscription exists, update it
        if (this.subscriptions.has(queue)) {
            const existingConfig = this.subscriptions.get(queue)!;
            existingConfig.func = callback;
            existingConfig.params = { ...params };
            existingConfig.active = true;

            // If a client connected, but a subscription is inactive, then creates a new one
            if (this.stompClient?.connected && !existingConfig.subscription) {
                existingConfig.subscription = this.stompClient.subscribe(
                    queue,
                    (task: any) => this.handleMessage(task, callback),
                    params,
                );
            }
            return;
        }

        // Create a new subscription
        const newConfig: TaskConfig = {
            func: callback,
            params: { ...params },
            active: true,
            subscription: undefined,
        };

        this.subscriptions.set(queue, newConfig);

        if (this.stompClient?.connected) {
            newConfig.subscription = this.stompClient.subscribe(
                queue,
                (task: any) => this.handleMessage(task, callback),
                params,
            );
        }
    }

    public unsubscribe(queue: string) {
        if (!this.subscriptions.has(queue))
            return;

        const config = this.subscriptions.get(queue)!;
        config.active = false;

        if (config.subscription) {
            config.subscription.unsubscribe();
            config.subscription = undefined;
        }
    }

    public updateSubscription(queue: string, active: boolean): void {
        if (!active)
            return this.unsubscribe(queue);

        const config = this.subscriptions.get(queue);
        if (config && !config.subscription && this.stompClient?.connected) {
            config.subscription = this.stompClient.subscribe(
                queue,
                (task: any) => this.handleMessage(task, config.func),
                config.params,
            );
            config.active = true;
        }
    }

    private async handleMessage(message: IMessage, callback: TaskHandler): Promise<void> {
        this.reconnectionCount = 0;

        let data = message.body;
        try {
            data = JSON.parse(data);
        } catch (e) {}

        if (this.onTaskStarted && !this.onTaskStarted(data))
            return message.nack();

        try {
            const res = await callback.bind(this)(data);
            if ((typeof res === 'undefined' || res) && (!this.onTaskFinished || this.onTaskFinished(data)))
                message.ack();
            else
                message.nack();
        } catch (e) {
            console.error('Error while processing a task:', message, e);
            message.nack({ requeue: "false" });
        }
    }

    public sendMessage(queue: string, message: any, headers?: { [key: string]: string }): void {
        if (!this.stompClient)
            return;

        if (!headers)
            headers = {};

        try {
            if (typeof message === 'string')
                this.stompClient.publish({
                    destination: queue,
                    headers: headers,
                    body: message,
                });
            else if (typeof message === 'object') {
                try {
                    this.stompClient.publish({
                        destination: queue,
                        headers: headers,
                        body: JSON.stringify(message),
                    });
                } catch (e) {
                    this.stompClient.publish({
                        destination: queue,
                        headers: headers,
                        body: String(message),
                    });
                }
            }
        } catch (e) {
            console.log(e);
            console.error(e);
        }
    }

    public disconnect(): void {
        if (!this.stompClient)
            return;

        this.subscriptions.forEach(({ active, subscription }) => {
            if (active && subscription)
                subscription.unsubscribe();
        });

        this.stompClient.disconnect();
    }
}
