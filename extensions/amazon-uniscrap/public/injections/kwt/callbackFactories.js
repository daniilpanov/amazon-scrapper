function createPerPageCallback(sq) {
    return ({ countSponsored, countOrganic, res }) => {
        chrome.runtime.sendMessage({
            action: 'sendMessage',
            data: {
                queue: 'result.success.kwt',
                msg: { searchQuery: sq, countSponsored, countOrganic, chunk: res },
            },
        });
    }
}

function createErrorCallback(sq) {
    return exception => {
        chrome.runtime.sendMessage({
            action: 'sendMessage',
            data: {
                queue: 'result.error.kwt',
                msg: { searchQuery: sq, error: exception.message },
            },
        });
    }
}
