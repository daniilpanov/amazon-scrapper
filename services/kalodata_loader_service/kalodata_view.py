import requests

s = requests.session()


r = s.post(
    "https://www.kalodata.com/product/detail/creator/getConversionRadio",
    headers={"content-length": "76"},
    json={
        "id": "1729388618695479397",
        "startDate": "2024-10-01",
        "endDate": "2024-10-30",
    },
)
# {
#   "success": true,
#   "data": {
#     "creatorNum": 32,
#     "creatorConversionRatio": 0.40625
#   },
#   "message": null,
#   "cached": null,
#   "code": null
# }


r = s.post(
    "https://www.kalodata.com/product/detail/creator/queryList",
    headers={"content-length": "161"},
    json={
        "id": "1729388618695479397",
        "startDate": "2024-10-01",
        "endDate": "2024-10-30",
        "authority": True,
        "pageNo": 1,
        "pageSize": 10,
        "sort": [{"field": "revenue", "type": "DESC"}],
    },
)
# {
#   "success": true,
#   "data": [
#     {
#       "revenue": "$4.86k",
#       "sale": "162",
#       "video_revenue": "$4.83k",
#       "followers": 75665,
#       "nickname": "purelywhitedeluxe",
#       "handle": "purelywhitedeluxe",
#       "id": "6769722348687508485",
#       "live_revenue": "$29.99"
#     },
#     {
#       "revenue": "$3.63k",
#       "sale": "117",
#       "video_revenue": "$3.63k",
#       "followers": 15835,
#       "nickname": "Aylin",
#       "handle": "aylin.ykt",
#       "id": "6743417375129830405",
#       "live_revenue": "$0.00"
#     },
#     {
#       "revenue": "$539.79",
#       "sale": "18",
#       "video_revenue": "$0.00",
#       "followers": 83770,
#       "nickname": "Ryan Maxwell",
#       "handle": "ryan.maxwel22",
#       "id": "7272783854074463274",
#       "live_revenue": "$539.79"
#     },
#     {
#       "revenue": "$247.43",
#       "sale": "7",
#       "video_revenue": "$247.43",
#       "followers": 21328,
#       "nickname": "The Home Place Cape Cod",
#       "handle": "thehomeplacecapecod",
#       "id": "7137977376573473838",
#       "live_revenue": "$0.00"
#     },
#     {
#       "revenue": "$209.93",
#       "sale": "7",
#       "video_revenue": "$0.00",
#       "followers": 40194,
#       "nickname": "sam\ud83d\ude3e",
#       "handle": "bfusuplug",
#       "id": "6923265281813251077",
#       "live_revenue": "$209.93"
#     },
#     {
#       "revenue": "$59.98",
#       "sale": "2",
#       "video_revenue": "$59.98",
#       "followers": 11678,
#       "nickname": "Jack",
#       "handle": "jackgoertzen",
#       "id": "6809703549300360197",
#       "live_revenue": "$0.00"
#     },
#     {
#       "revenue": "$29.99",
#       "sale": "1",
#       "video_revenue": "$0.00",
#       "followers": 7696,
#       "nickname": "Courtney | Boy Mom | TTS \ud83e\udef6\ud83c\udffb",
#       "handle": "regular.boymom",
#       "id": "7384456145614275626",
#       "live_revenue": "$29.99"
#     },
#     {
#       "revenue": "$29.99",
#       "sale": "1",
#       "video_revenue": "$29.99",
#       "followers": 10211,
#       "nickname": "Nellysstores",
#       "handle": "nellysstores",
#       "id": "7238042757184406571",
#       "live_revenue": "$0.00"
#     },
#     {
#       "revenue": "$29.99",
#       "sale": "1",
#       "video_revenue": "$0.00",
#       "followers": 22637,
#       "nickname": "brookie\ud83d\udc9d",
#       "handle": "brookechello",
#       "id": "6719889468524692486",
#       "live_revenue": "$29.99"
#     },
#     {
#       "revenue": "$29.99",
#       "sale": "1",
#       "video_revenue": "$29.99",
#       "followers": 2866,
#       "nickname": "Andi",
#       "handle": "mrsded2022",
#       "id": "6811131039425430534",
#       "live_revenue": "$0.00"
#     }
#   ],
#   "message": null,
#   "cached": null,
#   "code": null
# }


r = s.post(
    "https://www.kalodata.com/product/detail/creator/count",
    headers={"content-length": "161"},
    json={
        "id": "1729388618695479397",
        "startDate": "2024-10-01",
        "endDate": "2024-10-30",
        "authority": True,
        "pageNo": 1,
        "pageSize": 10,
        "sort": [{"field": "revenue", "type": "DESC"}],
    },
)
# {
#   "success": true,
#   "data": 32,
#   "message": null,
#   "cached": null,
#   "code": null
# }


r = s.post(
    "https://www.kalodata.com/product/detail/video/queryList",
    headers={"content-length": "161"},
    json={
        "id": "1729388618695479397",
        "startDate": "2024-10-01",
        "endDate": "2024-10-30",
        "authority": True,
        "pageNo": 1,
        "pageSize": 10,
        "sort": [{"field": "revenue", "type": "DESC"}],
    },
)
# {
#   "success": true,
#   "data": [
#     {
#       "duration": "28s",
#       "sale": "161",
#       "revenue": "$4.83k",
#       "ad": 1,
#       "create_time": "2024/06/11 13:39:30",
#       "content_type": "video",
#       "description": "Over A Million Kits Sold \ud83e\udd0d",
#       "id": "7379301694561078574",
#       "views": "507.59k"
#     },
#     {
#       "duration": "48s",
#       "sale": "45",
#       "revenue": "$1.35k",
#       "ad": 0,
#       "create_time": "2024/09/23 11:26:48",
#       "content_type": "video",
#       "description": "seriously if you don\u2019t have this kit you\u2019re missing outttt @purelywhitedeluxe \ud83c\udf1f",
#       "id": "7417860347098418474",
#       "views": "13.34k"
#     },
#     {
#       "duration": "48s",
#       "sale": "23",
#       "revenue": "$752.27",
#       "ad": 1,
#       "create_time": "2024/09/30 12:07:39",
#       "content_type": "video",
#       "description": "We love a good sale!!\ud83e\udd29 @purelywhitedeluxe ",
#       "id": "7420468469872905518",
#       "views": "4.87k"
#     },
#     {
#       "duration": "43s",
#       "sale": "23",
#       "revenue": "$752.27",
#       "ad": 1,
#       "create_time": "2024/09/30 12:20:57",
#       "content_type": "video",
#       "description": "Replying to @Ava Rose my holy grail product is now on sale!! @purelywhitedeluxe \u26a1\ufe0f\u26a1\ufe0f",
#       "id": "7420471900469513515",
#       "views": "5.32k"
#     },
#     {
#       "duration": "57s",
#       "sale": "9",
#       "revenue": "$269.89",
#       "ad": 1,
#       "create_time": "2024/10/21 11:03:35",
#       "content_type": "video",
#       "description": "1000/10 cannot recommend this kit enough \ud83e\udd29 @purelywhitedeluxe ",
#       "id": "7428244751637384490",
#       "views": "7.93k"
#     },
#     {
#       "duration": "56s",
#       "sale": "8",
#       "revenue": "$239.87",
#       "ad": 1,
#       "create_time": "2024/10/15 11:31:28",
#       "content_type": "video",
#       "description": "I mean seriously this kit works WONDERS @purelywhitedeluxe \ud83e\udd29\ud83e\udd29",
#       "id": "7426025411986951454",
#       "views": "13.78k"
#     },
#     {
#       "duration": "1m 1s",
#       "sale": "7",
#       "revenue": "$209.91",
#       "ad": 1,
#       "create_time": "2024/10/21 11:13:56",
#       "content_type": "video",
#       "description": "@purelywhitedeluxe makes for a perfect gift to give during the holiday season! \ud83c\udf81\ud83d\udc4f",
#       "id": "7428247408401845547",
#       "views": "5.49k"
#     },
#     {
#       "duration": "59s",
#       "sale": "5",
#       "revenue": "$162.45",
#       "ad": 0,
#       "create_time": "2024/10/07 14:05:31",
#       "content_type": "video",
#       "description": "Round 1 of the Purely White Deluxe Teeth Whitening Kit was a big success! I see a big difference in the Whitening. No sensitivity or burning. #smile #Teeth #oralhealth #inspire #Whitening #TikTokShop ",
#       "id": "7423096369440738591",
#       "views": "640"
#     },
#     {
#       "duration": "41s",
#       "sale": "2",
#       "revenue": "$84.98",
#       "ad": 0,
#       "create_time": "2024/10/07 13:51:17",
#       "content_type": "video",
#       "description": "Smile! #Teeth #Whitening #kit #inspire ",
#       "id": "7423092694542568734",
#       "views": "261"
#     },
#     {
#       "duration": "53s",
#       "sale": "2",
#       "revenue": "$59.97",
#       "ad": 1,
#       "create_time": "2024/10/15 11:35:15",
#       "content_type": "video",
#       "description": "My teeth look & feel amazing \ud83e\udd79\ud83e\udef6\ud83c\udffc @purelywhitedeluxe ",
#       "id": "7426026387984747806",
#       "views": "3.51k"
#     }
#   ],
#   "message": null,
#   "cached": null,
#   "code": null
# }


r = s.post(
    "https://www.kalodata.com/product/detail/access",
    headers={"content-length": "93"},
    json={
        "id": "1729388618695479397",
        "startDate": "2024-10-01",
        "endDate": "2024-10-30",
        "authority": True,
    },
)
# {
#   "success": true,
#   "data": "ok",
#   "message": null,
#   "cached": null,
#   "code": null
# }


r = s.post(
    "https://www.kalodata.com/product/detail/total",
    headers={"content-length": "93"},
    json={
        "id": "1729388618695479397",
        "startDate": "2024-10-01",
        "endDate": "2024-10-30",
        "authority": True,
    },
)
# {
#   "success": true,
#   "data": {
#     "sale": "327",
#     "revenue": "$9.97k",
#     "video_revenue": "$8.89k",
#     "related_creator_count": 217,
#     "day_live_revenue": "$28.99",
#     "day_sale": "10.9",
#     "day_revenue": "$332.29",
#     "day_video_revenue": "$296.30",
#     "shopping_mall_revenue": "$209.93",
#     "unit_price": "$30.49",
#     "day_shopping_mall_revenue": "$7.00",
#     "live_revenue": "$869.68"
#   },
#   "message": null,
#   "cached": null,
#   "code": null
# }


