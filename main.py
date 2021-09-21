import json
import time

import requests
import os
from lxml import etree
import re
import cloudscraper


# 读取 config 文件
def read_json(fileName):
    with open(fileName, 'rb') as load_f:
        load_dict = json.load(load_f)
        load_f.close()
        return load_dict


# 将 json_obj 写入 config 文件
def write_json(fileName, json_obj):
    with open(fileName, 'w', encoding='utf-8-sig') as dump_f:
        json.dump(json_obj, dump_f, ensure_ascii=False)
        dump_f.close()


# 获得网页代码
def get_html(url):
    scraper = cloudscraper.create_scraper()
    headers = {
        'USER-AGENT': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
    # 发送请求，获得响应
    # response = requests.get(url=url, headers=headers)
    # response = scraper.get(url=url, headers=headers)
    response = scraper.get(url)
    # 获得网页源代码
    html = response.text
    # print(html)
    html = etree.HTML(html)
    return html


# 获取标题
def get_title_jp(html, count):
    title = html.xpath(
        "//div[@id='videos']/div[@class='grid columns']/div[@class='grid-item column'][" + str(
            count) + "]/a[@class='box']/div[@class='video-title']/text()")[0]
    return title


# 获取发行时间
def get_release_jp(html, count):
    release = html.xpath(
        "//div[@id='videos']/div[@class='grid columns']/div[@class='grid-item column'][" + str(
            count) + "]/a[@class='box']/div[@class='meta']/text()")[0]
    try:
        if re.search('\d{4}-\d{2}-\d{2}', release):
            release_result = re.search('\d{4}-\d{2}-\d{2}', release).group()
        elif re.search('\d{2}/\d{2}/\d{4}', release):
            release_result = re.search('\d{4}', release).group() + '-'
            release_result += re.search('\d{2}/\d{2}', release).group()
            release_result = release_result.replace('/', '-')
    except Exception as error_info:
        print('获取发行时间失败，原因：', error_info)
    return release_result


# 获取番号
def get_number_jp(html, count):
    number = html.xpath(
        "//div[@id='videos']/div[@class='grid columns']/div[@class='grid-item column'][" + str(
            count) + "]/a[@class='box']/div[@class='uid']/text()")[0]
    return number


# 获取番号对应网址
def get_site_jp(html, count):
    site = 'https://javdb.com' + html.xpath(
        "//div[@id='videos']/div[@class='grid columns']/div[@class='grid-item column'][" + str(
            count) + "]/a[@class='box']/@href")[0]
    return site


# 获取封面地址
def get_cover_jp(html, count):
    cover = html.xpath("//div[@class='grid-item column']/a[@class='box']/div/img/@data-src")[count - 1]
    if 'thumbs' not in cover:
        cover = html.xpath("//div[@class='grid-item column']/a[@class='box']/div/img/@src")[count - 1]
    if not 'https' in cover:
        cover = 'https:' + cover
    cover = cover.replace('thumbs', 'covers')
    return cover


# 获取单个影片信息
def get_movie_info(html, count):
    # 封面 番号 发行日期 网址 封面
    title = get_title_jp(html, count)
    number = get_number_jp(html, count)
    release = get_release_jp(html, count)
    site = get_site_jp(html, count)
    cover = get_cover_jp(html, count)
    return title, number, release, site, cover


# 从 actor_info 中获取演员页地址
def get_actor_site(config_value, actor_info, page):
    link_prefix = config_value['linkPrefix']
    link_suffix = config_value['linkSuffix'].replace('currentPage', str(page))
    return link_prefix + actor_info['linkKeyword'] + link_suffix


# 下载函数
def download_file_with_filename(cover_url, filename, filepath, timeout, retry_count, current_time):
    print('   [+]' + filename + ' 下载中......')
    for i in range(retry_count):
        try:
            # 文件夹不存在就创建
            # 二层目录 以当前时间为文件夹名
            filepath = filepath + "/" + current_time
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            # 请求数据
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
            r = requests.get(cover_url, timeout=timeout, headers=headers)
            if r == '':
                print('   [-]封面下载失败，返回结果为空!')
                return
            # 写入图片
            with open(str(filepath) + "/" + filename, "wb") as code:
                code.write(r.content)
            print('   [+]下载成功!')
            return
        except Exception as err_info:
            i += 1
            print('   [-]封面下载 :  重试 ' + str(i) + '/' + str(retry_count) + '，错误：' + str(err_info))
    print('   [-]下载失败!')


# 下载封面
def download_movie_cover(cover_url, number, actor, release, config_value, current_time):
    # 获取需要的变量
    downloadCover = config_value['downloadCover']
    switch = downloadCover['switch']
    img_path = downloadCover['imgPath']
    img_name = downloadCover['imgName']
    timeout = downloadCover['timeout']
    retry_count = downloadCover['retryCount']
    # 是否开启下载
    if switch == 0:
        return
    # 封面名称处理
    img_name = img_name.replace('number', number).replace('actor', actor).replace('release', release)
    # 下载
    download_file_with_filename(cover_url, img_name, img_path, timeout, retry_count, current_time)


# 检查是否符合过滤条件
def check_filter(title, number, filterTitleKeywords, filterNumberOrPrefix):
    # 检查前缀
    for numberPrefix in filterNumberOrPrefix:
        if numberPrefix in number:
            return False
    if number in filterNumberOrPrefix:
        return False
    # 检查标题
    for filterKeyword in filterTitleKeywords:
        if filterKeyword in title:
            return False
    return True


def main_function(config_value):
    current_time = str(time.strftime("%Y-%m-%d %H-%M-%S", time.localtime()))
    # 最后检查时间 优先级高于 lastDownloadMovieReleaseDate
    lastCheckTime = config_value['lastCheckTime']
    # 演员列表
    actor_list = config_value['actorList']
    # 过滤条件
    filterTitleKeywords = config_value['filterTitleKeywords']
    filterNumberOrPrefix = config_value['filterNumberOrPrefix']
    # 输出基本信息
    print('========================================================================')
    print('最后检查时间：' + lastCheckTime)
    # 第一层循环 循环演员列表
    for actor_info in actor_list:
        # 间隔
        print('========================================================================')
        # 获取需要的变量
        actor = actor_info['actor']
        lastDownloadMovieNumber = actor_info['lastDownloadMovieNumber']
        lastDownloadMovieReleaseDate = actor_info['lastDownloadMovieReleaseDate']
        check = int(str(actor_info['check']))
        count_new_movie = 0  # 是否有更新
        # 判断 番号 发行日期是否为空
        if lastDownloadMovieNumber and lastDownloadMovieReleaseDate:
            print('演员：' + actor + ' | 上次下载番号：' + lastDownloadMovieNumber + ' | 最后检查时间：' + lastDownloadMovieReleaseDate)
        elif lastDownloadMovieNumber and not lastDownloadMovieReleaseDate:
            print('演员：' + actor + ' | 上次下载番号：' + lastDownloadMovieNumber)
        elif not lastDownloadMovieNumber and lastDownloadMovieReleaseDate:
            print('演员：' + actor + ' | 最后检查时间：' + lastDownloadMovieReleaseDate)
        elif not lastDownloadMovieNumber and not lastDownloadMovieReleaseDate:
            print('演员：' + actor)
        # 此演员不需要检查就跳过
        if not check:
            continue
        # 第二层循环 循环演员所有页面
        page = 1
        while 1:
            # 获取地址、网页数据
            actor_site = get_actor_site(config_value, actor_info, page)
            actor_html = get_html(actor_site)
            page += 1
            # 第三层循环 循环每个页面中的影片信息
            counts = len(actor_html.xpath(
                "//div[@id='videos']/div[@class='grid columns']/div[@class='grid-item column']"))
            # 遍历完所有页面 停止
            if counts == 0:
                break
            count = 1
            while count <= counts:
                # 获取单个影片信息
                title, number, release, site, cover = get_movie_info(actor_html, count)
                # 判断是否输出并下载封面
                # 先判断 lastDownloadMovieReleaseDate 再判断 lastCheckTime
                downloadFile = False
                if lastDownloadMovieReleaseDate and lastDownloadMovieReleaseDate < release:
                    downloadFile = True
                elif lastDownloadMovieReleaseDate and lastDownloadMovieReleaseDate >= release:
                    downloadFile = False
                elif not lastDownloadMovieReleaseDate and lastCheckTime and lastCheckTime < release:
                    downloadFile = True
                elif not lastDownloadMovieReleaseDate and lastCheckTime and lastCheckTime >= release:
                    downloadFile = False
                # 判断 lastDownloadMovieNumber
                if lastDownloadMovieNumber and lastDownloadMovieNumber == number:
                    downloadFile = False
                # 全为空时
                if not lastDownloadMovieReleaseDate and not lastCheckTime and not lastDownloadMovieNumber:
                    downloadFile = True
                # 如果不符合过滤条件
                if downloadFile and check_filter(title, number, filterTitleKeywords, filterNumberOrPrefix):
                    count_new_movie += 1
                    print('{0: <20}'.format('[' + str(count_new_movie) + ']番号：' + number) + '{0: <20}'.format(
                        '发行日期：' + release) +
                          ('网址：' + site))
                    # 下载封面
                    download_movie_cover(cover, number, actor, release, config_value, current_time)
                else:
                    # 跳出第三次循环
                    break
                count += 1
            # 跳出第二次循环
            if count != counts:
                break
        if not count_new_movie:
            print('无影片更新\n')
        else:
            print('\n')


if __name__ == '__main__':
    # 读取config文件
    configFileName = "config.json"
    config_value = read_json(configFileName)

    # 主功能
    main_function(config_value)

    # 修改最后一次检查时间为现在时刻
    # 写入后会变成一行 所以废弃
    # config_value['lastCheckTime'] = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    # write_json(configFileName, config_value)

    input("[+]按任意键结束，你可以在结束之前查看和错误信息。")
