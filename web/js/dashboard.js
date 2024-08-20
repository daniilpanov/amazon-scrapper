///
const endpoint = 'http://195.201.194.213:8832/tasks/get_groups';
///
const pageContent = document.getElementById('main_row');

async function update() {
    try {
        const fromServerData = await getServerData(endpoint);
        if (fromServerData) {
            try {
                pageContent.innerHTML = '';

                const uniqueScripts = await sortByGroup(fromServerData);

                for (const element of uniqueScripts) {
                    const groupElement = document.createElement('div');
                    groupElement.classList.add('tasks-rect');
                    const infoBar = document.createElement('div');
                    infoBar.classList.add('tasks-rect-info');
                    const header = document.createElement('div');
                    header.classList.add('tasks-rect-header');
                    header.innerHTML = element?.script;
                    const status = document.createElement('div');
                    status.classList.add('tasks-rect-status');
                    let completedFully = 0;
                    let tasksGroups = 0;
                    let totalErrors = 0;
                    const aliases = [];

                    for (const key in element.aliases) {
                        ++tasksGroups;
                        const aliasElement = document.createElement('div');
                        aliasElement.classList.add('alias');
                        aliasElement.innerHTML += `<div class="alias-header">${key}</div>`;
                        let tasksCount = 0;
                        let errorsCount = 0;
                        let completedCount = 0;
                        for (const task of element.aliases[key]) {
                            ++tasksCount;
                            switch (task.status) {
                                case 3: ++completedCount; break;
                                case 4: ++errorsCount; break;
                                default: break;
                            }
                        }
                        if (tasksCount === completedCount) {
                            ++completedFully;
                        }
                        totalErrors += errorsCount;

                        aliasElement.innerHTML += `
                            <div class="alias-stage">Total tasks: ${tasksCount}<br />Completed: ${(completedCount / tasksCount * 100).toFixed(2)}%<br />Errors: ${errorsCount}</div>
                            <div class="alias-progress"></div>`;
                        aliases.push(aliasElement);
                    }

                    status.innerHTML = `Done: ${completedFully} of ${tasksGroups}<br />Errors: ${totalErrors}`;
                    infoBar.appendChild(header);
                    infoBar.appendChild(status);
                    groupElement.appendChild(infoBar);
                    pageContent.appendChild(groupElement);

                    aliases.forEach(aliasElement => groupElement.appendChild(aliasElement));
                }
            } catch (error) {
                console.log(error);
                pageContent.innerHTML = '<h4>Unknown error. Check console</h4>';
            }
        } else {
            pageContent.innerHTML = '<h4>No active tasks</h4>';
        }
    } catch (error) {
        console.log(error);
        // pageContent.innerHTML = '<h1>Data fetching error. Check console</h1>';
    }
}

update();
setInterval(update, 10000);

async function getServerData(url) {
    const response = await fetch(url).then((res) => res.json());
    if (!response) throw new Error('Fetching error');
    if (!response.length) return false;
    return response;
}

async function sortByGroup(arr) {
    const scriptMap = new Map();
    let counter = 0;

    arr.forEach(obj => {
        const script = obj.script;

        if (!scriptMap.has(script)) {
            scriptMap.set(script, { taskBodies: [], alias: {} });
        }

        const scriptData = scriptMap.get(script);
        scriptData.taskBodies.push(...obj.taskBodies);

        if (!scriptData.alias[`${obj.alias} (#${counter})`]) {
            scriptData.alias[`${obj.alias} (#${counter})`] = [];
        }
        scriptData.alias[`${obj.alias} (#${counter})`].push(...obj.taskBodies);
        counter++;
    });

    return Array.from(scriptMap.entries(), ([script, value]) => ({
        script,
        aliases: Object.fromEntries(Object.entries(value.alias).map(([aliasName, taskBodies]) => [aliasName, taskBodies]))
    }));
}