r = s.post(
    "https://www.kalodata.com/product/detail/history",
    headers={"content-length": "93"},
    json={
        "id": "1729388618695479397",
        "startDate": "2024-10-01",
        "endDate": "2024-10-30",
        "authority": True,
    },
)
# {
#   "success": true,
#   "data": [
#     {
#       "revenue": 239.92,
#       "sale": 8,
#       "video_revenue": 239.92,
#       "partition_day": "2024-10-01",
#       "unit_price": 29.99,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 0.0,
#       "sale": 0,
#       "video_revenue": 0.0,
#       "partition_day": "2024-10-02",
#       "unit_price": 0.0,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 809.73,
#       "sale": 27,
#       "video_revenue": 599.8,
#       "partition_day": "2024-10-03",
#       "unit_price": 29.99,
#       "live_revenue": 209.93
#     },
#     {
#       "revenue": 779.74,
#       "sale": 26,
#       "video_revenue": 779.74,
#       "partition_day": "2024-10-04",
#       "unit_price": 29.99,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 449.85,
#       "sale": 15,
#       "video_revenue": 449.85,
#       "partition_day": "2024-10-05",
#       "unit_price": 29.99,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 209.93,
#       "sale": 7,
#       "video_revenue": 209.93,
#       "partition_day": "2024-10-06",
#       "unit_price": 29.99,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 552.37,
#       "sale": 13,
#       "video_revenue": 552.37,
#       "partition_day": "2024-10-07",
#       "unit_price": 42.49,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 389.87,
#       "sale": 13,
#       "video_revenue": 329.89,
#       "partition_day": "2024-10-08",
#       "unit_price": 29.99,
#       "live_revenue": 29.99
#     },
#     {
#       "revenue": 179.94,
#       "sale": 6,
#       "video_revenue": 0.0,
#       "partition_day": "2024-10-09",
#       "unit_price": 29.99,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 179.94,
#       "sale": 6,
#       "video_revenue": 0.0,
#       "partition_day": "2024-10-10",
#       "unit_price": 29.99,
#       "live_revenue": 179.94
#     },
#     {
#       "revenue": 359.88,
#       "sale": 12,
#       "video_revenue": 359.88,
#       "partition_day": "2024-10-11",
#       "unit_price": 29.99,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 269.91,
#       "sale": 9,
#       "video_revenue": 239.92,
#       "partition_day": "2024-10-12",
#       "unit_price": 29.99,
#       "live_revenue": 29.99
#     },
#     {
#       "revenue": 239.92,
#       "sale": 8,
#       "video_revenue": 239.92,
#       "partition_day": "2024-10-13",
#       "unit_price": 29.99,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 449.85,
#       "sale": 15,
#       "video_revenue": 389.87,
#       "partition_day": "2024-10-14",
#       "unit_price": 29.99,
#       "live_revenue": 59.98
#     },
#     {
#       "revenue": 239.92,
#       "sale": 8,
#       "video_revenue": 149.95,
#       "partition_day": "2024-10-15",
#       "unit_price": 29.99,
#       "live_revenue": 89.97
#     },
#     {
#       "revenue": 299.9,
#       "sale": 10,
#       "video_revenue": 239.92,
#       "partition_day": "2024-10-16",
#       "unit_price": 29.99,
#       "live_revenue": 59.98
#     },
#     {
#       "revenue": 0.0,
#       "sale": 0,
#       "video_revenue": 0.0,
#       "partition_day": "2024-10-17",
#       "unit_price": 0.0,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 269.91,
#       "sale": 9,
#       "video_revenue": 269.91,
#       "partition_day": "2024-10-18",
#       "unit_price": 29.99,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 629.79,
#       "sale": 21,
#       "video_revenue": 629.79,
#       "partition_day": "2024-10-19",
#       "unit_price": 29.99,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 539.82,
#       "sale": 18,
#       "video_revenue": 509.83,
#       "partition_day": "2024-10-20",
#       "unit_price": 29.99,
#       "live_revenue": 29.99
#     },
#     {
#       "revenue": 419.72,
#       "sale": 14,
#       "video_revenue": 419.72,
#       "partition_day": "2024-10-21",
#       "unit_price": 29.98,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 299.8,
#       "sale": 10,
#       "video_revenue": 269.82,
#       "partition_day": "2024-10-22",
#       "unit_price": 29.98,
#       "live_revenue": 29.98
#     },
#     {
#       "revenue": 449.7,
#       "sale": 15,
#       "video_revenue": 419.72,
#       "partition_day": "2024-10-23",
#       "unit_price": 29.98,
#       "live_revenue": 29.98
#     },
#     {
#       "revenue": 329.78,
#       "sale": 11,
#       "video_revenue": 299.8,
#       "partition_day": "2024-10-24",
#       "unit_price": 29.98,
#       "live_revenue": 29.98
#     },
#     {
#       "revenue": 179.94,
#       "sale": 6,
#       "video_revenue": 179.94,
#       "partition_day": "2024-10-25",
#       "unit_price": 29.99,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 239.92,
#       "sale": 8,
#       "video_revenue": 209.93,
#       "partition_day": "2024-10-26",
#       "unit_price": 29.99,
#       "live_revenue": 29.99
#     },
#     {
#       "revenue": 359.88,
#       "sale": 12,
#       "video_revenue": 359.88,
#       "partition_day": "2024-10-27",
#       "unit_price": 29.99,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 239.92,
#       "sale": 8,
#       "video_revenue": 209.93,
#       "partition_day": "2024-10-28",
#       "unit_price": 29.99,
#       "live_revenue": 29.99
#     },
#     {
#       "revenue": 299.9,
#       "sale": 10,
#       "video_revenue": 299.9,
#       "partition_day": "2024-10-29",
#       "unit_price": 29.99,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 59.98,
#       "sale": 2,
#       "video_revenue": 29.99,
#       "partition_day": "2024-10-30",
#       "unit_price": 29.99,
#       "live_revenue": 29.99
#     }
#   ],
#   "message": null,
#   "cached": null,
#   "code": null
# }


r = s.post(
    "https://www.kalodata.com/product/detail/history",
    headers={"content-length": "93"},
    json={
        "id": "1729388618695479397",
        "startDate": "2024-10-01",
        "endDate": "2024-10-30",
        "authority": True,
    },
)
# {
#   "success": true,
#   "data": [
#     {
#       "revenue": 239.92,
#       "sale": 8,
#       "video_revenue": 239.92,
#       "partition_day": "2024-10-01",
#       "unit_price": 29.99,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 0.0,
#       "sale": 0,
#       "video_revenue": 0.0,
#       "partition_day": "2024-10-02",
#       "unit_price": 0.0,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 809.73,
#       "sale": 27,
#       "video_revenue": 599.8,
#       "partition_day": "2024-10-03",
#       "unit_price": 29.99,
#       "live_revenue": 209.93
#     },
#     {
#       "revenue": 779.74,
#       "sale": 26,
#       "video_revenue": 779.74,
#       "partition_day": "2024-10-04",
#       "unit_price": 29.99,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 449.85,
#       "sale": 15,
#       "video_revenue": 449.85,
#       "partition_day": "2024-10-05",
#       "unit_price": 29.99,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 209.93,
#       "sale": 7,
#       "video_revenue": 209.93,
#       "partition_day": "2024-10-06",
#       "unit_price": 29.99,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 552.37,
#       "sale": 13,
#       "video_revenue": 552.37,
#       "partition_day": "2024-10-07",
#       "unit_price": 42.49,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 389.87,
#       "sale": 13,
#       "video_revenue": 329.89,
#       "partition_day": "2024-10-08",
#       "unit_price": 29.99,
#       "live_revenue": 29.99
#     },
#     {
#       "revenue": 179.94,
#       "sale": 6,
#       "video_revenue": 0.0,
#       "partition_day": "2024-10-09",
#       "unit_price": 29.99,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 179.94,
#       "sale": 6,
#       "video_revenue": 0.0,
#       "partition_day": "2024-10-10",
#       "unit_price": 29.99,
#       "live_revenue": 179.94
#     },
#     {
#       "revenue": 359.88,
#       "sale": 12,
#       "video_revenue": 359.88,
#       "partition_day": "2024-10-11",
#       "unit_price": 29.99,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 269.91,
#       "sale": 9,
#       "video_revenue": 239.92,
#       "partition_day": "2024-10-12",
#       "unit_price": 29.99,
#       "live_revenue": 29.99
#     },
#     {
#       "revenue": 239.92,
#       "sale": 8,
#       "video_revenue": 239.92,
#       "partition_day": "2024-10-13",
#       "unit_price": 29.99,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 449.85,
#       "sale": 15,
#       "video_revenue": 389.87,
#       "partition_day": "2024-10-14",
#       "unit_price": 29.99,
#       "live_revenue": 59.98
#     },
#     {
#       "revenue": 239.92,
#       "sale": 8,
#       "video_revenue": 149.95,
#       "partition_day": "2024-10-15",
#       "unit_price": 29.99,
#       "live_revenue": 89.97
#     },
#     {
#       "revenue": 299.9,
#       "sale": 10,
#       "video_revenue": 239.92,
#       "partition_day": "2024-10-16",
#       "unit_price": 29.99,
#       "live_revenue": 59.98
#     },
#     {
#       "revenue": 0.0,
#       "sale": 0,
#       "video_revenue": 0.0,
#       "partition_day": "2024-10-17",
#       "unit_price": 0.0,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 269.91,
#       "sale": 9,
#       "video_revenue": 269.91,
#       "partition_day": "2024-10-18",
#       "unit_price": 29.99,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 629.79,
#       "sale": 21,
#       "video_revenue": 629.79,
#       "partition_day": "2024-10-19",
#       "unit_price": 29.99,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 539.82,
#       "sale": 18,
#       "video_revenue": 509.83,
#       "partition_day": "2024-10-20",
#       "unit_price": 29.99,
#       "live_revenue": 29.99
#     },
#     {
#       "revenue": 419.72,
#       "sale": 14,
#       "video_revenue": 419.72,
#       "partition_day": "2024-10-21",
#       "unit_price": 29.98,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 299.8,
#       "sale": 10,
#       "video_revenue": 269.82,
#       "partition_day": "2024-10-22",
#       "unit_price": 29.98,
#       "live_revenue": 29.98
#     },
#     {
#       "revenue": 449.7,
#       "sale": 15,
#       "video_revenue": 419.72,
#       "partition_day": "2024-10-23",
#       "unit_price": 29.98,
#       "live_revenue": 29.98
#     },
#     {
#       "revenue": 329.78,
#       "sale": 11,
#       "video_revenue": 299.8,
#       "partition_day": "2024-10-24",
#       "unit_price": 29.98,
#       "live_revenue": 29.98
#     },
#     {
#       "revenue": 179.94,
#       "sale": 6,
#       "video_revenue": 179.94,
#       "partition_day": "2024-10-25",
#       "unit_price": 29.99,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 239.92,
#       "sale": 8,
#       "video_revenue": 209.93,
#       "partition_day": "2024-10-26",
#       "unit_price": 29.99,
#       "live_revenue": 29.99
#     },
#     {
#       "revenue": 359.88,
#       "sale": 12,
#       "video_revenue": 359.88,
#       "partition_day": "2024-10-27",
#       "unit_price": 29.99,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 239.92,
#       "sale": 8,
#       "video_revenue": 209.93,
#       "partition_day": "2024-10-28",
#       "unit_price": 29.99,
#       "live_revenue": 29.99
#     },
#     {
#       "revenue": 299.9,
#       "sale": 10,
#       "video_revenue": 299.9,
#       "partition_day": "2024-10-29",
#       "unit_price": 29.99,
#       "live_revenue": 0.0
#     },
#     {
#       "revenue": 59.98,
#       "sale": 2,
#       "video_revenue": 29.99,
#       "partition_day": "2024-10-30",
#       "unit_price": 29.99,
#       "live_revenue": 29.99
#     }
#   ],
#   "message": null,
#   "cached": null,
#   "code": null
# }


