from sys import exit
from traceback import print_exc, format_exc
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from time import sleep
import argparse
from rich import print
from EsportsHelper.LoginHandler import LoginHandler
from EsportsHelper.VersionManager import VersionManager
from EsportsHelper.Webdriver import Webdriver
from EsportsHelper.Logger import Logger
from EsportsHelper.Config import Config
from EsportsHelper.Match import Match

CURRENT_VERSION = "1.1.0"
global driver


def info():
    print("[green]=========================================================")
    print(f"[green]========[/green]        感谢使用 [blue]电竞助手[/blue] v{CURRENT_VERSION}!        [green]========[/green]")
    print("[green]============[/green] 本程序开源于github链接地址如下: [green]============[/green]")
    print("[green]====[/green]   https://github.com/Yudaotor/EsportsHelper     [green]====[/green]")
    print("[green]====[/green] 如觉得不错的话可以进上面链接请我喝杯咖啡支持下. [green]====[/green]")
    print("[green]====[/green] 请在使用前[red]阅读教程文件[/red], 以确保你的配置符合要求! [green]====[/green]")
    print("[green]====[/green] 如需关闭请勿直接右上角×关闭，请按Ctrl+C来关闭. [green]====[/green]")
    print("[green]=========================================================")
    print()


def main():
    global driver
    info()
    parser = argparse.ArgumentParser(prog='EsportsHelper.exe', description='EsportsHelper help you to watch matches')
    parser.add_argument('-c', '--config', dest="configPath", default="./config.yaml",
                        help='config file path')
    args = parser.parse_args()
    Path("./logs/").mkdir(parents=True, exist_ok=True)
    Path("./driver/").mkdir(parents=True, exist_ok=True)
    log = Logger().createLogger()
    config = Config(log, args.configPath)
    if not VersionManager.isLatestVersion(CURRENT_VERSION):
        log.warning("\n==!!! 新版本可用 !!!==\n ==请从此处下载: ==")
        print("[yellow]\n==!!! 新版本可用 !!!==\n ==请从此处下载: https://github.com/Yudaotor/EsportsHelper/releases/latest ==[/yellow]")
    try:
        driver = Webdriver(config).createWebdriver()
    except TypeError:
        print_exc()
        log.error(format_exc())
        print("[red]눈_눈 生成WEBDRIVER失败!\n无法找到最新版谷歌浏览器!如没有下载或不是最新版请检查好再次尝试\n以上都检查过的话如还不行检查节点或是尝试可以用管理员方式打开\n按任意键退出...")
        input()
        exit()
    except Exception:
        print_exc()
        log.error(format_exc())
        print("[red]눈_눈 生成WEBDRIVER失败!\n是否有谷歌浏览器?\n是不是网络问题?请检查VPN节点是否可用\n按任意键退出...")
        input()
        exit()
    loginHandler = LoginHandler(log=log, driver=driver)
    try:
        driver.get(
            "https://lolesports.com/schedule?leagues=lcs,north_american_challenger_league,lcs_challengers_qualifiers,college_championship,cblol-brazil,lck,lcl,lco,lec,ljl-japan,lla,lpl,pcs,turkiye-sampiyonluk-ligi,vcs,worlds,all-star,european-masters,lfl,nlc,elite_series,liga_portuguesa,pg_nationals,ultraliga,superliga,primeleague,hitpoint_masters,esports_balkan_league,greek_legends,arabian_league,lck_academy,ljl_academy,lck_challengers_league,cblol_academy,liga_master_flo,movistar_fiber_golden_league,elements_league,claro_gaming_stars_league,honor_division,volcano_discover_league,honor_league,msi,tft_esports")
    except Exception as e:
        driver.get("https://lolesports.com/schedule")
    driver.set_window_size(960, 768)
    try:
        loginHandler.automaticLogIn(config.username, config.password)
    except TimeoutException:
        log.error("눈_눈 自动登录失败,账号密码是否正确?")
        print("[red]눈_눈 自动登录失败,账号密码是否正确?[/red]")
        if config.headless:
            driver.quit()
            log.info("退出中...")
            print("[green]退出中...[/green]")
            input("按任意键退出")
            exit()
    retryTimes = 4
    while not driver.find_elements(by=By.CSS_SELECTOR, value="div.riotbar-summoner-name"):
        retryTimes = retryTimes - 1
        if retryTimes < 0:
            driver.quit()
            log.error("눈_눈 自动登录失败")
            print("[red]눈_눈 自动登录失败[/red]")
            log.info("退出中...")
            print("[yellow]退出中...[/yellow]")
            input("按任意键退出")
            exit()
        print("[red]눈_눈 自动登录失败...[/red]")
        log.error("눈_눈 自动登录失败...")
        log.info("눈_눈 等待手动登录中...")
        print("[yellow]눈_눈 等待手动登录中...[/yellow]")
        sleep(15)
    log.info("∩_∩ 好嘞 登录成功")
    print("[green]∩_∩ 好嘞 登录成功[/green]")

    Match(log=log, driver=driver, config=config).watchMatches(delay=config.delay)


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        global driver
        if driver is not None:
            driver.quit()
        print("[red]------程序退出------")
        exit()
