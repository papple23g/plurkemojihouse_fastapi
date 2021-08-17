'''
210817 目前搬移資料做法: 將本腳本執行後輸出的字串餵入 POST /emoji_list 請求中
'''

import requests
import json

# url = 'https://papple23g-mysite2.herokuapp.com/PlurkEmojiHouse/search_by_tag?search_tag=&page=3325&user_uid=fwOlGfeWdDg0dtknxTnKHgeW8Ev1&num_of_emoji_per_page=20'
url = 'https://papple23g-mysite2.herokuapp.com/PlurkEmojiHouse/search_by_tag?search_tag=Deemo'
res = requests.get(url)
_emoji_dict_list = res.json()

emoji_dict_list = [
    dict(
        url=emoji_dict['url'],
        tags_str=emoji_dict['tags'],
        average_hash_str=emoji_dict['imagehash_str'],
    )
    for emoji_dict in _emoji_dict_list
]

print(json.dumps(emoji_dict_list, indent=4))
