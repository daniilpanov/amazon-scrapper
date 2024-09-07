function getUsualMetrics(el) {
    const data = {};
    const metrics_items = el?.children[0]?.children;
    for (const metric of metrics_items) {
        let key = metric?.children[0]?.innerText.trim();
        let value = metric?.children[1]?.innerText.trim();
        if (value[0] === '$') {
            value = value.slice(1);
            key += ', $';
        } else if (value[value.length - 1] === '%') {
            value = value.slice(0, value.length - 1);
            key += ', %';
        }
        value = Number.parseFloat(value);
        data[key] = value;
    }
    return data;
}

function getDiagrams(diagrams) {
    const data = {};
    for (const diagram of diagrams) {
        const diagram_items = diagram?.children[0].children;
        let key = diagram_items[0]?.innerText.trim() + ', %';
        let [sub_keys, sub_values] = [...(diagram_items[1]?.children[1]?.children || [])].slice(1);
        sub_keys = sub_keys.children;
        sub_values = sub_values.children;
        let sub_data = {};
        let tVal;
        for (let i = 0; i < Math.min(sub_keys.length, sub_values.length); ++i) {
            tVal = sub_values[i].innerText.trim();
            tVal = tVal.slice(0, tVal.length - 1);
            sub_data[sub_keys[i].innerText.trim()] = Number.parseFloat(tVal);
        }
        data[key] = sub_data;
    }
    return data;
}

function parsePage() {
    const divs = document.querySelectorAll('main > div > div > div.arco-spin-children > div > div:nth-child(2) > div');
    let grouped_divs = {};
    let data = {url: document.location.href};
    let curr = null;
    for (const adiv of divs) {
        if (adiv.id) {
            curr = adiv.id;
        } else {
            grouped_divs[curr] = adiv;
        }
    }
    // Sales
    if (grouped_divs.sales_tab) {
        const items = grouped_divs.sales_tab.children;
        data['Sales period'] = items[1]?.innerText.trim();
        const sales_data = items[2];
        const [raw_data, diagrams_root] = sales_data?.children[0]?.children;

        // Metrics
        data = {...data, ...getUsualMetrics(raw_data)};

        // Diagrams
        const diagrams = diagrams_root.children[0].children[0].children[0].children[0].children[0].children;
        data = {...data, ...getDiagrams(diagrams)};
    }

    // Collaboration metrics
    if (grouped_divs.collab_history) {
        const items = grouped_divs.collab_history.children;
        const raw_data = items[1]?.children[0]?.children[0];

        // Metrics
        data = {...data, ...getUsualMetrics(raw_data)};
    }

    // Video
    if (grouped_divs.video_tab) {
        const items = grouped_divs.video_tab.children;
        const raw_data = items[1]?.children[0]?.children[0];

        // Metrics
        data = {...data, ...getUsualMetrics(raw_data)};
    }

    // LIVE
    if (grouped_divs.live_tab) {
        const items = grouped_divs.live_tab.children;
        data['LIVE period'] = items[0]?.children[0]?.children[1]?.innerText.trim();
        const raw_data = items[1]?.children[0]?.children[0];

        // Metrics
        data = {...data, ...getUsualMetrics(raw_data)};
    }

    // Followers
    if (grouped_divs.followers_tab) {
        const items = grouped_divs.followers_tab.children[1]?.children[0]?.children[0].children[0].children[0].children;

        // Diagrams
        const diagrams = items[0]?.children;
        data = {...data, ...getDiagrams(diagrams)};
    }

    return data;
}