from public.log import master_server_logger
from public.message import momo_calendar_msg
from public.config import data_path
from public.scheduler import scheduler
from public.utils import is_file_today
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, timedelta
from threading import Thread, Lock
import platform
import re
import json
import os


class CalendarBrowser(Firefox):
    __SERVICE_PATH = 'geckodriver.exe' if platform.system() == 'Windows' else 'geckodriver'

    JSON_PATH = data_path('momo.json')
    ICS_PATH = data_path('momo.ics')

    __update_lock = Lock()

    def __init__(self):
        options = FirefoxOptions()
        options.set_preference('webdriver.timezone', 'Asia/Shanghai')
        options.set_preference('intl.accept_languages', 'zh-CN')
        service = Service(CalendarBrowser.__SERVICE_PATH)
        super().__init__(options=options, service=service)
        self.__waiter = WebDriverWait(self, 60)

        self.event_dict_list = []

    def __del__(self):
        self.close()

    def close(self):
        try:
            super().close()
        except:
            pass

    def __wait_element(self, by, val) -> WebElement:
        return self.__waiter.until(EC.presence_of_element_located((by, val)))

    def __generate_dict_one_day(self, day):
        day_str = day.strftime('%Y-%m-%d')
        self.get(f'https://timetreeapp.com/public_calendars/momomitsuki/daily/{day_str}')
        main = self.__wait_element(By.TAG_NAME, 'main')
        self.__wait_element(By.TAG_NAME, 'h2')
        try:
            ul = main.find_element(By.XPATH, '//ul[@data-date]')
        except NoSuchElementException:
            return

        for a in ul.find_elements(By.TAG_NAME, 'a'):
            title, time_str = a.text.split('\n', 1)
            if m := re.search(r'(\d+):(\d+)', time_str):
                hour, minute = map(int, m.groups())
            else:
                master_server_logger.exception(f'momo_calendar 已跳过日程：获取{day_str}时间失败')
                continue  # TODO 适配全天类日程
            time = day.replace(hour=hour, minute=minute)
            self.event_dict_list.append({'title': title, 'time': time.strftime('%Y%m%dT%H%M%S')})

    def _generate_json(self):
        now = datetime.now()
        day = datetime(year=now.year, month=now.month, day=1)
        while day.month == now.month:
            self.__generate_dict_one_day(day)
            day += timedelta(days=1)

        # 保存中间件，方便拆分步骤
        with open(self.JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump({'list': self.event_dict_list}, f, ensure_ascii=False)

    def _generate_ics(self):
        with open(self.JSON_PATH, encoding='utf-8') as f:
            event_json = json.load(f)
            self.event_dict_list = event_json['list']

        event_list = []
        for event_dict in self.event_dict_list:
            title = event_dict['title']
            time = event_dict['time']
            # noinspection SpellCheckingInspection
            event_list.append(fr'''
BEGIN:VEVENT
DTSTAMP;TZID=Asia/Dongjing:{time}
UID:美月momo{time}@bilibili.com
DTSTART;TZID=Asia/Dongjing:{time}
DURATION:PT0M
SUMMARY:{title}
URL:http://live.bilibili.com/23698286
DESCRIPTION:http://live.bilibili.com/23698286\n点击上方链接打开哔哩哔哩，进入直播间
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:直播即将开始
TRIGGER:-PT10M
END:VALARM
END:VEVENT
''')
        event_list_str = ''.join(event_list)
        # noinspection SpellCheckingInspection
        result = f'''\
BEGIN:VCALENDAR
PRODID:-//美月momo//美月momo 直播日程表//CN
VERSION:2.0
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:美月momo 直播日程表
X-WR-TIMEZONE:Asia/Dongjing
X-WR-CALDESC:美月momo 直播日程表，由 comiee 制作
BEGIN:VTIMEZONE
TZID:Asia/Dongjing
X-LIC-LOCATION:Asia/Dongjing
BEGIN:STANDARD
TZOFFSETFROM:+0900
TZOFFSETTO:+0900
TZNAME:CST
DTSTART:19700101T000000
END:STANDARD
END:VTIMEZONE

{event_list_str}

END:VCALENDAR'''
        with open(self.ICS_PATH, 'w', encoding='utf-8') as f:
            f.write(result)

    def _generate(self):
        try:
            self._generate_json()
            self._generate_ics()
            master_server_logger.info('momo_calendar 日历已更新')
        except Exception:
            master_server_logger.exception('momo_calendar 日历更新失败')
        finally:
            self.close()

    @classmethod
    def need_update(cls):
        if cls.__update_lock.locked():
            return False
        if is_file_today(cls.ICS_PATH):
            return False
        return True

    @classmethod
    def generate(cls):
        with cls.__update_lock:
            cls()._generate()


@scheduler.scheduled_job('cron', hour='4', misfire_grace_time=None)
@momo_calendar_msg.on_receive
def momo_calendar():
    if CalendarBrowser.need_update():
        Thread(target=CalendarBrowser.generate).start()
    if os.path.exists(CalendarBrowser.ICS_PATH):
        with open(CalendarBrowser.ICS_PATH, encoding='utf-8') as f:
            return f.read()
    return ''
