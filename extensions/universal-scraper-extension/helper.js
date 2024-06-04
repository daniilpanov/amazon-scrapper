// Wait for element by the CSS Selector using setTimeout
function waitForElement(path_to_element, callback, stop_callback, counter = 0) {
    const el = document.querySelectorAll(path_to_element);
    if (!el || (typeof el.length !== 'undefined' && !el.length)) {
        if (!stop_callback || !stop_callback(counter++)) {
            return setTimeout(waitForElement, 250, path_to_element, callback);
        }
    }
    else {
        return callback(el);
    }
}
// Removing element while the elements look like its are presented on the page
function cycleRemove(path) {
    const el = document.querySelector(path)
    if (el) {
        el.click();
        setTimeout(cycleRemove, 100, path)
    }
}
