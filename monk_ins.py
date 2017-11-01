#encoding: utf-8
'''
Crawl ahmad_monk's Ins
'''

import sys
import urllib
import time
import traceback
import sqlite3
import requests

def usage():
    print '''Input Error!\nUsage: python %s full/history''' % sys.argv[0]
    exit(-1)

def generate_url(end_cursor):
    '''
    generate url to get info
    '''
    url_pattern = 'https://www.instagram.com/graphql/query/?query_id=17888483320059182&variables={req_param}'
    req_param = '{"id":"22543622","first":20,"after":"'+end_cursor+'"}'
    url = url_pattern.format(req_param = urllib.quote(req_param))
    return url
def init_sqlite():
    conn = sqlite3.connect("ins.sqlite")
    cursor = conn.cursor()

    cursor.execute('''create table if not exists ahmad_monk
                    (id text primary key,
                    timestamp text,
                    comments integer,
                    like integer,
                    image_url text,
                    dim text
                    )''')
    conn.commit()
    return conn, cursor

def insert_into_sqlite(cursor, media_info):
    insert_sql = 'insert into ahmad_monk values(?,?,?,?,?,?)'
    cursor.execute(insert_sql, (media_info['id'], 
                                str(media_info['taken_at_timestamp']), 
                                (not media_info['comments_disabled'])*int(media_info['edge_media_to_comment']['count']),
                                media_info['edge_media_preview_like']['count'],
                                media_info['display_url'],
                                str(media_info['dimensions']['height'])+'*'+str(media_info['dimensions']['width'])
                                ))

def get_latest_time_from_sqlite(cursor):
    cursor.execute('select')
    
def get_media_nodes(crawl_type):
    '''
    get media info, save in sqlite
    type: full/increment
    '''
    end_cursor = ''
    has_next_page = True
    conn, cursor = init_sqlite()
    while has_next_page:
        url = generate_url(end_cursor)
        page_info = requests.get(url, verify = False).json()
        media_info = page_info['data']['user']['edge_owner_to_timeline_media']
        media_nodes = media_info['edges']
        #total_count = int(media_info['count'])
        has_next_page = media_info['page_info']['has_next_page']
        end_cursor = media_info['page_info']['end_cursor']
        for media in media_nodes:
            cursor.execute("select * from ahmad_monk where id='%s'"%media['node']['id'])
            if cursor.fetchall():
                if crawl_type == 'full':
                    continue
                else:
                    return
            if not cursor.fetchall() and media['node']['__typename'] == 'GraphImage':
                try:
                    insert_into_sqlite(cursor, media['node'])
                    conn.commit()
                except:
                    traceback.print_exc()
    conn.close()

def main():
    if len(sys.argv)!=2 or sys.argv[1] not in ['full','increment']:
        usage()
    elif sys.argv[1] == 'full':
        get_media_nodes('full')
    else:
        while True:
            get_media_nodes('increment')
            time.sleep(86400)

if __name__ == '__main__':
    main()