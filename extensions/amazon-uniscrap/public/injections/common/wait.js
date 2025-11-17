/**
 * Waiting for element and its children are loaded fully
 * @param waitElementQuerySelector : string
 * @param timeout : number
 */
function waitLoading(waitElementQuerySelector, timeout = 1000) {
    if (!waitElementQuerySelector) return null;

    return new Promise(resolve => {
        let mainTimeout = setTimeout(resolve, timeout);
        let appElement = document.querySelector(waitElementQuerySelector);
        if (appElement)
            return resolve(appElement);

        let waitTimeout;
        const observer = new MutationObserver((mutationsList, observer) => {
            for (let mutation of mutationsList) {
                if (mutation.type !== 'childList' && mutation.type !== 'subtree')
                    continue;

                appElement = document.querySelector(waitElementQuerySelector);
                if (!appElement)
                    continue;

                if (mainTimeout !== undefined)
                    clearTimeout(mainTimeout);

                if (waitTimeout !== undefined)
                    clearTimeout(waitTimeout);

                waitTimeout = setTimeout((r, el, obs) => {
                    obs.disconnect();
                    r(el);
                }, 100, resolve, appElement, observer);
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
        });
    });
}
