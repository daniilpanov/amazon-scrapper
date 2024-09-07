function parsePage(shift = 0) {
    const rootEl = document.getElementsByClassName('arco-table-body');
    if (!rootEl || !rootEl.length) {
        return false;
    }

    const all_rows = rootEl[0].getElementsByTagName('tr');
    if (!all_rows || !all_rows.length) {
        return false;
    }

    const data = [];
    for (let i = shift; i < all_rows.length; ++i) {
        const cells = all_rows[i].getElementsByTagName('td');
        const profile_cell = cells[0];
        // const video_cell = cells[1];
        const gmv_val = Number.parseFloat((cells[2]?.innerText.trim().slice(1, -1) || '0').replaceAll(',', ''));
        const items_sold_val = Number.parseFloat((cells[3]?.innerText.trim().slice(0, -1) || '0').replaceAll(',', ''));
        const avg_video_views = Number.parseFloat((cells[4]?.innerText.trim().slice(0, -1) || '0').replaceAll(',', ''));
        const engagement_rate = Number.parseFloat((cells[5]?.innerText.trim().slice(0, -1) || '0').replaceAll(',', ''));

        const profile_avatar = profile_cell.querySelector('[data-tid="m4b_avatar"] img')['src'] || null;
        const profile_data = profile_cell.querySelectorAll('div > span > div > div:not([data-tid="m4b_avatar"]) > span');

        let [profile_name, profile_description] = profile_data[0].children;
        profile_description = profile_description?.innerText?.trim() || null;

        let profile_tags = profile_name.children;
        profile_name = profile_tags[0]?.innerText?.trim() || null;
        profile_tags = [...profile_tags].slice(1);
        let profile_tags_str = [];
        for (const profileTag of profile_tags) {
            const el = profileTag.innerText?.trim();
            if (el) {
                profile_tags_str.push(el);
            }
        }
        profile_tags = profile_tags_str.join(', ');

        const profile_categories = profile_data[1]?.children[1]?.innerText?.trim().replaceAll('\n', '') || null;

        const profile_followers = profile_data[2].children[1]?.innerText?.trim().split(', ') || null;
        let [profile_followers_count, profile_followers_gender_p, profile_followers_age] = profile_followers;
        profile_followers_age = profile_followers_age || null;
        profile_followers_count = Number.parseFloat(profile_followers_count.slice(0, -1) || '0');
        let [profile_followers_gender, profile_followers_gender_percents] = profile_followers_gender_p?.split(' ') || [null, '0'];
        profile_followers_gender_percents = Number.parseFloat(profile_followers_gender_percents.slice(0, -1) || '0');

        data.push({
            'Profile_name': profile_name,
            'Profile_description': profile_description,
            'Profile_tags': profile_tags,
            'Profile_categories': profile_categories,
            'Profile followers count, K': profile_followers_count,
            'Profile followers gender': profile_followers_gender,
            'Profile followers gender, %': profile_followers_gender_percents,
            'Profile followers age': profile_followers_age,
            'Profile_avatar': profile_avatar,
            'GMV, $K': gmv_val,
            'Items sold, K': items_sold_val,
            'Avg. video views, K': avg_video_views,
            'Engagement rate, %': engagement_rate,
        });
    }

    return data;
}
