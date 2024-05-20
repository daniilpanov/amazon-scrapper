from io import BytesIO
from time import sleep

import requests
from bs4 import BeautifulSoup
from pytube import YouTube
from functions import base_chrome_init

base_url = 'https://sellercentral.amazon.com/'


def init():
    chrome = base_chrome_init(
        False,
        base_url + 'ap/signin?openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select'
                   '&openid.assoc_handle=sc_na_amazon_v2&openid.mode=checkid_setup&language=en_US'
                   '&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select'
                   '&pageId=sc_na_amazon_v2&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0',
    )
    chrome.type('#ap_email', 'karim@nyle.ai')
    chrome.type('#ap_password', 'Bogolor2@')
    chrome.submit('#ap_password')
    sleep(2)
    chrome.wait_for_loading()
    return chrome


def collect_courses_links(bwr):
    bwr.get(base_url + 'learn/courses?ref_=su_course_accordion&moduleId=b3514f1e-49b7-4372-b2c3-0c43a188c38c&courseId=0366307b-7a21-413a-b731-02bccfce8fa2&modLanguage=English')
    soup = BeautifulSoup(bwr.get_page_source(), features='lxml')
    all_courses = soup.find(attrs={'id': 'courselisting-expander'})
    if not all_courses:
        return False
    courses = all_courses.find_all('div', recursive=False)
    if not courses:
        return False
    data = []  # {course_name, module_name, course_id, module_id}
    for course in courses:
        row = {'course_name': course['data-a-expander-name'], 'course_id': course['id']}
        expanded = course.find('div', recursive=False)
        if expanded:
            for item in (expanded.find_all('div') or []):
                curr_row = row.copy()
                curr_row['module_name'] = item.text.strip()
                curr_row['module_id'] = item['data-module-id']
                data.append(curr_row)
    return data


def scrap_media(bwr, course_id, module_id):
    link_template = base_url + 'learn/courses?ref_=su_course_accordion&moduleId={}&courseId={}&modLanguage=English'
    bwr.get(base_url + link_template.format(module_id, course_id))
    soup = BeautifulSoup(bwr.get_page_source(), features='lxml')
    yt_video = soup.find('iframe', {'id': 'module-video'})
    internal_video = soup.select_one('div#module-video > .airy > .airy-renderer-container > video')
    pdf_document = soup.find('div', {'id': 'module-document'})
    details = soup.select_one('div.module-details.a-grid-top')
    data = {}
    if details:
        data['details'] = details.text.strip()
    if yt_video:
        data_video = BytesIO()
        YouTube(yt_video['src']).streams.get_highest_resolution().stream_to_buffer(data_video)
        data_video.seek(0)
        data['video'] = data_video.read()
    if internal_video:
        src = internal_video['src']
        try:
            res = requests.get(src)
            if res.status_code == 200:
                data['video'] = res.content
        except requests.exceptions.RequestException:
            pass
    if pdf_document and 'data-src-english' in pdf_document:
        try:
            res = requests.get(pdf_document['data-src-english'])
            if res.status_code == 200:
                data['document'] = res.content
        except requests.exceptions.RequestException:
            pass


if __name__ == '__main__':
    wd = init()
    links = collect_courses_links(wd)
    print(scrap_media(wd, links[0]['course_id'], links[0]['module_id']))
