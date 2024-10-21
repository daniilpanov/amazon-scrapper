async function getASINsLinks() {
    const pagination = document.getElementsByClassName('a-pagination');
    let pages_count = 1, current_page = 1, asins_blocks, result = [];
    document.getElementById('navFooter')?.scrollIntoView();
    await new Promise(r => setTimeout(r, 1000));
    document.querySelector('div.a-cardui[id*="asin-index"]:last-child')?.scrollIntoView();
    await new Promise(r => setTimeout(r, 1000));
    document.querySelector('div.a-cardui[id*="asin-index"]:last-child')?.scrollIntoView();
    await new Promise(r => setTimeout(r, 250));
    document.getElementById('navFooter')?.scrollIntoView();
    await new Promise(r => setTimeout(r, 250));
    if (pagination && pagination.length) {
        pages_count = Number((pagination[0].getElementsByTagName('li')?.length || 3) - 2);
        if (pages_count < 1) {
            pages_count = 1;
        }
        current_page = Number(pagination[0].querySelector('li.a-selected > a')?.textContent.trim() || 1);
        pagination[0].scrollIntoView();
    }
    asins_blocks = document.querySelectorAll('div.a-cardui[id*="asin-index"]');
    let asin_block, row;
    for (asin_block of asins_blocks) {
        // Get product ASIN
        let asin = asin_block.querySelector('a')?.href.match(/B0[0-9A-Z]{8}/g);
        if (!asin || !asin.length) {
            continue;
        }
        asin = asin[0];
        // Initialize row (item in the result array)
        row = {asin};
        // Get product title
        const title_info = asin_block.querySelector('a[href*="/dp/"]:not(.aok-block)');
        if (title_info) {
            row.title = title_info.textContent.trim();
        } else {
            row.title = null;
        }
        // Get info about reviews -> get score
        const reviews_info = asin_block.querySelector('a[href*="product-reviews"]')?.innerText.replaceAll('\u2009', '\n').split('\n');
        if (reviews_info) {
            row.score = reviews_info.length ? Number(reviews_info[0].split(' ')[0].trim().replaceAll(',', '')) : 0;
        } else {
            row.score = null;
        }
        // Set an order number in current BSR
        row.number_in_BSR = Number(asin_block.children[0]?.children[0]?.textContent.slice(1) || 0) || null;
        // Get an image
        try {
            const img_urls = Object.keys(JSON.parse(asin_block.querySelector('img')?.getAttribute('data-a-dynamic-image')));
            row.image = img_urls.length ? img_urls[img_urls.length - 1] : null;
        } catch (e) {
            row.image = null;
        }
        result.push(row);
    }

    return {result, pages_count, current_page};
}

function goToNextPage() {
    const new_page = document.querySelector('.a-pagination .a-last:not(.a-disabled) > a');
    if (new_page) {
        new_page.click();
        return true;
    }
    return false;
}