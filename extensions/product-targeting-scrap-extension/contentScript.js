async function sendTask(data) {
    let tabs = 0;
    const msg = await chrome.runtime.sendMessage(data);
    console.log('Message sent');
    switch (msg) {
        case 'OK':
            console.log('task started:', data);
            ++tabs;
            break;
        case 'fail':
            console.log('task can not be started due to unknown error:', data);
            break;
        case 'busy':
            console.log('task is busy:', data);
            break;
    }
    console.log(tabs);
    return tabs;
}


const current_window = await chrome.windows.getCurrent();
let interval_id, tabs_limit = ((await chrome.tabs.query({windowId: current_window.id})).length || 2), curr_limit = tabs_limit;
const self = await chrome.management.getSelf();

async function main() {
    const config = {limit: 2};
    // Limit by the tabs counting
    const curr_tabs_limit = tabs_limit + config.limit;
    let tabs = await chrome.tabs.query({windowId: current_window.id});
    let tabs_count = tabs.length;
    if (tabs_count >= curr_tabs_limit) {
        console.log('exit from function! limit!', curr_tabs_limit, tabs_count);
        return interval_id = setTimeout(main, 10000);
    }
    curr_limit = curr_tabs_limit - tabs_count;
    try {
        const res = await fetch('http://195.201.194.213:8832/tasks/get_available/pt');
        const data = await res.json();
        for (let i in data) {
            console.log('Available space left:', curr_limit, '; limit & count:', curr_tabs_limit, tabs_count);
            if (curr_limit <= 0) {
                console.log('exit from cycle! limit!');
                break;
            }
            curr_limit -= await sendTask({
                ...data[i].data,
                task_id: data[i]._id,
                header_id: data[i].header_id,
                stage: data[i].stage,
                alias: data[i].taskHeader.alias,
                windowId: current_window.id,
                script: data[i].script,
            })
        }
    } catch (e) {
        console.log(e);
    }
    interval_id = setTimeout(main, 10000);
}

await main();