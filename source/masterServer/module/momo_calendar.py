from public.log import master_server_logger
from public.message import momo_calendar_msg
from public.config import data_path
from selenium.webdriver import Firefox
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, timedelta
import traceback
import re
import json
import os


class CalendarBrowser(Firefox):
    __SERVICE_PATH = "D:/geckodriver.exe"

    JSON_PATH = data_path('momo.json')
    ICS_PATH = data_path('momo.ics')

    def __init__(self):
        super().__init__(service=Service(CalendarBrowser.__SERVICE_PATH))
        self.__waiter = WebDriverWait(self, 60)

        self.event_dict_list = []

    def __del__(self):
        self.close()

    def __wait_element(self, by, val) -> WebElement:
        return self.__waiter.until(EC.presence_of_element_located((by, val)))

    def _generate_dict_one_day(self, day):
        day_str = day.strftime('%Y-%m-%d')
        self.get(f'https://timetreeapp.com/public_calendars/momomitsuki/daily/{day_str}')
        main = self.__wait_element(By.TAG_NAME, 'main')
        self.__wait_element(By.TAG_NAME, 'h2')
        try:
            ul = main.find_element(By.XPATH, '//ul[@data-date]')
        except NoSuchElementException:
            return

        for a in ul.find_elements(By.TAG_NAME, 'a'):
            title, time_str = a.text.split('\n')
            hour, minute = map(int, re.search(r'(\d+):(\d+)', time_str).groups())
            time = day.replace(hour=hour, minute=minute)
            self.event_dict_list.append({'title': title, 'time': time.strftime('%Y%m%dT%H%M%S')})

    def _generate_json(self):
        now = datetime.now()
        day = datetime(year=now.year, month=now.month, day=1)
        while day.month == now.month:
            self._generate_dict_one_day(day)
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
            event_list.append(f'''\
BEGIN:VEVENT
DTSTAMP;TZID=Asia/Dongjing:{time}
UID:美月momo{time}@bilibili.com
DTSTART;TZID=Asia/Dongjing:{time}
DURATION:PT0M
SUMMARY:{title}
URL:null
DESCRIPTION:null\n点击上方链接打开哔哩哔哩，进入直播间
LOCATION:@美月もも 直播间
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:直播即将开始
TRIGGER:-PT10M
END:VALARM
END:VEVENT''')
        event_list_str = '\n\n'.join(event_list)
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

    def generate(self):
        self._generate_json()
        self._generate_ics()


def is_file_today(path):
    if not os.path.exists(path):
        return False
    if datetime.fromtimestamp(os.path.getmtime(path)).date() != datetime.now().date():
        return False
    return True


@momo_calendar_msg.on_receive
def momo_calendar():
    try:
        if not is_file_today(CalendarBrowser.ICS_PATH):
            CalendarBrowser().generate()
        return CalendarBrowser.ICS_PATH
    except Exception:
        master_server_logger.error(f'momo_calendar {traceback.format_exc()}')
        return ''
