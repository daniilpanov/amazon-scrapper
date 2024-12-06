AbortSignal.timeout ??= function timeout(ms) {
    const ctrl = new AbortController();
    setTimeout(() => ctrl.abort(), ms);
    return ctrl.signal;
};

let lastUpdate = Date.now();
const urlList = [
    'https://localhost',
    'http://localhost',
    'https://cp.nyle.ai',
    'http://cp.nyle.ai',
    'https://195.201.194.213',
    'http://195.201.194.213',
];
let currentUrl = urlList[0];

const URL_EXPIRATION_TIME = 5 * 60 * 1000;

async function endp(uri, force = false) {
    if (!force && Date.now() - lastUpdate < URL_EXPIRATION_TIME) {
        return currentUrl + uri;
    }

    for (const url of urlList) {
        try {
            const response = await fetch(url + ':8832/ping', { method: 'GET', signal: AbortSignal.timeout(5000) });
            console.log(response.ok);
            if (response.ok) {
                currentUrl = new URL(url).origin;
                lastUpdate = Date.now();
                return currentUrl + uri;
            }
        } catch (error) {
            console.log(error);
        }
    }

    return null;
}

console.log('URL:', await endp(':8832/ping', true));

async function sendTask(data) {
    const msg = await chrome.runtime.sendMessage(data);
    console.log('Message sent');
    switch (msg) {
        case 'OK':
            console.log('task started:', data);
            break;
        case 'fail':
            console.log('task can not be started due to unknown error:', data);
            break;
        case 'busy':
            console.log('task is busy:', data);
            break;
        default:
            console.log('no message!');
            break;
    }
}

const current_window = await chrome.windows.getCurrent();
const config = { limit: 2 };
let tabs_count = ((await chrome.tabs.query({ windowId: current_window.id })).length || 2);
const real_tabs_limit = tabs_count + config.limit;
const self = await chrome.management.getSelf();
let interval_id, curr_limit;

async function main() {
    // Limit by the tabs counting
    let tabs = await chrome.tabs.query({ windowId: current_window.id });
    tabs_count = tabs.length;
    if (tabs_count >= real_tabs_limit) {
        console.log('exit from function! limit!', real_tabs_limit, tabs_count);
        return interval_id = setTimeout(main, 10000);
    }
    curr_limit = real_tabs_limit - tabs_count;
    for (let i = 0; i <= 1; ++i) {
        try {
            const res = await fetch(await endp(':8832/tasks/get_available/bsr?stage=' + i));
            const data = await res.json();
            for (let i in data) {
                console.log('Available space left:', curr_limit, '; limit & count:', real_tabs_limit, tabs_count);
                if (curr_limit <= 0) {
                    console.log('exit from cycle! limit!');
                    break;
                }
                await sendTask({
                    ...data[i].data,
                    task_id: data[i]._id,
                    header_id: data[i].header_id,
                    stage: data[i].stage,
                    alias: data[i].taskHeader.alias,
                    windowId: current_window.id,
                    script: data[i].script,
                });
                --curr_limit;
            }
        } catch (e) {
            console.log(e);
        }
    }
    interval_id = setTimeout(main, 10000);
}

await main();