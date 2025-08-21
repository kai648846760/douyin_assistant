# api_endpoints.py
# -*- coding: utf-8 -*-
# @Author: Loki Wang

# 单个作品信息API (用于解析单个视频URL)
SINGLE_VIDEO_API = "https://www.douyin.com/aweme/v1/web/aweme/detail/"

# 用户主页作品列表API
USER_POST_API = "https://www.douyin.com/aweme/v1/web/aweme/post/"

# 用户点赞作品列表API
USER_LIKE_API = "https://www.douyin.com/aweme/v1/web/aweme/like/"

# 用户收藏作品列表API (称之为collection, 对应抖音的“收藏”)
USER_FAVORITE_API = "https://www.douyin.com/aweme/v1/web/aweme/favorite/"

# 用户收藏夹作品列表API (f2称之为collects, 对应抖音的“收藏夹”)
USER_COLLECTS_API = "https://www.douyin.com/aweme/v1/web/aweme/collects/"

# 用户合集作品列表API (f2称之为mix)
USER_MIX_API = "https://www.douyin.com/aweme/v1/web/mix/aweme/"

# 原声(音乐)作品列表API
MUSIC_API = "https://www.douyin.com/aweme/v1/web/music/aweme/"

# (直播API与视频下载机制完全不同，此处暂不添加)