import Stomp from './stomp';
import browser from 'webextension-polyfill';
import { tiktokProcess } from './processes/tiktok-process';
import { kalodataProcess } from './processes/kalodata-process';
import { jungleScoutProcess } from './processes/jungle-scout-process';
import { waitWhileProcess } from './processes/wait-while-process';
import { KWTProcess } from './processes/kwt-process';
import { BSRProcess } from './processes/bsr-process';

/// TYPES ///
type Action = (message: any) => any;
type ActionMap = { [key: string]: Action };
type HandlersMap = { [queue: string]: { action: string, state: boolean } };
type MsgType = {
    action: string;
    data: any;
};
type BrowserStorageCache = {
    oldValue?: any,
    newValue?: any,
};

/// VALUES ///
const actions: ActionMap = {
    getHandlers,
    sendMessage,
    tiktokProcess,
    kalodataProcess,
    jungleScoutProcess,
    waitWhileProcess,
    KWTProcess,
    BSRProcess,
};

const queueHandlers: HandlersMap = {
    'tiktok': { action: 'tiktokProcess', state: false },
    'kalodata': { action: 'kalodataProcess', state: false },
    'junglescout': { action: 'jungleScoutProcess', state: false },
    'spfd': { action: 'waitWhileProcess', state: false },
    'kwt': { action: 'KWTProcess', state: true },
    'bsr': { action: 'BSRProcess', state: true },
};

let stompConnection: Stomp | null = null;

/// FUNCTIONS ///
function getHandlers() { return queueHandlers; }

async function init() {
    await browser.storage.local.set({
        'stomp': true,
        'subscriptions': queueHandlers,
    });
}

function sendMessage(data: any) {
    if (!stompConnection) return;
    if (!data.queue || typeof data.queue !== 'string') return;

    if (!stompConnection.connected)
        fullConnectSTOMP().then(() => stompConnection!.sendMessage(data.queue, data.msg, data.headers));
    else
        stompConnection.sendMessage(data.queue, data.msg, data.headers);
}

function fetchTimeout(url: string, timeout: number = 3000, options: any = {}): Promise<Response> {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    return fetch(url, {...options, signal: controller.signal})
        .finally(() => clearTimeout(id));
}

async function fullConnectSTOMP() {
    if (!(await browser.storage.local.get('stomp')).stomp as boolean) {
        stompConnection = null;
        return null;
    }

    const address = import.meta.env.VITE_STOMP_HOST;
    await fetchTimeout('http://' + address + ':15672');
    stompConnection = new Stomp(`ws://${address}:15674/ws`, 5);

    for (const queue in queueHandlers) {
        stompConnection.subscribe(`/amq/queue/${queue}`, actions[queueHandlers[queue].action]);
        stompConnection.updateSubscription(`/amq/queue/${queue}`, queueHandlers[queue].state);
    }

    await stompConnection.connect();
    return stompConnection;
}

/// CODE ///
browser.storage.local.get('stomp').then(async ({ isStompActive }) => {
    if (typeof isStompActive !== 'boolean') await init();
}).catch(init);

browser.storage.local.get('subscriptions').then(({ subscriptions }) => {
    for (const queue in subscriptions)
        queueHandlers[queue] = subscriptions[queue];
});

fullConnectSTOMP();

/// LISTENERS ///
browser.runtime.onInstalled.addListener(init);

browser.storage.local.onChanged.addListener(async (changes: { [key: string]: BrowserStorageCache }) => {
    if (changes.stomp?.newValue === false) {
        if (stompConnection) {
            stompConnection.needReconnect = false;
            stompConnection.disconnect();
            stompConnection = null;
        }
        return;
    } else if (changes.stomp?.newValue === true) {
        if (!stompConnection) fullConnectSTOMP();
    }

    if (changes.subscriptions && stompConnection) {
        const newSubs = changes.subscriptions.newValue;
        for (const [queue, active] of Object.entries(newSubs)) {
            queueHandlers[queue].state = active as boolean;
            stompConnection.updateSubscription(`/amq/queue/${queue}`, active as boolean);
        }
    }
});

browser.runtime.onMessage.addListener((message: MsgType, sender, sendResponse: (res?: any) => void) => {
    console.log('Message sent: ' + JSON.stringify(message));
    if (typeof message === 'object') {
        if (message.hasOwnProperty('action') && actions.hasOwnProperty(message.action)) {
            const res = actions[message.action](message.data);
            if (typeof res.then === 'function') sendResponse();
            else sendResponse(res);
        }
    }
});
