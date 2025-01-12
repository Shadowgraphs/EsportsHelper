from random import randint
from sys import exit
from traceback import print_exc, format_exc
import requests
from rich import print
from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
from time import sleep
from datetime import datetime, timedelta
from urllib3.exceptions import MaxRetryError
from EsportsHelper.Rewards import Rewards
from EsportsHelper.Twitch import Twitch
from EsportsHelper.Youtube import Youtube


class Match:
    def __init__(self, log, driver, config) -> None:
        self.log = log
        self.driver = driver
        self.config = config
        self.rewards = Rewards(log=log, driver=driver, config=config)
        self.twitch = Twitch(driver=driver, log=log)
        self.youtube = Youtube(driver=driver, log=log)
        self.currentWindows = {}
        self.mainWindow = self.driver.current_window_handle
        self.OVERRIDES = {}
        self.retryTimes = 3
        try:
            req = requests.session()
            headers = {'Content-Type': 'text/plain; charset=utf-8', 'Connection': 'close'}
            remoteOverrideFile = req.get("https://raw.githubusercontent.com/Yudaotor/EsportsHelper/main/override.txt", headers=headers)
            if remoteOverrideFile.status_code == 200:
                override = remoteOverrideFile.text.split(",")
                first = True
                for o in override:
                    temp = o.split("|")
                    if len(temp) == 2:
                        if first:
                            first = False
                        else:
                            temp[0] = temp[0][1:]
                        self.OVERRIDES[temp[0]] = temp[1]
        except MaxRetryError:
            self.log.error("获取文件失败, 请稍等再试")
            print(f"[red]〒.〒 获取文件失败, 请稍等再试[/red]")
            input("按任意键退出")
        except Exception as ex:
            print_exc()
            print(f"[red]〒.〒 获取文件失败,请检查网络是否能连上github[/red]")
            input("按任意键退出")

    def watchMatches(self, delay):
        self.currentWindows = {}
        self.mainWindow = self.driver.current_window_handle
        while True:
            try:
                self.log.info("●_● 开始检查直播...")
                print(f"[green]●_● 开始检查直播...[/green]")
                self.driver.switch_to.window(self.mainWindow)
                isDrop, imgUrl, title = self.rewards.checkNewDrops()
                if isDrop:
                    for tit in title:
                        self.log.info(f"ΩДΩ {self.config.username}发现新的掉落: {tit}")
                        print(f"[blue]ΩДΩ {self.config.username}发现新的掉落: {tit}[/blue]")
                    if self.config.connectorDropsUrl != "":
                        self.rewards.notifyDrops(imgUrl=imgUrl, title=title)
                sleep(3)
                try:
                    self.driver.get("https://lolesports.com/schedule?leagues=lcs,north_american_challenger_league,lcs_challengers_qualifiers,college_championship,cblol-brazil,lck,lcl,lco,lec,ljl-japan,lla,lpl,pcs,turkiye-sampiyonluk-ligi,vcs,worlds,all-star,european-masters,lfl,nlc,elite_series,liga_portuguesa,pg_nationals,ultraliga,superliga,primeleague,hitpoint_masters,esports_balkan_league,greek_legends,arabian_league,lck_academy,ljl_academy,lck_challengers_league,cblol_academy,liga_master_flo,movistar_fiber_golden_league,elements_league,claro_gaming_stars_league,honor_division,volcano_discover_league,honor_league,msi,tft_esports")
                except Exception as e:
                    self.driver.get("https://lolesports.com/schedule")
                sleep(5)
                liveMatches = self.getMatchInfo()
                sleep(3)
                if len(liveMatches) == 0:
                    self.log.info("〒.〒 没有赛区正在直播")
                    print(f"[green]〒.〒 没有赛区正在直播[/green]")
                else:
                    self.log.info(f"ㅎ.ㅎ 现在有 {len(liveMatches)} 个赛区正在直播中")
                    print(f"[green]ㅎ.ㅎ 现在有 {len(liveMatches)} 个赛区正在直播中[/green]")

                self.closeFinishedTabs(liveMatches=liveMatches)

                self.startWatchNewMatches(liveMatches=liveMatches, disWatchMatches=self.config.disWatchMatches)
                sleep(3)
                randomDelay = randint(int(delay * 0.08), int(delay * 0.15))
                newDelay = randomDelay * 10
                self.driver.switch_to.window(self.mainWindow)
                self.log.info(f"下一次检查在: {datetime.now() + timedelta(seconds=newDelay)}")
                self.log.debug("============================================")
                print(f"[green]下一次检查在: {(datetime.now() + timedelta(seconds=newDelay)).strftime('%m{m}%d{d} %H{h}%M{f}%S{s}').format(m='月',d='日',h='时',f='分',s='秒')}[/green]")
                print(f"[green]============================================[/green]")
                sleep(newDelay)
                self.retryTimes = 3
            except WebDriverException as e:
                self.retryTimes -= 1
                self.log.error("Q_Q webdriver发生错误, 重试中")
                print(f"[red]Q_Q webdriver发生错误, 重试中[/red]")
                sleep(2)
                if self.retryTimes <= 0:
                    self.log.error("Q_Q webdriver发生错误, 将于3秒后退出...")
                    print(f"[red]Q_Q webdriver发生错误, 将于3秒后退出...[/red]")
                    sleep(3)
                    self.driver.quit()
                    exit()
            except Exception as e:
                self.retryTimes -= 1
                self.log.error("Q_Q 发生错误")
                print(f"[red]Q_Q 发生错误[/red]")
                print_exc()
                self.log.error(format_exc())
                sleep(2)
                if self.retryTimes <= 0:
                    self.log.error("Q_Q 发生错误, 将于3秒后退出...")
                    print(f"[red]Q_Q 发生错误, 将于3秒后退出...[/red]")
                    sleep(3)
                    self.driver.quit()
                    exit()

    def getMatchInfo(self):
        try:
            matches = []
            elements = self.driver.find_elements(by=By.CSS_SELECTOR, value=".EventMatch .event.live")
            for element in elements:
                matches.append(element.get_attribute("href"))
            return matches
        except Exception as e:
            self.log.error("Q_Q 获取比赛列表失败")
            print(f"[red]Q_Q 获取比赛列表失败[/red]")
            print_exc()
            self.log.error(format_exc())
            return []

    def closeFinishedTabs(self, liveMatches):
        try:
            removeList = []
            for k in self.currentWindows.keys():
                self.driver.switch_to.window(self.currentWindows[k])
                if k not in liveMatches:
                    splitUrl = k.split('/')
                    if splitUrl[-2] != "live":
                        match = splitUrl[-2]
                    else:
                        match = splitUrl[-1]
                    self.log.info(f"̋0.0 {match} 比赛结束")
                    print(f"[yellow]̋0.0 {match} 比赛结束[/yellow]")
                    self.driver.close()
                    removeList.append(k)
                    self.driver.switch_to.window(self.mainWindow)
                    sleep(5)
                else:
                    self.rewards.checkRewards(k)
            for k in removeList:
                self.currentWindows.pop(k, None)
            self.driver.switch_to.window(self.mainWindow)
        except Exception as e:
            print_exc()
            self.log.error(format_exc())

    def startWatchNewMatches(self, liveMatches, disWatchMatches):
        newLiveMatches = set(liveMatches) - set(self.currentWindows.keys())
        for match in newLiveMatches:

            flag = True
            for disMatch in disWatchMatches:
                if match.find(disMatch) != -1:
                    splitUrl = match.split('/')
                    if splitUrl[-2] != "live":
                        skipName = splitUrl[-2]
                    else:
                        skipName = splitUrl[-1]
                    self.log.info(f"(╯#-_-)╯ {skipName}比赛跳过")
                    print(f"[yellow](╯#-_-)╯ {skipName}比赛跳过")
                    flag = False
                    break
            if not flag:
                continue

            self.driver.switch_to.new_window('tab')
            sleep(1)
            self.currentWindows[match] = self.driver.current_window_handle
            if match in self.OVERRIDES:
                url = self.OVERRIDES[match]
                self.driver.get(url)
                if not self.rewards.checkRewards(url):
                    return
                try:
                    if self.twitch.setTwitchQuality():
                        self.log.info(">_< Twitch 160p清晰度设置成功")
                        print("[green]>_< Twitch 160p清晰度设置成功")
                    else:
                        self.log.critical("°D° Twitch 清晰度设置失败")
                        print("[red]°D° Twitch 清晰度设置失败")
                except Exception:
                    self.log.critical("°D° 无法设置 Twitch 清晰度.")
                    print("[red]°D° 无法设置 Twitch 清晰度.")
                    print_exc()
                    self.log.error(format_exc())
            else:
                url = match
                self.driver.get(url)
                try:
                    if self.youtube.setYoutubeQuality():
                        self.log.info(">_< Youtube 144p清晰度设置成功")
                        print("[green]>_< Youtube 144p清晰度设置成功")
                    else:
                        self.log.critical("°D° Youtube 清晰度设置失败")
                        print("[red]°D° Youtube 清晰度设置失败")
                    self.rewards.checkRewards(url)
                except Exception:
                    self.log.critical(f"°D° 无法设置 Youtube 清晰度.")
                    print("[red]°D° 无法设置 Youtube 清晰度.")
                    print_exc()
                    self.log.error(format_exc())
            sleep(5)
