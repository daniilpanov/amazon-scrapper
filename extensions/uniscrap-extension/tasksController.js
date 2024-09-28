const tasksListTable = document.getElementById('tasksList');
const taskRowTemplate = document.getElementById('taskRowTemplate');

const scriptTypesSelect = document.getElementById('scriptTypes');
const customScriptTypeInput = document.getElementById('customScriptType');
const extensionKeywordsInput = document.getElementById('extensionKeywords');
const tasksLimitInput = document.getElementById('tasksLimit');
const saveConfigButton = document.getElementById('saveConfig');

let savedConfig = {
    scriptType: null,
    extensionKeywords: null,
    limit: 10,
};

let currentConfig = {
    scriptType: null,
    extensionKeywords: null,
    limit: 10,
};

const baseConfig = {
    'bsr': {
        scriptType: 'bsr',
        extensionKeywords: 'amazon bsr scraper',
        limit: 2,
    },
    'products': {
        scriptType: 'products',
        extensionKeywords: 'amazon products scraper',
        limit: 5,
    },
    'h10': {
        scriptType: 'h10',
        extensionKeywords: 'amazon helium10 scraper',
        limit: 3,
    },
    '100asins': {
        scriptType: '100asins',
        extensionKeywords: 'amazon 100 asins scraper',
        limit: 3,
    },
    'pt': {
        scriptType: 'pt',
        extensionKeywords: 'product targeting',
        limit: 10,
    },
};

scriptTypesSelect.addEventListener('change', function () {
    if (!this.value) {
        currentConfig = {
            scriptType: null,
            extensionKeywords: null,
            limit: 10,
        };
    } else {
        currentConfig = baseConfig[this.value];
    }
    extensionKeywordsInput.value = currentConfig.extensionKeywords ?? '';
    customScriptTypeInput.value = currentConfig.scriptType ?? '';
    tasksLimitInput.value = currentConfig.limit;
});

saveConfigButton.addEventListener('click', function () {
    if (currentConfig.limit === savedConfig.limit
        && currentConfig.extensionKeywords === savedConfig.extensionKeywords
        && currentConfig.scriptType === savedConfig.scriptType) {
        alert('No changes in configuration!');
        return;
    }
    savedConfig.limit = currentConfig.limit;
    savedConfig.extensionKeywords = currentConfig.extensionKeywords;
    savedConfig.scriptType = currentConfig.scriptType;
    alert('Config saved!');
});

function createRow(task_id, alias, tab) {

}

function removeRow(id) {
    if (id.task_id) {
        document.querySelector(`[data-bs-task-id=${id.task_id}}]`)?.remove();
    } else if (id.tab_id) {
        document.querySelector(`[data-bs-tab-id=${id.task_id}}]`)?.remove();
    }
}

function getConfig() {
    return savedConfig;
}
