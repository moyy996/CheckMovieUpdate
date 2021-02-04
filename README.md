# 视频更新检查工具

## 参数说明

```

{
  "lastCheckTime": 最后检查更新的时间，手动设置
  "filterTitleKeywords": 标题过滤关键字列表
  "filterNumberOrPrefix": 番号过滤列表,可以是番号、番号前缀
  "linkPrefix": 演员页网址前缀
  "linkSuffix": 演员页网址后缀，currentPage会被程序替换成页码，可以为空
  "downloadCover": {
    "switch": 是否下载封面，1为开，0为关
    "imgPath": 存放封面文件夹名称
    "imgName": 封面名称，参数：actor 演员名称，number 番号，release 发行日期，.png 图片格式
    "timeout": 超时请求时间
    "retryCount": 出错请求次数
  },
  "actorList": [
    {
      "actor": 演员名称
      "linkKeyword": 网址关键字：演员页网址前缀后面、演员页网址后缀前面的部分
      "lastDownloadMovieNumber": 最后下载的视频番号
      "lastDownloadMovieReleaseDate": 最后下载的视频发行日期
      "check": 是否检查，1为开，0为关
    },
    {
      "actor": 演员名称2
      "linkKeyword": 网址关键字：演员页网址前缀后面、演员页网址后缀前面的部分
      "lastDownloadMovieNumber": 最后下载的视频番号
      "lastDownloadMovieReleaseDate": 最后下载的视频发行日期
      "check": 是否检查，1为开，0为关
    }
  ]
}

```
## 效果图
<div align="center">
<img src="https://github.com/moyy996/CheckMovieUpdate/blob/main/Img/main.png" height="700">
<img src="https://github.com/moyy996/CheckMovieUpdate/blob/main/Img/image.png" height="300">
</div>


