import requests

s = requests.Session()

s.headers.update(
    {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-GB,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,en-US;q=0.6",
        "country": "US",
        "currency": "USD",
        "dnt": "1",
        "language": "en-US",
        "origin": "https://www.kalodata.com",
        "priority": "u=1, i",
        "referer": "https://www.kalodata.com/product/detail?id=1729388618695479397&language=en-US&currency=USD&region=US&dateRange=%5B%222024-10-01%22%2C%222024-10-30%22%5D&cateValue=%5B%5D",
        "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    }
)

r = s.post(
    "https://www.kalodata.com/user/queryProfile",
    headers={"content-length": "0"},
)
# {
#   "success": true,
#   "data": {
#     "username": "EMAIL:ohara_uhura@mepost.pw",
#     "firstName": "Ohara",
#     "lastName": "Uhura",
#     "phoneCountryCode": null,
#     "phoneNumber": null,
#     "tiktokUserId": null,
#     "identity": "None of the above",
#     "industry": [],
#     "language": "en-US",
#     "currency": "USD",
#     "innerUser": 0,
#     "subAccount": false,
#     "mainPhoneNumber": null,
#     "havePremium": false,
#     "haveStandard": false,
#     "requirementIds": null,
#     "requirement": null,
#     "referralCode": null,
#     "platform": null,
#     "agencyWhite": 0,
#     "closeNoticeStatus": 0,
#     "completed": true,
#     "passwordExist": false,
#     "businessOnTiktok": "No",
#     "companySize": "1-5",
#     "source": "Others",
#     "creatorHandle": null,
#     "phoneVerified": 0,
#     "tiktokVerified": 0,
#     "tiktokUserHandle": null,
#     "tags": [],
#     "email": "ohara_uhura@mepost.pw",
#     "emailVerified": 1,
#     "bizCountry": "russia",
#     "bizCountryGroup": "united states",
#     "defaultCountry": "US",
#     "secId": "b48eba5d3d104b1813b0af3e394a72d6",
#     "mainSecId": "b48eba5d3d104b1813b0af3e394a72d6",
#     "isCharmCountry": true,
#     "avatarUrl": null
#   },
#   "message": null,
#   "cached": null,
#   "code": null
# }


s.headers.update({"content-type": "application/json"})

r = s.post(
    "https://www.kalodata.com/api/firstDay0",
    headers={"content-length": "16"},
    json={"country": "US"},
)
# {
#   "success": true,
#   "data": "2023-07-21",
#   "message": null,
#   "cached": null,
#   "code": null
# }


r = s.get(
    "https://www.kalodata.com/api/allLastDay",
    headers={"origin": None},
)
# {
#   "success": true,
#   "data": [
#     {
#       "country": "TH",
#       "lastDay": "2024-10-31"
#     },
#     {
#       "country": "VN",
#       "lastDay": "2024-10-31"
#     },
#     {
#       "country": "PH",
#       "lastDay": "2024-10-31"
#     },
#     {
#       "country": "ID",
#       "lastDay": "2024-10-31"
#     },
#     {
#       "country": "GB",
#       "lastDay": "2024-10-31"
#     },
#     {
#       "country": "MY",
#       "lastDay": "2024-10-31"
#     },
#     {
#       "country": "US",
#       "lastDay": "2024-10-30"
#     }
#   ],
#   "message": null,
#   "cached": null,
#   "code": null
# }


r = s.post(
    "https://www.kalodata.com/api/configurations",
    headers={"content-length": "128"},
    json=[
        {"key": "global.language"},
        {"key": "global.currency"},
        {"key": "global.country"},
        {"key": "contact.qrcode"},
        {"key": "user.telephone"},
    ],
)
# {
#   "success": true,
#   "data": {
#     "user.telephone": [
#       {
#         "code": "86",
#         "phoneRule": "^1\\d{10}$",
#         "msg_language": "zh-CN",
#         "icon": "https://d149xzut2sq6e3.cloudfront.net/upload/f7c58d73.png",
#         "language": "zh-CN",
#         "id": 1,
#         "label": "China",
#         "telephoneCode": "86",
#         "value": "CN",
#         "order": 6
#       },
#       {
#         "code": "62",
#         "phoneRule": "^(8|08)\\d{8,12}$",
#         "msg_language": "id-ID",
#         "icon": "https://d149xzut2sq6e3.cloudfront.net/upload/64e4436f.png",
#         "language": "id",
#         "id": 6,
#         "label": "Indonesia",
#         "telephoneCode": "62",
#         "value": "ID",
#         "order": 2
#       },
#       {
#         "code": "66",
#         "phoneRule": "^(6|8|9|06|08|09)\\d{8}$",
#         "msg_language": "th-TH",
#         "icon": "https://d149xzut2sq6e3.cloudfront.net/upload/2b795cca.png",
#         "language": "th",
#         "id": 7,
#         "label": "Thailand",
#         "telephoneCode": "66",
#         "value": "TH",
#         "order": 5
#       },
#       {
#         "code": "60",
#         "phoneRule": "^(1|01)\\d{7,9}$",
#         "msg_language": "en-US",
#         "icon": "https://d149xzut2sq6e3.cloudfront.net/upload/63a2a1f6.png",
#         "language": "ms",
#         "id": 8,
#         "label": "Malaysia",
#         "telephoneCode": "60",
#         "value": "MY",
#         "order": 8
#       },
#       {
#         "code": "84",
#         "phoneRule": "^(0?([35789]|1\\d))\\d{8}$",
#         "msg_language": "vi-VN",
#         "icon": "https://d149xzut2sq6e3.cloudfront.net/upload/3a7e0766.png",
#         "language": "vi",
#         "id": 9,
#         "label": "Vietnam",
#         "telephoneCode": "84",
#         "value": "VN",
#         "order": 4
#       },
#       {
#         "code": "63",
#         "phoneRule": "^(9|09)\\d{9}$",
#         "msg_language": "en-US",
#         "icon": "https://d149xzut2sq6e3.cloudfront.net/upload/980debe7.png",
#         "language": "en-US",
#         "id": 10,
#         "label": "Philippines",
#         "telephoneCode": "63",
#         "value": "PH",
#         "order": 7
#       },
#       {
#         "code": "1",
#         "phoneRule": "^\\d{10}$",
#         "msg_language": "en-US",
#         "icon": "https://d149xzut2sq6e3.cloudfront.net/upload/ff5174b4.png",
#         "language": "en-US",
#         "id": 12,
#         "label": "United States",
#         "telephoneCode": "1",
#         "value": "US",
#         "order": 1
#       },
#       {
#         "code": "44",
#         "phoneRule": "^(7|07)\\d{9,10}$",
#         "msg_language": "en-US",
#         "icon": "https://d149xzut2sq6e3.cloudfront.net/upload/125a71c5.png",
#         "language": "en-US",
#         "id": 13,
#         "label": "United Kingdom",
#         "telephoneCode": "44",
#         "value": "GB",
#         "order": 3
#       }
#     ],
#     "global.language": [
#       {
#         "id": 1,
#         "label": "\u4e2d\u6587(\u7b80\u4f53)",
#         "value": "zh-CN"
#       },
#       {
#         "id": 2,
#         "label": "English (US)",
#         "value": "en-US"
#       },
#       {
#         "id": 3,
#         "label": "Bahasa Indonesia",
#         "value": "id-ID"
#       },
#       {
#         "id": 4,
#         "label": "\u0e44\u0e17\u0e22",
#         "value": "th-TH"
#       },
#       {
#         "id": 5,
#         "label": "Ti\u1ebfng Vi\u1ec7t",
#         "value": "vi-VN"
#       }
#     ],
#     "global.currency": [
#       {
#         "symbol": "\u00a5",
#         "id": 1,
#         "label": "CNY(\u00a5)",
#         "value": "CNY"
#       },
#       {
#         "symbol": "$",
#         "id": 2,
#         "label": "USD($)",
#         "value": "USD"
#       },
#       {
#         "symbol": "Rp",
#         "id": 3,
#         "label": "IDR(Rp)",
#         "value": "IDR"
#       },
#       {
#         "symbol": "RM",
#         "id": 4,
#         "label": "MYR(RM)",
#         "value": "MYR"
#       },
#       {
#         "symbol": "\u0e3f",
#         "id": 5,
#         "label": "THB(\u0e3f)",
#         "value": "THB"
#       },
#       {
#         "symbol": "\u20ab",
#         "id": 6,
#         "label": "VND(\u20ab)",
#         "value": "VND"
#       },
#       {
#         "symbol": "\u20b1",
#         "id": 7,
#         "label": "PHP(\u20b1)",
#         "value": "PHP"
#       },
#       {
#         "symbol": "\u00a3",
#         "id": 8,
#         "label": "GBP(\u00a3)",
#         "value": "GBP"
#       }
#     ],
#     "contact.qrcode": [
#       {
#         "country": "Indonesia",
#         "imageURL": "https://d149xzut2sq6e3.cloudfront.net/upload/017363a0.png",
#         "name": "WhatsApp",
#         "link": "https://chat.whatsapp.com/IRZgeyFfE7MArh66Nk5A4q",
#         "phoneCode": "62",
#         "language": "id-ID",
#         "id": 1,
#         "type": "Group Chat",
#         "order": 2
#       },
#       {
#         "country": "Thailand",
#         "imageURL": "https://d149xzut2sq6e3.cloudfront.net/upload/d02dac20.png",
#         "name": "Line Group",
#         "link": "https://lin.ee/JBT52Ym ",
#         "phoneCode": "66",
#         "language": "th-TH",
#         "id": 2,
#         "type": "Group Chat",
#         "order": 3
#       },
#       {
#         "country": "Indonesia",
#         "imageURL": "https://d4ewq8axz3ayo.cloudfront.net/global/qrcodes/Tiktok-Indonesia.png",
#         "name": null,
#         "link": null,
#         "phoneCode": "62",
#         "language": "id-ID",
#         "id": 4,
#         "type": "TikTok",
#         "order": 1
#       },
#       {
#         "country": "Thailand",
#         "imageURL": "https://d4ewq8axz3ayo.cloudfront.net/global/qrcodes/Tiktok-Thailand.png",
#         "name": null,
#         "link": null,
#         "phoneCode": "66",
#         "language": "th-TH",
#         "id": 5,
#         "type": "TikTok",
#         "order": 2
#       },
#       {
#         "country": "Vietnam",
#         "imageURL": "https://d149xzut2sq6e3.cloudfront.net/upload/c7ef5e7b.jpeg",
#         "name": null,
#         "link": "https://www.tiktok.com/@kalodata_vietnam",
#         "phoneCode": "84",
#         "language": "vi-VN",
#         "id": 6,
#         "type": "TikTok",
#         "order": 3
#       },
#       {
#         "country": "China",
#         "imageURL": "https://d149xzut2sq6e3.cloudfront.net/upload/33a2a482.jpeg",
#         "name": "WeChat",
#         "link": "https://work.weixin.qq.com/ca/cawcde8bee79df7fc7",
#         "phoneCode": "86",
#         "language": "zh-CN",
#         "id": 7,
#         "type": "Group Chat",
#         "order": 5
#       },
#       {
#         "country": "Malaysia",
#         "imageURL": "https://d149xzut2sq6e3.cloudfront.net/upload/a754f3f4.jpg",
#         "name": "WhatsApp",
#         "link": "https://wa.me/message/SKJRQVZVFEJ4C1?src=qr",
#         "phoneCode": "60",
#         "language": "en-US",
#         "id": 8,
#         "type": "Group Chat",
#         "order": 1
#       },
#       {
#         "country": "Philippines",
#         "imageURL": "https://d149xzut2sq6e3.cloudfront.net/upload/b440ca90.jpg",
#         "name": "Telegram",
#         "link": "https://t.me/kalodataph",
#         "phoneCode": "63",
#         "language": "en-US",
#         "id": 9,
#         "type": "Group Chat",
#         "order": 6
#       },
#       {
#         "country": "Vietnam",
#         "imageURL": "https://d149xzut2sq6e3.cloudfront.net/upload/ef96ca95.jpeg",
#         "name": "Zalo Group",
#         "link": "https://zalo.me/g/oqpdob428",
#         "phoneCode": "84",
#         "language": "vi-VN",
#         "id": 10,
#         "type": "Group Chat",
#         "order": 4
#       },
#       {
#         "country": "Indonesia",
#         "imageURL": "https://d149xzut2sq6e3.cloudfront.net/upload/017363a0.png",
#         "name": "WhatsApp",
#         "link": "https://chat.whatsapp.com/IRZgeyFfE7MArh66Nk5A4q",
#         "phoneCode": "62",
#         "language": "id-ID",
#         "id": 11,
#         "type": "Group Chat",
#         "order": 2
#       },
#       {
#         "country": "United States",
#         "imageURL": "https://d149xzut2sq6e3.cloudfront.net/upload/1c56586b.jpeg",
#         "name": "Discord",
#         "link": "https://discord.gg/bbFFS86BCA",
#         "phoneCode": "1",
#         "language": "en-US",
#         "id": 12,
#         "type": "Group Chat",
#         "order": null
#       }
#     ],
#     "global.country": [
#       {
#         "name": "Indonesia",
#         "icon": "https://d149xzut2sq6e3.cloudfront.net/upload/a4039600.png",
#         "id": 1,
#         "label": "Indonesia",
#         "value": "ID",
#         "order": 2
#       },
#       {
#         "name": "Malaysia",
#         "icon": "https://d149xzut2sq6e3.cloudfront.net/upload/824dea09.png",
#         "id": 2,
#         "label": "Malaysia",
#         "value": "MY",
#         "order": 3
#       },
#       {
#         "name": "Thailand",
#         "icon": "https://d149xzut2sq6e3.cloudfront.net/upload/ccf1ad16.jpeg",
#         "id": 3,
#         "label": "Thailand",
#         "value": "TH",
#         "order": 4
#       },
#       {
#         "name": "Vietnam",
#         "icon": "https://d149xzut2sq6e3.cloudfront.net/upload/a7a48f24.png",
#         "id": 7,
#         "label": "Vietnam",
#         "value": "VN",
#         "order": 5
#       },
#       {
#         "name": "Philippines",
#         "icon": "https://d149xzut2sq6e3.cloudfront.net/upload/3ff3dab0.png",
#         "id": 8,
#         "label": "Philippines",
#         "value": "PH",
#         "order": 6
#       },
#       {
#         "name": "United States",
#         "icon": "https://d149xzut2sq6e3.cloudfront.net/upload/4d0a8f83.png",
#         "id": 9,
#         "label": "United States",
#         "value": "US",
#         "order": 1
#       },
#       {
#         "name": "United Kingdom",
#         "icon": "https://d149xzut2sq6e3.cloudfront.net/upload/98e7ee9e.png",
#         "id": 12,
#         "label": "United Kingdom",
#         "value": "GB",
#         "order": 9
#       }
#     ]
#   },
#   "message": null,
#   "cached": true,
#   "code": null
# }


r = s.post(
    "https://www.kalodata.com/api/configurations",
    headers={"content-length": "32"},
    json=[{"key": "global.category.tree"}],
)
# {
#   "success": true,
#   "data": {
#     "global.category.tree": [
#       {
#         "children": [
#           {
#             "children": [
#               {
#                 "label": "Blouses & Shirts",
#                 "value": "601265"
#               },
#               {
#                 "label": "T-shirts",
#                 "value": "601302"
#               },
#               {
#                 "label": "Hoodies & Jumpers",
#                 "value": "601295"
#               },
#               {
#                 "label": "Vest, Tank & Tube Tops",
#                 "value": "843400"
#               },
#               {
#                 "label": "Bodysuits",
#                 "value": "843528"
#               },
#               {
#                 "label": "Women's Vests",
#                 "value": "601282"
#               },
#               {
#                 "label": "Knitwear",
#                 "value": "601284"
#               },
#               {
#                 "label": "Jackets & Coats",
#                 "value": "601267"
#               }
#             ],
#             "label": "Women's Tops",
#             "value": "842248"
#           },
#           {
#             "children": [
#               {
#                 "label": "Skirts",
#                 "value": "601264"
#               },
#               {
#                 "label": "Shorts",
#                 "value": "601266"
#               },
#               {
#                 "label": "Trousers",
#                 "value": "601277"
#               },
#               {
#                 "label": "Jeans",
#                 "value": "601276"
#               },
#               {
#                 "label": "Leggings",
#                 "value": "601274"
#               }
#             ],
#             "label": "Women's Bottoms",
#             "value": "842376"
#           },
#           {
#             "children": [
#               {
#                 "label": "Casual Dresses",
#                 "value": "601281"
#               },
#               {
#                 "label": "Formal Dresses",
#                 "value": "601271"
#               },
#               {
#                 "label": "Wedding Dresses",
#                 "value": "601270"
#               }
#             ],
#             "label": "Women's Dresses",
#             "value": "842504"
#           },
#           {
#             "children": [
#               {
#                 "label": "Costumes & Accessories",
#                 "value": "843656"
#               },
#               {
#                 "label": "Workwear & Uniforms",
#                 "value": "843784"
#               },
#               {
#                 "label": "Traditional Dress",
#                 "value": "843912"
#               }
#             ],
#             "label": "Women's Special Clothing",
#             "value": "842632"
#           },
#           {
#             "children": [
#               {
#                 "label": "Sets",
#                 "value": "601291"
#               },
#               {
#                 "label": "Suits",
#                 "value": "601296"
#               },
#               {
#                 "label": "Couples' Clothing Sets",
#                 "value": "844040"
#               },
#               {
#                 "label": "Family Clothing Sets",
#                 "value": "844296"
#               },
#               {
#                 "label": "Overalls",
#                 "value": "601280"
#               }
#             ],
#             "label": "Women's Suits & Overalls",
#             "value": "842760"
#           },
#           {
#             "children": [
#               {
#                 "label": "Bras",
#                 "value": "601262"
#               },
#               {
#                 "label": "Knickers",
#                 "value": "601247"
#               },
#               {
#                 "label": "Tights",
#                 "value": "844552"
#               },
#               {
#                 "label": "Thermal Underwear",
#                 "value": "844680"
#               },
#               {
#                 "label": "Bra Accessories",
#                 "value": "844936"
#               },
#               {
#                 "label": "Shapewear",
#                 "value": "601259"
#               },
#               {
#                 "label": "Lingerie",
#                 "value": "845192"
#               },
#               {
#                 "label": "Socks",
#                 "value": "845448"
#               },
#               {
#                 "label": "Bralettes",
#                 "value": "845576"
#               },
#               {
#                 "label": "Underwear Sets",
#                 "value": "845704"
#               }
#             ],
#             "label": "Women's Underwear",
#             "value": "842888"
#           },
#           {
#             "children": [
#               {
#                 "label": "Pyjamas",
#                 "value": "845832"
#               },
#               {
#                 "label": "Bathrobes & Dressing Gowns",
#                 "value": "845960"
#               },
#               {
#                 "label": "Nightdresses",
#                 "value": "846088"
#               }
#             ],
#             "label": "Women's Sleepwear",
#             "value": "843016"
#           },
#           {
#             "children": [
#               {
#                 "label": "Batik",
#                 "value": "846216"
#               },
#               {
#                 "label": "Lace",
#                 "value": "846344"
#               },
#               {
#                 "label": "Cotton",
#                 "value": "846472"
#               },
#               {
#                 "label": "Wool",
#                 "value": "846600"
#               },
#               {
#                 "label": "Velvet, Silk & Satin",
#                 "value": "846728"
#               },
#               {
#                 "label": "Leather",
#                 "value": "846856"
#               },
#               {
#                 "label": "Polyester",
#                 "value": "846984"
#               },
#               {
#                 "label": "Denim",
#                 "value": "847112"
#               },
#               {
#                 "label": "Canvas",
#                 "value": "847240"
#               },
#               {
#                 "label": "Kain Pasang",
#                 "value": "847368"
#               },
#               {
#                 "label": "Songket",
#                 "value": "847496"
#               }
#             ],
#             "label": "Dressmaking Fabrics",
#             "value": "843144"
#           }
#         ],
#         "label": "Womenswear & Underwear",
#         "value": "601152"
#       },
#       {
#         "children": [
#           {
#             "children": [
#               {
#                 "label": "Shirts",
#                 "value": "601195"
#               },
#               {
#                 "label": "T-shirts",
#                 "value": "601226"
#               },
#               {
#                 "label": "Hoodies & Jumpers",
#                 "value": "601213"
#               },
#               {
#                 "label": "Waistcoats & Gilets",
#                 "value": "601194"
#               },
#               {
#                 "label": "Knitwear",
#                 "value": "601223"
#               },
#               {
#                 "label": "Jackets & Coats",
#                 "value": "601197"
#               }
#             ],
#             "label": "Men's Tops",
#             "value": "839944"
#           },
#           {
#             "children": [
#               {
#                 "label": "Shorts",
#                 "value": "601196"
#               },
#               {
#                 "label": "Trousers",
#                 "value": "601218"
#               },
#               {
#                 "label": "Jeans",
#                 "value": "601202"
#               }
#             ],
#             "label": "Men's Bottoms",
#             "value": "840072"
#           },
#           {
#             "children": [
#               {
#                 "label": "Sets",
#                 "value": "601210"
#               },
#               {
#                 "label": "Suits",
#                 "value": "601216"
#               },
#               {
#                 "label": "Overalls",
#                 "value": "840840"
#               }
#             ],
#             "label": "Men's Suits & Overalls",
#             "value": "840712"
#           },
#           {
#             "children": [
#               {
#                 "label": "Costumes & Accessories",
#                 "value": "840968"
#               },
#               {
#                 "label": "Workwear & Uniforms",
#                 "value": "841096"
#               },
#               {
#                 "label": "Traditional Dress",
#                 "value": "841224"
#               }
#             ],
#             "label": "Men's Special Clothing",
#             "value": "840328"
#           },
#           {
#             "children": [
#               {
#                 "label": "Underwear",
#                 "value": "841352"
#               },
#               {
#                 "label": "Vests",
#                 "value": "841480"
#               },
#               {
#                 "label": "Thermal Underwear",
#                 "value": "841608"
#               },
#               {
#                 "label": "Socks",
#                 "value": "841736"
#               }
#             ],
#             "label": "Men's Underwear",
#             "value": "840456"
#           },
#           {
#             "children": [
#               {
#                 "label": "Pyjamas",
#                 "value": "841864"
#               },
#               {
#                 "label": "Bathrobes & Dressing Gowns",
#                 "value": "841992"
#               },
#               {
#                 "label": "Nightshirts",
#                 "value": "842120"
#               }
#             ],
#             "label": "Men's Sleepwear",
#             "value": "840584"
#           }
#         ],
#         "label": "Menswear & Underwear",
#         "value": "824328"
#       },
#       {
#         "children": [
#           {
#             "children": [
#               {
#                 "label": "Costumes & Accessories",
#                 "value": "802440"
#               },
#               {
#                 "label": "Underwear",
#                 "value": "802568"
#               },
#               {
#                 "label": "Nightwear",
#                 "value": "802696"
#               },
#               {
#                 "label": "Swimwear",
#                 "value": "802824"
#               },
#               {
#                 "label": "Tops",
#                 "value": "802952"
#               },
#               {
#                 "label": "Coats & Jackets",
#                 "value": "803080"
#               },
#               {
#                 "label": "Bottoms",
#                 "value": "803208"
#               },
#               {
#                 "label": "Suits & Sets",
#                 "value": "803336"
#               },
#               {
#                 "label": "Socks",
#                 "value": "803464"
#               }
#             ],
#             "label": "Boys' Clothes",
#             "value": "802312"
#           },
#           {
#             "children": [
#               {
#                 "label": "Costumes & Accessories",
#                 "value": "803720"
#               },
#               {
#                 "label": "Underwear",
#                 "value": "803848"
#               },
#               {
#                 "label": "Nightwear",
#                 "value": "803976"
#               },
#               {
#                 "label": "Kids' Swimwear",
#                 "value": "804104"
#               },
#               {
#                 "label": "Tops",
#                 "value": "804232"
#               },
#               {
#                 "label": "Coats & Jackets",
#                 "value": "804360"
#               },
#               {
#                 "label": "Bottoms",
#                 "value": "804488"
#               },
#               {
#                 "label": "Suits & Sets",
#                 "value": "804616"
#               },
#               {
#                 "label": "Dresses",
#                 "value": "804744"
#               },
#               {
#                 "label": "Skirts",
#                 "value": "804872"
#               },
#               {
#                 "label": "Socks",
#                 "value": "805000"
#               }
#             ],
#             "label": "Girls' Clothes",
#             "value": "803592"
#           },
#           {
#             "children": [
#               {
#                 "label": "Sandals & Flip Flops",
#                 "value": "805384"
#               },
#               {
#                 "label": "Trainers",
#                 "value": "805512"
#               },
#               {
#                 "label": "Slippers",
#                 "value": "805640"
#               },
#               {
#                 "label": "Formal Shoes",
#                 "value": "805768"
#               },
#               {
#                 "label": "Flat Shoes",
#                 "value": "805896"
#               },
#               {
#                 "label": "Boots",
#                 "value": "805256"
#               }
#             ],
#             "label": "Boys' Footwear",
#             "value": "805128"
#           },
#           {
#             "children": [
#               {
#                 "label": "Boots",
#                 "value": "806152"
#               },
#               {
#                 "label": "Sandals & Flip Flops",
#                 "value": "806280"
#               },
#               {
#                 "label": "Trainers",
#                 "value": "806408"
#               },
#               {
#                 "label": "Slippers",
#                 "value": "806536"
#               },
#               {
#                 "label": "Flat Shoes",
#                 "value": "806664"
#               }
#             ],
#             "label": "Girls' Footwear",
#             "value": "806024"
#           },
#           {
#             "children": [
#               {
#                 "label": "Bags & Luggage",
#                 "value": "806920"
#               },
#               {
#                 "label": "Kids' Hats",
#                 "value": "807048"
#               },
#               {
#                 "label": "Eyewear",
#                 "value": "807176"
#               },
#               {
#                 "label": "Hair Accessories",
#                 "value": "807304"
#               },
#               {
#                 "label": "Gloves",
#                 "value": "807432"
#               },
#               {
#                 "label": "Belts",
#                 "value": "807560"
#               },
#               {
#                 "label": "Kids' Scarves & Shawls",
#                 "value": "807688"
#               },
#               {
#                 "label": "Watches",
#                 "value": "807816"
#               },
#               {
#                 "label": "Kids Costume Jewelry & Accessories",
#                 "value": "807944"
#               },
#               {
#                 "label": "Earmuffs",
#                 "value": "808072"
#               }
#             ],
#             "label": "Kids' Fashion Accessories",
#             "value": "806792"
#           }
#         ],
#         "label": "Kids' Fashion",
#         "value": "802184"
#       },
#       {
#         "children": [
#           {
#             "children": [
#               {
#                 "label": "Boots",
#                 "value": "601409"
#               },
#               {
#                 "label": "Casual Trainers",
#                 "value": "900872"
#               },
#               {
#                 "label": "Flats",
#                 "value": "901000"
#               },
#               {
#                 "label": " Heels",
#                 "value": "601396"
#               },
#               {
#                 "label": "Sandals & Flip Flops",
#                 "value": "901128"
#               },
#               {
#                 "label": "Slip-Ons",
#                 "value": "901256"
#               },
#               {
#                 "label": "Mules & Clogs",
#                 "value": "901384"
#               },
#               {
#                 "label": " Oxfords",
#                 "value": "601387"
#               },
#               {
#                 "label": " Slippers",
#                 "value": "601405"
#               }
#             ],
#             "label": "Women Shoes",
#             "value": "601381"
#           },
#           {
#             "children": [
#               {
#                 "label": " Boots",
#                 "value": "601376"
#               },
#               {
#                 "label": "Casual Trainers",
#                 "value": "601357"
#               },
#               {
#                 "label": "Flat Shoes",
#                 "value": "901512"
#               },
#               {
#                 "label": " Sandals & Flip Flops",
#                 "value": "601364"
#               },
#               {
#                 "label": "Slippers",
#                 "value": "601374"
#               },
#               {
#                 "label": "Formal Shoes",
#                 "value": "901640"
#               },
#               {
#                 "label": "Slip-Ons & Flat Shoes",
#                 "value": "901768"
#               },
#               {
#                 "label": "Oxfords",
#                 "value": "601369"
#               },
#               {
#                 "label": "Mules & Clogs",
#                 "value": "901896"
#               }
#             ],
#             "label": "Men Shoes",
#             "value": "601353"
#           },
#           {
#             "children": [
#               {
#                 "label": " Insoles & Heel Liners",
#                 "value": "601366"
#               },
#               {
#                 "label": "Shoe Horns & Trees",
#                 "value": "902024"
#               },
#               {
#                 "label": "Shoelaces",
#                 "value": "902152"
#               },
#               {
#                 "label": "Cleaning & Care",
#                 "value": "902280"
#               }
#             ],
#             "label": "Shoe Accessories",
#             "value": "900744"
#           }
#         ],
#         "label": "Shoes",
#         "value": "601352"
#       },
#       {
#         "children": [
#           {
#             "children": [
#               {
#                 "label": " Clutches & Wristlets ",
#                 "value": "601444"
#               },
#               {
#                 "label": "Bum Bags & Belt Bags",
#                 "value": "903048"
#               },
#               {
#                 "label": "Tote Bags",
#                 "value": "903176"
#               },
#               {
#                 "label": "Handbags",
#                 "value": "601445"
#               },
#               {
#                 "label": " Crossbody & Shoulder Bags",
#                 "value": "601439"
#               },
#               {
#                 "label": "Wallets",
#                 "value": "601441"
#               },
#               {
#                 "label": "Backpacks",
#                 "value": "601446"
#               }
#             ],
#             "label": "Women's Bags",
#             "value": "902408"
#           },
#           {
#             "children": [
#               {
#                 "label": "Tote Bags",
#                 "value": "903304"
#               },
#               {
#                 "label": "Briefcases",
#                 "value": "903432"
#               },
#               {
#                 "label": " Clutches",
#                 "value": "601431"
#               },
#               {
#                 "label": "Bum Bags & Belt Bags",
#                 "value": "903560"
#               },
#               {
#                 "label": " Crossbody & Shoulder Bags",
#                 "value": "601429"
#               },
#               {
#                 "label": " Wallets",
#                 "value": "601430"
#               },
#               {
#                 "label": "Backpacks",
#                 "value": "601432"
#               }
#             ],
#             "label": "Men's Bags",
#             "value": "902536"
#           },
#           {
#             "children": [
#               {
#                 "label": "Luggage",
#                 "value": "903688"
#               },
#               {
#                 "label": "Travel Bags",
#                 "value": "601419"
#               },
#               {
#                 "label": "Travel Organizers",
#                 "value": "903816"
#               },
#               {
#                 "label": "Passport Holders & Covers",
#                 "value": "903944"
#               },
#               {
#                 "label": " Luggage Accessories",
#                 "value": "601449"
#               }
#             ],
#             "label": "Luggage & Travel Bags",
#             "value": "902664"
#           },
#           {
#             "children": [
#               {
#                 "label": " Laptop Bags",
#                 "value": "601417"
#               },
#               {
#                 "label": "Instrument Bags & Cases",
#                 "value": "904072"
#               },
#               {
#                 "label": "Make-up Bags",
#                 "value": "601440"
#               },
#               {
#                 "label": "Lunch Bags",
#                 "value": "904200"
#               },
#               {
#                 "label": "Cooler Bags",
#                 "value": "904328"
#               },
#               {
#                 "label": "Shopping Bags",
#                 "value": "904456"
#               }
#             ],
#             "label": "Functional Bags",
#             "value": "902792"
#           },
#           {
#             "children": [
#               {
#                 "label": "Bag Straps & Chains",
#                 "value": "904584"
#               },
#               {
#                 "label": "Bag Hangers",
#                 "value": "904712"
#               },
#               {
#                 "label": "Charms & Twillies",
#                 "value": "904840"
#               },
#               {
#                 "label": "Bag Organizers",
#                 "value": "904968"
#               },
#               {
#                 "label": "Cleaning & Care",
#                 "value": "905096"
#               }
#             ],
#             "label": "Bag Accessories",
#             "value": "902920"
#           }
#         ],
#         "label": "Luggage & Bags",
#         "value": "824584"
#       },
#       {
#         "children": [
#           {
#             "children": [
#               {
#                 "label": "Scarves & Shawls",
#                 "value": "905992"
#               },
#               {
#                 "label": "Gloves",
#                 "value": "906120"
#               },
#               {
#                 "label": "Hats",
#                 "value": "906248"
#               },
#               {
#                 "label": "Belts",
#                 "value": "906376"
#               },
#               {
#                 "label": "Ties & Bowties",
#                 "value": "906504"
#               },
#               {
#                 "label": "Handkerchiefs",
#                 "value": "906632"
#               },
#               {
#                 "label": "Cufflinks",
#                 "value": "906888"
#               },
#               {
#                 "label": "Collar Clips & Brooches",
#                 "value": "605281"
#               },
#               {
#                 "label": "Face Covering Masks & Accessories",
#                 "value": "906760"
#               },
#               {
#                 "label": "Fashion Accessory Sets",
#                 "value": "605289"
#               }
#             ],
#             "label": "Clothes Accessories",
#             "value": "905224"
#           },
#           {
#             "children": [
#               {
#                 "label": "Sunglasses",
#                 "value": "605304"
#               },
#               {
#                 "label": " Frames & Glasses",
#                 "value": "605302"
#               },
#               {
#                 "label": "Glasses Cases & Accessories",
#                 "value": "907016"
#               }
#             ],
#             "label": "Eyewear",
#             "value": "905352"
#           },
#           {
#             "children": [
#               {
#                 "label": "Men's Watches",
#                 "value": "605251"
#               },
#               {
#                 "label": "Women's Watches",
#                 "value": "605254"
#               },
#               {
#                 "label": "Unisex Watches",
#                 "value": "907144"
#               },
#               {
#                 "label": " Couple Watches",
#                 "value": "605257"
#               },
#               {
#                 "label": " Watch Accessories",
#                 "value": "700795"
#               }
#             ],
#             "label": "Watches & Accessories",
#             "value": "905480"
#           },
#           {
#             "children": [
#               {
#                 "label": "Rings",
#                 "value": "605273"
#               },
#               {
#                 "label": "Earrings",
#                 "value": "605268"
#               },
#               {
#                 "label": " Bracelets & Bangles",
#                 "value": "605274"
#               },
#               {
#                 "label": "Anklets",
#                 "value": "605272"
#               },
#               {
#                 "label": "Necklaces",
#                 "value": "605280"
#               },
#               {
#                 "label": "Charms & Pendants",
#                 "value": "907400"
#               },
#               {
#                 "label": "Body Jewellery",
#                 "value": "907528"
#               },
#               {
#                 "label": "Key Chains",
#                 "value": "907656"
#               },
#               {
#                 "label": "Jewellery Sets",
#                 "value": "907784"
#               }
#             ],
#             "label": "Costume Jewellery & Accessories",
#             "value": "905608"
#           },
#           {
#             "children": [
#               {
#                 "label": "Platinum & Carat Gold",
#                 "value": "907912"
#               },
#               {
#                 "label": "Silver",
#                 "value": "908040"
#               },
#               {
#                 "label": "Diamond",
#                 "value": "908168"
#               },
#               {
#                 "label": "Jade",
#                 "value": "908296"
#               },
#               {
#                 "label": "Crystals & Gem Stones",
#                 "value": "939656"
#               }
#             ],
#             "label": "Precious Metal & Gemstones",
#             "value": "905736"
#           },
#           {
#             "children": [
#               {
#                 "label": " Headbands",
#                 "value": "605271"
#               },
#               {
#                 "label": "Hair Bands & Scrunchies",
#                 "value": "908424"
#               },
#               {
#                 "label": "Hair Clips & Hair Pins",
#                 "value": "908552"
#               },
#               {
#                 "label": "Human Hair Silk Base Lace Wigs",
#                 "value": "908680"
#               },
#               {
#                 "label": "Synthetic Costume Wigs",
#                 "value": "908808"
#               },
#               {
#                 "label": "Headpieces & Crowns",
#                 "value": "908936"
#               }
#             ],
#             "label": "Hair Accessories",
#             "value": "905864"
#           }
#         ],
#         "label": "Fashion Accessories",
#         "value": "605248"
#       },
#       {
#         "children": [
#           {
#             "children": [
#               {
#                 "label": "Tracksuits",
#                 "value": "603705"
#               },
#               {
#                 "label": "Sports Outerwear",
#                 "value": "603706"
#               },
#               {
#                 "label": "Sports T-shirts",
#                 "value": "835720"
#               },
#               {
#                 "label": "Sports Vests",
#                 "value": "835848"
#               },
#               {
#                 "label": "Jerseys",
#                 "value": "603042"
#               },
#               {
#                 "label": "Joggers",
#                 "value": "603704"
#               },
#               {
#                 "label": "Sports Shorts",
#                 "value": "835976"
#               },
#               {
#                 "label": "Sports Leggings",
#                 "value": "836104"
#               },
#               {
#                 "label": "Swimwear",
#                 "value": "700751"
#               },
#               {
#                 "label": "Sports Bras",
#                 "value": "603729"
#               },
#               {
#                 "label": "Kids' Sports Clothing",
#                 "value": "836232"
#               }
#             ],
#             "label": "Sport & Outdoor Clothing",
#             "value": "834568"
#           },
#           {
#             "children": [
#               {
#                 "label": "Basketball Shoes",
#                 "value": "603748"
#               },
#               {
#                 "label": "Running Shoes",
#                 "value": "603751"
#               },
#               {
#                 "label": "Training & Gym Shoes",
#                 "value": "836360"
#               },
#               {
#                 "label": "Tennis Shoes",
#                 "value": "603755"
#               },
#               {
#                 "label": "Volleyball Shoes",
#                 "value": "603750"
#               },
#               {
#                 "label": "Badminton Shoes",
#                 "value": "603758"
#               },
#               {
#                 "label": "Hiking Shoes",
#                 "value": "603856"
#               },
#               {
#                 "label": "Baseball Shoes",
#                 "value": "603744"
#               },
#               {
#                 "label": "Football Boots",
#                 "value": "603760"
#               },
#               {
#                 "label": "Dance Shoes",
#                 "value": "603171"
#               },
#               {
#                 "label": "Roller & Ice Skates",
#                 "value": "836488"
#               },
#               {
#                 "label": "Golf Shoes",
#                 "value": "603579"
#               },
#               {
#                 "label": "Kids' Sport Shoes",
#                 "value": "836616"
#               },
#               {
#                 "label": "Other Sports Shoes",
#                 "value": "603753"
#               }
#             ],
#             "label": "Sports Footwear",
#             "value": "834696"
#           },
#           {
#             "children": [
#               {
#                 "label": "Sports Eyewear",
#                 "value": "836744"
#               },
#               {
#                 "label": "Protective Gear",
#                 "value": "603872"
#               },
#               {
#                 "label": "Sports Socks",
#                 "value": "836872"
#               },
#               {
#                 "label": "Sports & Outdoor Hats",
#                 "value": "603654"
#               },
#               {
#                 "label": "Sports Bags",
#                 "value": "603682"
#               },
#               {
#                 "label": "Stopwatches & Timers",
#                 "value": "837000"
#               },
#               {
#                 "label": "Pedometers",
#                 "value": "603366"
#               },
#               {
#                 "label": "Sports Water Bottles",
#                 "value": "940168"
#               }
#             ],
#             "label": "Sports & Outdoor Accessories",
#             "value": "834824"
#           },
#           {
#             "children": [
#               {
#                 "label": "Football",
#                 "value": "603041"
#               },
#               {
#                 "label": "Basketball",
#                 "value": "603524"
#               },
#               {
#                 "label": "Volleyball",
#                 "value": "603437"
#               },
#               {
#                 "label": "Badminton",
#                 "value": "603065"
#               },
#               {
#                 "label": "Tennis",
#                 "value": "603221"
#               },
#               {
#                 "label": "Table Tennis",
#                 "value": "603396"
#               },
#               {
#                 "label": "Golf ",
#                 "value": "603573"
#               },
#               {
#                 "label": "Baseballs",
#                 "value": "603652"
#               },
#               {
#                 "label": "Squash",
#                 "value": "603641"
#               },
#               {
#                 "label": "Bowling",
#                 "value": "603646"
#               },
#               {
#                 "label": "Rugby",
#                 "value": "837128"
#               },
#               {
#                 "label": "Billiards & Snooker",
#                 "value": "603331"
#               },
#               {
#                 "label": "American Football",
#                 "value": "936328"
#               },
#               {
#                 "label": "Cricket",
#                 "value": "936584"
#               }
#             ],
#             "label": "Ball Sports Equipment",
#             "value": "834952"
#           },
#           {
#             "children": [
#               {
#                 "label": "Surfing",
#                 "value": "603131"
#               },
#               {
#                 "label": "Swimming",
#                 "value": "837256"
#               },
#               {
#                 "label": "Diving",
#                 "value": "700781"
#               },
#               {
#                 "label": "Boating",
#                 "value": "837384"
#               }
#             ],
#             "label": "Water Sports Equipment",
#             "value": "835080"
#           },
#           {
#             "children": [
#               {
#                 "label": "Skiing",
#                 "value": "700779"
#               },
#               {
#                 "label": "Snowboarding",
#                 "value": "837512"
#               },
#               {
#                 "label": "Ice Hockey",
#                 "value": "603625"
#               }
#             ],
#             "label": "Winter Sports Equipment",
#             "value": "835208"
#           },
#           {
#             "children": [
#               {
#                 "label": "Weight Training",
#                 "value": "837640"
#               },
#               {
#                 "label": "Skipping Ropes",
#                 "value": "603375"
#               },
#               {
#                 "label": "Hula Hoops",
#                 "value": "603353"
#               },
#               {
#                 "label": "Gym Balls",
#                 "value": "603358"
#               },
#               {
#                 "label": "Fitness Machines",
#                 "value": "837768"
#               },
#               {
#                 "label": "Ab Training",
#                 "value": "603355"
#               },
#               {
#                 "label": "Pull Up Bars",
#                 "value": "837896"
#               },
#               {
#                 "label": "Resistance Bands",
#                 "value": "939784"
#               },
#               {
#                 "label": "Roller Skating",
#                 "value": "939912"
#               },
#               {
#                 "label": "Scooters & Ride-ons",
#                 "value": "940040"
#               }
#             ],
#             "label": "Fitness Equipment",
#             "value": "835336"
#           },
#           {
#             "children": [
#               {
#                 "label": "Camping Kitchenware",
#                 "value": "603917"
#               },
#               {
#                 "label": "Camping Lighting",
#                 "value": "603970"
#               },
#               {
#                 "label": "Tents & Accessories",
#                 "value": "700782"
#               },
#               {
#                 "label": "Sleeping Bags & Bedding",
#                 "value": "604054"
#               },
#               {
#                 "label": "Binoculars & Telescopes",
#                 "value": "604065"
#               },
#               {
#                 "label": "Compasses",
#                 "value": "604059"
#               },
#               {
#                 "label": "Knives & Survival Kits",
#                 "value": "603835"
#               },
#               {
#                 "label": "Hammocks",
#                 "value": "603952"
#               },
#               {
#                 "label": "Hiking Sticks",
#                 "value": "838024"
#               },
#               {
#                 "label": "Picnic Mats & Baskets",
#                 "value": "838152"
#               },
#               {
#                 "label": "Camping Furniture",
#                 "value": "838280"
#               }
#             ],
#             "label": "Camping & Hiking Equipment",
#             "value": "835464"
#           },
#           {
#             "children": [
#               {
#                 "label": "Fishing",
#                 "value": "603818"
#               },
#               {
#                 "label": "Cycling",
#                 "value": "838408"
#               },
#               {
#                 "label": "Skateboarding",
#                 "value": "603493"
#               },
#               {
#                 "label": "Archery",
#                 "value": "603389"
#               },
#               {
#                 "label": "Boxing & Martial Arts",
#                 "value": "603288"
#               },
#               {
#                 "label": "Yoga & Pilates",
#                 "value": "603084"
#               },
#               {
#                 "label": "Darts",
#                 "value": "603605"
#               },
#               {
#                 "label": "Horse Riding",
#                 "value": "603477"
#               },
#               {
#                 "label": "Judo",
#                 "value": "603295"
#               },
#               {
#                 "label": "Taekwondo",
#                 "value": "603317"
#               },
#               {
#                 "label": "Wrestling",
#                 "value": "603301"
#               },
#               {
#                 "label": "Fencing",
#                 "value": "700741"
#               },
#               {
#                 "label": "Track & Field",
#                 "value": "603247"
#               },
#               {
#                 "label": "Nunchucks",
#                 "value": "603304"
#               },
#               {
#                 "label": "Indoor Recreation",
#                 "value": "700740"
#               }
#             ],
#             "label": "Leisure & Outdoor Recreation Equipment",
#             "value": "835592"
#           },
#           {
#             "children": [
#               {
#                 "label": "Premier League",
#                 "value": "936840"
#               },
#               {
#                 "label": "Basketball",
#                 "value": "936968"
#               },
#               {
#                 "label": "Cricket",
#                 "value": "937096"
#               },
#               {
#                 "label": "Golf",
#                 "value": "937224"
#               },
#               {
#                 "label": "Gaming",
#                 "value": "937352"
#               },
#               {
#                 "label": "Rugby",
#                 "value": "937480"
#               },
#               {
#                 "label": "Tennis",
#                 "value": "937608"
#               }
#             ],
#             "label": "Fan Shop",
#             "value": "936712"
#           },
#           {
#             "children": [
#               {
#                 "label": "Sports Trading Cards",
#                 "value": "937864"
#               },
#               {
#                 "label": "Jerseys",
#                 "value": "937992"
#               },
#               {
#                 "label": "Photographs",
#                 "value": "938120"
#               },
#               {
#                 "label": "Balls",
#                 "value": "938248"
#               },
#               {
#                 "label": "Trophies",
#                 "value": "938376"
#               },
#               {
#                 "label": "Figurines",
#                 "value": "938504"
#               },
#               {
#                 "label": "Gloves",
#                 "value": "938632"
#               },
#               {
#                 "label": "Hats",
#                 "value": "938760"
#               },
#               {
#                 "label": "Shoes",
#                 "value": "938888"
#               },
#               {
#                 "label": "Books",
#                 "value": "939016"
#               },
#               {
#                 "label": "Golf Clubs",
#                 "value": "939144"
#               },
#               {
#                 "label": "Flags & Banners",
#                 "value": "939272"
#               },
#               {
#                 "label": "Prints & Posters",
#                 "value": "939400"
#               },
#               {
#                 "label": "Magazines",
#                 "value": "939528"
#               }
#             ],
#             "label": "Sports Collectibles",
#             "value": "937736"
#           }
#         ],
#         "label": "Sports & Outdoor",
#         "value": "603014"
#       },
#       {
#         "children": [
#           {
#             "children": [
#               {
#                 "label": "Storage Bags",
#                 "value": "852744"
#               },
#               {
#                 "label": "Storage Boxes & Bins",
#                 "value": "600621"
#               },
#               {
#                 "label": "Storage Baskets",
#                 "value": "600686"
#               },
#               {
#                 "label": "Storage Holders & Racks",
#                 "value": "852872"
#               },
#               {
#                 "label": "Storage Bottles & Jars",
#                 "value": "853000"
#               },
#               {
#                 "label": "Hangers & Pegs",
#                 "value": "600748"
#               },
#               {
#                 "label": "Hooks & Rails",
#                 "value": "853128"
#               }
#             ],
#             "label": "Home Organizers",
#             "value": "851848"
#           },
#           {
#             "children": [
#               {
#                 "label": "Bathroom Gadgets",
#                 "value": "853256"
#               },
#               {
#                 "label": "Soap Dispensers",
#                 "value": "600416"
#               },
#               {
#                 "label": "Toothbrush Holders",
#                 "value": "600436"
#               },
#               {
#                 "label": "Soap Dishes",
#                 "value": "600447"
#               },
#               {
#                 "label": "Bathroom Sets",
#                 "value": "853384"
#               },
#               {
#                 "label": "Wash Tubs & Foot Baths",
#                 "value": "600451"
#               },
#               {
#                 "label": "Bathing Accessories",
#                 "value": "853512"
#               },
#               {
#                 "label": "Bath Mats",
#                 "value": "853640"
#               },
#               {
#                 "label": "Shower Caps",
#                 "value": "853768"
#               },
#               {
#                 "label": "Shower Curtains & Rods",
#                 "value": "600439"
#               },
#               {
#                 "label": "Toilet Seat Covers",
#                 "value": "600406"
#               },
#               {
#                 "label": "Bathroom Tumblers",
#                 "value": "600430"
#               },
#               {
#                 "label": "Toilet Brush & Plungers",
#                 "value": "600405"
#               }
#             ],
#             "label": "Bathroom Supplies",
#             "value": "851976"
#           },
#           {
#             "children": [
#               {
#                 "label": "Decorative Stickers",
#                 "value": "600338"
#               },
#               {
#                 "label": "Decorative Paintings",
#                 "value": "700656"
#               },
#               {
#                 "label": "Hooks & Shelves",
#                 "value": "600347"
#               },
#               {
#                 "label": "Tapestries",
#                 "value": "853896"
#               },
#               {
#                 "label": "Hanging Decor",
#                 "value": "854024"
#               },
#               {
#                 "label": "Photo Frames",
#                 "value": "600341"
#               },
#               {
#                 "label": "Clocks",
#                 "value": "600321"
#               },
#               {
#                 "label": "Candle Holders",
#                 "value": "854280"
#               },
#               {
#                 "label": "Candles",
#                 "value": "854152"
#               },
#               {
#                 "label": "Decorative Flowers, Plants & Fruit",
#                 "value": "700654"
#               },
#               {
#                 "label": "Vase & Fillers",
#                 "value": "700655"
#               },
#               {
#                 "label": "Statues & Figurines",
#                 "value": "600299"
#               },
#               {
#                 "label": "Mirrors",
#                 "value": "854408"
#               },
#               {
#                 "label": "Fridge Magnets",
#                 "value": "854536"
#               },
#               {
#                 "label": "Fengshui Ornaments",
#                 "value": "854664"
#               },
#               {
#                 "label": "Religious Decorations",
#                 "value": "854792"
#               }
#             ],
#             "label": "Home Decor",
#             "value": "852104"
#           },
#           {
#             "children": [
#               {
#                 "label": "Household Cleaners",
#                 "value": "600812"
#               },
#               {
#                 "label": "Home Fragrance",
#                 "value": "600477"
#               },
#               {
#                 "label": "Moth, Mould & Damp Proofing",
#                 "value": "600458"
#               },
#               {
#                 "label": "Dust Covers",
#                 "value": "700665"
#               },
#               {
#                 "label": "Pest & Weed Control",
#                 "value": "600466"
#               },
#               {
#                 "label": "Toilet Paper & Wipes",
#                 "value": "600839"
#               },
#               {
#                 "label": "Cleaning Gloves",
#                 "value": "600396"
#               },
#               {
#                 "label": "Squeegees",
#                 "value": "600418"
#               },
#               {
#                 "label": "Brooms ",
#                 "value": "600417"
#               },
#               {
#                 "label": "Mops",
#                 "value": "600423"
#               },
#               {
#                 "label": "Buckets",
#                 "value": "854920"
#               },
#               {
#                 "label": "Trash Bags",
#                 "value": "600401"
#               },
#               {
#                 "label": "Dusters/Duster Heads",
#                 "value": "600378"
#               },
#               {
#                 "label": "Formaldehyde Removers",
#                 "value": "600475"
#               },
#               {
#                 "label": "Sponges & Scouring Pads",
#                 "value": "855048"
#               },
#               {
#                 "label": "Cleaning Cloths",
#                 "value": "600409"
#               },
#               {
#                 "label": "Bins",
#                 "value": "600403"
#               },
#               {
#                 "label": "Aprons",
#                 "value": "600427"
#               }
#             ],
#             "label": "Home Care Supplies",
#             "value": "852232"
#           },
#           {
#             "children": [
#               {
#                 "label": "Laundry Balls & Discs",
#                 "value": "855176"
#               },
#               {
#                 "label": "Ironing Boards",
#                 "value": "600756"
#               },
#               {
#                 "label": "Washboards",
#                 "value": "855304"
#               },
#               {
#                 "label": "Washing Lines",
#                 "value": "600750"
#               },
#               {
#                 "label": "Washing Bags",
#                 "value": "600747"
#               },
#               {
#                 "label": "Drying Racks",
#                 "value": "600758"
#               }
#             ],
#             "label": "Laundry Tools & Accessories",
#             "value": "852360"
#           },
#           {
#             "children": [
#               {
#                 "label": "Balloons",
#                 "value": "600017"
#               },
#               {
#                 "label": "Backdrops & Banners",
#                 "value": "855432"
#               },
#               {
#                 "label": "Cards",
#                 "value": "855560"
#               },
#               {
#                 "label": "Disposable Tableware",
#                 "value": "855688"
#               },
#               {
#                 "label": "Party Hats, Masks & Accessories",
#                 "value": "855816"
#               },
#               {
#                 "label": "Party Bags & Gifts",
#                 "value": "855944"
#               },
#               {
#                 "label": "Cake Decorations",
#                 "value": "856072"
#               },
#               {
#                 "label": "Sprays, Confetti & Streamers",
#                 "value": "600019"
#               },
#               {
#                 "label": "Festive Decorations",
#                 "value": "600009"
#               }
#             ],
#             "label": "Festive & Party Supplies",
#             "value": "852488"
#           },
#           {
#             "children": [
#               {
#                 "label": "Umbrellas",
#                 "value": "600570"
#               },
#               {
#                 "label": "Raincoats",
#                 "value": "600573"
#               },
#               {
#                 "label": "Hot Water Bottles",
#                 "value": "856200"
#               },
#               {
#                 "label": "Heat Patches",
#                 "value": "700662"
#               },
#               {
#                 "label": "Ice Packs",
#                 "value": "856328"
#               },
#               {
#                 "label": "Lighter Accessories",
#                 "value": "856456"
#               },
#               {
#                 "label": "Wellington Boots",
#                 "value": "600574"
#               },
#               {
#                 "label": "Rain Cloths",
#                 "value": "600569"
#               }
#             ],
#             "label": "Miscellaneous Home",
#             "value": "852616"
#           }
#         ],
#         "label": "Home Supplies",
#         "value": "600001"
#       },
#       {
#         "children": [
#           {
#             "children": [
#               {
#                 "label": "Pillows & Bed Wedges",
#                 "value": "700653"
#               },
#               {
#                 "label": "Bedding Sets",
#                 "value": "808584"
#               },
#               {
#                 "label": "Sheets & Pillowcases",
#                 "value": "600165"
#               },
#               {
#                 "label": "Duvets ",
#                 "value": "808840"
#               },
#               {
#                 "label": "Quilts",
#                 "value": "700652"
#               },
#               {
#                 "label": "Bedspreads",
#                 "value": "809096"
#               },
#               {
#                 "label": "Blankets & Throws",
#                 "value": "600157"
#               },
#               {
#                 "label": "Bed Skirts",
#                 "value": "809352"
#               },
#               {
#                 "label": "Mattress Pads & Toppers",
#                 "value": "809480"
#               },
#               {
#                 "label": "Duvet Covers",
#                 "value": "809608"
#               },
#               {
#                 "label": "Mosquito Nets",
#                 "value": "809736"
#               },
#               {
#                 "label": "Kids' Bedding",
#                 "value": "809864"
#               }
#             ],
#             "label": "Bedding",
#             "value": "808328"
#           },
#           {
#             "children": [
#               {
#                 "label": "Carpets, Mats & Rugs\t",
#                 "value": "600221"
#               },
#               {
#                 "label": "Pad, Cushions and Covers",
#                 "value": "700661"
#               },
#               {
#                 "label": "Sofa Covers",
#                 "value": "810376"
#               },
#               {
#                 "label": "Curtains",
#                 "value": "810504"
#               },
#               {
#                 "label": "Chair Covers",
#                 "value": "600203"
#               },
#               {
#                 "label": "Tablecloths & Runners\t",
#                 "value": "600204"
#               },
#               {
#                 "label": "Towels",
#                 "value": "810888"
#               }
#             ],
#             "label": "Household Textiles",
#             "value": "809992"
#           },
#           {
#             "children": [
#               {
#                 "label": "Textiles & Fabrics",
#                 "value": "811144"
#               },
#               {
#                 "label": "Sewing Craft Kits",
#                 "value": "600251"
#               },
#               {
#                 "label": "Sewing Tool Kits",
#                 "value": "600252"
#               },
#               {
#                 "label": "Sewing Accessories & Haberdashery",
#                 "value": "811528"
#               },
#               {
#                 "label": "Sewing Machines",
#                 "value": "811656"
#               },
#               {
#                 "label": "Thread",
#                 "value": "811784"
#               },
#               {
#                 "label": "Needles",
#                 "value": "811912"
#               }
#             ],
#             "label": "Fabrics & Sewing Supplies",
#             "value": "811016"
#           }
#         ],
#         "label": "Textiles & Soft Furnishings",
#         "value": "600154"
#       },
#       {
#         "children": [
#           {
#             "children": [
#               {
#                 "label": "Coffee Filters",
#                 "value": "860424"
#               },
#               {
#                 "label": "Coffee Pots",
#                 "value": "600096"
#               },
#               {
#                 "label": "Manual Coffee Grinders",
#                 "value": "860680"
#               },
#               {
#                 "label": "Coffee Sets",
#                 "value": "600100"
#               },
#               {
#                 "label": "Milk Jugs",
#                 "value": "600102"
#               },
#               {
#                 "label": "Coffee-Making Tools\t",
#                 "value": "600103"
#               },
#               {
#                 "label": "Teapots",
#                 "value": "860808"
#               },
#               {
#                 "label": "Tea Sets",
#                 "value": "860936"
#               },
#               {
#                 "label": "Tea-Making Tools",
#                 "value": "861064"
#               }
#             ],
#             "label": "Tea & Coffeeware",
#             "value": "858504"
#           },
#           {
#             "children": [
#               {
#                 "label": "Chopping Boards",
#                 "value": "600151"
#               },
#               {
#                 "label": "Knife Sharpeners",
#                 "value": "861192"
#               },
#               {
#                 "label": "Kitchen Knives",
#                 "value": "600145"
#               },
#               {
#                 "label": "Knife Blocks & Storage",
#                 "value": "861320"
#               },
#               {
#                 "label": "Kitchen Scissors",
#                 "value": "861576"
#               },
#               {
#                 "label": "Knife Block Sets",
#                 "value": "861832"
#               }
#             ],
#             "label": "Kitchen Knives",
#             "value": "858632"
#           },
#           {
#             "children": [
#               {
#                 "label": "Barbecues",
#                 "value": "862216"
#               },
#               {
#                 "label": "Barbecue Utensils",
#                 "value": "862344"
#               }
#             ],
#             "label": "Barbecue",
#             "value": "858760"
#           },
#           {
#             "children": [
#               {
#                 "label": "Bar Utensils",
#                 "value": "600075"
#               },
#               {
#                 "label": "Bar Sets",
#                 "value": "600081"
#               },
#               {
#                 "label": "Wine Racks",
#                 "value": "600080"
#               }
#             ],
#             "label": "Bar & Wine Utensils",
#             "value": "858888"
#           },
#           {
#             "children": [
#               {
#                 "label": "Baking Sets",
#                 "value": "862600"
#               },
#               {
#                 "label": "Baking Tins & Moulds",
#                 "value": "600119"
#               },
#               {
#                 "label": "Oven Mitts",
#                 "value": "862856"
#               },
#               {
#                 "label": "Baking Trays",
#                 "value": "863112"
#               },
#               {
#                 "label": "Decorating Tools",
#                 "value": "863368"
#               },
#               {
#                 "label": "Baking Utensils",
#                 "value": "600152"
#               }
#             ],
#             "label": "Bakeware",
#             "value": "859016"
#           },
#           {
#             "children": [
#               {
#                 "label": "Cookware Sets",
#                 "value": "863624"
#               },
#               {
#                 "label": "Pans & Woks",
#                 "value": "863880"
#               },
#               {
#                 "label": "Pots",
#                 "value": "600146"
#               },
#               {
#                 "label": "Steamers",
#                 "value": "864008"
#               },
#               {
#                 "label": "Pressure Cookers",
#                 "value": "864264"
#               },
#               {
#                 "label": "Disposable Cookware",
#                 "value": "864392"
#               }
#             ],
#             "label": "Cookware",
#             "value": "859144"
#           },
#           {
#             "children": [
#               {
#                 "label": "Tableware Sets",
#                 "value": "600071"
#               },
#               {
#                 "label": "Bowls",
#                 "value": "600069"
#               },
#               {
#                 "label": "Plates",
#                 "value": "600064"
#               },
#               {
#                 "label": "Forks",
#                 "value": "600070"
#               },
#               {
#                 "label": "Knives",
#                 "value": "600072"
#               },
#               {
#                 "label": "Spoons",
#                 "value": "600073"
#               },
#               {
#                 "label": "Chopsticks",
#                 "value": "600063"
#               },
#               {
#                 "label": "Napkins",
#                 "value": "864648"
#               },
#               {
#                 "label": "Placemats & Coasters\t",
#                 "value": "600033"
#               },
#               {
#                 "label": "Lunch Boxes\t",
#                 "value": "600059"
#               }
#             ],
#             "label": "Cutlery & Tableware",
#             "value": "859272"
#           },
#           {
#             "children": [
#               {
#                 "label": "Cups & Saucers\t",
#                 "value": "600095"
#               },
#               {
#                 "label": "Mugs",
#                 "value": "600042"
#               },
#               {
#                 "label": "Glasses\t",
#                 "value": "600036"
#               },
#               {
#                 "label": "Water Bottles\t",
#                 "value": "600048"
#               },
#               {
#                 "label": "Kettles & Jugs",
#                 "value": "864904"
#               },
#               {
#                 "label": "Hip Flasks",
#                 "value": "865032"
#               },
#               {
#                 "label": "Vacuum Flasks",
#                 "value": "600032"
#               },
#               {
#                 "label": "Drinkware Accessories",
#                 "value": "600047"
#               }
#             ],
#             "label": "Drinkware",
#             "value": "859400"
#           },
#           {
#             "children": [
#               {
#                 "label": "Cooking Utensils",
#                 "value": "600148"
#               },
#               {
#                 "label": "Measuring Utensils",
#                 "value": "600121"
#               },
#               {
#                 "label": "Seasoning Utensils",
#                 "value": "865288"
#               },
#               {
#                 "label": "Fruit & Vegetable Utensils",
#                 "value": "600060"
#               },
#               {
#                 "label": "Kitchen Thermometers",
#                 "value": "865544"
#               },
#               {
#                 "label": "Kitchen Timers",
#                 "value": "600127"
#               },
#               {
#                 "label": "Pasta & Pizza Utensils",
#                 "value": "865800"
#               },
#               {
#                 "label": "Meat & Poultry Utensils",
#                 "value": "600132"
#               },
#               {
#                 "label": "Ice Cream Utensils",
#                 "value": "865928"
#               },
#               {
#                 "label": "Egg Utensils",
#                 "value": "866184"
#               },
#               {
#                 "label": "Seafood Utensils",
#                 "value": "866440"
#               },
#               {
#                 "label": "Drinking Utensils",
#                 "value": "866568"
#               },
#               {
#                 "label": "Openers",
#                 "value": "866824"
#               },
#               {
#                 "label": "Sieves and Colanders",
#                 "value": "600135"
#               },
#               {
#                 "label": "Oil Dispensers",
#                 "value": "866952"
#               },
#               {
#                 "label": "Peelers & Cutters",
#                 "value": "867208"
#               },
#               {
#                 "label": "Fire Starters",
#                 "value": "600123"
#               },
#               {
#                 "label": "Preserving Containers",
#                 "value": "600029"
#               },
#               {
#                 "label": "Other",
#                 "value": "600139"
#               }
#             ],
#             "label": "Kitchen Utensils & Gadgets",
#             "value": "859528"
#           }
#         ],
#         "label": "Kitchenware",
#         "value": "600024"
#       },
#       {
#         "children": [
#           {
#             "children": [
#               {
#                 "label": "Microwaves",
#                 "value": "848136"
#               },
#               {
#                 "label": "Countertop Ovens",
#                 "value": "848264"
#               },
#               {
#                 "label": "Juicers & Blenders ",
#                 "value": "848520"
#               },
#               {
#                 "label": "Coffee Machines & Accessories",
#                 "value": "934536"
#               },
#               {
#                 "label": "Bread Makers",
#                 "value": "934664"
#               },
#               {
#                 "label": "Toasters",
#                 "value": "847624"
#               },
#               {
#                 "label": "Electric Kettles",
#                 "value": "848392"
#               },
#               {
#                 "label": "Mixers",
#                 "value": "934792"
#               },
#               {
#                 "label": "Rice & Pressure Cookers",
#                 "value": "847752"
#               },
#               {
#                 "label": "Water Filters",
#                 "value": "934920"
#               },
#               {
#                 "label": "Water Coolers & Dispensers",
#                 "value": "935048"
#               },
#               {
#                 "label": "Electric Steamers",
#                 "value": "847880"
#               },
#               {
#                 "label": "Food Processors",
#                 "value": "935176"
#               },
#               {
#                 "label": "Fryers",
#                 "value": "935304"
#               },
#               {
#                 "label": "Vacuum Sealers",
#                 "value": "848008"
#               },
#               {
#                 "label": "Kitchen Appliance Parts",
#                 "value": "935432"
#               }
#             ],
#             "label": "Kitchen Appliances",
#             "value": "844168"
#           },
#           {
#             "children": [
#               {
#                 "label": "Vacuum Cleaners & Sweeping Robots",
#                 "value": "601102"
#               },
#               {
#                 "label": "Electric Mops",
#                 "value": "934152"
#               },
#               {
#                 "label": "Electric Window Cleaners\t",
#                 "value": "601116"
#               },
#               {
#                 "label": "Humidifiers",
#                 "value": "601092"
#               },
#               {
#                 "label": "Air Purifiers",
#                 "value": "601090"
#               },
#               {
#                 "label": "Fans",
#                 "value": "601104"
#               },
#               {
#                 "label": "Dehumidifiers",
#                 "value": "601108"
#               },
#               {
#                 "label": "Heaters",
#                 "value": "601095"
#               },
#               {
#                 "label": "Irons",
#                 "value": "601100"
#               },
#               {
#                 "label": "Clothes Steamers\t",
#                 "value": "601107"
#               },
#               {
#                 "label": "Clothes & Shoe Dryers",
#                 "value": "934280"
#               },
#               {
#                 "label": "Electronic Mosquito Killers",
#                 "value": "934408"
#               },
#               {
#                 "label": "Household Appliance Parts",
#                 "value": "601106"
#               }
#             ],
#             "label": "Home Appliances",
#             "value": "844808"
#           },
#           {
#             "children": [
#               {
#                 "label": "Air Conditioner",
#                 "value": "849928"
#               },
#               {
#                 "label": "Water Heaters",
#                 "value": "850056"
#               },
#               {
#                 "label": "Washing Machines & Dryers",
#                 "value": "850184"
#               },
#               {
#                 "label": "Fridges & Freezers",
#                 "value": "850312"
#               },
#               {
#                 "label": "Range Hoods",
#                 "value": "850440"
#               },
#               {
#                 "label": "Ovens, Ranges & Hobs",
#                 "value": "850568"
#               },
#               {
#                 "label": "Dishwashers",
#                 "value": "850696"
#               },
#               {
#                 "label": "Large Appliance Parts",
#                 "value": "850824"
#               },
#               {
#                 "label": "Television",
#                 "value": "600852"
#               }
#             ],
#             "label": "Large Home Appliances",
#             "value": "845064"
#           },
#           {
#             "children": [
#               {
#                 "label": "Laundry Equipment",
#                 "value": "850952"
#               },
#               {
#                 "label": "Cleaning Equipment",
#                 "value": "851080"
#               },
#               {
#                 "label": "Commercial Stoves",
#                 "value": "851208"
#               },
#               {
#                 "label": "Fan & Exhaust Equipment",
#                 "value": "851336"
#               },
#               {
#                 "label": "Refrigeration Equipment",
#                 "value": "851464"
#               },
#               {
#                 "label": "Food Processing Equipment",
#                 "value": "851592"
#               },
#               {
#                 "label": "Commercial Appliance Parts",
#                 "value": "851720"
#               }
#             ],
#             "label": "Commercial Appliances",
#             "value": "845320"
#           }
#         ],
#         "label": "Household Appliances",
#         "value": "600942"
#       },
#       {
#         "children": [
#           {
#             "children": [
#               {
#                 "label": "Makeup Base and Primers\t",
#                 "value": "601556"
#               },
#               {
#                 "label": "Blemish Balm and Colour Control\t",
#                 "value": "601550"
#               },
#               {
#                 "label": "Powder\t",
#                 "value": "601558"
#               },
#               {
#                 "label": "Concealer & Foundation\t",
#                 "value": "601554"
#               },
#               {
#                 "label": "Blusher\t",
#                 "value": "601560"
#               },
#               {
#                 "label": "Eyeshadow",
#                 "value": "601588"
#               },
#               {
#                 "label": "Mascara",
#                 "value": "601585"
#               },
#               {
#                 "label": "Eyeliner & Lipliner\t",
#                 "value": "601587"
#               },
#               {
#                 "label": "Eyebrow Pencils/Powder/Paste",
#                 "value": "601586"
#               },
#               {
#                 "label": "Makeup Fixer Spray",
#                 "value": "601552"
#               },
#               {
#                 "label": "Body Makeup",
#                 "value": "601582"
#               },
#               {
#                 "label": "Lipstick & Lip Gloss\t",
#                 "value": "601534"
#               },
#               {
#                 "label": "Bronzer & Highlighter\t",
#                 "value": "601555"
#               },
#               {
#                 "label": "Makeup Sets\t",
#                 "value": "601529"
#               },
#               {
#                 "label": "Makeup Remover\t",
#                 "value": "601618"
#               },
#               {
#                 "label": "Perfume\t",
#                 "value": "601583"
#               },
#               {
#                 "label": "Makeup Tools\t",
#                 "value": "601537"
#               }
#             ],
#             "label": "Makeup & Perfume",
#             "value": "848648"
#           },
#           {
#             "children": [
#               {
#                 "label": "Facial Cleansers\t",
#                 "value": "601609"
#               },
#               {
#                 "label": "Toners\t",
#                 "value": "601608"
#               },
#               {
#                 "label": "Moisturisers & Mists\t",
#                 "value": "601615"
#               },
#               {
#                 "label": "Serums & Essences\t",
#                 "value": "601619"
#               },
#               {
#                 "label": "Facial Massage Cream",
#                 "value": "601610"
#               },
#               {
#                 "label": "Face Scrubs & Peels\t",
#                 "value": "601613"
#               },
#               {
#                 "label": "Face Masks\t",
#                 "value": "601616"
#               },
#               {
#                 "label": "Nasal Treatment",
#                 "value": "601653"
#               },
#               {
#                 "label": "Eye Treatments\t",
#                 "value": "601646"
#               },
#               {
#                 "label": "Lip Treatments\t",
#                 "value": "601595"
#               },
#               {
#                 "label": "Skin Care Kits",
#                 "value": "601611"
#               },
#               {
#                 "label": "Facial Sunscreen & Sun Care\t",
#                 "value": "601602"
#               },
#               {
#                 "label": "Acne Treatments",
#                 "value": "873480"
#               },
#               {
#                 "label": "Skincare Tools\t",
#                 "value": "601733"
#               }
#             ],
#             "label": "Skincare",
#             "value": "848776"
#           },
#           {
#             "children": [
#               {
#                 "label": "Shampoo & Conditioner\t",
#                 "value": "601469"
#               },
#               {
#                 "label": "Mousse & Gel",
#                 "value": "601513"
#               },
#               {
#                 "label": "Hair Dye\t",
#                 "value": "601516"
#               },
#               {
#                 "label": "Heatless Styling Tools",
#                 "value": "700789"
#               }
#             ],
#             "label": "Hair Care & Styling",
#             "value": "848904"
#           },
#           {
#             "children": [
#               {
#                 "label": "Hand & Foot Masks\t",
#                 "value": "601454"
#               },
#               {
#                 "label": "Hand Wash\t",
#                 "value": "601508"
#               },
#               {
#                 "label": "Foot Odour Control\t",
#                 "value": "601456"
#               },
#               {
#                 "label": "Hand Lotions, Creams & Scrubs\t",
#                 "value": "601480"
#               },
#               {
#                 "label": "Nail Art & Nail Polish\t",
#                 "value": "601591"
#               },
#               {
#                 "label": "Manicure & Pedicure Tools\t",
#                 "value": "700790"
#               }
#             ],
#             "label": "Hand, Foot & Nail Care",
#             "value": "849032"
#           },
#           {
#             "children": [
#               {
#                 "label": "Body Wash & Soap",
#                 "value": "601493"
#               },
#               {
#                 "label": "Body Scrubs & Peels\t",
#                 "value": "601506"
#               },
#               {
#                 "label": "Body Masks",
#                 "value": "873608"
#               },
#               {
#                 "label": "Body Creams & Lotions\t",
#                 "value": "601492"
#               },
#               {
#                 "label": "Deodorants & Antiperspirants",
#                 "value": "601498"
#               },
#               {
#                 "label": "Body & Massage Oil",
#                 "value": "873736"
#               },
#               {
#                 "label": "Talcum Powder",
#                 "value": "601494"
#               },
#               {
#                 "label": "Body Care Kits",
#                 "value": "601490"
#               },
#               {
#                 "label": "Body Shaping Products",
#                 "value": "601686"
#               },
#               {
#                 "label": "Manual Massage Tools",
#                 "value": "700785"
#               },
#               {
#                 "label": "Hair Removal Cream, Wax & Shave",
#                 "value": "601495"
#               },
#               {
#                 "label": "Sunscreen & Sun Care",
#                 "value": "873864"
#               },
#               {
#                 "label": "Breast Care ",
#                 "value": "601511"
#               }
#             ],
#             "label": "Bath & Body Care",
#             "value": "849160"
#           },
#           {
#             "children": [
#               {
#                 "label": "Makeup",
#                 "value": "601565"
#               },
#               {
#                 "label": "Skincare\t",
#                 "value": "601627"
#               },
#               {
#                 "label": "Bath & Body Care\t",
#                 "value": "601520"
#               },
#               {
#                 "label": "Hair Care\t",
#                 "value": "601681"
#               },
#               {
#                 "label": "Razors\t",
#                 "value": "700791"
#               },
#               {
#                 "label": "Shaving Foam & Aftershave\t",
#                 "value": "601644"
#               }
#             ],
#             "label": "Men's Care",
#             "value": "849288"
#           },
#           {
#             "children": [
#               {
#                 "label": "Electric Shavers",
#                 "value": "873992"
#               },
#               {
#                 "label": "Electric Toothbrushes",
#                 "value": "874120"
#               },
#               {
#                 "label": "Oral Irrigators",
#                 "value": "874248"
#               },
#               {
#                 "label": "Hair Dryers",
#                 "value": "874376"
#               },
#               {
#                 "label": "Electric Eyebrow Shapers",
#                 "value": "601669"
#               },
#               {
#                 "label": "Curlers & Straighteners",
#                 "value": "874504"
#               },
#               {
#                 "label": "Hair Trimmers & Clippers",
#                 "value": "874632"
#               },
#               {
#                 "label": "Facial Beauty Devices\t",
#                 "value": "601672"
#               },
#               {
#                 "label": "Body Beauty Devices\t",
#                 "value": "601664"
#               },
#               {
#                 "label": "Massage Devices\t",
#                 "value": "601660"
#               },
#               {
#                 "label": "Accessories\t",
#                 "value": "601677"
#               }
#             ],
#             "label": "Personal Care Appliances",
#             "value": "849416"
#           },
#           {
#             "children": [
#               {
#                 "label": "Contact Lens\t",
#                 "value": "601462"
#               },
#               {
#                 "label": "Lens Solutions & Eyedrops\t",
#                 "value": "601461"
#               },
#               {
#                 "label": "Contact Lens Conditioning Kits",
#                 "value": "601463"
#               },
#               {
#                 "label": "Reading Glasses",
#                 "value": "874760"
#               },
#               {
#                 "label": "Sleep Masks\t",
#                 "value": "601737"
#               },
#               {
#                 "label": "Ear Drops",
#                 "value": "874888"
#               },
#               {
#                 "label": "Earwax Removal Products",
#                 "value": "875016"
#               },
#               {
#                 "label": "Ear Plugs",
#                 "value": "875144"
#               }
#             ],
#             "label": "Eye & Ear Care",
#             "value": "849544"
#           },
#           {
#             "children": [
#               {
#                 "label": "Toothbrushes\t",
#                 "value": "601697"
#               },
#               {
#                 "label": "Toothpastes",
#                 "value": "601696"
#               },
#               {
#                 "label": "Dental Floss & Picks",
#                 "value": "601698"
#               },
#               {
#                 "label": "Mouthwash",
#                 "value": "601694"
#               },
#               {
#                 "label": "Oral Spray",
#                 "value": "601693"
#               },
#               {
#                 "label": "Oral Care Kits",
#                 "value": "601692"
#               },
#               {
#                 "label": "Denture Care",
#                 "value": "875272"
#               },
#               {
#                 "label": "Teeth Whitening\t",
#                 "value": "601690"
#               },
#               {
#                 "label": "Nasal Cleaning",
#                 "value": "875400"
#               }
#             ],
#             "label": "Nasal & Oral Care",
#             "value": "849672"
#           },
#           {
#             "children": [
#               {
#                 "label": "Sanitary Towels\t",
#                 "value": "601477"
#               },
#               {
#                 "label": "Tampons",
#                 "value": "875528"
#               },
#               {
#                 "label": "Family Planning Tests",
#                 "value": "875656"
#               },
#               {
#                 "label": "Menstrual Cups",
#                 "value": "875784"
#               },
#               {
#                 "label": "Feminine Hygiene\t",
#                 "value": "601476"
#               },
#               {
#                 "label": "Vaginal Cream",
#                 "value": "601475"
#               }
#             ],
#             "label": "Feminine Care ",
#             "value": "849800"
#           }
#         ],
#         "label": "Beauty & Personal Care",
#         "value": "601450"
#       },
#       {
#         "children": [
#           {
#             "children": [
#               {
#                 "label": "Desktop Computers\t",
#                 "value": "601836"
#               },
#               {
#                 "label": "Laptops",
#                 "value": "601756"
#               },
#               {
#                 "label": "Tablets",
#                 "value": "825224"
#               }
#             ],
#             "label": "Desktop Computers, Laptops & Tablets",
#             "value": "824840"
#           },
#           {
#             "children": [
#               {
#                 "label": "Fans & Heatsinks",
#                 "value": "825480"
#               },
#               {
#                 "label": "Monitors",
#                 "value": "601783"
#               },
#               {
#                 "label": "Processors",
#                 "value": "825608"
#               },
#               {
#                 "label": "Motherboards",
#                 "value": "825736"
#               },
#               {
#                 "label": "Graphics Cards",
#                 "value": "825864"
#               },
#               {
#                 "label": "Power Supply Units",
#                 "value": "825992"
#               },
#               {
#                 "label": "RAM",
#                 "value": "826120"
#               },
#               {
#                 "label": "UPS & Stabilizers",
#                 "value": "826248"
#               },
#               {
#                 "label": "PC Cases",
#                 "value": "826376"
#               },
#               {
#                 "label": "Optical Drives",
#                 "value": "826504"
#               },
#               {
#                 "label": "Sound Cards",
#                 "value": "826632"
#               }
#             ],
#             "label": "Desktop & Laptop Components",
#             "value": "825352"
#           },
#           {
#             "children": [
#               {
#                 "label": "Keyboards & Mice\t",
#                 "value": "601760"
#               },
#               {
#                 "label": "USB Hubs & Card Readers",
#                 "value": "827016"
#               },
#               {
#                 "label": "Webcams",
#                 "value": "827144"
#               },
#               {
#                 "label": "Laptop Covers & Cases",
#                 "value": "827272"
#               },
#               {
#                 "label": "Cooling Pads",
#                 "value": "827400"
#               },
#               {
#                 "label": "Laptop Stands & Trays",
#                 "value": "827528"
#               },
#               {
#                 "label": "Keyboard & Trackpad Covers",
#                 "value": "827656"
#               },
#               {
#                 "label": "Laptop Batteries",
#                 "value": "827784"
#               },
#               {
#                 "label": "Laptop Chargers & Adaptors",
#                 "value": "827912"
#               },
#               {
#                 "label": "Mouse Pads",
#                 "value": "828040"
#               }
#             ],
#             "label": "Peripherals & Accessories",
#             "value": "826760"
#           },
#           {
#             "children": [
#               {
#                 "label": "Hard Drives",
#                 "value": "828296"
#               },
#               {
#                 "label": "SSD",
#                 "value": "828424"
#               },
#               {
#                 "label": "Network Attached Storage (NAS)",
#                 "value": "828552"
#               },
#               {
#                 "label": "Flash Drives & OTG Cables",
#                 "value": "828680"
#               },
#               {
#                 "label": "Hard Disk Enclosures & Docking Stations",
#                 "value": "828808"
#               },
#               {
#                 "label": "Compact Discs",
#                 "value": "828936"
#               },
#               {
#                 "label": "Software",
#                 "value": "829064"
#               }
#             ],
#             "label": "Data Storage & Software",
#             "value": "828168"
#           },
#           {
#             "children": [
#               {
#                 "label": "Modems & Wireless Routers",
#                 "value": "829320"
#               },
#               {
#                 "label": "Repeaters",
#                 "value": "829448"
#               },
#               {
#                 "label": "Wireless Adapters & Network Cards",
#                 "value": "829576"
#               },
#               {
#                 "label": "Powerline Adapters",
#                 "value": "829704"
#               },
#               {
#                 "label": "Network Switches & PoE",
#                 "value": "829832"
#               },
#               {
#                 "label": "Network Cables & Connectors",
#                 "value": "829960"
#               },
#               {
#                 "label": "KVM Switches",
#                 "value": "830088"
#               },
#               {
#                 "label": "Print Servers",
#                 "value": "830216"
#               }
#             ],
#             "label": "Network Components",
#             "value": "829192"
#           },
#           {
#             "children": [
#               {
#                 "label": "Typewriters",
#                 "value": "830472"
#               },
#               {
#                 "label": "Access Control & Attendance Devices",
#                 "value": "830600"
#               },
#               {
#                 "label": "Paper Shredders",
#                 "value": "830728"
#               },
#               {
#                 "label": "Money Counters",
#                 "value": "830856"
#               },
#               {
#                 "label": "Printers & Scanners",
#                 "value": "830984"
#               }
#             ],
#             "label": "Office Equipment",
#             "value": "830344"
#           },
#           {
#             "children": [
#               {
#                 "label": "Office Binding Supplies",
#                 "value": "831240"
#               },
#               {
#                 "label": "Office Cutting Supplies",
#                 "value": "831368"
#               },
#               {
#                 "label": "Writing & Correction Tools\t",
#                 "value": "603002"
#               },
#               {
#                 "label": "School & Educational Supplies",
#                 "value": "831624"
#               },
#               {
#                 "label": "Art Supplies",
#                 "value": "831752"
#               },
#               {
#                 "label": "Notebooks & Paper",
#                 "value": "831880"
#               },
#               {
#                 "label": "Envelopes & Postal Supplies",
#                 "value": "832008"
#               },
#               {
#                 "label": "Gifts & Wrapping",
#                 "value": "832136"
#               },
#               {
#                 "label": "Accounting Supplies",
#                 "value": "832264"
#               },
#               {
#                 "label": "Desk Organisers & Accessories",
#                 "value": "832392"
#               }
#             ],
#             "label": "Office Stationery & Supplies",
#             "value": "831112"
#           }
#         ],
#         "label": "Computers & Office Equipment",
#         "value": "601755"
#       },
#       {
#         "children": [
#           {
#             "children": [
#               {
#                 "label": " Mobile Phones",
#                 "value": "602097"
#               },
#               {
#                 "label": "Mobile Phone Parts",
#                 "value": "909832"
#               },
#               {
#                 "label": "Cases, Screen Protectors & Stickers",
#                 "value": "601925"
#               },
#               {
#                 "label": "Selfie Accessories",
#                 "value": "909960"
#               },
#               {
#                 "label": "Mobile Lenses & Flashes",
#                 "value": "910088"
#               },
#               {
#                 "label": " Cables, Chargers & Adapters",
#                 "value": "601937"
#               },
#               {
#                 "label": "Sim Cards & Accessories",
#                 "value": "910216"
#               },
#               {
#                 "label": "Phone Holders & Mounts",
#                 "value": "910344"
#               },
#               {
#                 "label": " Phone Batteries",
#                 "value": "601927"
#               },
#               {
#                 "label": " Phone Straps & Charms",
#                 "value": "601936"
#               },
#               {
#                 "label": "Casting Devices",
#                 "value": "910472"
#               },
#               {
#                 "label": "Walkie Talkies",
#                 "value": "910600"
#               },
#               {
#                 "label": "Power Banks",
#                 "value": "910728"
#               }
#             ],
#             "label": "Phones and Accessories",
#             "value": "909064"
#           },
#           {
#             "children": [
#               {
#                 "label": "Point & Shoot Cameras",
#                 "value": "910856"
#               },
#               {
#                 "label": "Mirrorless Cameras",
#                 "value": "910984"
#               },
#               {
#                 "label": "Action Cameras",
#                 "value": "911112"
#               },
#               {
#                 "label": "Video Camcorders",
#                 "value": "911240"
#               },
#               {
#                 "label": "Instant Cameras",
#                 "value": "911368"
#               },
#               {
#                 "label": "Film Cameras",
#                 "value": "911496"
#               },
#               {
#                 "label": "DSLRs",
#                 "value": "911624"
#               },
#               {
#                 "label": "Security Cameras & Systems",
#                 "value": "911752"
#               },
#               {
#                 "label": "Camera Lenses",
#                 "value": "911880"
#               },
#               {
#                 "label": "Drones & Accessories",
#                 "value": "912008"
#               },
#               {
#                 "label": " Camera Accessories",
#                 "value": "601893"
#               },
#               {
#                 "label": "Camera Care ",
#                 "value": "912136"
#               }
#             ],
#             "label": "Cameras & Photography",
#             "value": "909192"
#           },
#           {
#             "children": [
#               {
#                 "label": " Earphones & Headphones",
#                 "value": "601990"
#               },
#               {
#                 "label": "Microphones",
#                 "value": "912264"
#               },
#               {
#                 "label": "Speakers",
#                 "value": "602029"
#               },
#               {
#                 "label": "Projectors",
#                 "value": "912392"
#               },
#               {
#                 "label": "Home Cinema Systems",
#                 "value": "912520"
#               },
#               {
#                 "label": "MP3 & MP4 Players",
#                 "value": "912648"
#               },
#               {
#                 "label": "CD & DVD Players",
#                 "value": "912776"
#               },
#               {
#                 "label": "Voice Recorders",
#                 "value": "912904"
#               },
#               {
#                 "label": "Radio & Cassette Players",
#                 "value": "913032"
#               },
#               {
#                 "label": "Amplifiers & Mixers",
#                 "value": "913160"
#               },
#               {
#                 "label": "AV Receivers",
#                 "value": "913288"
#               },
#               {
#                 "label": "Audio & Video Accessories",
#                 "value": "913416"
#               }
#             ],
#             "label": "Audio & Video",
#             "value": "909320"
#           },
#           {
#             "children": [
#               {
#                 "label": "Home Games Consoles",
#                 "value": "913544"
#               },
#               {
#                 "label": "Handheld Games Consoles",
#                 "value": "913672"
#               },
#               {
#                 "label": "Video Games",
#                 "value": "913800"
#               },
#               {
#                 "label": "Console Accessories",
#                 "value": "913928"
#               }
#             ],
#             "label": " Gaming & Consoles ",
#             "value": "909448"
#           },
#           {
#             "children": [
#               {
#                 "label": "Smart Watches",
#                 "value": "602083"
#               },
#               {
#                 "label": "Fitness Trackers",
#                 "value": "914056"
#               },
#               {
#                 "label": "GPS Trackers",
#                 "value": "914184"
#               },
#               {
#                 "label": "VR Devices",
#                 "value": "914312"
#               },
#               {
#                 "label": " Wearable Accessories",
#                 "value": "602080"
#               }
#             ],
#             "label": "Smart & Wearable Devices",
#             "value": "909576"
#           },
#           {
#             "children": [
#               {
#                 "label": "E-book Readers",
#                 "value": "914440"
#               },
#               {
#                 "label": "E-dictionaries",
#                 "value": "914568"
#               }
#             ],
#             "label": "Education Devices",
#             "value": "909704"
#           }
#         ],
#         "label": "Phones & Electronics",
#         "value": "601739"
#       },
#       {
#         "children": [
#           {
#             "children": [
#               {
#                 "label": "Dog Food",
#                 "value": "812296"
#               },
#               {
#                 "label": "Dog Treats",
#                 "value": "812424"
#               },
#               {
#                 "label": "Cat Food",
#                 "value": "812552"
#               },
#               {
#                 "label": "Cat Treats",
#                 "value": "812680"
#               }
#             ],
#             "label": "Dog & Cat Food",
#             "value": "812168"
#           },
#           {
#             "children": [
#               {
#                 "label": "Beds, Sofas & Mats",
#                 "value": "812936"
#               },
#               {
#                 "label": "Houses",
#                 "value": "813064"
#               },
#               {
#                 "label": "Cages & Crates",
#                 "value": "813192"
#               },
#               {
#                 "label": "Scratching Pads & Posts",
#                 "value": "813320"
#               },
#               {
#                 "label": "Cat Hammocks ",
#                 "value": "813448"
#               },
#               {
#                 "label": "Cat & Dog Flaps",
#                 "value": "813576"
#               },
#               {
#                 "label": "Stairs & Ramps",
#                 "value": "813704"
#               },
#               {
#                 "label": "Playpens",
#                 "value": "813832"
#               }
#             ],
#             "label": "Dog & Cat Furniture",
#             "value": "812808"
#           },
#           {
#             "children": [
#               {
#                 "label": "Coats",
#                 "value": "814088"
#               },
#               {
#                 "label": "Shirts",
#                 "value": "814216"
#               },
#               {
#                 "label": "Jumpers & Hoodies",
#                 "value": "814344"
#               },
#               {
#                 "label": "Lifejackets",
#                 "value": "814472"
#               },
#               {
#                 "label": "Dresses",
#                 "value": "814600"
#               },
#               {
#                 "label": "Raincoats",
#                 "value": "814728"
#               },
#               {
#                 "label": "Boots & Paw Protectors",
#                 "value": "814856"
#               },
#               {
#                 "label": "Neck Accessories",
#                 "value": "814984"
#               },
#               {
#                 "label": "Eyewear",
#                 "value": "815112"
#               },
#               {
#                 "label": "Hair Accessories",
#                 "value": "815240"
#               },
#               {
#                 "label": "Hats",
#                 "value": "815368"
#               },
#               {
#                 "label": "Costumes",
#                 "value": "815496"
#               }
#             ],
#             "label": "Dog & Cat Clothing",
#             "value": "813960"
#           },
#           {
#             "children": [
#               {
#                 "label": "Litter Trays & Boxes",
#                 "value": "815752"
#               },
#               {
#                 "label": "Diapers, Pads & Trays",
#                 "value": "815880"
#               },
#               {
#                 "label": "Poop Bags & Scoopers",
#                 "value": "816008"
#               },
#               {
#                 "label": "Odour & Stain Removers",
#                 "value": "816136"
#               },
#               {
#                 "label": "Urine Detectors",
#                 "value": "816264"
#               }
#             ],
#             "label": "Dog & Cat Litter",
#             "value": "815624"
#           },
#           {
#             "children": [
#               {
#                 "label": "Shampoos & Conditioners",
#                 "value": "816520"
#               },
#               {
#                 "label": "Bath Accessories",
#                 "value": "816648"
#               },
#               {
#                 "label": "Combs & Brushes",
#                 "value": "816776"
#               },
#               {
#                 "label": "Hair Dryers",
#                 "value": "816904"
#               },
#               {
#                 "label": "Grooming Wipes",
#                 "value": "817032"
#               },
#               {
#                 "label": "Grooming Scissors",
#                 "value": "817160"
#               },
#               {
#                 "label": "Grooming Clippers",
#                 "value": "817288"
#               },
#               {
#                 "label": "Styptic Gels & Powders",
#                 "value": "817416"
#               },
#               {
#                 "label": "Claw Care",
#                 "value": "817544"
#               },
#               {
#                 "label": "Ear Care",
#                 "value": "817672"
#               },
#               {
#                 "label": "Oral Care",
#                 "value": "817800"
#               },
#               {
#                 "label": "Eye Care",
#                 "value": "817928"
#               },
#               {
#                 "label": "Hair Removal Products",
#                 "value": "818056"
#               }
#             ],
#             "label": "Dog & Cat Grooming",
#             "value": "816392"
#           },
#           {
#             "children": [
#               {
#                 "label": "Flea & Tick Treatments",
#                 "value": "818312"
#               },
#               {
#                 "label": "Medication",
#                 "value": "818440"
#               },
#               {
#                 "label": "Vitamins & Supplements",
#                 "value": "818568"
#               }
#             ],
#             "label": "Dog & Cat Healthcare",
#             "value": "818184"
#           },
#           {
#             "children": [
#               {
#                 "label": "Collars, Harnesses & Leads",
#                 "value": "818824"
#               },
#               {
#                 "label": "Training & Behaviour Aids",
#                 "value": "818952"
#               },
#               {
#                 "label": "Dog Toys",
#                 "value": "819080"
#               },
#               {
#                 "label": "Cat Toys",
#                 "value": "819208"
#               },
#               {
#                 "label": "Feeding Supplies",
#                 "value": "819336"
#               },
#               {
#                 "label": "Carriers & Travel Supplies",
#                 "value": "819464"
#               },
#               {
#                 "label": "Memorials",
#                 "value": "819592"
#               },
#               {
#                 "label": "Cameras & Monitors",
#                 "value": "819720"
#               }
#             ],
#             "label": "Dog & Cat Accessories",
#             "value": "818696"
#           },
#           {
#             "children": [
#               {
#                 "label": "Decorations",
#                 "value": "819976"
#               },
#               {
#                 "label": "Lighting",
#                 "value": "820104"
#               },
#               {
#                 "label": "Aquariums & Tanks",
#                 "value": "820232"
#               },
#               {
#                 "label": "Temperature Control ",
#                 "value": "820360"
#               },
#               {
#                 "label": "Water Treatment",
#                 "value": "820488"
#               },
#               {
#                 "label": "Pumps & Filters",
#                 "value": "820616"
#               },
#               {
#                 "label": "Cleaning Tools",
#                 "value": "820744"
#               },
#               {
#                 "label": "Feeding Tools",
#                 "value": "820872"
#               }
#             ],
#             "label": "Fish & Aquatic Supplies",
#             "value": "819848"
#           },
#           {
#             "children": [
#               {
#                 "label": "Decorations",
#                 "value": "821128"
#               },
#               {
#                 "label": "Terrariums & Shipping Supplies",
#                 "value": "821256"
#               },
#               {
#                 "label": "Cleaning Tools",
#                 "value": "821384"
#               },
#               {
#                 "label": "Temperature Products",
#                 "value": "821512"
#               },
#               {
#                 "label": "Lighting",
#                 "value": "821640"
#               },
#               {
#                 "label": "Feeding Tools",
#                 "value": "821768"
#               }
#             ],
#             "label": "Reptile & Amphibian Supplies",
#             "value": "821000"
#           },
#           {
#             "children": [
#               {
#                 "label": "Cages & Accessories",
#                 "value": "822024"
#               },
#               {
#                 "label": "Grooming Supplies",
#                 "value": "822152"
#               },
#               {
#                 "label": "Toys",
#                 "value": "822280"
#               },
#               {
#                 "label": "Swings & Perches",
#                 "value": "822408"
#               },
#               {
#                 "label": "Training Aids",
#                 "value": "822536"
#               },
#               {
#                 "label": "Feeding Tools",
#                 "value": "822664"
#               }
#             ],
#             "label": "Bird Supplies",
#             "value": "821896"
#           },
#           {
#             "children": [
#               {
#                 "label": "Houses & Habitats",
#                 "value": "822920"
#               },
#               {
#                 "label": "Toys",
#                 "value": "823048"
#               },
#               {
#                 "label": "Collars, Harnesses & Leads",
#                 "value": "823176"
#               },
#               {
#                 "label": "Feeding Supplies",
#                 "value": "823304"
#               },
#               {
#                 "label": "Exercise Wheels",
#                 "value": "823432"
#               },
#               {
#                 "label": "Grooming Supplies",
#                 "value": "823560"
#               },
#               {
#                 "label": "Carriers",
#                 "value": "823688"
#               },
#               {
#                 "label": "Health Supplies",
#                 "value": "823816"
#               },
#               {
#                 "label": "Odor & Stain Removers",
#                 "value": "823944"
#               }
#             ],
#             "label": "Small Animal Supplies",
#             "value": "822792"
#           }
#         ],
#         "label": "Pet Supplies",
#         "value": "602118"
#       },
#       {
#         "children": [
#           {
#             "children": [
#               {
#                 "label": "Swimwear",
#                 "value": "888456"
#               },
#               {
#                 "label": "Socks & Tights",
#                 "value": "888584"
#               },
#               {
#                 "label": "Bottoms",
#                 "value": "888712"
#               },
#               {
#                 "label": "Bodysuits & One-pieces",
#                 "value": "700694"
#               },
#               {
#                 "label": "Gift Sets",
#                 "value": "888968"
#               },
#               {
#                 "label": "Dresses",
#                 "value": "889096"
#               },
#               {
#                 "label": "Tops",
#                 "value": "889224"
#               },
#               {
#                 "label": "Jackets & Coats",
#                 "value": "889352"
#               },
#               {
#                 "label": "Sleepwear",
#                 "value": "889480"
#               },
#               {
#                 "label": "Baby Costume Jewellery",
#                 "value": "602301"
#               },
#               {
#                 "label": "Shoes\t",
#                 "value": "602787"
#               }
#             ],
#             "label": "Baby Clothing & Shoes",
#             "value": "877320"
#           },
#           {
#             "children": [
#               {
#                 "label": "Baby Carriers",
#                 "value": "889608"
#               },
#               {
#                 "label": "Prams and Pushchairs\t",
#                 "value": "700705"
#               },
#               {
#                 "label": "Pushchair Accessories",
#                 "value": "889736"
#               },
#               {
#                 "label": "Baby Vehicle Seats",
#                 "value": "889864"
#               },
#               {
#                 "label": "Vehicle Seat Accessories",
#                 "value": "889992"
#               },
#               {
#                 "label": "Nappy Bags",
#                 "value": "890120"
#               },
#               {
#                 "label": "Child Harnesses & Reins",
#                 "value": "890248"
#               }
#             ],
#             "label": "Baby Travel Essentials",
#             "value": "877576"
#           },
#           {
#             "children": [
#               {
#                 "label": "Baby Bottles & Accessories",
#                 "value": "700704"
#               },
#               {
#                 "label": "Baby Bottles Warmers, Coolers & Sterilisers",
#                 "value": "890376"
#               },
#               {
#                 "label": "Breast Pumps & Accessories",
#                 "value": "933640"
#               },
#               {
#                 "label": "Breast Pads",
#                 "value": "890504"
#               },
#               {
#                 "label": "Nursing Covers",
#                 "value": "890632"
#               },
#               {
#                 "label": "Baby Utensils\t",
#                 "value": "700707"
#               },
#               {
#                 "label": "Bibs & Burp Cloths",
#                 "value": "890760"
#               },
#               {
#                 "label": "Dummies",
#                 "value": "890888"
#               },
#               {
#                 "label": "Food Processors\t",
#                 "value": "602707"
#               }
#             ],
#             "label": "Nursing & Feeding",
#             "value": "877832"
#           },
#           {
#             "children": [
#               {
#                 "label": "Cots & Beds\t",
#                 "value": "602761"
#               },
#               {
#                 "label": "Bouncers, Jumpers & Swings",
#                 "value": "602760"
#               },
#               {
#                 "label": "Baby Chairs",
#                 "value": "700706"
#               },
#               {
#                 "label": "Baby Walkers",
#                 "value": "891016"
#               },
#               {
#                 "label": "Mattresses & Bedding\t",
#                 "value": "602734"
#               }
#             ],
#             "label": "Baby Furniture",
#             "value": "878216"
#           },
#           {
#             "children": [
#               {
#                 "label": "Monitors\t",
#                 "value": "602538"
#               },
#               {
#                 "label": "Mosquito Netting",
#                 "value": "891144"
#               },
#               {
#                 "label": "Bed Rails & Guards\t",
#                 "value": "602536"
#               },
#               {
#                 "label": "Edge & Corner Guards\t",
#                 "value": "602534"
#               },
#               {
#                 "label": "Electric Shock Protection",
#                 "value": "602533"
#               },
#               {
#                 "label": "Gates & Doorways",
#                 "value": "891272"
#               },
#               {
#                 "label": "Safety Locks & Straps\t",
#                 "value": "602532"
#               }
#             ],
#             "label": "Baby Safety",
#             "value": "878600"
#           },
#           {
#             "children": [
#               {
#                 "label": "Playgyms & Playmats",
#                 "value": "891400"
#               },
#               {
#                 "label": "Playpens",
#                 "value": "891528"
#               },
#               {
#                 "label": "Bath Toys",
#                 "value": "891656"
#               },
#               {
#                 "label": "Baby Sound Toys",
#                 "value": "891784"
#               },
#               {
#                 "label": "Pacifiers, Teethers & Teething Relief",
#                 "value": "891912"
#               },
#               {
#                 "label": "Early Education & Smart Toys",
#                 "value": "892040"
#               }
#             ],
#             "label": "Baby Toys",
#             "value": "878984"
#           },
#           {
#             "children": [
#               {
#                 "label": "Baby Baths & Bath Seats",
#                 "value": "892168"
#               },
#               {
#                 "label": "Towels & Shower Caps",
#                 "value": "892296"
#               },
#               {
#                 "label": "Baby Bath Supplies",
#                 "value": "892424"
#               },
#               {
#                 "label": "Hair Care & Body Wash\t",
#                 "value": "602317"
#               },
#               {
#                 "label": "Fragrances",
#                 "value": "892552"
#               },
#               {
#                 "label": "Baby Grooming Tools",
#                 "value": "892680"
#               },
#               {
#                 "label": "Wipes & Holders",
#                 "value": "892808"
#               },
#               {
#                 "label": "Laundry Detergent\t",
#                 "value": "602673"
#               },
#               {
#                 "label": "Potty Training & Commode Chairs",
#                 "value": "893448"
#               },
#               {
#                 "label": "Baby Hand Sanitizer",
#                 "value": "602672"
#               },
#               {
#                 "label": "Nappies",
#                 "value": "929672"
#               },
#               {
#                 "label": "Baby Clothes Sterilizers",
#                 "value": "602678"
#               },
#               {
#                 "label": "Baby Hair Trimmers",
#                 "value": "602608"
#               },
#               {
#                 "label": "Baby Hair Dryers",
#                 "value": "602622"
#               },
#               {
#                 "label": "Baby Skincare\t",
#                 "value": "602296"
#               },
#               {
#                 "label": "Nasal & Oral Care\t",
#                 "value": "602676"
#               },
#               {
#                 "label": "Baby Vitamins & Supplements",
#                 "value": "947592"
#               }
#             ],
#             "label": "Baby Care & Health",
#             "value": "879112"
#           },
#           {
#             "children": [
#               {
#                 "label": "Growth Milk Formula",
#                 "value": "933768"
#               },
#               {
#                 "label": "Porridge, Puree & Cereal",
#                 "value": "933896"
#               },
#               {
#                 "label": "Snack",
#                 "value": "934024"
#               }
#             ],
#             "label": "Formula Milk & Baby Food",
#             "value": "879496"
#           },
#           {
#             "children": [
#               {
#                 "label": "Nursing Clothes",
#                 "value": "892936"
#               },
#               {
#                 "label": "Maternity Clothing & Accessories",
#                 "value": "700718"
#               },
#               {
#                 "label": "Maternity Underwear\t",
#                 "value": "700710"
#               },
#               {
#                 "label": "Maternity Pillows",
#                 "value": "893064"
#               },
#               {
#                 "label": "Supporting Belts",
#                 "value": "893192"
#               },
#               {
#                 "label": "Maternity Skincare",
#                 "value": "893320"
#               },
#               {
#                 "label": "Maternity Vitamins & Supplement",
#                 "value": "947720"
#               }
#             ],
#             "label": "Maternity Supplies",
#             "value": "880008"
#           }
#         ],
#         "label": "Baby & Maternity",
#         "value": "602284"
#       },
#       {
#         "children": [
#           {
#             "children": [
#               {
#                 "label": "Dolls",
#                 "value": "861448"
#               },
#               {
#                 "label": "Doll Houses & Playsets ",
#                 "value": "861704"
#               },
#               {
#                 "label": "Doll Accessories\t",
#                 "value": "604390"
#               },
#               {
#                 "label": "Stuffed Toys\t",
#                 "value": "700699"
#               }
#             ],
#             "label": "Dolls & Stuffed Toys",
#             "value": "859656"
#           },
#           {
#             "children": [
#               {
#                 "label": "Arts & Crafts",
#                 "value": "862472"
#               },
#               {
#                 "label": "Maths Toys",
#                 "value": "862728"
#               },
#               {
#                 "label": "Science & Technology Toys",
#                 "value": "862984"
#               },
#               {
#                 "label": "Shape Sorters",
#                 "value": "863240"
#               },
#               {
#                 "label": "Musical Toys",
#                 "value": "863752"
#               },
#               {
#                 "label": "Toy Tablets & Computers",
#                 "value": "864136"
#               }
#             ],
#             "label": "Educational Toys",
#             "value": "859784"
#           },
#           {
#             "children": [
#               {
#                 "label": "Ride-ons Toys",
#                 "value": "864520"
#               },
#               {
#                 "label": "Playground Equipment",
#                 "value": "864776"
#               },
#               {
#                 "label": "Playhouses, Tents & Tunnels",
#                 "value": "865160"
#               },
#               {
#                 "label": "Pool, Water & Sand Toys",
#                 "value": "865416"
#               },
#               {
#                 "label": "Blasters & Toy Guns",
#                 "value": "865672"
#               },
#               {
#                 "label": "Sports Toys",
#                 "value": "866056"
#               },
#               {
#                 "label": "Flying Toys",
#                 "value": "866312"
#               },
#               {
#                 "label": "Kites & Wind Spinners",
#                 "value": "866696"
#               },
#               {
#                 "label": "Play House Toys",
#                 "value": "700698"
#               }
#             ],
#             "label": "Sports & Outdoor Play",
#             "value": "859912"
#           },
#           {
#             "children": [
#               {
#                 "label": "Airplanes & Helicopters",
#                 "value": "867080"
#               },
#               {
#                 "label": "Motorcycles",
#                 "value": "867336"
#               },
#               {
#                 "label": "Boats & Submarines",
#                 "value": "867464"
#               },
#               {
#                 "label": "Cars, Lorries & Trains",
#                 "value": "867592"
#               },
#               {
#                 "label": "Animals",
#                 "value": "867720"
#               },
#               {
#                 "label": "Tanks",
#                 "value": "867848"
#               },
#               {
#                 "label": "Robots ",
#                 "value": "867976"
#               },
#               {
#                 "label": "Electric Toy Accessories",
#                 "value": "868104"
#               }
#             ],
#             "label": "Electric & Remote Control Toys",
#             "value": "860040"
#           },
#           {
#             "children": [
#               {
#                 "label": "Magic Cubes",
#                 "value": "868232"
#               },
#               {
#                 "label": "Puzzles",
#                 "value": "868360"
#               },
#               {
#                 "label": "Dice",
#                 "value": "868488"
#               },
#               {
#                 "label": "Board Games",
#                 "value": "868616"
#               },
#               {
#                 "label": "Card Games",
#                 "value": "868744"
#               },
#               {
#                 "label": "Magic Acrobatics Equipment",
#                 "value": "868872"
#               }
#             ],
#             "label": "Games & Puzzles",
#             "value": "860168"
#           },
#           {
#             "children": [
#               {
#                 "label": "Pretend Play",
#                 "value": "869000"
#               },
#               {
#                 "label": "Novelty & Gag Toys",
#                 "value": "869128"
#               },
#               {
#                 "label": "Action & Toy Figures",
#                 "value": "869256"
#               },
#               {
#                 "label": "Model & Toy Vehicles\t",
#                 "value": "700700"
#               },
#               {
#                 "label": "Building Toys",
#                 "value": "869512"
#               },
#               {
#                 "label": "Stress Relief Toys",
#                 "value": "869640"
#               },
#               {
#                 "label": "Yo-yos ",
#                 "value": "869768"
#               },
#               {
#                 "label": "Capsule Toys",
#                 "value": "869896"
#               },
#               {
#                 "label": "Spinning Tops",
#                 "value": "870024"
#               }
#             ],
#             "label": "Classic & Novelty Toys",
#             "value": "860296"
#           },
#           {
#             "children": [
#               {
#                 "label": "Keyboards & Pianos",
#                 "value": "870152"
#               },
#               {
#                 "label": "Percussion Instruments",
#                 "value": "870280"
#               },
#               {
#                 "label": "Wind Instruments",
#                 "value": "870408"
#               },
#               {
#                 "label": "Ukuleles",
#                 "value": "870536"
#               },
#               {
#                 "label": "Guitars & Stringed Instruments",
#                 "value": "870664"
#               },
#               {
#                 "label": "Music Accessories",
#                 "value": "870792"
#               },
#               {
#                 "label": "Electronic Synthesizer",
#                 "value": "870920"
#               }
#             ],
#             "label": "Musical Instruments & Accessories",
#             "value": "860552"
#           }
#         ],
#         "label": "Toys & Hobbies",
#         "value": "604206"
#       },
#       {
#         "children": [
#           {
#             "children": [
#               {
#                 "label": "Code Readers & Scanners",
#                 "value": "941064"
#               },
#               {
#                 "label": "Diagnostic Tools",
#                 "value": "941192"
#               },
#               {
#                 "label": "Sheet Metal Tools",
#                 "value": "941320"
#               },
#               {
#                 "label": "Car Battery Repair Tools",
#                 "value": "941448"
#               },
#               {
#                 "label": "Car Inspection Tools",
#                 "value": "941576"
#               },
#               {
#                 "label": "Engine & Transmission Repair Tools",
#                 "value": "941704"
#               },
#               {
#                 "label": "Tyre Repair & Fitting Tools",
#                 "value": "941832"
#               },
#               {
#                 "label": "Assembly & Disassembly Tools",
#                 "value": "941960"
#               },
#               {
#                 "label": "Car Body Repair Tools",
#                 "value": "942088"
#               }
#             ],
#             "label": "Car Repair Tools",
#             "value": "940296"
#           },
#           {
#             "children": [
#               {
#                 "label": "Decorative Lights",
#                 "value": "942216"
#               },
#               {
#                 "label": "Light Bars & Work Lights",
#                 "value": "942344"
#               },
#               {
#                 "label": "Headlight Bulbs (LED)",
#                 "value": "942472"
#               },
#               {
#                 "label": "Wires",
#                 "value": "942600"
#               },
#               {
#                 "label": "Covers",
#                 "value": "942728"
#               },
#               {
#                 "label": "Bases",
#                 "value": "942856"
#               },
#               {
#                 "label": "Indicator Lights",
#                 "value": "942984"
#               },
#               {
#                 "label": "Fog Lights",
#                 "value": "946440"
#               },
#               {
#                 "label": "Headlight Bulbs (Xenon)",
#                 "value": "943240"
#               },
#               {
#                 "label": "Headlight Bulbs (Halogen)",
#                 "value": "943368"
#               }
#             ],
#             "label": "Car Lights",
#             "value": "940424"
#           },
#           {
#             "children": [
#               {
#                 "label": "Quad Bike Parts & Accessories",
#                 "value": "943496"
#               },
#               {
#                 "label": "Boat Parts & Accessories",
#                 "value": "943624"
#               },
#               {
#                 "label": "Motorhome Parts & Accessories",
#                 "value": "943752"
#               },
#               {
#                 "label": "Electric Vehicle Parts",
#                 "value": "943880"
#               },
#               {
#                 "label": "Lorry Parts",
#                 "value": "944008"
#               },
#               {
#                 "label": "Watercraft Parts & Accessories",
#                 "value": "944136"
#               },
#               {
#                 "label": "Transportation & Storage",
#                 "value": "944264"
#               },
#               {
#                 "label": "Salvage Car Parts",
#                 "value": "944392"
#               },
#               {
#                 "label": "Snowmobile Parts",
#                 "value": "944520"
#               }
#             ],
#             "label": "Quads, Motorhomes & Boats",
#             "value": "940680"
#           },
#           {
#             "children": [
#               {
#                 "label": "Polishing Machines & Accessories",
#                 "value": "944648"
#               },
#               {
#                 "label": "Paint & Window Repair Tools",
#                 "value": "944776"
#               },
#               {
#                 "label": "Interior Care",
#                 "value": "944904"
#               },
#               {
#                 "label": "Car Wash Accessories",
#                 "value": "945032"
#               },
#               {
#                 "label": "Water Guns & Snow Foam Lances",
#                 "value": "945160"
#               },
#               {
#                 "label": "Cleaning & Care Fluids",
#                 "value": "945288"
#               },
#               {
#                 "label": "Window Repair",
#                 "value": "945416"
#               },
#               {
#                 "label": "Paint Care",
#                 "value": "945544"
#               },
#               {
#                 "label": "Engine Care",
#                 "value": "945672"
#               },
#               {
#                 "label": "Car Washers",
#                 "value": "945800"
#               }
#             ],
#             "label": "Car Washing & Maintenance",
#             "value": "940808"
#           },
#           {
#             "children": [
#               {
#                 "label": "Motorcycle Filters",
#                 "value": "945928"
#               },
#               {
#                 "label": "Frames & Fittings",
#                 "value": "946056"
#               },
#               {
#                 "label": "Motorcycle Accessories",
#                 "value": "946184"
#               },
#               {
#                 "label": "Protective Gear",
#                 "value": "946312"
#               }
#             ],
#             "label": "Motorcycle Accessories",
#             "value": "940936"
#           },
#           {
#             "children": [
#               {
#                 "label": "Intelligent Systems",
#                 "value": "930312"
#               },
#               {
#                 "label": "Video Surveillance",
#                 "value": "930440"
#               },
#               {
#                 "label": "Alarm Systems & Security",
#                 "value": "930568"
#               },
#               {
#                 "label": "Electronic Accessories",
#                 "value": "930696"
#               },
#               {
#                 "label": "Car Video Players",
#                 "value": "930952"
#               },
#               {
#                 "label": "GPS & Accessories",
#                 "value": "931080"
#               },
#               {
#                 "label": "Car Electrical Appliances",
#                 "value": "931208"
#               },
#               {
#                 "label": "Car Audio",
#                 "value": "931336"
#               }
#             ],
#             "label": "Car Electronics",
#             "value": "929928"
#           },
#           {
#             "children": [
#               {
#                 "label": "Sunshades",
#                 "value": "605242"
#               },
#               {
#                 "label": "Side Mirror Folding Kits",
#                 "value": "931464"
#               },
#               {
#                 "label": "Car Covers & Shelters",
#                 "value": "931592"
#               },
#               {
#                 "label": "Car Stickers",
#                 "value": "931720"
#               },
#               {
#                 "label": "Window Tints",
#                 "value": "931848"
#               },
#               {
#                 "label": "Window Films & Solar Protection",
#                 "value": "931976"
#               },
#               {
#                 "label": "Number Plates",
#                 "value": "932104"
#               },
#               {
#                 "label": "Car Tax Disc Holders",
#                 "value": "932232"
#               },
#               {
#                 "label": "Reflective Strips",
#                 "value": "932360"
#               }
#             ],
#             "label": "Car Exterior Accessories",
#             "value": "930056"
#           },
#           {
#             "children": [
#               {
#                 "label": "Stowing & Tidying",
#                 "value": "605213"
#               },
#               {
#                 "label": "Neck Pillows",
#                 "value": "932488"
#               },
#               {
#                 "label": "Car Mats",
#                 "value": "700684"
#               },
#               {
#                 "label": "Interior Stickers",
#                 "value": "932616"
#               },
#               {
#                 "label": "Rear Racks & Accessories",
#                 "value": "932744"
#               },
#               {
#                 "label": "Anti-Slip Mats",
#                 "value": "605219"
#               },
#               {
#                 "label": "Interior Mouldings",
#                 "value": "932872"
#               },
#               {
#                 "label": "Decoration",
#                 "value": "605201"
#               },
#               {
#                 "label": "Car Key Cases",
#                 "value": "933000"
#               },
#               {
#                 "label": "Mounts & Holders",
#                 "value": "605215"
#               },
#               {
#                 "label": "Fasteners & Clips",
#                 "value": "933128"
#               }
#             ],
#             "label": "Car Interior Accessories",
#             "value": "930184"
#           }
#         ],
#         "label": "Automotive & Motorcycle",
#         "value": "605196"
#       },
#       {
#         "children": [
#           {
#             "children": [
#               {
#                 "label": "Lighting Accessories",
#                 "value": "893576"
#               },
#               {
#                 "label": "Bulbs, Tubes & Strips",
#                 "value": "893704"
#               },
#               {
#                 "label": "Indoor Lighting",
#                 "value": "893832"
#               },
#               {
#                 "label": "Portable Lighting",
#                 "value": "893960"
#               },
#               {
#                 "label": "Outdoor Lighting",
#                 "value": "894088"
#               },
#               {
#                 "label": "Novelty Lighting",
#                 "value": "894216"
#               },
#               {
#                 "label": "Professional Lighting",
#                 "value": "894344"
#               },
#               {
#                 "label": "Commercial Lighting",
#                 "value": "894472"
#               }
#             ],
#             "label": "Lights & Lighting",
#             "value": "872456"
#           },
#           {
#             "children": [
#               {
#                 "label": "Connectors & Terminals",
#                 "value": "894600"
#               },
#               {
#                 "label": "Switches & Accessories",
#                 "value": "894728"
#               },
#               {
#                 "label": "Relays & Breakers",
#                 "value": "894856"
#               },
#               {
#                 "label": "Power Supplies",
#                 "value": "894984"
#               },
#               {
#                 "label": "Motors & Generators",
#                 "value": "895112"
#               },
#               {
#                 "label": "Electrical Sockets & Accessories",
#                 "value": "895240"
#               },
#               {
#                 "label": "Wires & Cables ",
#                 "value": "895368"
#               },
#               {
#                 "label": "Transformers",
#                 "value": "895496"
#               }
#             ],
#             "label": "Electrical Equipment & Supplies",
#             "value": "872584"
#           },
#           {
#             "children": [
#               {
#                 "label": "Kitchen Taps",
#                 "value": "895624"
#               },
#               {
#                 "label": "Kitchen Sinks",
#                 "value": "895752"
#               },
#               {
#                 "label": "Kitchen Cabinets",
#                 "value": "895880"
#               },
#               {
#                 "label": "Water Filtration Devices",
#                 "value": "896008"
#               },
#               {
#                 "label": "Kitchen Fixture Accessories",
#                 "value": "896136"
#               },
#               {
#                 "label": "Kitchen Fixture Sets",
#                 "value": "896264"
#               }
#             ],
#             "label": "Kitchen Fixtures",
#             "value": "872712"
#           },
#           {
#             "children": [
#               {
#                 "label": "Smart Home Controls",
#                 "value": "896392"
#               },
#               {
#                 "label": "Temperature Control Systems",
#                 "value": "896520"
#               },
#               {
#                 "label": "Automatic Curtain Control Systems",
#                 "value": "896648"
#               },
#               {
#                 "label": "Smart Motion Sensors",
#                 "value": "896776"
#               }
#             ],
#             "label": "Smart Home Systems",
#             "value": "872840"
#           },
#           {
#             "children": [
#               {
#                 "label": "Heating, Cooling & Ventilation",
#                 "value": "896904"
#               },
#               {
#                 "label": "Doors, Gates & Windows",
#                 "value": "897032"
#               },
#               {
#                 "label": "Wallpaper",
#                 "value": "897160"
#               },
#               {
#                 "label": "Paint Supplies & Tools",
#                 "value": "897288"
#               },
#               {
#                 "label": "Roofing & Flooring",
#                 "value": "897416"
#               },
#               {
#                 "label": "Ladders",
#                 "value": "897544"
#               },
#               {
#                 "label": "Trollies",
#                 "value": "897672"
#               }
#             ],
#             "label": "Building Supplies",
#             "value": "872968"
#           },
#           {
#             "children": [
#               {
#                 "label": "Shower Equipment",
#                 "value": "897800"
#               },
#               {
#                 "label": "Hooks & Bars",
#                 "value": "897928"
#               },
#               {
#                 "label": "Bathroom Sinks",
#                 "value": "898056"
#               },
#               {
#                 "label": "Bathroom Taps",
#                 "value": "898184"
#               },
#               {
#                 "label": "Bidets & Bidet Parts",
#                 "value": "898312"
#               },
#               {
#                 "label": "Toilets & Toilet Parts",
#                 "value": "898440"
#               },
#               {
#                 "label": "Bathroom Mirrors",
#                 "value": "898568"
#               },
#               {
#                 "label": "Bathroom Fixture Accessories",
#                 "value": "898696"
#               },
#               {
#                 "label": "Bathroom Fixture Sets",
#                 "value": "898824"
#               }
#             ],
#             "label": "Bathroom Fixtures",
#             "value": "873096"
#           },
#           {
#             "children": [
#               {
#                 "label": "Security Alarms",
#                 "value": "898952"
#               },
#               {
#                 "label": "Doorbells & Intercoms",
#                 "value": "899080"
#               },
#               {
#                 "label": "Work Safety Equipment",
#                 "value": "899208"
#               },
#               {
#                 "label": "Safes",
#                 "value": "899336"
#               },
#               {
#                 "label": "Emergency Kits",
#                 "value": "899464"
#               }
#             ],
#             "label": "Security & Safety",
#             "value": "873224"
#           },
#           {
#             "children": [
#               {
#                 "label": "Beekeeping Supplies",
#                 "value": "899592"
#               },
#               {
#                 "label": "Plant Care Tools",
#                 "value": "899720"
#               },
#               {
#                 "label": "Pest Control",
#                 "value": "899848"
#               },
#               {
#                 "label": "Garden Decor",
#                 "value": "899976"
#               },
#               {
#                 "label": "Watering & Irrigation",
#                 "value": "900104"
#               },
#               {
#                 "label": "Garden Pots & Planters",
#                 "value": "900232"
#               },
#               {
#                 "label": "Garden Buildings",
#                 "value": "900360"
#               }
#             ],
#             "label": "Garden Supplies",
#             "value": "873352"
#           }
#         ],
#         "label": "Home Improvement",
#         "value": "604968"
#       },
#       {
#         "children": [
#           {
#             "children": [
#               {
#                 "label": "Electric Drills",
#                 "value": "881544"
#               },
#               {
#                 "label": "Electric Screwdrivers",
#                 "value": "881672"
#               },
#               {
#                 "label": "Electric Saws",
#                 "value": "881800"
#               },
#               {
#                 "label": "Blowers",
#                 "value": "881928"
#               },
#               {
#                 "label": "Angle Grinders",
#                 "value": "882056"
#               },
#               {
#                 "label": "Polishers",
#                 "value": "882184"
#               },
#               {
#                 "label": "Electric Wrenches",
#                 "value": "882312"
#               },
#               {
#                 "label": "Nail Guns",
#                 "value": "882440"
#               },
#               {
#                 "label": "Spray Guns",
#                 "value": "882568"
#               },
#               {
#                 "label": "Heat Guns",
#                 "value": "882696"
#               },
#               {
#                 "label": "Glue Guns",
#                 "value": "882824"
#               },
#               {
#                 "label": "Power Tool Accessories",
#                 "value": "882952"
#               },
#               {
#                 "label": "Power Tool Sets",
#                 "value": "883080"
#               }
#             ],
#             "label": "Power Tools",
#             "value": "871560"
#           },
#           {
#             "children": [
#               {
#                 "label": "Industrial Tweezers",
#                 "value": "883208"
#               },
#               {
#                 "label": "Hammers",
#                 "value": "883336"
#               },
#               {
#                 "label": "Knives",
#                 "value": "883464"
#               },
#               {
#                 "label": "Pliers",
#                 "value": "883592"
#               },
#               {
#                 "label": "Saws",
#                 "value": "883720"
#               },
#               {
#                 "label": "Scissors",
#                 "value": "883848"
#               },
#               {
#                 "label": "Screwdrivers",
#                 "value": "883976"
#               },
#               {
#                 "label": "Wrenches",
#                 "value": "884104"
#               },
#               {
#                 "label": "Chisels",
#                 "value": "884232"
#               },
#               {
#                 "label": "Axes",
#                 "value": "884360"
#               },
#               {
#                 "label": "Tool Kits",
#                 "value": "884488"
#               }
#             ],
#             "label": "Hand Tools",
#             "value": "871688"
#           },
#           {
#             "children": [
#               {
#                 "label": "Optical Instruments",
#                 "value": "884616"
#               },
#               {
#                 "label": "Pressure Measuring Instruments",
#                 "value": "884744"
#               },
#               {
#                 "label": "Temperature Measuring Instruments",
#                 "value": "884872"
#               },
#               {
#                 "label": "Hand Measuring Tools",
#                 "value": "885000"
#               },
#               {
#                 "label": "Physical Measuring Instruments",
#                 "value": "885128"
#               },
#               {
#                 "label": "Electrical Measuring Instruments",
#                 "value": "885256"
#               }
#             ],
#             "label": "Measuring Tools",
#             "value": "871816"
#           },
#           {
#             "children": [
#               {
#                 "label": "Grass Trimmers",
#                 "value": "885384"
#               },
#               {
#                 "label": "Leaf Blowers & Vacuums",
#                 "value": "885512"
#               },
#               {
#                 "label": "Spades & Shovels",
#                 "value": "885640"
#               },
#               {
#                 "label": "Pruning Tools",
#                 "value": "885768"
#               },
#               {
#                 "label": "Hoes & Rakes",
#                 "value": "885896"
#               },
#               {
#                 "label": "Forks & Scoops",
#                 "value": "886024"
#               },
#               {
#                 "label": "Gardening Gloves & Protective Gear",
#                 "value": "886152"
#               },
#               {
#                 "label": "Garden Cleaning Tools",
#                 "value": "886280"
#               }
#             ],
#             "label": "Garden Tools",
#             "value": "871944"
#           },
#           {
#             "children": [
#               {
#                 "label": "Electric Soldering Irons",
#                 "value": "886408"
#               },
#               {
#                 "label": "Soldering Stations",
#                 "value": "886536"
#               },
#               {
#                 "label": "Welders",
#                 "value": "886664"
#               },
#               {
#                 "label": "Welding Accessories",
#                 "value": "886792"
#               }
#             ],
#             "label": "Soldering Equipment",
#             "value": "872072"
#           },
#           {
#             "children": [
#               {
#                 "label": "Tool Bags",
#                 "value": "886920"
#               },
#               {
#                 "label": "Tool Cases & Boxes",
#                 "value": "887048"
#               },
#               {
#                 "label": "Tool Racks & Bars",
#                 "value": "887176"
#               }
#             ],
#             "label": "Tool Organizers",
#             "value": "872200"
#           },
#           {
#             "children": [
#               {
#                 "label": "Furniture Hardware",
#                 "value": "887304"
#               },
#               {
#                 "label": "Window Hardware",
#                 "value": "887432"
#               },
#               {
#                 "label": "Door Hardware ",
#                 "value": "887560"
#               },
#               {
#                 "label": "Mechanical Hardware",
#                 "value": "887688"
#               },
#               {
#                 "label": "Fasteners & Hooks",
#                 "value": "887816"
#               },
#               {
#                 "label": "Ropes, Chains & Pulleys",
#                 "value": "887944"
#               },
#               {
#                 "label": "Padlocks & Hasps",
#                 "value": "888072"
#               },
#               {
#                 "label": "Adhesives, Tapes & Sealers",
#                 "value": "888200"
#               },
#               {
#                 "label": "Clamps",
#                 "value": "888328"
#               }
#             ],
#             "label": "Hardware",
#             "value": "872328"
#           }
#         ],
#         "label": "Tools & Hardware",
#         "value": "604579"
#       },
#       {
#         "children": [
#           {
#             "children": [
#               {
#                 "label": "Beer",
#                 "value": "915592"
#               },
#               {
#                 "label": "Wine",
#                 "value": "915720"
#               },
#               {
#                 "label": "Cider",
#                 "value": "915848"
#               },
#               {
#                 "label": "Pre-Mixed & Ready to Drink",
#                 "value": "915976"
#               },
#               {
#                 "label": "Sake, Soju & Umeshu",
#                 "value": "916104"
#               },
#               {
#                 "label": "Sparkling Wine & Champagne",
#                 "value": "916232"
#               },
#               {
#                 "label": "Spirits",
#                 "value": "916360"
#               }
#             ],
#             "label": "Beer, Wine & Spirits",
#             "value": "914696"
#           },
#           {
#             "children": [
#               {
#                 "label": "Tea",
#                 "value": "916488"
#               },
#               {
#                 "label": "Chocolate & Malted Drinks",
#                 "value": "916616"
#               },
#               {
#                 "label": "Coffee",
#                 "value": "700612"
#               },
#               {
#                 "label": "Juice & Smoothies",
#                 "value": "916744"
#               },
#               {
#                 "label": "Fizzy Drinks",
#                 "value": "916872"
#               },
#               {
#                 "label": "Water & Flavored Water",
#                 "value": "917000"
#               },
#               {
#                 "label": "Non-Dairy Milk",
#                 "value": "917128"
#               },
#               {
#                 "label": "Sports & Energy Drinks",
#                 "value": "917256"
#               },
#               {
#                 "label": "Non-Alcoholic Drinks ",
#                 "value": "917384"
#               },
#               {
#                 "label": "Powdered Drink Mixes",
#                 "value": "917512"
#               },
#               {
#                 "label": "Drink Toppings",
#                 "value": "917640"
#               },
#               {
#                 "label": "Syrups & Concentrates",
#                 "value": "917768"
#               }
#             ],
#             "label": "Drinks",
#             "value": "914824"
#           },
#           {
#             "children": [
#               {
#                 "label": "Rice",
#                 "value": "917896"
#               },
#               {
#                 "label": "Pasta & Noodles",
#                 "value": "918024"
#               },
#               {
#                 "label": "Beans & Grains",
#                 "value": "918152"
#               },
#               {
#                 "label": "Canned, Jarred & Packaged Foods",
#                 "value": "918280"
#               },
#               {
#                 "label": "Pickled Vegetables, Pickles & Chutney",
#                 "value": "918408"
#               },
#               {
#                 "label": "Instant Rice & Porridge",
#                 "value": "918536"
#               },
#               {
#                 "label": "Instant Hotpot",
#                 "value": "918664"
#               },
#               {
#                 "label": " Instant Noodles\t",
#                 "value": "700644"
#               },
#               {
#                 "label": "Breakfast Cereal, Granola & Oats",
#                 "value": "918792"
#               }
#             ],
#             "label": "Instant Food",
#             "value": "914952"
#           },
#           {
#             "children": [
#               {
#                 "label": "Oils",
#                 "value": "918920"
#               },
#               {
#                 "label": "Sugar & Sweeteners",
#                 "value": "919048"
#               },
#               {
#                 "label": "Herbs, Spices & Seasonings",
#                 "value": "919176"
#               },
#               {
#                 "label": "Salt",
#                 "value": "919304"
#               },
#               {
#                 "label": "Cooking Sauces",
#                 "value": "919432"
#               },
#               {
#                 "label": "Vinegar ",
#                 "value": "919560"
#               },
#               {
#                 "label": "Cooking Wine",
#                 "value": "919688"
#               },
#               {
#                 "label": "Stock, Gravy & Instant Soup",
#                 "value": "919816"
#               },
#               {
#                 "label": "Cooking Pastes & Seasoning Kits",
#                 "value": "919944"
#               },
#               {
#                 "label": "Flavour Enhancers",
#                 "value": "920072"
#               },
#               {
#                 "label": "Flour",
#                 "value": "920200"
#               },
#               {
#                 "label": "Honey & Maple Syrup",
#                 "value": "920328"
#               },
#               {
#                 "label": "Jams, Dressings & Spreads",
#                 "value": "920456"
#               }
#             ],
#             "label": "Staples & Cooking Essentials",
#             "value": "915080"
#           },
#           {
#             "children": [
#               {
#                 "label": "Food Flavouring & Extracts",
#                 "value": "920584"
#               },
#               {
#                 "label": "Baking Powder & Soda",
#                 "value": "920712"
#               },
#               {
#                 "label": "Baking Mixes",
#                 "value": "920840"
#               },
#               {
#                 "label": "Baking Flours",
#                 "value": "920968"
#               },
#               {
#                 "label": "Food Colouring",
#                 "value": "921096"
#               },
#               {
#                 "label": "Frosting, Icing & Decorations",
#                 "value": "921224"
#               },
#               {
#                 "label": "Creamers",
#                 "value": "921352"
#               },
#               {
#                 "label": "Butter & Margarine",
#                 "value": "921480"
#               },
#               {
#                 "label": "Cheese & Cheese Powder",
#                 "value": "921608"
#               }
#             ],
#             "label": "Baking",
#             "value": "915208"
#           },
#           {
#             "children": [
#               {
#                 "label": "Candy",
#                 "value": "921736"
#               },
#               {
#                 "label": "Chocolate & Chocolate Snacks",
#                 "value": "700768"
#               },
#               {
#                 "label": " Biscuits, Cookies & Wafers\t",
#                 "value": "700553"
#               },
#               {
#                 "label": "Crisps & Puffed Snacks",
#                 "value": "700554"
#               },
#               {
#                 "label": "Seeds",
#                 "value": "921864"
#               },
#               {
#                 "label": "Popcorn",
#                 "value": "921992"
#               },
#               {
#                 "label": "Seaweed",
#                 "value": "922120"
#               },
#               {
#                 "label": "Nuts & Peas",
#                 "value": "922248"
#               },
#               {
#                 "label": "Custard Puddings & Jelly",
#                 "value": "922376"
#               },
#               {
#                 "label": "Dried Snacks",
#                 "value": "922504"
#               },
#               {
#                 "label": "Chewing & Bubble Gum",
#                 "value": "946952"
#               },
#               {
#                 "label": "Bars",
#                 "value": "947080"
#               }
#             ],
#             "label": "Snacks",
#             "value": "915336"
#           },
#           {
#             "children": [
#               {
#                 "label": "Meat",
#                 "value": "922632"
#               },
#               {
#                 "label": "Seafood",
#                 "value": "922760"
#               },
#               {
#                 "label": "Vegetarian Meat Alternatives",
#                 "value": "922888"
#               },
#               {
#                 "label": "Bread",
#                 "value": "923016"
#               },
#               {
#                 "label": "Cakes & Pies",
#                 "value": "923144"
#               },
#               {
#                 "label": "Pastries",
#                 "value": "923272"
#               },
#               {
#                 "label": "Ice Cream",
#                 "value": "923400"
#               },
#               {
#                 "label": "Eggs",
#                 "value": "923528"
#               },
#               {
#                 "label": "Tofu",
#                 "value": "923656"
#               },
#               {
#                 "label": "Vegetables",
#                 "value": "923784"
#               },
#               {
#                 "label": "Fruit",
#                 "value": "923912"
#               },
#               {
#                 "label": "Mushroom",
#                 "value": "924040"
#               },
#               {
#                 "label": "Frozen Food",
#                 "value": "924168"
#               },
#               {
#                 "label": "Processed Meat & Seafood",
#                 "value": "924296"
#               },
#               {
#                 "label": "Meal Kits",
#                 "value": "946824"
#               }
#             ],
#             "label": "Fresh & Frozen Food",
#             "value": "915464"
#           }
#         ],
#         "label": "Food & Beverages",
#         "value": "700437"
#       },
#       {
#         "children": [
#           {
#             "children": [
#               {
#                 "label": "Weight Management",
#                 "value": "700647"
#               },
#               {
#                 "label": "Beauty Supplements",
#                 "value": "700648"
#               },
#               {
#                 "label": "Fitness Supplements",
#                 "value": "700649"
#               },
#               {
#                 "label": "Wellness Supplements",
#                 "value": "700650"
#               }
#             ],
#             "label": "Food Supplement",
#             "value": "700646"
#           },
#           {
#             "children": [
#               {
#                 "label": "Medical Masks",
#                 "value": "924680"
#               },
#               {
#                 "label": "Bathroom Scales",
#                 "value": "924808"
#               },
#               {
#                 "label": "First Aid Supplies",
#                 "value": "924936"
#               },
#               {
#                 "label": "Health Monitors & Tests",
#                 "value": "925064"
#               },
#               {
#                 "label": "Thermometers",
#                 "value": "926216"
#               },
#               {
#                 "label": "Wheelchairs",
#                 "value": "925192"
#               },
#               {
#                 "label": "Braces & Supports",
#                 "value": "925320"
#               },
#               {
#                 "label": "Hearing Aids",
#                 "value": "925448"
#               },
#               {
#                 "label": "PPE Masks",
#                 "value": "947208"
#               },
#               {
#                 "label": "Medication Aids",
#                 "value": "950664"
#               }
#             ],
#             "label": "Medical Supplies",
#             "value": "924424"
#           },
#           {
#             "children": [
#               {
#                 "label": "Condoms",
#                 "value": "925576"
#               },
#               {
#                 "label": "Lubricants",
#                 "value": "925704"
#               },
#               {
#                 "label": "Sex Toys",
#                 "value": "925832"
#               },
#               {
#                 "label": "Performance Enhancers",
#                 "value": "925960"
#               },
#               {
#                 "label": "Sex Furniture",
#                 "value": "926088"
#               }
#             ],
#             "label": "Sexual Wellness",
#             "value": "924552"
#           },
#           {
#             "children": [
#               {
#                 "label": "Pain Relief",
#                 "value": "949512"
#               },
#               {
#                 "label": "Coughs & Colds",
#                 "value": "949640"
#               },
#               {
#                 "label": "Digestion & Nausea",
#                 "value": "949768"
#               },
#               {
#                 "label": "Eczema, Psoriasis and Rosacea Care",
#                 "value": "949896"
#               },
#               {
#                 "label": "Allergies, Sinus & Asthma",
#                 "value": "950024"
#               },
#               {
#                 "label": "Baby & Child Medicine",
#                 "value": "950152"
#               },
#               {
#                 "label": "Scars & Stretchmarks",
#                 "value": "950280"
#               },
#               {
#                 "label": "Antifungals",
#                 "value": "950408"
#               },
#               {
#                 "label": "Cuts & Wounds",
#                 "value": "950536"
#               }
#             ],
#             "label": "OTC Medications & Treatments",
#             "value": "949384"
#           },
#           {
#             "children": [
#               {
#                 "label": "Herbal Medicine",
#                 "value": "950920"
#               },
#               {
#                 "label": "Acupuncture",
#                 "value": "951048"
#               },
#               {
#                 "label": "Essential Oil for Aromatherapy",
#                 "value": "951176"
#               }
#             ],
#             "label": "Alternative Medications & Treatments",
#             "value": "950792"
#           }
#         ],
#         "label": "Health",
#         "value": "700645"
#       },
#       {
#         "children": [
#           {
#             "children": [
#               {
#                 "label": "Psychology & Relationships",
#                 "value": "927496"
#               },
#               {
#                 "label": "Religion & Philosophy",
#                 "value": "927624"
#               },
#               {
#                 "label": "Politics, Law & Social Sciences",
#                 "value": "927752"
#               },
#               {
#                 "label": "Natural Sciences",
#                 "value": "927880"
#               },
#               {
#                 "label": "History & Culture",
#                 "value": "928008"
#               },
#               {
#                 "label": "Career & Self-Help ",
#                 "value": "928136"
#               },
#               {
#                 "label": "Parenting & Family",
#                 "value": "928264"
#               }
#             ],
#             "label": "Humanities & Social Sciences",
#             "value": "927112"
#           },
#           {
#             "children": [
#               {
#                 "label": "Recipes & Cooking",
#                 "value": "928392"
#               },
#               {
#                 "label": "Crafts & DIY",
#                 "value": "928520"
#               },
#               {
#                 "label": "Health, Fitness & Dieting",
#                 "value": "928648"
#               },
#               {
#                 "label": "Cookbooks, Food & Wine",
#                 "value": "928776"
#               },
#               {
#                 "label": "Medical",
#                 "value": "928904"
#               }
#             ],
#             "label": "Lifestyle & Health",
#             "value": "927240"
#           },
#           {
#             "children": [
#               {
#                 "label": "Travel & Maps",
#                 "value": "929032"
#               },
#               {
#                 "label": "Language & Dictionaries",
#                 "value": "929160"
#               },
#               {
#                 "label": "Comics & Manga",
#                 "value": "929288"
#               },
#               {
#                 "label": "Horoscopes",
#                 "value": "929416"
#               },
#               {
#                 "label": "Computers & Networking",
#                 "value": "929544"
#               }
#             ],
#             "label": "Hobbies & Skills",
#             "value": "927368"
#           }
#         ],
#         "label": "Books, Magazines & Audio",
#         "value": "801928"
#       },
#       {
#         "children": [
#           {
#             "children": [
#               {
#                 "label": "Tables & Desks",
#                 "value": "875912"
#               },
#               {
#                 "label": "Chairs",
#                 "value": "876040"
#               },
#               {
#                 "label": "Stools & Benches",
#                 "value": "876168"
#               },
#               {
#                 "label": "Beds",
#                 "value": "876296"
#               },
#               {
#                 "label": "Mattresses",
#                 "value": "876424"
#               },
#               {
#                 "label": "Sofas\t",
#                 "value": "604468"
#               },
#               {
#                 "label": "Cupboards & Cabinets",
#                 "value": "876680"
#               },
#               {
#                 "label": "Shelves & Racks",
#                 "value": "604497"
#               },
#               {
#                 "label": "Wardrobes",
#                 "value": "876936"
#               },
#               {
#                 "label": "Indoor Furniture Sets",
#                 "value": "877064"
#               },
#               {
#                 "label": "TV Stands & Bedside Tables",
#                 "value": "877192"
#               }
#             ],
#             "label": "Indoor Furniture",
#             "value": "871048"
#           },
#           {
#             "children": [
#               {
#                 "label": "Outdoor Sofas",
#                 "value": "877448"
#               },
#               {
#                 "label": "Outdoor Chairs",
#                 "value": "877704"
#               },
#               {
#                 "label": "Patio Umbrellas ",
#                 "value": "877960"
#               },
#               {
#                 "label": "Patio Swings",
#                 "value": "878088"
#               },
#               {
#                 "label": "Outdoor Furniture Sets",
#                 "value": "878344"
#               },
#               {
#                 "label": "Outdoor Tables",
#                 "value": "878472"
#               },
#               {
#                 "label": "Stools & Benches",
#                 "value": "878728"
#               },
#               {
#                 "label": "Outdoor Shelves",
#                 "value": "878856"
#               }
#             ],
#             "label": "Outdoor Furniture",
#             "value": "871176"
#           },
#           {
#             "children": [
#               {
#                 "label": "Beds",
#                 "value": "879240"
#               },
#               {
#                 "label": "Sofas",
#                 "value": "879368"
#               },
#               {
#                 "label": "Chairs",
#                 "value": "879624"
#               },
#               {
#                 "label": "Stools & Benches",
#                 "value": "879752"
#               },
#               {
#                 "label": "Cabinets",
#                 "value": "879880"
#               },
#               {
#                 "label": "Furniture Sets",
#                 "value": "880136"
#               },
#               {
#                 "label": "Tables & Desks",
#                 "value": "880264"
#               },
#               {
#                 "label": "Wardrobes",
#                 "value": "880392"
#               },
#               {
#                 "label": "Bedside Tables",
#                 "value": "880520"
#               },
#               {
#                 "label": "Mattresses",
#                 "value": "880648"
#               },
#               {
#                 "label": "Shelves & Racks",
#                 "value": "933512"
#               }
#             ],
#             "label": "Children's Furniture",
#             "value": "871304"
#           },
#           {
#             "children": [
#               {
#                 "label": "Salon Furniture",
#                 "value": "880904"
#               },
#               {
#                 "label": "Hotel Furniture",
#                 "value": "881032"
#               },
#               {
#                 "label": "School Furniture",
#                 "value": "881160"
#               },
#               {
#                 "label": "Restaurant Furniture",
#                 "value": "881288"
#               },
#               {
#                 "label": "Office Furniture",
#                 "value": "881416"
#               }
#             ],
#             "label": "Commercial Furniture",
#             "value": "871432"
#           }
#         ],
#         "label": "Furniture",
#         "value": "604453"
#       },
#       {
#         "label": "Virtual Products",
#         "value": "834312"
#       }
#     ]
#   },
#   "message": null,
#   "cached": true,
#   "code": null
# }


r = s.post(
    "https://www.kalodata.com/api/configurations",
    headers={"content-length": "1855"},
    json=[
        {"key": "video.filter.revenue"},
        {"key": "video.filter.video_type"},
        {"key": "video.filter.creator_followers"},
        {"key": "video.filter.views"},
        {"key": "video.filter.duration"},
        {"key": "video.filter.publish_date"},
        {"key": "video.filter.engagement_rate"},
        {"key": "video.filter.ad.cost"},
        {"key": "video.filter.ad.roas"},
        {"key": "video.filter.ad.view_ratio"},
        {"key": "video.filter.ad.creator_debut"},
        {"key": "video.filter.ad.revenue_ratio"},
        {"key": "livestream.filter.revenue"},
        {"key": "livestream.filter.live_type"},
        {"key": "livestream.filter.creator_followers"},
        {"key": "livestream.filter.unit_price"},
        {"key": "livestream.filter.time_range"},
        {"key": "livestream.filter.live_recorded"},
        {"key": "product.filter.revenue"},
        {"key": "product.filter.affiliate_type"},
        {"key": "product.filter.unit_price"},
        {"key": "product.filter.creator"},
        {"key": "product.filter.sales_channel"},
        {"key": "product.filter.creator_conversion_ratio"},
        {"key": "product.filter.launch_date"},
        {"key": "product.filter.commission_rate"},
        {"key": "creator.filter.revenue"},
        {"key": "creator.filter.creator_type"},
        {"key": "creator.filter.content_type"},
        {"key": "creator.filter.avg_promote_video_views"},
        {"key": "creator.filter.followers"},
        {"key": "creator.filter.avg_normal_video_views"},
        {"key": "creator.filter.engagement_rate"},
        {"key": "creator.filter.creator_content"},
        {"key": "creator.filter.mcn_status"},
        {"key": "creator.filter.ad.creator_debut"},
        {"key": "seller.filter.revenue"},
        {"key": "seller.filter.unit_price"},
        {"key": "seller.filter.seller_type"},
        {"key": "seller.filter.operation_mode"},
        {"key": "global.filter.revenue"},
        {"key": "global.filter.revenue_growth"},
        {"key": "global.filter.average_revenue"},
        {"key": "global.filter.top3_revenue"},
        {"key": "global.filter.top10_revenue"},
        {"key": "global.filter.category_level"},
        {"key": "global.filter.revenue_trend"},
        {"key": "global.filter.is_full_service"},
        {"key": "global.filter.delivery_type"},
    ],
)
# {
#   "success": true,
#   "data": {
#     "global.filter.is_full_service": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "1",
#         "label": "Yes"
#       },
#       {
#         "value": "0",
#         "label": "No"
#       }
#     ],
#     "product.filter.launch_date": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<3",
#         "label": "Within 3 Days"
#       },
#       {
#         "value": "<7",
#         "label": "Within 7 Days"
#       },
#       {
#         "value": "<30",
#         "label": "Within 30 Days"
#       }
#     ],
#     "creator.filter.avg_promote_video_views": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<10K",
#         "label": "<10K"
#       },
#       {
#         "value": "10K-50K",
#         "label": "10K-50K"
#       },
#       {
#         "value": "200K-1M",
#         "label": "200K-1M"
#       }
#     ],
#     "video.filter.engagement_rate": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "LOW",
#         "label": "Low"
#       },
#       {
#         "value": "MEDIUM",
#         "label": "Medium"
#       },
#       {
#         "value": "HIGH",
#         "label": "High"
#       }
#     ],
#     "creator.filter.mcn_status": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "membershipkey": "CREATOR.MCN_SIGN",
#         "label": "Signed",
#         "value": "SIGNED",
#         "enable": {
#           "grade": 2
#         }
#       },
#       {
#         "label": "Not Signed",
#         "value": "NOT_SIGNED",
#         "enable": {
#           "grade": 2
#         }
#       }
#     ],
#     "video.filter.publish_date": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "-1",
#         "label": "Yesterday"
#       },
#       {
#         "value": "-3",
#         "label": "Within 3 days"
#       },
#       {
#         "value": "-7",
#         "label": "Within 7 days"
#       }
#     ],
#     "seller.filter.unit_price": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<5",
#         "label": "<5"
#       },
#       {
#         "value": "5-20",
#         "label": "5-20"
#       },
#       {
#         "value": "20-100",
#         "label": "20-100"
#       },
#       {
#         "value": ">100",
#         "label": ">100"
#       }
#     ],
#     "livestream.filter.time_range": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "00:00-08:00",
#         "label": "00:00-08:00"
#       },
#       {
#         "value": "08:00-16:00",
#         "label": "08:00-16:00"
#       },
#       {
#         "value": "16:00-24:00",
#         "label": "16:00-24:00"
#       }
#     ],
#     "global.filter.revenue_trend": [
#       {
#         "value": "",
#         "label": "Default"
#       },
#       {
#         "label": "Growing",
#         "value": "GROWING",
#         "tips": {
#           "shopTip": "Filter out shops that are still experiencing revenue growth within the target time range, helping you quickly find potential trending shops.",
#           "videoTip": "Filter out videos that are still experiencing revenue growth within the target time range, helping you quickly find potential trending videos.",
#           "creatorTip": "Filter out creators that are still experiencing revenue growth within the target time range, helping you quickly find potential trending creators.",
#           "productTip": "Filter out products that are still experiencing revenue growth within the target time range, helping you quickly find potential trending products."
#         }
#       }
#     ],
#     "video.filter.ad.view_ratio": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<0",
#         "label": "No-ad"
#       },
#       {
#         "value": "0-25",
#         "label": "0-25"
#       },
#       {
#         "value": "25-50",
#         "label": "25-50"
#       },
#       {
#         "value": "51-75",
#         "label": "51-75"
#       },
#       {
#         "value": ">75",
#         "label": ">75"
#       }
#     ],
#     "creator.filter.creator_content": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "website": "https://web.whatsapp.com/",
#         "label": "WhatsApp",
#         "value": "WHATSAPP",
#         "key": "whatsapp",
#         "enable": {
#           "grade": 2
#         }
#       },
#       {
#         "link": "mailto: {}",
#         "label": "Email",
#         "value": "EMAIL",
#         "key": "email",
#         "enable": {
#           "grade": 2
#         }
#       },
#       {
#         "website": "https://www.facebook.com/",
#         "label": "Facebook",
#         "value": "FACEBOOK",
#         "key": "facebook",
#         "enable": {
#           "grade": 2
#         }
#       },
#       {
#         "website": "https://www.instagram.com/",
#         "enable": {
#           "grade": 2
#         },
#         "link": "https://www.instagram.com/{}/",
#         "label": "Instagram",
#         "value": "INSTAGRAM",
#         "key": "ins_id"
#       },
#       {
#         "website": "https://www.youtube.com/",
#         "enable": {
#           "grade": 2
#         },
#         "link": "https://www.youtube.com/channel/{}",
#         "label": "YouTube",
#         "value": "YOUTUBE",
#         "key": "youtube_channel_id"
#       },
#       {
#         "website": "https://twitter.com/",
#         "enable": {
#           "grade": 2
#         },
#         "link": "https://twitter.com/{}",
#         "label": "Twitter",
#         "value": "TWITTER",
#         "key": "twitter_name"
#       }
#     ],
#     "global.filter.delivery_type": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "local",
#         "label": "Ship From Local"
#       },
#       {
#         "value": "global",
#         "label": "Ship From Oversea"
#       }
#     ],
#     "product.filter.affiliate_type": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "PUBLIC_PLAN",
#         "label": "Yes"
#       },
#       {
#         "value": "NON_AFFILIATE",
#         "label": "No"
#       }
#     ],
#     "video.filter.ad.roas": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<1",
#         "label": "<1"
#       },
#       {
#         "value": "1-2.5",
#         "label": "1-2.5"
#       },
#       {
#         "value": "2.5-5",
#         "label": "2.5-5"
#       },
#       {
#         "value": ">5",
#         "label": ">5"
#       }
#     ],
#     "creator.filter.revenue": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<100",
#         "label": "<100"
#       },
#       {
#         "value": "100-1000",
#         "label": "100-1000"
#       },
#       {
#         "value": "1000-10000",
#         "label": "1000-10000"
#       },
#       {
#         "value": ">10000",
#         "label": ">10000"
#       }
#     ],
#     "video.filter.creator_followers": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<50000",
#         "label": "<50000"
#       },
#       {
#         "value": "50000-500000",
#         "label": "50000-500000"
#       },
#       {
#         "value": "500000-1000000",
#         "label": "500000-1000000"
#       },
#       {
#         "value": ">1000000",
#         "label": ">1000000"
#       }
#     ],
#     "video.filter.revenue": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<100",
#         "label": "<100"
#       },
#       {
#         "value": "100-1000",
#         "label": "100-1000"
#       },
#       {
#         "value": "1000-10000",
#         "label": "1000-10000"
#       },
#       {
#         "value": ">10000",
#         "label": ">10000"
#       }
#     ],
#     "product.filter.creator": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<10",
#         "label": "<10"
#       },
#       {
#         "value": "10-50",
#         "label": "10-50"
#       },
#       {
#         "value": "50-200",
#         "label": "50-200"
#       },
#       {
#         "value": ">200",
#         "label": ">200"
#       }
#     ],
#     "livestream.filter.live_recorded": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "tip": "Long recordings, refer to recordings with a duration exceeding 30 minutes.",
#         "label": "Long Record",
#         "value": "FULL_RECORDED"
#       },
#       {
#         "tip": "Snippets refer to recordings with a duration of 1-2 minutes.",
#         "label": "Long Record & Snippet",
#         "value": "ALL_RECORDED"
#       }
#     ],
#     "livestream.filter.revenue": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<100",
#         "label": "<100"
#       },
#       {
#         "value": "100-1000",
#         "label": "100-1000"
#       },
#       {
#         "value": "1000-10000",
#         "label": "1000-10000"
#       },
#       {
#         "value": ">10000",
#         "label": ">10000"
#       }
#     ],
#     "creator.filter.avg_normal_video_views": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<1",
#         "label": "<1"
#       },
#       {
#         "value": "1-10",
#         "label": "1-10"
#       },
#       {
#         "value": "10-20",
#         "label": "10-20"
#       }
#     ],
#     "video.filter.views": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<10000",
#         "label": "<10000"
#       },
#       {
#         "value": "10000-100000",
#         "label": "10000-100000"
#       },
#       {
#         "value": "100000-1000000",
#         "label": "100000-1000000"
#       },
#       {
#         "value": ">1000000",
#         "label": ">1000000"
#       }
#     ],
#     "video.filter.ad.cost": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<100",
#         "label": "<100"
#       },
#       {
#         "value": "100-1000",
#         "label": "100-1000"
#       },
#       {
#         "value": "1000-10000",
#         "label": "1000-10000"
#       },
#       {
#         "value": ">10000",
#         "label": ">10000"
#       }
#     ],
#     "creator.filter.ad.creator_debut": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "label": "Within 3 Days",
#         "value": "<4",
#         "enable": {
#           "grade": 2
#         }
#       },
#       {
#         "label": "Within 7 Days",
#         "value": "<8",
#         "enable": {
#           "grade": 2
#         }
#       },
#       {
#         "label": "Within 30 Days",
#         "value": "<31",
#         "enable": {
#           "grade": 2
#         }
#       },
#       {
#         "label": "Not Within 30 Days",
#         "value": ">30",
#         "enable": {
#           "grade": 2
#         }
#       }
#     ],
#     "video.filter.ad.creator_debut": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<4",
#         "label": "Within 3 Days"
#       },
#       {
#         "value": "<8",
#         "label": "Within 7 Days"
#       },
#       {
#         "value": "<31",
#         "label": "Within 30 Days"
#       },
#       {
#         "value": ">30",
#         "label": "Not Within 30 Days"
#       }
#     ],
#     "global.filter.revenue_growth": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": ">0",
#         "label": ">0"
#       },
#       {
#         "value": ">30",
#         "label": ">30"
#       },
#       {
#         "value": ">70",
#         "label": ">70"
#       },
#       {
#         "value": ">100",
#         "label": ">100"
#       }
#     ],
#     "creator.filter.engagement_rate": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "LOW",
#         "label": "Low"
#       },
#       {
#         "value": "MEDIUM",
#         "label": "Medium"
#       },
#       {
#         "value": "HIGH",
#         "label": "High"
#       }
#     ],
#     "seller.filter.seller_type": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "BRAND",
#         "label": "Brand"
#       },
#       {
#         "value": "RETAILER",
#         "label": "Retailer"
#       }
#     ],
#     "livestream.filter.creator_followers": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<50000",
#         "label": "<50000"
#       },
#       {
#         "value": "50000-500000",
#         "label": "50000-500000"
#       },
#       {
#         "value": "500000-1000000",
#         "label": "500000-1000000"
#       },
#       {
#         "value": ">1000000",
#         "label": ">1000000"
#       }
#     ],
#     "creator.filter.followers": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<50000",
#         "label": "<50000"
#       },
#       {
#         "value": "50000-500000",
#         "label": "50000-500000"
#       },
#       {
#         "value": "500000-1000000",
#         "label": "500000-1000000"
#       },
#       {
#         "value": ">1000000",
#         "label": ">1000000"
#       }
#     ],
#     "product.filter.unit_price": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<5",
#         "label": "<5"
#       },
#       {
#         "value": "5-20",
#         "label": "5-20"
#       },
#       {
#         "value": "20-100",
#         "label": "20-100"
#       },
#       {
#         "value": ">100",
#         "label": ">100"
#       }
#     ],
#     "video.filter.duration": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<15",
#         "label": "<15"
#       },
#       {
#         "value": "15-30",
#         "label": "15-30"
#       },
#       {
#         "value": "30-60",
#         "label": "30-60"
#       },
#       {
#         "value": ">60",
#         "label": ">60"
#       }
#     ],
#     "product.filter.creator_conversion_ratio": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<20",
#         "label": "<20"
#       },
#       {
#         "value": "20-45",
#         "label": "20-45"
#       },
#       {
#         "value": "45-75",
#         "label": "45-75"
#       },
#       {
#         "value": ">75",
#         "label": "75-100"
#       }
#     ],
#     "global.filter.revenue": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<100",
#         "label": "<100"
#       },
#       {
#         "value": "100-1000",
#         "label": "100-1000"
#       },
#       {
#         "value": "1000-10000",
#         "label": "1000-10000"
#       },
#       {
#         "value": ">10000",
#         "label": ">10000"
#       }
#     ],
#     "global.filter.category_level": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "1",
#         "label": "L1"
#       },
#       {
#         "value": "2",
#         "label": "L2"
#       },
#       {
#         "memberFeature": "OVERVIEW.LEVEL_THIRD",
#         "label": "L3",
#         "value": "3"
#       }
#     ],
#     "video.filter.ad.revenue_ratio": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<0",
#         "label": "No-ad"
#       },
#       {
#         "value": "0-25",
#         "label": "0-25"
#       },
#       {
#         "value": "25-50",
#         "label": "25-50"
#       },
#       {
#         "value": "51-75",
#         "label": "51-75"
#       },
#       {
#         "value": ">75",
#         "label": ">75"
#       }
#     ],
#     "global.filter.average_revenue": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<100",
#         "label": "<100"
#       },
#       {
#         "value": "100-500",
#         "label": "100-500"
#       },
#       {
#         "value": "500-1500",
#         "label": "500-1500"
#       },
#       {
#         "value": ">1500",
#         "label": ">1500"
#       }
#     ],
#     "product.filter.commission_rate": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<10",
#         "label": "<10%"
#       },
#       {
#         "value": "10-15",
#         "label": "10%-15%"
#       },
#       {
#         "value": "15-35",
#         "label": "15%-20%"
#       },
#       {
#         "value": "20-30",
#         "label": "20%-30%"
#       },
#       {
#         "value": ">=30",
#         "label": "\u226530%"
#       }
#     ],
#     "global.filter.top3_revenue": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<50",
#         "label": "<50"
#       },
#       {
#         "value": "<80",
#         "label": "<80"
#       }
#     ],
#     "product.filter.revenue": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<100",
#         "label": "<100"
#       },
#       {
#         "value": "100-1000",
#         "label": "100-1000"
#       },
#       {
#         "value": "1000-10000",
#         "label": "1000-10000"
#       },
#       {
#         "value": ">10000",
#         "label": ">10000"
#       }
#     ],
#     "livestream.filter.live_type": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "SINGLE_SHOP",
#         "label": "Single Shop"
#       },
#       {
#         "value": "MULTI_SHOPS",
#         "label": "Multiple Shops"
#       }
#     ],
#     "creator.filter.content_type": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "VIDEO",
#         "label": "Video"
#       },
#       {
#         "value": "LIVE",
#         "label": "Live"
#       }
#     ],
#     "livestream.filter.unit_price": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<5",
#         "label": "<5"
#       },
#       {
#         "value": "5-20",
#         "label": "5-20"
#       },
#       {
#         "value": "20-100",
#         "label": "20-100"
#       },
#       {
#         "value": ">100",
#         "label": ">100"
#       }
#     ],
#     "creator.filter.creator_type": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "BELONGED_TO_SELLER",
#         "label": "Seller Operated"
#       },
#       {
#         "value": "INDEPENDENT",
#         "label": "Independent"
#       }
#     ],
#     "product.filter.sales_channel": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "LIVE",
#         "label": "Live"
#       },
#       {
#         "value": "VIDEO",
#         "label": "Video"
#       },
#       {
#         "tip": "Sales in the shopping mall, no creators involved.",
#         "label": "Shopping Mall",
#         "value": "SHOWCASE"
#       }
#     ],
#     "video.filter.video_type": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "ECOMMERCE",
#         "label": "Product attached"
#       },
#       {
#         "value": "SELLER_RECOMMEND",
#         "label": "Pure promotional"
#       },
#       {
#         "value": "others",
#         "label": "Others"
#       }
#     ],
#     "seller.filter.operation_mode": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "tip": "Official shop and creators whose most sales come from this shop.",
#         "label": "Self-Operated Accounts",
#         "value": "SELF_ACCOUNTS"
#       },
#       {
#         "tip": "Sales generated by affiliate creators.",
#         "label": "Affiliate",
#         "value": "AFFILIATE"
#       },
#       {
#         "tip": "Sales in the shopping mall, no creators involved.",
#         "label": "Shopping Mall",
#         "value": "SHOPPING_MALL"
#       }
#     ],
#     "seller.filter.revenue": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<100",
#         "label": "<100"
#       },
#       {
#         "value": "100-1000",
#         "label": "100-1000"
#       },
#       {
#         "value": "1000-10000",
#         "label": "1000-10000"
#       },
#       {
#         "value": ">10000",
#         "label": ">10000"
#       }
#     ],
#     "global.filter.top10_revenue": [
#       {
#         "value": "",
#         "label": "All"
#       },
#       {
#         "value": "<50",
#         "label": "<50"
#       },
#       {
#         "value": "<80",
#         "label": "<80"
#       }
#     ]
#   },
#   "message": null,
#   "cached": true,
#   "code": null
# }


r = s.post(
    "https://www.kalodata.com/homepage/dialog/queryList",
    headers={"content-length": "0", "content-type": None},
)
# {
#   "success": true,
#   "data": [
#     {
#       "id": 84,
#       "title": null,
#       "online": true,
#       "type": "template3",
#       "order": 1,
#       "action": "NAVIGATE",
#       "btnText": "Buy Now!",
#       "action_link": "/pricing",
#       "desc": "We've reached 1 million users, thanks to your support! \ud83c\udf89 ",
#       "desc2": "Celebrate with 20% off all plans \u2014 this November only!",
#       "image": null,
#       "image2": null,
#       "phoneCountryCode": null,
#       "bannerImage": "https://d149xzut2sq6e3.cloudfront.net/upload/d4260397.jpg",
#       "btnColor": null,
#       "countryCode": "US",
#       "membership": null,
#       "bizCountryGroup": "united states",
#       "startTime": "2024-11-01T04:00:00.000Z",
#       "endTime": "2024-12-01T07:00:00.000Z"
#     }
#   ],
#   "message": null,
#   "cached": null,
#   "code": null
# }


r = s.post(
    "https://www.kalodata.com/user/queryMembership",
    headers={"content-length": "16"},
    json={"country": "US"},
)
# {
#   "success": true,
#   "data": {
#     "id": null,
#     "userId": 928990,
#     "country": "United States",
#     "countryCode": null,
#     "level": "trial",
#     "start": null,
#     "end": null,
#     "startDate": null,
#     "endDate": null,
#     "day": 6,
#     "expired": false,
#     "type": null,
#     "regionType": null,
#     "gmtCreated": null,
#     "createTime": null,
#     "grade": 0
#   },
#   "message": null,
#   "cached": null,
#   "code": null
# }


r = s.get(
    "https://www.kalodata.com/v1/countryV1/contacts",
    params={"type": "pc"},
    headers={"origin": None, "content-type": None},
)
# {
#   "success": true,
#   "data": {
#     "im": null,
#     "medias": [
#       {
#         "name": "TikTok",
#         "qrcode": null,
#         "desc": null,
#         "link": "https://www.tiktok.com/@kalodata_us",
#         "title": null,
#         "linkText": null,
#         "schemeUrl": "https://www.tiktok.com/@kalodata_us"
#       },
#       {
#         "name": "Facebook",
#         "qrcode": null,
#         "desc": null,
#         "link": "https://www.facebook.com/kalodata.tt",
#         "title": null,
#         "linkText": null,
#         "schemeUrl": "https://www.facebook.com/kalodata.tt"
#       },
#       {
#         "name": "Twitter",
#         "qrcode": null,
#         "desc": null,
#         "link": "https://twitter.com/kalodata",
#         "title": null,
#         "linkText": null,
#         "schemeUrl": "twitter://user?screen_name=kalodata"
#       }
#     ],
#     "community": {
#       "name": "Discord",
#       "qrcode": "https://d149xzut2sq6e3.cloudfront.net/upload/1c56586b.jpeg",
#       "desc": null,
#       "link": "https://discord.gg/bbFFS86BCA",
#       "title": null,
#       "linkText": null,
#       "schemeUrl": "discord://discord.gg/bbFFS86BCA"
#     },
#     "communityMap": {
#       "default": {
#         "default": {
#           "name": "Discord",
#           "qrcode": "https://d149xzut2sq6e3.cloudfront.net/upload/1c56586b.jpeg",
#           "desc": null,
#           "link": "https://discord.gg/bbFFS86BCA",
#           "title": null,
#           "linkText": null,
#           "schemeUrl": "discord://discord.gg/bbFFS86BCA"
#         }
#       }
#     },
#     "email": "kalodata_us@kalowave.com",
#     "country": [
#       "united states"
#     ],
#     "language": [
#       "en-US"
#     ]
#   },
#   "message": null,
#   "cached": null,
#   "code": null
# }


r = s.post(
    "https://www.kalodata.com/user/features",
    headers={"content-length": "700"},
    json={
        "country": "US",
        "list": [
            "OVERVIEW.POTENTIAL_LIST",
            "OVERVIEW.DETAIL",
            "OVERVIEW.LEVEL_THIRD",
            "OVERVIEW.DATA_RANGE",
            "VIDEO.LIST",
            "VIDEO.DETAIL",
            "LIVESTREAM.LIST",
            "LIVESTREAM.DETAIL",
            "PRODUCT.LIST",
            "PRODUCT.DETAIL",
            "CREATOR.LIST",
            "DATA.EXPORT",
            "CREATOR.DETAIL",
            "CREATOR.MCN_SIGN",
            "CREATOR.CONTACT",
            "CREATOR.COLLABORATED_SHOP",
            "FORYOU.TABLELIST",
            "FORYOU.COLLABORATED_SHOP",
            "FORYOU.HOT",
            "FORYOU.FOCUSCOUNT",
            "SHOP.LIST",
            "SHOP.DETAIL",
            "DOWNLOAD.VIDEO",
            "FILTER.CUSTOM_RANGE",
            "LIST.DATE_RANGE",
            "DETAIL.DATE_RANGE",
            "LIST.DATE_SPACING",
            "DETAIL.DATE_SPACING",
            "LIVESTREAM.FULL_RECORD",
            "LIST.CATE_CASCADER_LIST",
            "FILTER.CUSTOM_TIMES",
            "AD.ANALYSIS",
            "AD.CREATOR_DEBUT",
            "DETAIL.ACCESS_TIMES",
            "CUSTOMIZED.DATA.EXPORT",
        ],
    },
)
# {
#   "success": true,
#   "data": {
#     "FORYOU.HOT": {
#       "key": "FORYOU.HOT",
#       "type": "LIST",
#       "enable": null,
#       "count": -1,
#       "guidance": {
#         "actionType": {
#           "name": "Upgrade",
#           "desc": "Upgrade to view more data"
#         },
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Upgrade to view more data",
#         "cause": null
#       },
#       "progress": null
#     },
#     "FORYOU.COLLABORATED_SHOP": {
#       "key": "FORYOU.COLLABORATED_SHOP",
#       "type": "MODULE",
#       "enable": null,
#       "count": 0,
#       "guidance": {
#         "actionType": {
#           "name": "Upgrade",
#           "desc": "Upgrade to view more data"
#         },
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Upgrade to view more data",
#         "cause": null
#       },
#       "progress": null
#     },
#     "FORYOU.FOCUSCOUNT": {
#       "key": "FORYOU.FOCUSCOUNT",
#       "type": "ASSETS",
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
#         "message": "Member Trial has Expired",
#         "cause": null
#       },
#       "progress": {
#         "total": 10,
#         "used": 0,
#         "remain": 10,
#         "full": false
#       }
#     },
#     "LIVESTREAM.LIST": {
#       "key": "LIVESTREAM.LIST",
#       "type": "LIST",
#       "enable": null,
#       "count": 500,
#       "guidance": {
#         "actionType": {
#           "name": "Upgrade",
#           "desc": "Upgrade to view more data"
#         },
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Upgrade to view more data",
#         "cause": null
#       },
#       "progress": null
#     },
#     "DETAIL.DATE_SPACING": {
#       "key": "DETAIL.DATE_SPACING",
#       "type": "LIST",
#       "enable": null,
#       "count": 0,
#       "guidance": {
#         "actionType": null,
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Query exceeds span",
#         "cause": null
#       },
#       "progress": null
#     },
#     "DETAIL.DATE_RANGE": {
#       "key": "DETAIL.DATE_RANGE",
#       "type": "LIST",
#       "enable": null,
#       "count": 30,
#       "guidance": {
#         "actionType": null,
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Query out of time range",
#         "cause": null
#       },
#       "progress": null
#     },
#     "CREATOR.COLLABORATED_SHOP": {
#       "key": "CREATOR.COLLABORATED_SHOP",
#       "type": "MODULE",
#       "enable": null,
#       "count": 0,
#       "guidance": {
#         "actionType": {
#           "name": "Upgrade",
#           "desc": "Upgrade to view more data"
#         },
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Upgrade to view more data",
#         "cause": null
#       },
#       "progress": null
#     },
#     "LIST.DATE_RANGE": {
#       "key": "LIST.DATE_RANGE",
#       "type": "LIST",
#       "enable": null,
#       "count": 30,
#       "guidance": {
#         "actionType": null,
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Query out of time range",
#         "cause": null
#       },
#       "progress": null
#     },
#     "FILTER.CUSTOM_TIMES": {
#       "key": "FILTER.CUSTOM_TIMES",
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
#         "message": "Today's query times has been used up",
#         "cause": null
#       },
#       "progress": {
#         "total": 10,
#         "used": 2,
#         "remain": 8,
#         "full": false
#       }
#     },
#     "AD.CREATOR_DEBUT": {
#       "key": "AD.CREATOR_DEBUT",
#       "type": "MODULE",
#       "enable": null,
#       "count": 0,
#       "guidance": {
#         "actionType": {
#           "name": "Upgrade",
#           "desc": "Upgrade to view more data"
#         },
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Upgrade to view more data",
#         "cause": null
#       },
#       "progress": null
#     },
#     "OVERVIEW.DATA_RANGE": {
#       "key": "OVERVIEW.DATA_RANGE",
#       "type": "LIST",
#       "enable": null,
#       "count": 30,
#       "guidance": {
#         "actionType": {
#           "name": "Upgrade",
#           "desc": "Upgrade to view more data"
#         },
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Upgrade to view more data",
#         "cause": null
#       },
#       "progress": null
#     },
#     "LIST.DATE_SPACING": {
#       "key": "LIST.DATE_SPACING",
#       "type": "LIST",
#       "enable": null,
#       "count": 31,
#       "guidance": {
#         "actionType": null,
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Query exceeds span",
#         "cause": null
#       },
#       "progress": null
#     },
#     "FORYOU.TABLELIST": {
#       "key": "FORYOU.TABLELIST",
#       "type": "LIST",
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
#         "message": "Upgrade to view more data",
#         "cause": null
#       },
#       "progress": null
#     },
#     "SHOP.LIST": {
#       "key": "SHOP.LIST",
#       "type": "LIST",
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
#         "message": "Upgrade to view more data",
#         "cause": null
#       },
#       "progress": null
#     },
#     "LIVESTREAM.DETAIL": {
#       "key": "LIVESTREAM.DETAIL",
#       "type": "MODULE",
#       "enable": null,
#       "count": 1,
#       "guidance": {
#         "actionType": {
#           "name": "Upgrade",
#           "desc": "Upgrade to view more data"
#         },
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Upgrade to view more data",
#         "cause": null
#       },
#       "progress": null
#     },
#     "DATA.EXPORT": {
#       "key": "DATA.EXPORT",
#       "type": "BENEFIT",
#       "enable": null,
#       "count": 0,
#       "guidance": {
#         "actionType": {
#           "name": "Upgrade",
#           "desc": "Upgrade to view more data"
#         },
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Member Trial has Expired",
#         "cause": null
#       },
#       "progress": {
#         "total": 0,
#         "used": 0,
#         "remain": 0,
#         "full": true
#       }
#     },
#     "VIDEO.LIST": {
#       "key": "VIDEO.LIST",
#       "type": "LIST",
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
#         "message": "Upgrade to view more data",
#         "cause": null
#       },
#       "progress": null
#     },
#     "CREATOR.DETAIL": {
#       "key": "CREATOR.DETAIL",
#       "type": "MODULE",
#       "enable": null,
#       "count": 1,
#       "guidance": {
#         "actionType": {
#           "name": "Upgrade",
#           "desc": "Upgrade to view more data"
#         },
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Upgrade to view more data",
#         "cause": null
#       },
#       "progress": null
#     },
#     "CREATOR.CONTACT": {
#       "key": "CREATOR.CONTACT",
#       "type": "MODULE",
#       "enable": null,
#       "count": 0,
#       "guidance": {
#         "actionType": {
#           "name": "Upgrade",
#           "desc": "Upgrade to view more data"
#         },
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Upgrade to view more data",
#         "cause": null
#       },
#       "progress": null
#     },
#     "FILTER.CUSTOM_RANGE": {
#       "key": "FILTER.CUSTOM_RANGE",
#       "type": "MODULE",
#       "enable": null,
#       "count": 0,
#       "guidance": {
#         "actionType": {
#           "name": "Upgrade",
#           "desc": "Upgrade to view more data"
#         },
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Upgrade to view more data",
#         "cause": null
#       },
#       "progress": null
#     },
#     "CUSTOMIZED.DATA.EXPORT": {
#       "key": "CUSTOMIZED.DATA.EXPORT",
#       "type": "BENEFIT",
#       "enable": null,
#       "count": 0,
#       "guidance": {
#         "actionType": {
#           "name": "Upgrade",
#           "desc": "Upgrade to view more data"
#         },
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Member Trial has Expired",
#         "cause": null
#       },
#       "progress": {
#         "total": 0,
#         "used": 0,
#         "remain": 0,
#         "full": true
#       }
#     },
#     "SHOP.DETAIL": {
#       "key": "SHOP.DETAIL",
#       "type": "MODULE",
#       "enable": null,
#       "count": 0,
#       "guidance": {
#         "actionType": {
#           "name": "Upgrade",
#           "desc": "Upgrade to view more data"
#         },
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Upgrade to view more data",
#         "cause": null
#       },
#       "progress": null
#     },
#     "OVERVIEW.DETAIL": {
#       "key": "OVERVIEW.DETAIL",
#       "type": "MODULE",
#       "enable": null,
#       "count": 1,
#       "guidance": {
#         "actionType": {
#           "name": "Upgrade",
#           "desc": "Upgrade to view more data"
#         },
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Upgrade to view more data",
#         "cause": null
#       },
#       "progress": null
#     },
#     "CREATOR.MCN_SIGN": {
#       "key": "CREATOR.MCN_SIGN",
#       "type": "MODULE",
#       "enable": null,
#       "count": 0,
#       "guidance": {
#         "actionType": {
#           "name": "Upgrade",
#           "desc": "Upgrade to view more data"
#         },
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Upgrade to view more data",
#         "cause": null
#       },
#       "progress": null
#     },
#     "OVERVIEW.POTENTIAL_LIST": {
#       "key": "OVERVIEW.POTENTIAL_LIST",
#       "type": "LIST",
#       "enable": null,
#       "count": 1,
#       "guidance": {
#         "actionType": {
#           "name": "Upgrade",
#           "desc": "Upgrade to view more data"
#         },
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Upgrade to view more data",
#         "cause": null
#       },
#       "progress": null
#     },
#     "PRODUCT.DETAIL": {
#       "key": "PRODUCT.DETAIL",
#       "type": "MODULE",
#       "enable": null,
#       "count": 1,
#       "guidance": {
#         "actionType": {
#           "name": "Upgrade",
#           "desc": "Upgrade to view more data"
#         },
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Upgrade to view more data",
#         "cause": null
#       },
#       "progress": null
#     },
#     "AD.ANALYSIS": {
#       "key": "AD.ANALYSIS",
#       "type": "MODULE",
#       "enable": null,
#       "count": 0,
#       "guidance": {
#         "actionType": {
#           "name": "Upgrade",
#           "desc": "Upgrade to view more data"
#         },
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Upgrade to view more data",
#         "cause": null
#       },
#       "progress": null
#     },
#     "CREATOR.LIST": {
#       "key": "CREATOR.LIST",
#       "type": "LIST",
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
#         "message": "Upgrade to view more data",
#         "cause": null
#       },
#       "progress": null
#     },
#     "VIDEO.DETAIL": {
#       "key": "VIDEO.DETAIL",
#       "type": "MODULE",
#       "enable": null,
#       "count": 1,
#       "guidance": {
#         "actionType": {
#           "name": "Upgrade",
#           "desc": "Upgrade to view more data"
#         },
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Upgrade to view more data",
#         "cause": null
#       },
#       "progress": null
#     },
#     "DOWNLOAD.VIDEO": {
#       "key": "DOWNLOAD.VIDEO",
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
#         "message": "Member Trial has Expired",
#         "cause": null
#       },
#       "progress": {
#         "total": 10,
#         "used": 0,
#         "remain": 10,
#         "full": false
#       }
#     },
#     "PRODUCT.LIST": {
#       "key": "PRODUCT.LIST",
#       "type": "LIST",
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
#         "message": "Upgrade to view more data",
#         "cause": null
#       },
#       "progress": null
#     },
#     "LIVESTREAM.FULL_RECORD": {
#       "key": "LIVESTREAM.FULL_RECORD",
#       "type": "BENEFIT",
#       "enable": null,
#       "count": 1,
#       "guidance": {
#         "actionType": {
#           "name": "Upgrade",
#           "desc": "Upgrade to view more data"
#         },
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Member Trial has Expired",
#         "cause": null
#       },
#       "progress": {
#         "total": 1,
#         "used": 0,
#         "remain": 1,
#         "full": false
#       }
#     },
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
#     },
#     "OVERVIEW.LEVEL_THIRD": {
#       "key": "OVERVIEW.LEVEL_THIRD",
#       "type": "MODULE",
#       "enable": null,
#       "count": 1,
#       "guidance": {
#         "actionType": {
#           "name": "Upgrade",
#           "desc": "Upgrade to view more data"
#         },
#         "targetLevel": null,
#         "purchasePrices": null,
#         "target": null,
#         "message": "Upgrade to view more data",
#         "cause": null
#       },
#       "progress": null
#     }
#   },
#   "message": "trial",
#   "cached": null,
#   "code": null
# }


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