r = s.post(
    "https://www.kalodata.com/product/detail",
    headers={"content-length": "93"},
    json={
        "id": "1729388618695479397",
        "startDate": "2024-10-01",
        "endDate": "2024-10-30",
        "authority": True,
    },
)
# {
#   "success": true,
#   "data": {
#     "sec_cate_id": "Makeup & Perfume",
#     "is_full_service": 0,
#     "shop_rating": "",
#     "ter_cate_id": "Makeup Tools\t",
#     "partition_day": "2024-10-30",
#     "review_count": 0,
#     "brand_name": "purelywhite deluxe",
#     "unit_price": "$29.99",
#     "creator_gmv_concentration": "92.5%",
#     "product_title": "PurelyWHITE Teeth Whitening Kit | Advanced 10X LED Light, Instant Whitening, Oral Stain Remover For Sensitive Teeth",
#     "is_affiliate": 1,
#     "min_in_30_price": "$29.98",
#     "min_original_price": "$29.99",
#     "delivery_type": "local",
#     "min_real_price": "$29.99",
#     "max_original_price": "$29.99",
#     "pri_cate_id": "Beauty & Personal Care",
#     "max_real_price": "$29.99",
#     "seller_type": "BRAND",
#     "name": "PurelyWHITE DELUXE",
#     "commission_rate": "10%",
#     "id": "1729388618695479397",
#     "collect_day": "2023-08-16",
#     "seller_id": "7495139564816533605"
#   },
#   "message": null,
#   "cached": null,
#   "code": null
# }


r = s.post(
    "https://www.kalodata.com/user/features",
    headers={"content-length": "47"},
    json={"country": "US", "list": ["DETAIL.ACCESS_TIMES"]},
)
# {
#   "success": true,
#   "data": {
#     "DETAIL.ACCESS_TIMES": {
#       "key": "DETAIL.ACCESS_TIMES",
#       "type": "BENEFIT",
#       "enable": null,
#       "count": 10,
#       "guidance": {
#         "actionType": {
#           "name": "Upgrade",
#           "desc": "Upgrade to view more data"
#         },
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Today's detail times has been used up",
#         "cause": null
#       },
#       "progress": {
#         "total": 10,
#         "used": 3,
#         "remain": 7,
#         "full": false
#       }
#     }
#   },
#   "message": "trial",
#   "cached": null,
#   "code": null
# }


r = s.get(
    "https://www.kalodata.com/product/detail/getImageCount",
    params={"productId": "1729388618695479397"},
    headers={"origin": None, "content-type": None},
)
# {
#   "success": true,
#   "data": 6,
#   "message": null,
#   "cached": null,
#   "code": null
# }

r = s.post(
    "https://www.kalodata.com/product/detail/video/count",
    headers={"content-length": "161"},
    json={
        "id": "1729388618695479397",
        "startDate": "2024-10-01",
        "endDate": "2024-10-30",
        "authority": True,
        "pageNo": 1,
        "pageSize": 10,
        "sort": [{"field": "revenue", "type": "DESC"}],
    },
)
# {
#   "success": true,
#   "data": 46,
#   "message": null,
#   "cached": null,
#   "code": null
# }


