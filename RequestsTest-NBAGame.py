# coding utf-8
import uuid

import datetime
import requests
from lxml import etree

import pymysql
from pymysql.converters import escape_string

class NBAGame(object):

    def __init__(self, dayStr):
        self.day = dayStr
        self.url = 'https://tiyu.baidu.com/match/NBA/tab/%E8%B5%9B%E7%A8%8B/date_time/{}'.format(self.day)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
        }

    # get a UUID - URL safe, Base64
    def get_uuid(self):
        r_uuid = uuid.uuid1()
        return str(r_uuid).replace('-', '')

    def get_data(self, url):
        # 发送列表请求，获取响应
        response = requests.get(url, headers=self.headers)
        return response.content

    def run(self):
        next_url = self.url
        # 发送列表请求，获取响应
        list_page_data = self.get_data(next_url)
        # 解析列表页面的响应，提取帖子列表数据和下一页url
        date_num,data_list = self.pare_list_page(list_page_data)

        print(date_num)

        conn = pymysql.connect(host='192.168.2.104', port=3306, user='root', passwd='123456', db='NBA', charset='utf8')

        args_game_data = []
        args_player_data = []
        for data in data_list:
            game_id = self.get_uuid()
            args_game_data.append((game_id,conn.escape_string(data['item_type']),f"{self.day} {conn.escape_string(data['item_date'])}",conn.escape_string(data['away_team']),conn.escape_string(data['away_team_score']),conn.escape_string(data['home_team']),conn.escape_string(data['home_team_score']),conn.escape_string(data['game_status'])))

            detail_url = data['item_url']
            team_data_list = self.get_player_data(detail_url)

            for team_data_detail in team_data_list:
                # 球队名称
                team = str(team_data_detail['team_name']).replace("['球员统计-","").replace("']","")
                for i in range(len(team_data_detail['player_name_list'])):
                    if i == 0:
                        continue

                    # 球员名字
                    player_name = team_data_detail['player_name_list'][i].xpath('./text()')[0]
                    if player_name == '统计':
                        continue

                    playing_time = ''
                    score = ''
                    backboard = ''
                    secondary_attack = ''
                    steal = ''
                    block_shot = ''
                    shoot = ''
                    three_pointer = ''
                    penalty_shot = ''
                    fault = ''
                    foul = ''
                    rapm = ''

                    for player_data in team_data_detail['player_data_list']:
                        data = player_data.xpath('./p')
                        title = conn.escape_string(data[0].xpath("./text()")[0])
                        if title == '时间':
                            playing_time = conn.escape_string(data[i].xpath("./text()")[0])
                            continue
                        if title == '得分':
                            score = conn.escape_string(data[i].xpath("./text()")[0])
                            continue
                        if title == '篮板':
                            backboard = conn.escape_string(data[i].xpath("./text()")[0])
                            continue
                        if title == '助攻':
                            secondary_attack = conn.escape_string(data[i].xpath("./text()")[0])
                            continue
                        if title == '抢断':
                            steal = conn.escape_string(data[i].xpath("./text()")[0])
                            continue
                        if title == '盖帽':
                            block_shot = conn.escape_string(data[i].xpath("./text()")[0])
                            continue
                        if title == '投篮':
                            shoot = conn.escape_string(data[i].xpath("./text()")[0])
                            continue
                        if title == '三分':
                            three_pointer = conn.escape_string(data[i].xpath("./text()")[0])
                            continue
                        if title == '罚球':
                            penalty_shot = conn.escape_string(data[i].xpath("./text()")[0])
                            continue
                        if title == '失误':
                            fault = conn.escape_string(data[i].xpath("./text()")[0])
                            continue
                        if title == '犯规':
                            foul = conn.escape_string(data[i].xpath("./text()")[0])
                            continue
                        if title == '+/-值':
                            rapm = conn.escape_string(data[i].xpath("./text()")[0])
                            continue

                    args_player_data.append((self.get_uuid(),game_id,player_name,playing_time,score,backboard,secondary_attack,steal,block_shot,shoot,three_pointer,penalty_shot,fault,foul,rapm,team))


        cursor = conn.cursor()

        game_data_sql = "INSERT INTO game_schedule(ID,GAME_TYPE,GAME_DATETIME,GUEST_TEAM,GUEST_SCORE,HOME_TEAM,HOME_SCORE,GAME_STATUS) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
        try:
            cursor.executemany(game_data_sql, args_game_data)
        except Exception as e:
            print("插入比赛结果: %s 时出错：%s" % (game_data_sql, e))

        player_data_sql = """INSERT INTO player_data(ID,GAME_ID,PLAYER_NAME,PLAYING_TIME,SCORE,BACKBOARD,SECONDARY_ATTACK,STEAL,BLOCK_SHOT,SHOOT,THREE_POINTER,PENALTY_SHOT,FAULT,FOUL,RAPM,TEAM) 
                          values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        try:
            cursor.executemany(player_data_sql, args_player_data)
        except Exception as e:
            print("插入球员数据: %s 时出错：%s" % (player_data_sql, e))

        print('执行完成')

        cursor.close()
        conn.commit()
        conn.close()

    def pare_list_page(self, data):
        data = data.decode().replace('<!--','').replace('-->','')
        html = etree.HTML(data)

        # 时间和比赛场数
        game_date = html.xpath('//div/div[2]/div/div/div/main/section/div[1]/b-grouplist-sticky/div/div[3]/div/div[1]/div[2]/div/div/div/div[2]/div[1]/div[1]/div[1]/text()')[0]
        game_count = html.xpath('//div/div[2]/div/div/div/main/section/div[1]/b-grouplist-sticky/div/div[3]/div/div[1]/div[2]/div/div/div/div[2]/div[1]/div[1]/div[2]/text()')[0]
        date_num = f"{datetime.datetime.now().strftime('%Y')}-{game_date.strip()}：{game_count.strip()}"

        # 比赛明细
        el_list = html.xpath('//div/div[2]/div/div/div/main/section/div[1]/b-grouplist-sticky/div/div[3]/div/div[1]/div[2]/div/div/div/div[2]/div[1]/div[2]/div')

        data_list = []
        for el in el_list:
            temp = {}
            # 明细链接
            temp['item_url'] ='https:'+ el.xpath('./a[1]/@href')[0]
            # 比赛时间
            temp['item_date'] = el.xpath('./a[1]//*[contains(@class,"font-14 c-gap-bottom-small")]/text()')[0]
            # 比赛类型
            temp['item_type'] = el.xpath('./a[1]//*[contains(@class,"font-12 c-color-gray")]/text()')[0]
            # 客场球队
            temp['away_team'] = el.xpath('./a[1]//*//div[@class="team-row"]/*//span[@class="inline-block team-name team-name-360 team-name-320 c-line-clamp1"]/text()')[0]
            # 客场球队得分
            temp['away_team_score'] = el.xpath('./a[1]//*//div[@class="team-row"]/*//span[@class="inline-block team-score-num c-line-clamp1"]/text()')[0]
            # 主场球队
            temp['home_team'] = el.xpath('./a[1]//*//div[@class="c-gap-top-small team-row"]/*//span[@class="inline-block team-name team-name-360 team-name-320"]/text()')[0]
            # 主场球队得分
            temp['home_team_score'] = el.xpath('./a[1]//*//div[@class="c-gap-top-small team-row"]/*//span[@class="inline-block team-score-num c-line-clamp1"]/text()')[0]
            # 比赛状态
            temp['game_status'] = el.xpath('./a[1]//*//div[@class="vs-info-status"]/*//span[1]/text()')[0]

            data_list.append(temp)

        return date_num,data_list

    def get_player_data(self, detail_url):
        detail_data = self.get_data(detail_url)
        data = detail_data.decode().replace('<!--','').replace('-->','')
        html = etree.HTML(data)

        # 数据集合
        all_player_data_list = html.xpath('//*/div[@class="wa-basketball-first-container"]')

        team_data_list = []
        for team_data in all_player_data_list:
            team_data_detail = {}
            # 球员统计-76人
            team_data_detail['team_name'] = team_data.xpath('./div[@class="basketball-first-title"][1]/text()')
            # 球员
            team_data_detail['player_name_list'] = team_data.xpath('./*/div[@class="first-list-left"][1]/p')
            # 数据
            data_list = team_data.xpath('./*/div[@class="first-list-right"]//*/div[@class="first-list-col"]')
            team_data_detail['player_data_list'] = data_list

            team_data_list.append(team_data_detail)
        return team_data_list

if __name__ == '__main__':
    date_today = datetime.datetime.now().strftime('%Y-%m-%d')
    get_nba_game = NBAGame(date_today)
    get_nba_game.run()