import os

from public.log import master_server_logger
from public.message import momo_calendar_msg
from public.config import data_path
from selenium.webdriver import Firefox
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from datetime import datetime
from ics import Calendar, Event
import traceback
import re


class CalendarBrowser(Firefox):
    __SERVICE_PATH = "D:/geckodriver.exe"
    __MONTH_DICT = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12
    }

    def __init__(self):
        super().__init__(service=Service(CalendarBrowser.__SERVICE_PATH))
        self.__waiter = WebDriverWait(self, 60)

    def __del__(self):
        self.close() # TODO 可能与外部的close冲突

    def __wait_element(self, *args) -> WebElement:
        return self.__waiter.until(EC.presence_of_element_located(args))

    def __parse_one_date(self, s: str, d: datetime) -> datetime:
        m = re.search(r'(\w+) (\d+), (\d+)', s)
        return d.replace(
            month=self.__MONTH_DICT[m.group(1)],
            day=int(m.group(2)),
            year=int(m.group(3)),
        )

    def __parse_date(self, s: str, begin: datetime, end: datetime) -> tuple[datetime, datetime]:
        if '-' in s:
            a, b = s.split('-')
            return (
                self.__parse_one_date(a, begin),
                self.__parse_one_date(b, end),
            )
        else:
            return (
                self.__parse_one_date(s, begin),
                self.__parse_one_date(s, end),
            )

    def __parse_one_time(self, s: str, d: datetime) -> datetime:
        m = re.search(r'(\d+):(\d+) ([AP])M', s)
        return d.replace(
            hour=m.group(1) + 12 * (m.group(3) == 'P'),
            minute=m.group(2),
        )

    def __parse_time(self, s: str, begin: datetime, end: datetime) -> tuple[datetime, datetime]:
        if '-' in s:
            a, b = s.split('-')
            return (
                self.__parse_one_time(a, begin),
                self.__parse_one_time(b, end),
            )
        else:
            return (
                self.__parse_one_time(s, begin),
                self.__parse_one_time(s, end),
            )

    def __get_event_info(self, event: Event, url: str) -> None:
        self.get(url)
        main = self.__wait_element(By.CLASS_NAME, 'main')
        if description_elements := main.find_elements(By.CLASS_NAME, 'description'):
            event.description = description_elements[0].text

        begin = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)
        for dl in main.find_elements(By.TAG_NAME, 'dl'):
            dt = dl.find_element(By.TAG_NAME, 'dt').text
            dd = dl.find_element(By.TAG_NAME, 'dd').text
            match dt:
                case 'Date':
                    begin, end = self.__parse_date(dd, begin, end)
                case 'Time':
                    begin, end = self.__parse_time(dd, begin, end)
                case 'URL':
                    event.location = dd
        event.begin = begin
        event.end = end

    def generate_calendar(self) -> Calendar:
        self.get('https://timetreeapp.com/public_calendars/momomitsuki')
        main = self.__wait_element(By.CLASS_NAME, 'main')
        cal = Calendar()

        event_dict = {}
        for calendarEvent in main.find_elements(By.CLASS_NAME, 'publicCalendarEventItem'):
            event = Event()
            event.title = calendarEvent.find_element(By.CLASS_NAME, 'title').text
            url = calendarEvent.find_element(By.CLASS_NAME, 'event').get_attribute('href')
            event_dict[event] = url
        # __get_event_info中有get操作，会导致element不可用，需要先把url缓存下来
        for event, url in event_dict.items():
            self.__get_event_info(event, url)
            cal.events.add(event)
        return cal

    def generate_ics(self,calendar):
        path=data_path('momo.ics')
        with open(path, 'w') as f:
            f.write(calendar.serialize())

        os.system('adb connect 192.168.1.100')
        os.system(f'adb push {path} /storage/emulated/0/360')


@momo_calendar_msg.on_receive
def momo_calendar():
    try:
        calendar_browser=CalendarBrowser()
        calendar=calendar_browser.generate_calendar()
        calendar_browser.close()
        return calendar.serialize()
    except Exception:
        master_server_logger.error(f'momo_calendar {traceback.format_exc()}')
        return ''
