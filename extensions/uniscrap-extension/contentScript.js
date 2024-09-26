async function sendTask(ext_name, data, script) {
    const all_extensions = await chrome.management.getAll();
    let found = false;
    let tabs = 0;
    for (const ext of all_extensions) {
        if (ext.name.toLowerCase().includes(ext_name)) {
            found = true;
            const msg = await chrome.runtime.sendMessage(ext.id, data);
            console.log('Message sent to', ext.name, `[${ext.id}]`);
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
        }
    }
    if (!found) {
        console.log('No extensions found for script', script);
    }
    return tabs;
}


const current_window = await chrome.windows.getCurrent();
let interval_id, tabs_limit = ((await chrome.tabs.query({windowId: current_window.id})).length || 2), curr_limit = tabs_limit;
const self = await chrome.management.getSelf();

async function main() {
    const config = getConfig();
    const curr_tabs_limit = tabs_limit + config.limit;
    // Limit by the tabs counting
    let tabs = await chrome.tabs.query({windowId: current_window.id});
    let is_finished;
    for (const tab of tabs) {
        try {
            is_finished = await chrome.scripting.executeScript({
                target: {tabId: tab.id},
                func: () => {
                    return window.finish_collecting || false;
                },
            });
            if (is_finished[0]?.result) {
                await chrome.tabs.remove(tab.id);
            }
        } catch (e) {
        }
    }
    tabs = await chrome.tabs.query({windowId: current_window.id});
    let tabs_count = tabs.length;
    if (tabs_count >= curr_tabs_limit) {
        console.log('exit from function! limit!', curr_tabs_limit, tabs_count);
        return interval_id = setTimeout(main, 10000);
    }
    curr_limit = curr_tabs_limit - tabs_count;
    try {
        const res = await fetch('http://195.201.194.213:8832/tasks/get_available');
        const data = await res.json();
        for (let i in data) {
            console.log('Available space left:', curr_limit, '; limit & count:', curr_tabs_limit, tabs_count);
            if (curr_limit <= 0) {
                console.log('exit from cycle! limit!');
                break;
            }
            if (data[i].script !== config.scriptType) {
                continue;
            }
            curr_limit -= await sendTask(config.extensionKeywords, {
                ...data[i].data,
                task_id: data[i]._id,
                header_id: data[i].header_id,
                stage: data[i].stage,
                alias: data[i].taskHeader.alias,
                windowId: current_window.id,
                script: data[i].script,
            }, data[i].script)
        }
    } catch (e) {
        console.log(e);
    }
    interval_id = setTimeout(main, 10000);
}

await main();