r = s.post(
    "https://www.kalodata.com/product/detail/live/queryList",
    headers={"content-length": "161"},
    json={
        "id": "1729388618695479397",
        "startDate": "2024-10-01",
        "endDate": "2024-10-30",
        "authority": True,
        "pageNo": 1,
        "pageSize": 10,
        "sort": [{"field": "revenue", "type": "DESC"}],
    },
)
# {
#   "success": true,
#   "data": [
#     {
#       "create_time": "2024/10/03 13:51:16",
#       "shortUrl": "",
#       "handle": "bfusuplug",
#       "unit_price": "$29.99",
#       "title": "gaming and promotions",
#       "record_type": "SCREENSHOT",
#       "finish_time": "2024/10/03 14:01:04",
#       "is_purchase": false,
#       "duration": "9m",
#       "screenshotUrl": "",
#       "sale": "6",
#       "revenue": "$179.94",
#       "id": "7421607625563720491",
#       "views": 283
#     },
#     {
#       "create_time": "2024/10/10 20:17:36",
#       "shortUrl": "",
#       "handle": "ryan.maxwel22",
#       "unit_price": "$29.99",
#       "title": "Lets Go LIVE!",
#       "record_type": "SCREENSHOT",
#       "finish_time": "2024/10/11 03:58:19",
#       "is_purchase": false,
#       "duration": "7h 40m",
#       "screenshotUrl": "https://d15xsrghoj5xvi.cloudfront.net/live/7424305212980710186/screenshot.png?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEDIaDmFwLXNvdXRoZWFzdC0xIkcwRQIgaHt0FT%2FgmTS8vkNPMYywMa27bkZvx%2FB6seMmRNBQEioCIQDw4P5lDMyXKQQflaLzwoJ3HtmNVfbXEe3yJZS4DioB%2FSrUBQir%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAEaDDEzNjM3Njc4NDc4OCIMTrswYh99exxy3sXNKqgFfdM%2Bx28OUTnbk75p%2BM3lGFAK4Riwq0ISrveq5wXakZ17eWk1gioAyccwu34dtgWk15OUWDM85i7zeKgcS13VRilSfuMc6u66U%2FLgH525UzcS4d%2B6jtyCP9LblZVHgSsDcYZcuauQsnhm1sq49n%2BzvLlYDnapIQACc5aYhI4GngjGYGk%2BvXxORU5cqeJ3Jwl9Ccm%2FPI%2BoTrhRci%2BsELob8%2BZFRe%2FxqaEhqIzAq3w0XCPhBeFaBttjYPi6WC8%2FYQs%2Fx05koqi2VECn5tsdZVYeBzMFa9Wta5ZIbzShe%2BiOuDxCcT%2FCPfMqgW%2F928ymH3xYVlRFUcHDBp%2BYS5af%2FW4v15L%2FpU2hlRSFP219FPpEhZISxBgEkTGxG93sgycBCc6zI6H%2Bo4S159qnK48845NolmSR4prfyhgZ0%2BzP912Y6IjxDKj50N4nTLzRRJ5vBBsM8ubu9EKPANHnuIeVfLHZ2wp4ExuPXLAPyS%2BmgpgGRiIIZoX3C3S1m747s%2FmY4g1YyWO2s4pOR5PoFtMVCIBIcTGz17IJdyHBr51yWrbBt1CU5T2VoY7MkpDYcXSLRfyK1b%2FY0mpxMYg0oAVFbBMbJSHSTEAFT93pd8WOQZmptlqoFmhcFyPeBDWIPPxcRLQJJ%2Fa2v7CCrK72u3kMPzV1O%2FqcjVFo7XXOgVgFxB0Bvojh8Ch2KS%2BrMmZXqr%2FB%2BugHxdKdjKLIhstYtyqeUyGHsSuVnannXCzNDvr4Gwsa39gDh9JWPVPvOxHuOpetq3dgGinVqU4%2BIIneIrvI0stDR%2BBobcYUJtFDKEAY8c2S%2BwkXWmTo0rYw4genoBzn%2BijB1hOWJIwVy9HAZ5HZpqnwiTXzvJP2gXleMK3nJz5xjULcU5rq69a24Qhox0k8faBS1BwBzFQO4zEwtKGUuQY6sQG6qV%2FgdjXa0W73A5qMaTq6b97EBAEu6ljV1OW1StfGHrWCbvqf69EVkAUHV1afvadQh6gpyqahQjCF6W9foYe%2B%2FTeoWdpHA32StkM3%2FIE6Tp4EklIsmjLwpOgIpCRkNQPrwipwjiZN%2Bh5BQo1TJv2oxWsjgvOIU5X7uKHkOqEm4IcIxU2J2pPb4b6B63refiDbrYcer8Q4HO3rqC%2FZFDJq0lqLtVoRdXqxkWx1kUmB2j8%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20241101T200156Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=ASIAR7QFQS6KIKAUCIS3%2F20241101%2Fap-southeast-1%2Fs3%2Faws4_request&X-Amz-Signature=4390f4c96739cadf2a1c73f42547f904119e8793704d1685c8d3505c8b98e00a",
#       "sale": "6",
#       "revenue": "$179.94",
#       "id": "7424305212980710186",
#       "views": 5260
#     },
#     {
#       "create_time": "2024/10/14 11:11:26",
#       "shortUrl": "https://d15xsrghoj5xvi.cloudfront.net/live_short/7425647629306055467.mp4?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEDIaDmFwLXNvdXRoZWFzdC0xIkcwRQIgaHt0FT%2FgmTS8vkNPMYywMa27bkZvx%2FB6seMmRNBQEioCIQDw4P5lDMyXKQQflaLzwoJ3HtmNVfbXEe3yJZS4DioB%2FSrUBQir%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAEaDDEzNjM3Njc4NDc4OCIMTrswYh99exxy3sXNKqgFfdM%2Bx28OUTnbk75p%2BM3lGFAK4Riwq0ISrveq5wXakZ17eWk1gioAyccwu34dtgWk15OUWDM85i7zeKgcS13VRilSfuMc6u66U%2FLgH525UzcS4d%2B6jtyCP9LblZVHgSsDcYZcuauQsnhm1sq49n%2BzvLlYDnapIQACc5aYhI4GngjGYGk%2BvXxORU5cqeJ3Jwl9Ccm%2FPI%2BoTrhRci%2BsELob8%2BZFRe%2FxqaEhqIzAq3w0XCPhBeFaBttjYPi6WC8%2FYQs%2Fx05koqi2VECn5tsdZVYeBzMFa9Wta5ZIbzShe%2BiOuDxCcT%2FCPfMqgW%2F928ymH3xYVlRFUcHDBp%2BYS5af%2FW4v15L%2FpU2hlRSFP219FPpEhZISxBgEkTGxG93sgycBCc6zI6H%2Bo4S159qnK48845NolmSR4prfyhgZ0%2BzP912Y6IjxDKj50N4nTLzRRJ5vBBsM8ubu9EKPANHnuIeVfLHZ2wp4ExuPXLAPyS%2BmgpgGRiIIZoX3C3S1m747s%2FmY4g1YyWO2s4pOR5PoFtMVCIBIcTGz17IJdyHBr51yWrbBt1CU5T2VoY7MkpDYcXSLRfyK1b%2FY0mpxMYg0oAVFbBMbJSHSTEAFT93pd8WOQZmptlqoFmhcFyPeBDWIPPxcRLQJJ%2Fa2v7CCrK72u3kMPzV1O%2FqcjVFo7XXOgVgFxB0Bvojh8Ch2KS%2BrMmZXqr%2FB%2BugHxdKdjKLIhstYtyqeUyGHsSuVnannXCzNDvr4Gwsa39gDh9JWPVPvOxHuOpetq3dgGinVqU4%2BIIneIrvI0stDR%2BBobcYUJtFDKEAY8c2S%2BwkXWmTo0rYw4genoBzn%2BijB1hOWJIwVy9HAZ5HZpqnwiTXzvJP2gXleMK3nJz5xjULcU5rq69a24Qhox0k8faBS1BwBzFQO4zEwtKGUuQY6sQG6qV%2FgdjXa0W73A5qMaTq6b97EBAEu6ljV1OW1StfGHrWCbvqf69EVkAUHV1afvadQh6gpyqahQjCF6W9foYe%2B%2FTeoWdpHA32StkM3%2FIE6Tp4EklIsmjLwpOgIpCRkNQPrwipwjiZN%2Bh5BQo1TJv2oxWsjgvOIU5X7uKHkOqEm4IcIxU2J2pPb4b6B63refiDbrYcer8Q4HO3rqC%2FZFDJq0lqLtVoRdXqxkWx1kUmB2j8%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20241101T200156Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=ASIAR7QFQS6KIKAUCIS3%2F20241101%2Fap-southeast-1%2Fs3%2Faws4_request&X-Amz-Signature=38c3c2a8e724bcdb084eb3c41e4d09eeef5ea176284a1e86e0cda41cab5f4c3b",
#       "handle": "ryan.maxwel22",
#       "unit_price": "$29.99",
#       "title": "Lets Go LIVE!",
#       "record_type": "SHORT",
#       "finish_time": "2024/10/15 00:38:56",
#       "is_purchase": false,
#       "duration": "13h 27m",
#       "screenshotUrl": "https://d15xsrghoj5xvi.cloudfront.net/live/7425647629306055467/screenshot.png?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEDIaDmFwLXNvdXRoZWFzdC0xIkcwRQIgaHt0FT%2FgmTS8vkNPMYywMa27bkZvx%2FB6seMmRNBQEioCIQDw4P5lDMyXKQQflaLzwoJ3HtmNVfbXEe3yJZS4DioB%2FSrUBQir%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAEaDDEzNjM3Njc4NDc4OCIMTrswYh99exxy3sXNKqgFfdM%2Bx28OUTnbk75p%2BM3lGFAK4Riwq0ISrveq5wXakZ17eWk1gioAyccwu34dtgWk15OUWDM85i7zeKgcS13VRilSfuMc6u66U%2FLgH525UzcS4d%2B6jtyCP9LblZVHgSsDcYZcuauQsnhm1sq49n%2BzvLlYDnapIQACc5aYhI4GngjGYGk%2BvXxORU5cqeJ3Jwl9Ccm%2FPI%2BoTrhRci%2BsELob8%2BZFRe%2FxqaEhqIzAq3w0XCPhBeFaBttjYPi6WC8%2FYQs%2Fx05koqi2VECn5tsdZVYeBzMFa9Wta5ZIbzShe%2BiOuDxCcT%2FCPfMqgW%2F928ymH3xYVlRFUcHDBp%2BYS5af%2FW4v15L%2FpU2hlRSFP219FPpEhZISxBgEkTGxG93sgycBCc6zI6H%2Bo4S159qnK48845NolmSR4prfyhgZ0%2BzP912Y6IjxDKj50N4nTLzRRJ5vBBsM8ubu9EKPANHnuIeVfLHZ2wp4ExuPXLAPyS%2BmgpgGRiIIZoX3C3S1m747s%2FmY4g1YyWO2s4pOR5PoFtMVCIBIcTGz17IJdyHBr51yWrbBt1CU5T2VoY7MkpDYcXSLRfyK1b%2FY0mpxMYg0oAVFbBMbJSHSTEAFT93pd8WOQZmptlqoFmhcFyPeBDWIPPxcRLQJJ%2Fa2v7CCrK72u3kMPzV1O%2FqcjVFo7XXOgVgFxB0Bvojh8Ch2KS%2BrMmZXqr%2FB%2BugHxdKdjKLIhstYtyqeUyGHsSuVnannXCzNDvr4Gwsa39gDh9JWPVPvOxHuOpetq3dgGinVqU4%2BIIneIrvI0stDR%2BBobcYUJtFDKEAY8c2S%2BwkXWmTo0rYw4genoBzn%2BijB1hOWJIwVy9HAZ5HZpqnwiTXzvJP2gXleMK3nJz5xjULcU5rq69a24Qhox0k8faBS1BwBzFQO4zEwtKGUuQY6sQG6qV%2FgdjXa0W73A5qMaTq6b97EBAEu6ljV1OW1StfGHrWCbvqf69EVkAUHV1afvadQh6gpyqahQjCF6W9foYe%2B%2FTeoWdpHA32StkM3%2FIE6Tp4EklIsmjLwpOgIpCRkNQPrwipwjiZN%2Bh5BQo1TJv2oxWsjgvOIU5X7uKHkOqEm4IcIxU2J2pPb4b6B63refiDbrYcer8Q4HO3rqC%2FZFDJq0lqLtVoRdXqxkWx1kUmB2j8%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20241101T200156Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=ASIAR7QFQS6KIKAUCIS3%2F20241101%2Fap-southeast-1%2Fs3%2Faws4_request&X-Amz-Signature=414cc7f3cc1e34e1a6d0a7bc764c5f1fc977a79828158abb83c605866896ed4b",
#       "sale": "2",
#       "revenue": "$59.98",
#       "id": "7425647629306055467",
#       "views": 6398
#     },
#     {
#       "create_time": "2024/10/23 17:46:28",
#       "shortUrl": "https://d15xsrghoj5xvi.cloudfront.net/live_short/7429090147800861483.mp4?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEDIaDmFwLXNvdXRoZWFzdC0xIkcwRQIgaHt0FT%2FgmTS8vkNPMYywMa27bkZvx%2FB6seMmRNBQEioCIQDw4P5lDMyXKQQflaLzwoJ3HtmNVfbXEe3yJZS4DioB%2FSrUBQir%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAEaDDEzNjM3Njc4NDc4OCIMTrswYh99exxy3sXNKqgFfdM%2Bx28OUTnbk75p%2BM3lGFAK4Riwq0ISrveq5wXakZ17eWk1gioAyccwu34dtgWk15OUWDM85i7zeKgcS13VRilSfuMc6u66U%2FLgH525UzcS4d%2B6jtyCP9LblZVHgSsDcYZcuauQsnhm1sq49n%2BzvLlYDnapIQACc5aYhI4GngjGYGk%2BvXxORU5cqeJ3Jwl9Ccm%2FPI%2BoTrhRci%2BsELob8%2BZFRe%2FxqaEhqIzAq3w0XCPhBeFaBttjYPi6WC8%2FYQs%2Fx05koqi2VECn5tsdZVYeBzMFa9Wta5ZIbzShe%2BiOuDxCcT%2FCPfMqgW%2F928ymH3xYVlRFUcHDBp%2BYS5af%2FW4v15L%2FpU2hlRSFP219FPpEhZISxBgEkTGxG93sgycBCc6zI6H%2Bo4S159qnK48845NolmSR4prfyhgZ0%2BzP912Y6IjxDKj50N4nTLzRRJ5vBBsM8ubu9EKPANHnuIeVfLHZ2wp4ExuPXLAPyS%2BmgpgGRiIIZoX3C3S1m747s%2FmY4g1YyWO2s4pOR5PoFtMVCIBIcTGz17IJdyHBr51yWrbBt1CU5T2VoY7MkpDYcXSLRfyK1b%2FY0mpxMYg0oAVFbBMbJSHSTEAFT93pd8WOQZmptlqoFmhcFyPeBDWIPPxcRLQJJ%2Fa2v7CCrK72u3kMPzV1O%2FqcjVFo7XXOgVgFxB0Bvojh8Ch2KS%2BrMmZXqr%2FB%2BugHxdKdjKLIhstYtyqeUyGHsSuVnannXCzNDvr4Gwsa39gDh9JWPVPvOxHuOpetq3dgGinVqU4%2BIIneIrvI0stDR%2BBobcYUJtFDKEAY8c2S%2BwkXWmTo0rYw4genoBzn%2BijB1hOWJIwVy9HAZ5HZpqnwiTXzvJP2gXleMK3nJz5xjULcU5rq69a24Qhox0k8faBS1BwBzFQO4zEwtKGUuQY6sQG6qV%2FgdjXa0W73A5qMaTq6b97EBAEu6ljV1OW1StfGHrWCbvqf69EVkAUHV1afvadQh6gpyqahQjCF6W9foYe%2B%2FTeoWdpHA32StkM3%2FIE6Tp4EklIsmjLwpOgIpCRkNQPrwipwjiZN%2Bh5BQo1TJv2oxWsjgvOIU5X7uKHkOqEm4IcIxU2J2pPb4b6B63refiDbrYcer8Q4HO3rqC%2FZFDJq0lqLtVoRdXqxkWx1kUmB2j8%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20241101T200156Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=ASIAR7QFQS6KIKAUCIS3%2F20241101%2Fap-southeast-1%2Fs3%2Faws4_request&X-Amz-Signature=58dd00191db810fffa9f4276c0b4f5ef09959bbfeac67e6c2aac31bad9860981",
#       "handle": "ryan.maxwel22",
#       "unit_price": "$29.98",
#       "title": "Lets Go LIVE!",
#       "record_type": "SHORT",
#       "finish_time": "2024/10/24 03:51:55",
#       "is_purchase": false,
#       "duration": "10h 5m",
#       "screenshotUrl": "https://d15xsrghoj5xvi.cloudfront.net/live/7429090147800861483/screenshot.png?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEDIaDmFwLXNvdXRoZWFzdC0xIkcwRQIgaHt0FT%2FgmTS8vkNPMYywMa27bkZvx%2FB6seMmRNBQEioCIQDw4P5lDMyXKQQflaLzwoJ3HtmNVfbXEe3yJZS4DioB%2FSrUBQir%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAEaDDEzNjM3Njc4NDc4OCIMTrswYh99exxy3sXNKqgFfdM%2Bx28OUTnbk75p%2BM3lGFAK4Riwq0ISrveq5wXakZ17eWk1gioAyccwu34dtgWk15OUWDM85i7zeKgcS13VRilSfuMc6u66U%2FLgH525UzcS4d%2B6jtyCP9LblZVHgSsDcYZcuauQsnhm1sq49n%2BzvLlYDnapIQACc5aYhI4GngjGYGk%2BvXxORU5cqeJ3Jwl9Ccm%2FPI%2BoTrhRci%2BsELob8%2BZFRe%2FxqaEhqIzAq3w0XCPhBeFaBttjYPi6WC8%2FYQs%2Fx05koqi2VECn5tsdZVYeBzMFa9Wta5ZIbzShe%2BiOuDxCcT%2FCPfMqgW%2F928ymH3xYVlRFUcHDBp%2BYS5af%2FW4v15L%2FpU2hlRSFP219FPpEhZISxBgEkTGxG93sgycBCc6zI6H%2Bo4S159qnK48845NolmSR4prfyhgZ0%2BzP912Y6IjxDKj50N4nTLzRRJ5vBBsM8ubu9EKPANHnuIeVfLHZ2wp4ExuPXLAPyS%2BmgpgGRiIIZoX3C3S1m747s%2FmY4g1YyWO2s4pOR5PoFtMVCIBIcTGz17IJdyHBr51yWrbBt1CU5T2VoY7MkpDYcXSLRfyK1b%2FY0mpxMYg0oAVFbBMbJSHSTEAFT93pd8WOQZmptlqoFmhcFyPeBDWIPPxcRLQJJ%2Fa2v7CCrK72u3kMPzV1O%2FqcjVFo7XXOgVgFxB0Bvojh8Ch2KS%2BrMmZXqr%2FB%2BugHxdKdjKLIhstYtyqeUyGHsSuVnannXCzNDvr4Gwsa39gDh9JWPVPvOxHuOpetq3dgGinVqU4%2BIIneIrvI0stDR%2BBobcYUJtFDKEAY8c2S%2BwkXWmTo0rYw4genoBzn%2BijB1hOWJIwVy9HAZ5HZpqnwiTXzvJP2gXleMK3nJz5xjULcU5rq69a24Qhox0k8faBS1BwBzFQO4zEwtKGUuQY6sQG6qV%2FgdjXa0W73A5qMaTq6b97EBAEu6ljV1OW1StfGHrWCbvqf69EVkAUHV1afvadQh6gpyqahQjCF6W9foYe%2B%2FTeoWdpHA32StkM3%2FIE6Tp4EklIsmjLwpOgIpCRkNQPrwipwjiZN%2Bh5BQo1TJv2oxWsjgvOIU5X7uKHkOqEm4IcIxU2J2pPb4b6B63refiDbrYcer8Q4HO3rqC%2FZFDJq0lqLtVoRdXqxkWx1kUmB2j8%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20241101T200156Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=ASIAR7QFQS6KIKAUCIS3%2F20241101%2Fap-southeast-1%2Fs3%2Faws4_request&X-Amz-Signature=912f2f849ee5c0f09f8452b6316d7ef75f6b8ef81638c879d5365e8102e7c5e4",
#       "sale": "2",
#       "revenue": "$59.96",
#       "id": "7429090147800861483",
#       "views": 9380
#     },
#     {
#       "create_time": "2024/10/15 17:31:03",
#       "shortUrl": "",
#       "handle": "purelywhitedeluxe",
#       "unit_price": "$29.99",
#       "title": "EXCLUSIVE LIVE FLASH SALE\u2728\u2601",
#       "record_type": "SCREENSHOT",
#       "finish_time": "2024/10/15 18:54:38",
#       "is_purchase": false,
#       "duration": "1h 23m",
#       "screenshotUrl": "https://d15xsrghoj5xvi.cloudfront.net/live/7426117497297881899/screenshot.png?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEDIaDmFwLXNvdXRoZWFzdC0xIkcwRQIgaHt0FT%2FgmTS8vkNPMYywMa27bkZvx%2FB6seMmRNBQEioCIQDw4P5lDMyXKQQflaLzwoJ3HtmNVfbXEe3yJZS4DioB%2FSrUBQir%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAEaDDEzNjM3Njc4NDc4OCIMTrswYh99exxy3sXNKqgFfdM%2Bx28OUTnbk75p%2BM3lGFAK4Riwq0ISrveq5wXakZ17eWk1gioAyccwu34dtgWk15OUWDM85i7zeKgcS13VRilSfuMc6u66U%2FLgH525UzcS4d%2B6jtyCP9LblZVHgSsDcYZcuauQsnhm1sq49n%2BzvLlYDnapIQACc5aYhI4GngjGYGk%2BvXxORU5cqeJ3Jwl9Ccm%2FPI%2BoTrhRci%2BsELob8%2BZFRe%2FxqaEhqIzAq3w0XCPhBeFaBttjYPi6WC8%2FYQs%2Fx05koqi2VECn5tsdZVYeBzMFa9Wta5ZIbzShe%2BiOuDxCcT%2FCPfMqgW%2F928ymH3xYVlRFUcHDBp%2BYS5af%2FW4v15L%2FpU2hlRSFP219FPpEhZISxBgEkTGxG93sgycBCc6zI6H%2Bo4S159qnK48845NolmSR4prfyhgZ0%2BzP912Y6IjxDKj50N4nTLzRRJ5vBBsM8ubu9EKPANHnuIeVfLHZ2wp4ExuPXLAPyS%2BmgpgGRiIIZoX3C3S1m747s%2FmY4g1YyWO2s4pOR5PoFtMVCIBIcTGz17IJdyHBr51yWrbBt1CU5T2VoY7MkpDYcXSLRfyK1b%2FY0mpxMYg0oAVFbBMbJSHSTEAFT93pd8WOQZmptlqoFmhcFyPeBDWIPPxcRLQJJ%2Fa2v7CCrK72u3kMPzV1O%2FqcjVFo7XXOgVgFxB0Bvojh8Ch2KS%2BrMmZXqr%2FB%2BugHxdKdjKLIhstYtyqeUyGHsSuVnannXCzNDvr4Gwsa39gDh9JWPVPvOxHuOpetq3dgGinVqU4%2BIIneIrvI0stDR%2BBobcYUJtFDKEAY8c2S%2BwkXWmTo0rYw4genoBzn%2BijB1hOWJIwVy9HAZ5HZpqnwiTXzvJP2gXleMK3nJz5xjULcU5rq69a24Qhox0k8faBS1BwBzFQO4zEwtKGUuQY6sQG6qV%2FgdjXa0W73A5qMaTq6b97EBAEu6ljV1OW1StfGHrWCbvqf69EVkAUHV1afvadQh6gpyqahQjCF6W9foYe%2B%2FTeoWdpHA32StkM3%2FIE6Tp4EklIsmjLwpOgIpCRkNQPrwipwjiZN%2Bh5BQo1TJv2oxWsjgvOIU5X7uKHkOqEm4IcIxU2J2pPb4b6B63refiDbrYcer8Q4HO3rqC%2FZFDJq0lqLtVoRdXqxkWx1kUmB2j8%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20241101T200156Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=ASIAR7QFQS6KIKAUCIS3%2F20241101%2Fap-southeast-1%2Fs3%2Faws4_request&X-Amz-Signature=58b91a4c00a7a6b0259709de166506c2c7dcdefa4c42e95dc7eaf4a1346f408a",
#       "sale": "1",
#       "revenue": "$29.99",
#       "id": "7426117497297881899",
#       "views": 789
#     },
#     {
#       "create_time": "2024/10/11 14:17:49",
#       "shortUrl": "",
#       "handle": "ryan.maxwel22",
#       "unit_price": "$29.99",
#       "title": "Lets Go LIVE!",
#       "record_type": "SCREENSHOT",
#       "finish_time": "2024/10/12 03:52:15",
#       "is_purchase": false,
#       "duration": "13h 34m",
#       "screenshotUrl": "https://d15xsrghoj5xvi.cloudfront.net/live/7424583379372231467/screenshot.png?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEDIaDmFwLXNvdXRoZWFzdC0xIkcwRQIgaHt0FT%2FgmTS8vkNPMYywMa27bkZvx%2FB6seMmRNBQEioCIQDw4P5lDMyXKQQflaLzwoJ3HtmNVfbXEe3yJZS4DioB%2FSrUBQir%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAEaDDEzNjM3Njc4NDc4OCIMTrswYh99exxy3sXNKqgFfdM%2Bx28OUTnbk75p%2BM3lGFAK4Riwq0ISrveq5wXakZ17eWk1gioAyccwu34dtgWk15OUWDM85i7zeKgcS13VRilSfuMc6u66U%2FLgH525UzcS4d%2B6jtyCP9LblZVHgSsDcYZcuauQsnhm1sq49n%2BzvLlYDnapIQACc5aYhI4GngjGYGk%2BvXxORU5cqeJ3Jwl9Ccm%2FPI%2BoTrhRci%2BsELob8%2BZFRe%2FxqaEhqIzAq3w0XCPhBeFaBttjYPi6WC8%2FYQs%2Fx05koqi2VECn5tsdZVYeBzMFa9Wta5ZIbzShe%2BiOuDxCcT%2FCPfMqgW%2F928ymH3xYVlRFUcHDBp%2BYS5af%2FW4v15L%2FpU2hlRSFP219FPpEhZISxBgEkTGxG93sgycBCc6zI6H%2Bo4S159qnK48845NolmSR4prfyhgZ0%2BzP912Y6IjxDKj50N4nTLzRRJ5vBBsM8ubu9EKPANHnuIeVfLHZ2wp4ExuPXLAPyS%2BmgpgGRiIIZoX3C3S1m747s%2FmY4g1YyWO2s4pOR5PoFtMVCIBIcTGz17IJdyHBr51yWrbBt1CU5T2VoY7MkpDYcXSLRfyK1b%2FY0mpxMYg0oAVFbBMbJSHSTEAFT93pd8WOQZmptlqoFmhcFyPeBDWIPPxcRLQJJ%2Fa2v7CCrK72u3kMPzV1O%2FqcjVFo7XXOgVgFxB0Bvojh8Ch2KS%2BrMmZXqr%2FB%2BugHxdKdjKLIhstYtyqeUyGHsSuVnannXCzNDvr4Gwsa39gDh9JWPVPvOxHuOpetq3dgGinVqU4%2BIIneIrvI0stDR%2BBobcYUJtFDKEAY8c2S%2BwkXWmTo0rYw4genoBzn%2BijB1hOWJIwVy9HAZ5HZpqnwiTXzvJP2gXleMK3nJz5xjULcU5rq69a24Qhox0k8faBS1BwBzFQO4zEwtKGUuQY6sQG6qV%2FgdjXa0W73A5qMaTq6b97EBAEu6ljV1OW1StfGHrWCbvqf69EVkAUHV1afvadQh6gpyqahQjCF6W9foYe%2B%2FTeoWdpHA32StkM3%2FIE6Tp4EklIsmjLwpOgIpCRkNQPrwipwjiZN%2Bh5BQo1TJv2oxWsjgvOIU5X7uKHkOqEm4IcIxU2J2pPb4b6B63refiDbrYcer8Q4HO3rqC%2FZFDJq0lqLtVoRdXqxkWx1kUmB2j8%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20241101T200156Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=ASIAR7QFQS6KIKAUCIS3%2F20241101%2Fap-southeast-1%2Fs3%2Faws4_request&X-Amz-Signature=2a88570826cf067b96828252e1635c330625782bacbf98c2463831420fbd326b",
#       "sale": "1",
#       "revenue": "$29.99",
#       "id": "7424583379372231467",
#       "views": 9550
#     },
#     {
#       "create_time": "2024/10/26 19:23:34",
#       "shortUrl": "https://d15xsrghoj5xvi.cloudfront.net/live_short/7430228573119679274.mp4?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEDIaDmFwLXNvdXRoZWFzdC0xIkcwRQIgaHt0FT%2FgmTS8vkNPMYywMa27bkZvx%2FB6seMmRNBQEioCIQDw4P5lDMyXKQQflaLzwoJ3HtmNVfbXEe3yJZS4DioB%2FSrUBQir%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAEaDDEzNjM3Njc4NDc4OCIMTrswYh99exxy3sXNKqgFfdM%2Bx28OUTnbk75p%2BM3lGFAK4Riwq0ISrveq5wXakZ17eWk1gioAyccwu34dtgWk15OUWDM85i7zeKgcS13VRilSfuMc6u66U%2FLgH525UzcS4d%2B6jtyCP9LblZVHgSsDcYZcuauQsnhm1sq49n%2BzvLlYDnapIQACc5aYhI4GngjGYGk%2BvXxORU5cqeJ3Jwl9Ccm%2FPI%2BoTrhRci%2BsELob8%2BZFRe%2FxqaEhqIzAq3w0XCPhBeFaBttjYPi6WC8%2FYQs%2Fx05koqi2VECn5tsdZVYeBzMFa9Wta5ZIbzShe%2BiOuDxCcT%2FCPfMqgW%2F928ymH3xYVlRFUcHDBp%2BYS5af%2FW4v15L%2FpU2hlRSFP219FPpEhZISxBgEkTGxG93sgycBCc6zI6H%2Bo4S159qnK48845NolmSR4prfyhgZ0%2BzP912Y6IjxDKj50N4nTLzRRJ5vBBsM8ubu9EKPANHnuIeVfLHZ2wp4ExuPXLAPyS%2BmgpgGRiIIZoX3C3S1m747s%2FmY4g1YyWO2s4pOR5PoFtMVCIBIcTGz17IJdyHBr51yWrbBt1CU5T2VoY7MkpDYcXSLRfyK1b%2FY0mpxMYg0oAVFbBMbJSHSTEAFT93pd8WOQZmptlqoFmhcFyPeBDWIPPxcRLQJJ%2Fa2v7CCrK72u3kMPzV1O%2FqcjVFo7XXOgVgFxB0Bvojh8Ch2KS%2BrMmZXqr%2FB%2BugHxdKdjKLIhstYtyqeUyGHsSuVnannXCzNDvr4Gwsa39gDh9JWPVPvOxHuOpetq3dgGinVqU4%2BIIneIrvI0stDR%2BBobcYUJtFDKEAY8c2S%2BwkXWmTo0rYw4genoBzn%2BijB1hOWJIwVy9HAZ5HZpqnwiTXzvJP2gXleMK3nJz5xjULcU5rq69a24Qhox0k8faBS1BwBzFQO4zEwtKGUuQY6sQG6qV%2FgdjXa0W73A5qMaTq6b97EBAEu6ljV1OW1StfGHrWCbvqf69EVkAUHV1afvadQh6gpyqahQjCF6W9foYe%2B%2FTeoWdpHA32StkM3%2FIE6Tp4EklIsmjLwpOgIpCRkNQPrwipwjiZN%2Bh5BQo1TJv2oxWsjgvOIU5X7uKHkOqEm4IcIxU2J2pPb4b6B63refiDbrYcer8Q4HO3rqC%2FZFDJq0lqLtVoRdXqxkWx1kUmB2j8%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20241101T200156Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=ASIAR7QFQS6KIKAUCIS3%2F20241101%2Fap-southeast-1%2Fs3%2Faws4_request&X-Amz-Signature=4d7456860be6fd6d86ea28c326ae0627c027719d2391ed556834eb260fefadef",
#       "handle": "ryan.maxwel22",
#       "unit_price": "$29.99",
#       "title": "Lets Go LIVE!",
#       "record_type": "SHORT",
#       "finish_time": "2024/10/27 02:52:14",
#       "is_purchase": false,
#       "duration": "7h 28m",
#       "screenshotUrl": "https://d15xsrghoj5xvi.cloudfront.net/live/7430228573119679274/screenshot.png?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEDIaDmFwLXNvdXRoZWFzdC0xIkcwRQIgaHt0FT%2FgmTS8vkNPMYywMa27bkZvx%2FB6seMmRNBQEioCIQDw4P5lDMyXKQQflaLzwoJ3HtmNVfbXEe3yJZS4DioB%2FSrUBQir%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAEaDDEzNjM3Njc4NDc4OCIMTrswYh99exxy3sXNKqgFfdM%2Bx28OUTnbk75p%2BM3lGFAK4Riwq0ISrveq5wXakZ17eWk1gioAyccwu34dtgWk15OUWDM85i7zeKgcS13VRilSfuMc6u66U%2FLgH525UzcS4d%2B6jtyCP9LblZVHgSsDcYZcuauQsnhm1sq49n%2BzvLlYDnapIQACc5aYhI4GngjGYGk%2BvXxORU5cqeJ3Jwl9Ccm%2FPI%2BoTrhRci%2BsELob8%2BZFRe%2FxqaEhqIzAq3w0XCPhBeFaBttjYPi6WC8%2FYQs%2Fx05koqi2VECn5tsdZVYeBzMFa9Wta5ZIbzShe%2BiOuDxCcT%2FCPfMqgW%2F928ymH3xYVlRFUcHDBp%2BYS5af%2FW4v15L%2FpU2hlRSFP219FPpEhZISxBgEkTGxG93sgycBCc6zI6H%2Bo4S159qnK48845NolmSR4prfyhgZ0%2BzP912Y6IjxDKj50N4nTLzRRJ5vBBsM8ubu9EKPANHnuIeVfLHZ2wp4ExuPXLAPyS%2BmgpgGRiIIZoX3C3S1m747s%2FmY4g1YyWO2s4pOR5PoFtMVCIBIcTGz17IJdyHBr51yWrbBt1CU5T2VoY7MkpDYcXSLRfyK1b%2FY0mpxMYg0oAVFbBMbJSHSTEAFT93pd8WOQZmptlqoFmhcFyPeBDWIPPxcRLQJJ%2Fa2v7CCrK72u3kMPzV1O%2FqcjVFo7XXOgVgFxB0Bvojh8Ch2KS%2BrMmZXqr%2FB%2BugHxdKdjKLIhstYtyqeUyGHsSuVnannXCzNDvr4Gwsa39gDh9JWPVPvOxHuOpetq3dgGinVqU4%2BIIneIrvI0stDR%2BBobcYUJtFDKEAY8c2S%2BwkXWmTo0rYw4genoBzn%2BijB1hOWJIwVy9HAZ5HZpqnwiTXzvJP2gXleMK3nJz5xjULcU5rq69a24Qhox0k8faBS1BwBzFQO4zEwtKGUuQY6sQG6qV%2FgdjXa0W73A5qMaTq6b97EBAEu6ljV1OW1StfGHrWCbvqf69EVkAUHV1afvadQh6gpyqahQjCF6W9foYe%2B%2FTeoWdpHA32StkM3%2FIE6Tp4EklIsmjLwpOgIpCRkNQPrwipwjiZN%2Bh5BQo1TJv2oxWsjgvOIU5X7uKHkOqEm4IcIxU2J2pPb4b6B63refiDbrYcer8Q4HO3rqC%2FZFDJq0lqLtVoRdXqxkWx1kUmB2j8%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20241101T200156Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=ASIAR7QFQS6KIKAUCIS3%2F20241101%2Fap-southeast-1%2Fs3%2Faws4_request&X-Amz-Signature=23e7386dc7e2131e59cf5564711b7ea4347bd661b24ed969642682b1f86bb974",
#       "sale": "1",
#       "revenue": "$29.99",
#       "id": "7430228573119679274",
#       "views": 7512
#     },
#     {
#       "create_time": "2024/10/20 10:40:48",
#       "shortUrl": "https://d15xsrghoj5xvi.cloudfront.net/live_short/7427866853743119146.mp4?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEDIaDmFwLXNvdXRoZWFzdC0xIkcwRQIgaHt0FT%2FgmTS8vkNPMYywMa27bkZvx%2FB6seMmRNBQEioCIQDw4P5lDMyXKQQflaLzwoJ3HtmNVfbXEe3yJZS4DioB%2FSrUBQir%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAEaDDEzNjM3Njc4NDc4OCIMTrswYh99exxy3sXNKqgFfdM%2Bx28OUTnbk75p%2BM3lGFAK4Riwq0ISrveq5wXakZ17eWk1gioAyccwu34dtgWk15OUWDM85i7zeKgcS13VRilSfuMc6u66U%2FLgH525UzcS4d%2B6jtyCP9LblZVHgSsDcYZcuauQsnhm1sq49n%2BzvLlYDnapIQACc5aYhI4GngjGYGk%2BvXxORU5cqeJ3Jwl9Ccm%2FPI%2BoTrhRci%2BsELob8%2BZFRe%2FxqaEhqIzAq3w0XCPhBeFaBttjYPi6WC8%2FYQs%2Fx05koqi2VECn5tsdZVYeBzMFa9Wta5ZIbzShe%2BiOuDxCcT%2FCPfMqgW%2F928ymH3xYVlRFUcHDBp%2BYS5af%2FW4v15L%2FpU2hlRSFP219FPpEhZISxBgEkTGxG93sgycBCc6zI6H%2Bo4S159qnK48845NolmSR4prfyhgZ0%2BzP912Y6IjxDKj50N4nTLzRRJ5vBBsM8ubu9EKPANHnuIeVfLHZ2wp4ExuPXLAPyS%2BmgpgGRiIIZoX3C3S1m747s%2FmY4g1YyWO2s4pOR5PoFtMVCIBIcTGz17IJdyHBr51yWrbBt1CU5T2VoY7MkpDYcXSLRfyK1b%2FY0mpxMYg0oAVFbBMbJSHSTEAFT93pd8WOQZmptlqoFmhcFyPeBDWIPPxcRLQJJ%2Fa2v7CCrK72u3kMPzV1O%2FqcjVFo7XXOgVgFxB0Bvojh8Ch2KS%2BrMmZXqr%2FB%2BugHxdKdjKLIhstYtyqeUyGHsSuVnannXCzNDvr4Gwsa39gDh9JWPVPvOxHuOpetq3dgGinVqU4%2BIIneIrvI0stDR%2BBobcYUJtFDKEAY8c2S%2BwkXWmTo0rYw4genoBzn%2BijB1hOWJIwVy9HAZ5HZpqnwiTXzvJP2gXleMK3nJz5xjULcU5rq69a24Qhox0k8faBS1BwBzFQO4zEwtKGUuQY6sQG6qV%2FgdjXa0W73A5qMaTq6b97EBAEu6ljV1OW1StfGHrWCbvqf69EVkAUHV1afvadQh6gpyqahQjCF6W9foYe%2B%2FTeoWdpHA32StkM3%2FIE6Tp4EklIsmjLwpOgIpCRkNQPrwipwjiZN%2Bh5BQo1TJv2oxWsjgvOIU5X7uKHkOqEm4IcIxU2J2pPb4b6B63refiDbrYcer8Q4HO3rqC%2FZFDJq0lqLtVoRdXqxkWx1kUmB2j8%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20241101T200156Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=ASIAR7QFQS6KIKAUCIS3%2F20241101%2Fap-southeast-1%2Fs3%2Faws4_request&X-Amz-Signature=edd54004c572dfbcf6db06f2a83dbfe5a71693d292008f30996886496b936c15",
#       "handle": "ryan.maxwel22",
#       "unit_price": "$29.99",
#       "title": "Lets Go LIVE!",
#       "record_type": "SHORT",
#       "finish_time": "2024/10/20 18:50:26",
#       "is_purchase": false,
#       "duration": "8h 9m",
#       "screenshotUrl": "https://d15xsrghoj5xvi.cloudfront.net/live/7427866853743119146/screenshot.png?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEDIaDmFwLXNvdXRoZWFzdC0xIkcwRQIgaHt0FT%2FgmTS8vkNPMYywMa27bkZvx%2FB6seMmRNBQEioCIQDw4P5lDMyXKQQflaLzwoJ3HtmNVfbXEe3yJZS4DioB%2FSrUBQir%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAEaDDEzNjM3Njc4NDc4OCIMTrswYh99exxy3sXNKqgFfdM%2Bx28OUTnbk75p%2BM3lGFAK4Riwq0ISrveq5wXakZ17eWk1gioAyccwu34dtgWk15OUWDM85i7zeKgcS13VRilSfuMc6u66U%2FLgH525UzcS4d%2B6jtyCP9LblZVHgSsDcYZcuauQsnhm1sq49n%2BzvLlYDnapIQACc5aYhI4GngjGYGk%2BvXxORU5cqeJ3Jwl9Ccm%2FPI%2BoTrhRci%2BsELob8%2BZFRe%2FxqaEhqIzAq3w0XCPhBeFaBttjYPi6WC8%2FYQs%2Fx05koqi2VECn5tsdZVYeBzMFa9Wta5ZIbzShe%2BiOuDxCcT%2FCPfMqgW%2F928ymH3xYVlRFUcHDBp%2BYS5af%2FW4v15L%2FpU2hlRSFP219FPpEhZISxBgEkTGxG93sgycBCc6zI6H%2Bo4S159qnK48845NolmSR4prfyhgZ0%2BzP912Y6IjxDKj50N4nTLzRRJ5vBBsM8ubu9EKPANHnuIeVfLHZ2wp4ExuPXLAPyS%2BmgpgGRiIIZoX3C3S1m747s%2FmY4g1YyWO2s4pOR5PoFtMVCIBIcTGz17IJdyHBr51yWrbBt1CU5T2VoY7MkpDYcXSLRfyK1b%2FY0mpxMYg0oAVFbBMbJSHSTEAFT93pd8WOQZmptlqoFmhcFyPeBDWIPPxcRLQJJ%2Fa2v7CCrK72u3kMPzV1O%2FqcjVFo7XXOgVgFxB0Bvojh8Ch2KS%2BrMmZXqr%2FB%2BugHxdKdjKLIhstYtyqeUyGHsSuVnannXCzNDvr4Gwsa39gDh9JWPVPvOxHuOpetq3dgGinVqU4%2BIIneIrvI0stDR%2BBobcYUJtFDKEAY8c2S%2BwkXWmTo0rYw4genoBzn%2BijB1hOWJIwVy9HAZ5HZpqnwiTXzvJP2gXleMK3nJz5xjULcU5rq69a24Qhox0k8faBS1BwBzFQO4zEwtKGUuQY6sQG6qV%2FgdjXa0W73A5qMaTq6b97EBAEu6ljV1OW1StfGHrWCbvqf69EVkAUHV1afvadQh6gpyqahQjCF6W9foYe%2B%2FTeoWdpHA32StkM3%2FIE6Tp4EklIsmjLwpOgIpCRkNQPrwipwjiZN%2Bh5BQo1TJv2oxWsjgvOIU5X7uKHkOqEm4IcIxU2J2pPb4b6B63refiDbrYcer8Q4HO3rqC%2FZFDJq0lqLtVoRdXqxkWx1kUmB2j8%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20241101T200156Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=ASIAR7QFQS6KIKAUCIS3%2F20241101%2Fap-southeast-1%2Fs3%2Faws4_request&X-Amz-Signature=6273d6d52794d0ee17482fa85860ce2ca6f36df03f3d50133eb625cf0bc61498",
#       "sale": "1",
#       "revenue": "$29.99",
#       "id": "7427866853743119146",
#       "views": 10557
#     },
#     {
#       "create_time": "2024/10/15 12:08:08",
#       "shortUrl": "https://d15xsrghoj5xvi.cloudfront.net/live_short/7426034111493655342.mp4?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEDIaDmFwLXNvdXRoZWFzdC0xIkcwRQIgaHt0FT%2FgmTS8vkNPMYywMa27bkZvx%2FB6seMmRNBQEioCIQDw4P5lDMyXKQQflaLzwoJ3HtmNVfbXEe3yJZS4DioB%2FSrUBQir%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAEaDDEzNjM3Njc4NDc4OCIMTrswYh99exxy3sXNKqgFfdM%2Bx28OUTnbk75p%2BM3lGFAK4Riwq0ISrveq5wXakZ17eWk1gioAyccwu34dtgWk15OUWDM85i7zeKgcS13VRilSfuMc6u66U%2FLgH525UzcS4d%2B6jtyCP9LblZVHgSsDcYZcuauQsnhm1sq49n%2BzvLlYDnapIQACc5aYhI4GngjGYGk%2BvXxORU5cqeJ3Jwl9Ccm%2FPI%2BoTrhRci%2BsELob8%2BZFRe%2FxqaEhqIzAq3w0XCPhBeFaBttjYPi6WC8%2FYQs%2Fx05koqi2VECn5tsdZVYeBzMFa9Wta5ZIbzShe%2BiOuDxCcT%2FCPfMqgW%2F928ymH3xYVlRFUcHDBp%2BYS5af%2FW4v15L%2FpU2hlRSFP219FPpEhZISxBgEkTGxG93sgycBCc6zI6H%2Bo4S159qnK48845NolmSR4prfyhgZ0%2BzP912Y6IjxDKj50N4nTLzRRJ5vBBsM8ubu9EKPANHnuIeVfLHZ2wp4ExuPXLAPyS%2BmgpgGRiIIZoX3C3S1m747s%2FmY4g1YyWO2s4pOR5PoFtMVCIBIcTGz17IJdyHBr51yWrbBt1CU5T2VoY7MkpDYcXSLRfyK1b%2FY0mpxMYg0oAVFbBMbJSHSTEAFT93pd8WOQZmptlqoFmhcFyPeBDWIPPxcRLQJJ%2Fa2v7CCrK72u3kMPzV1O%2FqcjVFo7XXOgVgFxB0Bvojh8Ch2KS%2BrMmZXqr%2FB%2BugHxdKdjKLIhstYtyqeUyGHsSuVnannXCzNDvr4Gwsa39gDh9JWPVPvOxHuOpetq3dgGinVqU4%2BIIneIrvI0stDR%2BBobcYUJtFDKEAY8c2S%2BwkXWmTo0rYw4genoBzn%2BijB1hOWJIwVy9HAZ5HZpqnwiTXzvJP2gXleMK3nJz5xjULcU5rq69a24Qhox0k8faBS1BwBzFQO4zEwtKGUuQY6sQG6qV%2FgdjXa0W73A5qMaTq6b97EBAEu6ljV1OW1StfGHrWCbvqf69EVkAUHV1afvadQh6gpyqahQjCF6W9foYe%2B%2FTeoWdpHA32StkM3%2FIE6Tp4EklIsmjLwpOgIpCRkNQPrwipwjiZN%2Bh5BQo1TJv2oxWsjgvOIU5X7uKHkOqEm4IcIxU2J2pPb4b6B63refiDbrYcer8Q4HO3rqC%2FZFDJq0lqLtVoRdXqxkWx1kUmB2j8%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20241101T200156Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=ASIAR7QFQS6KIKAUCIS3%2F20241101%2Fap-southeast-1%2Fs3%2Faws4_request&X-Amz-Signature=b9031206000d649cef183c79ba67910b859baa5f15bbc941320111b9d1973db8",
#       "handle": "ryan.maxwel22",
#       "unit_price": "$29.99",
#       "title": "Lets Go LIVE!",
#       "record_type": "SHORT",
#       "finish_time": "2024/10/15 20:53:20",
#       "is_purchase": false,
#       "duration": "8h 45m",
#       "screenshotUrl": "https://d15xsrghoj5xvi.cloudfront.net/live/7426034111493655342/screenshot.png?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEDIaDmFwLXNvdXRoZWFzdC0xIkcwRQIgaHt0FT%2FgmTS8vkNPMYywMa27bkZvx%2FB6seMmRNBQEioCIQDw4P5lDMyXKQQflaLzwoJ3HtmNVfbXEe3yJZS4DioB%2FSrUBQir%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAEaDDEzNjM3Njc4NDc4OCIMTrswYh99exxy3sXNKqgFfdM%2Bx28OUTnbk75p%2BM3lGFAK4Riwq0ISrveq5wXakZ17eWk1gioAyccwu34dtgWk15OUWDM85i7zeKgcS13VRilSfuMc6u66U%2FLgH525UzcS4d%2B6jtyCP9LblZVHgSsDcYZcuauQsnhm1sq49n%2BzvLlYDnapIQACc5aYhI4GngjGYGk%2BvXxORU5cqeJ3Jwl9Ccm%2FPI%2BoTrhRci%2BsELob8%2BZFRe%2FxqaEhqIzAq3w0XCPhBeFaBttjYPi6WC8%2FYQs%2Fx05koqi2VECn5tsdZVYeBzMFa9Wta5ZIbzShe%2BiOuDxCcT%2FCPfMqgW%2F928ymH3xYVlRFUcHDBp%2BYS5af%2FW4v15L%2FpU2hlRSFP219FPpEhZISxBgEkTGxG93sgycBCc6zI6H%2Bo4S159qnK48845NolmSR4prfyhgZ0%2BzP912Y6IjxDKj50N4nTLzRRJ5vBBsM8ubu9EKPANHnuIeVfLHZ2wp4ExuPXLAPyS%2BmgpgGRiIIZoX3C3S1m747s%2FmY4g1YyWO2s4pOR5PoFtMVCIBIcTGz17IJdyHBr51yWrbBt1CU5T2VoY7MkpDYcXSLRfyK1b%2FY0mpxMYg0oAVFbBMbJSHSTEAFT93pd8WOQZmptlqoFmhcFyPeBDWIPPxcRLQJJ%2Fa2v7CCrK72u3kMPzV1O%2FqcjVFo7XXOgVgFxB0Bvojh8Ch2KS%2BrMmZXqr%2FB%2BugHxdKdjKLIhstYtyqeUyGHsSuVnannXCzNDvr4Gwsa39gDh9JWPVPvOxHuOpetq3dgGinVqU4%2BIIneIrvI0stDR%2BBobcYUJtFDKEAY8c2S%2BwkXWmTo0rYw4genoBzn%2BijB1hOWJIwVy9HAZ5HZpqnwiTXzvJP2gXleMK3nJz5xjULcU5rq69a24Qhox0k8faBS1BwBzFQO4zEwtKGUuQY6sQG6qV%2FgdjXa0W73A5qMaTq6b97EBAEu6ljV1OW1StfGHrWCbvqf69EVkAUHV1afvadQh6gpyqahQjCF6W9foYe%2B%2FTeoWdpHA32StkM3%2FIE6Tp4EklIsmjLwpOgIpCRkNQPrwipwjiZN%2Bh5BQo1TJv2oxWsjgvOIU5X7uKHkOqEm4IcIxU2J2pPb4b6B63refiDbrYcer8Q4HO3rqC%2FZFDJq0lqLtVoRdXqxkWx1kUmB2j8%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20241101T200156Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=ASIAR7QFQS6KIKAUCIS3%2F20241101%2Fap-southeast-1%2Fs3%2Faws4_request&X-Amz-Signature=2b90c8e2bc108a6f27659eacbff049c092f426968e249341ed0fc17a7d74c6a9",
#       "sale": "1",
#       "revenue": "$29.99",
#       "id": "7426034111493655342",
#       "views": 4440
#     },
#     {
#       "create_time": "2024/10/30 15:49:57",
#       "shortUrl": "https://d15xsrghoj5xvi.cloudfront.net/live_short/7431657710921255722.mp4?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEDIaDmFwLXNvdXRoZWFzdC0xIkcwRQIgaHt0FT%2FgmTS8vkNPMYywMa27bkZvx%2FB6seMmRNBQEioCIQDw4P5lDMyXKQQflaLzwoJ3HtmNVfbXEe3yJZS4DioB%2FSrUBQir%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAEaDDEzNjM3Njc4NDc4OCIMTrswYh99exxy3sXNKqgFfdM%2Bx28OUTnbk75p%2BM3lGFAK4Riwq0ISrveq5wXakZ17eWk1gioAyccwu34dtgWk15OUWDM85i7zeKgcS13VRilSfuMc6u66U%2FLgH525UzcS4d%2B6jtyCP9LblZVHgSsDcYZcuauQsnhm1sq49n%2BzvLlYDnapIQACc5aYhI4GngjGYGk%2BvXxORU5cqeJ3Jwl9Ccm%2FPI%2BoTrhRci%2BsELob8%2BZFRe%2FxqaEhqIzAq3w0XCPhBeFaBttjYPi6WC8%2FYQs%2Fx05koqi2VECn5tsdZVYeBzMFa9Wta5ZIbzShe%2BiOuDxCcT%2FCPfMqgW%2F928ymH3xYVlRFUcHDBp%2BYS5af%2FW4v15L%2FpU2hlRSFP219FPpEhZISxBgEkTGxG93sgycBCc6zI6H%2Bo4S159qnK48845NolmSR4prfyhgZ0%2BzP912Y6IjxDKj50N4nTLzRRJ5vBBsM8ubu9EKPANHnuIeVfLHZ2wp4ExuPXLAPyS%2BmgpgGRiIIZoX3C3S1m747s%2FmY4g1YyWO2s4pOR5PoFtMVCIBIcTGz17IJdyHBr51yWrbBt1CU5T2VoY7MkpDYcXSLRfyK1b%2FY0mpxMYg0oAVFbBMbJSHSTEAFT93pd8WOQZmptlqoFmhcFyPeBDWIPPxcRLQJJ%2Fa2v7CCrK72u3kMPzV1O%2FqcjVFo7XXOgVgFxB0Bvojh8Ch2KS%2BrMmZXqr%2FB%2BugHxdKdjKLIhstYtyqeUyGHsSuVnannXCzNDvr4Gwsa39gDh9JWPVPvOxHuOpetq3dgGinVqU4%2BIIneIrvI0stDR%2BBobcYUJtFDKEAY8c2S%2BwkXWmTo0rYw4genoBzn%2BijB1hOWJIwVy9HAZ5HZpqnwiTXzvJP2gXleMK3nJz5xjULcU5rq69a24Qhox0k8faBS1BwBzFQO4zEwtKGUuQY6sQG6qV%2FgdjXa0W73A5qMaTq6b97EBAEu6ljV1OW1StfGHrWCbvqf69EVkAUHV1afvadQh6gpyqahQjCF6W9foYe%2B%2FTeoWdpHA32StkM3%2FIE6Tp4EklIsmjLwpOgIpCRkNQPrwipwjiZN%2Bh5BQo1TJv2oxWsjgvOIU5X7uKHkOqEm4IcIxU2J2pPb4b6B63refiDbrYcer8Q4HO3rqC%2FZFDJq0lqLtVoRdXqxkWx1kUmB2j8%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20241101T200156Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=ASIAR7QFQS6KIKAUCIS3%2F20241101%2Fap-southeast-1%2Fs3%2Faws4_request&X-Amz-Signature=6b5fb97be9d541e67227b3f81d7a8866e5f130f5ca6280abb533ca88e95fb16e",
#       "handle": "ryan.maxwel22",
#       "unit_price": "$29.99",
#       "title": "Lets Go LIVE!",
#       "record_type": "SHORT",
#       "finish_time": "2024/10/31 00:55:30",
#       "is_purchase": false,
#       "duration": "9h 5m",
#       "screenshotUrl": "https://d15xsrghoj5xvi.cloudfront.net/live/7431657710921255722/screenshot.png?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEDIaDmFwLXNvdXRoZWFzdC0xIkcwRQIgaHt0FT%2FgmTS8vkNPMYywMa27bkZvx%2FB6seMmRNBQEioCIQDw4P5lDMyXKQQflaLzwoJ3HtmNVfbXEe3yJZS4DioB%2FSrUBQir%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAEaDDEzNjM3Njc4NDc4OCIMTrswYh99exxy3sXNKqgFfdM%2Bx28OUTnbk75p%2BM3lGFAK4Riwq0ISrveq5wXakZ17eWk1gioAyccwu34dtgWk15OUWDM85i7zeKgcS13VRilSfuMc6u66U%2FLgH525UzcS4d%2B6jtyCP9LblZVHgSsDcYZcuauQsnhm1sq49n%2BzvLlYDnapIQACc5aYhI4GngjGYGk%2BvXxORU5cqeJ3Jwl9Ccm%2FPI%2BoTrhRci%2BsELob8%2BZFRe%2FxqaEhqIzAq3w0XCPhBeFaBttjYPi6WC8%2FYQs%2Fx05koqi2VECn5tsdZVYeBzMFa9Wta5ZIbzShe%2BiOuDxCcT%2FCPfMqgW%2F928ymH3xYVlRFUcHDBp%2BYS5af%2FW4v15L%2FpU2hlRSFP219FPpEhZISxBgEkTGxG93sgycBCc6zI6H%2Bo4S159qnK48845NolmSR4prfyhgZ0%2BzP912Y6IjxDKj50N4nTLzRRJ5vBBsM8ubu9EKPANHnuIeVfLHZ2wp4ExuPXLAPyS%2BmgpgGRiIIZoX3C3S1m747s%2FmY4g1YyWO2s4pOR5PoFtMVCIBIcTGz17IJdyHBr51yWrbBt1CU5T2VoY7MkpDYcXSLRfyK1b%2FY0mpxMYg0oAVFbBMbJSHSTEAFT93pd8WOQZmptlqoFmhcFyPeBDWIPPxcRLQJJ%2Fa2v7CCrK72u3kMPzV1O%2FqcjVFo7XXOgVgFxB0Bvojh8Ch2KS%2BrMmZXqr%2FB%2BugHxdKdjKLIhstYtyqeUyGHsSuVnannXCzNDvr4Gwsa39gDh9JWPVPvOxHuOpetq3dgGinVqU4%2BIIneIrvI0stDR%2BBobcYUJtFDKEAY8c2S%2BwkXWmTo0rYw4genoBzn%2BijB1hOWJIwVy9HAZ5HZpqnwiTXzvJP2gXleMK3nJz5xjULcU5rq69a24Qhox0k8faBS1BwBzFQO4zEwtKGUuQY6sQG6qV%2FgdjXa0W73A5qMaTq6b97EBAEu6ljV1OW1StfGHrWCbvqf69EVkAUHV1afvadQh6gpyqahQjCF6W9foYe%2B%2FTeoWdpHA32StkM3%2FIE6Tp4EklIsmjLwpOgIpCRkNQPrwipwjiZN%2Bh5BQo1TJv2oxWsjgvOIU5X7uKHkOqEm4IcIxU2J2pPb4b6B63refiDbrYcer8Q4HO3rqC%2FZFDJq0lqLtVoRdXqxkWx1kUmB2j8%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20241101T200156Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=ASIAR7QFQS6KIKAUCIS3%2F20241101%2Fap-southeast-1%2Fs3%2Faws4_request&X-Amz-Signature=45b40d82ae9e13b401b3a642fa974daf15c566bc76a5809be0915ba3e471dcf9",
#       "sale": "1",
#       "revenue": "$29.99",
#       "id": "7431657710921255722",
#       "views": 11181
#     }
#   ],
#   "message": null,
#   "cached": null,
#   "code": null
# }


r = s.post(
    "https://www.kalodata.com/product/detail/live/count",
    headers={"content-length": "161"},
    json={
        "id": "1729388618695479397",
        "startDate": "2024-10-01",
        "endDate": "2024-10-30",
        "authority": True,
        "pageNo": 1,
        "pageSize": 10,
        "sort": [{"field": "revenue", "type": "DESC"}],
    },
)
# {
#   "success": true,
#   "data": 32,
#   "message": null,
#   "cached": null,
#   "code": null
# }
