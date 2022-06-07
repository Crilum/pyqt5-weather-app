#!/usr/bin/env python3

from re import L, T
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtGui, QtWidgets
import requests
from geopy.geocoders import Nominatim
import json
from pathlib import Path
import sys
import os
from qt_material import apply_stylesheet
from qt_material import list_themes


class Forecast():
    def __init__(self, json):

        if os.path.isfile(f"{os.path.expanduser('~')}/.config/weatherGui/preferences.txt"):
            conf = open(
                f"{os.path.expanduser('~')}/.config/weatherGui/preferences.txt", 'r')
            content = conf.readlines()
            self.fmt = content[0].split(" ")[1].strip()
            #print(f"debug@format| Setting format to '{self.fmt}'..")
            if self.fmt == "Imperial":
                self.jsonFmt = "mile"
                self.jsonTemp = "f"
                self.prettyTemp = "F"
                self.prettyWind = "mph"
            elif self.fmt == "Metric":
                self.jsonFmt = "km"
                self.jsonTemp = "c"
                self.prettyTemp = "C"
                self.prettyWind = "km/h"
            else:
                self.jsonFmt = "mile"
                self.jsonTemp = "f"
                self.prettyTemp = "F"
                self.prettyWind = "mph"
                message = QMessageBox()
                message.setText(
                    "Error:\nBad format config!\nIf you changed the config manually, please check it.")
                message.exec_()
        else:
            print('debug@format| Not loading conf, conffile not found')
        self.json = json
        self.forecast_days = json["next_days"]
        self.currCond = json["currentConditions"]

        if 1 == 1:
            mo = self.forecast_days[0]
            day_ = mo["day"]
            moHigh = mo["max_temp"][self.jsonTemp]
            moLow = mo["min_temp"][self.jsonTemp]
            moCond = mo["comment"]
            self.mo_forecast = f"Today    -      High: {moHigh}° {self.prettyTemp}      Low: {moLow}° {self.prettyTemp}           {moCond}"
            out("debug@forecast", self.mo_forecast)

            tu = self.forecast_days[1]
            day_ = tu["day"]
            tuHigh = tu["max_temp"][self.jsonTemp]
            tuLow = tu["min_temp"][self.jsonTemp]
            tuCond = tu["comment"]
            self.tu_forecast = f"{day_}     -     High: {tuHigh}° {self.prettyTemp}      Low: {tuLow}° {self.prettyTemp}           {tuCond}"
            out("debug@forecast", self.tu_forecast)

            we = self.forecast_days[2]
            day_ = we["day"]
            weHigh = we["max_temp"][self.jsonTemp]
            weLow = we["min_temp"][self.jsonTemp]
            weCond = we["comment"]
            self.we_forecast = f"{day_}     -     High: {weHigh}° {self.prettyTemp}      Low: {weLow}° {self.prettyTemp}           {weCond}"
            out("debug@forecast", self.we_forecast)

            th = self.forecast_days[3]
            day_ = th["day"]
            thHigh = th["max_temp"][self.jsonTemp]
            thLow = th["min_temp"][self.jsonTemp]
            thCond = th["comment"]
            self.th_forecast = f"{day_}     -    High: {thHigh}° {self.prettyTemp}      Low: {thLow}° {self.prettyTemp}           {thCond}"
            out("debug@forecast", self.th_forecast)

            fr = self.forecast_days[4]
            day_ = fr["day"]
            frHigh = fr["max_temp"][self.jsonTemp]
            frLow = fr["min_temp"][self.jsonTemp]
            frCond = fr["comment"]
            self.fr_forecast = f"{day_}     -     High: {frHigh}° {self.prettyTemp}     Low: {frLow}° {self.prettyTemp}           {frCond}"
            out("debug@forecast", self.fr_forecast)

            sa = self.forecast_days[5]
            day_ = sa["day"]
            saHigh = sa["max_temp"][self.jsonTemp]
            saLow = sa["min_temp"][self.jsonTemp]
            saCond = sa["comment"]
            self.sa_forecast = f"{day_}     -     High: {saHigh}° {self.prettyTemp}     Low: {saLow}° {self.prettyTemp}           {saCond}"
            out("debug@forecast", self.sa_forecast)

            su = self.forecast_days[6]
            day_ = su["day"]
            suHigh = su["max_temp"][self.jsonTemp]
            suLow = su["min_temp"][self.jsonTemp]
            suCond = su["comment"]
            self.su_forecast = f"{day_}     -     High: {suHigh}° {self.prettyTemp}      Low: {suLow}° {self.prettyTemp}           {suCond}"
            out("debug@forecast", self.su_forecast)

            mo1 = self.forecast_days[7]
            day_ = mo1["day"]
            mo1High = mo1["max_temp"][self.jsonTemp]
            mo1Low = mo1["min_temp"][self.jsonTemp]
            mo1Cond = mo1["comment"]
            self.mo1_forecast = f"{day_}     -     High: {mo1High}° {self.prettyTemp}      Low: {mo1Low}° {self.prettyTemp}           {mo1Cond}"
            out("debug@forecast", self.mo1_forecast)


def out(type, msg):
    if not prefs.output == "None":
        if prefs.output == "Debug":
            if str(type).__contains__("debug") or str(type).__contains__("info") or str(type).__contains__("error"):
                print(f"{type}| {str(msg)}")
        elif prefs.output == "Info":
            if str(type).__contains__("info") or  str(type).__contains__("error"):
                print(f"{type}| {str(msg)}")
        elif prefs.output == "Errors only":
            if str(type).__contains__("error"):
                print(f"{type}| {str(msg)}")


class weatherGui(QMainWindow):
    def __init__(self):
        super(weatherGui, self).__init__()
        out("info@weatherGui", "loading ui file...")
        uic.loadUi("weather.ui", self)
        self.setWindowTitle("WeatherGui")
        self.loadPrefs()
        
        self.show()

        self.getWeather.clicked.connect(lambda: self.getWeather_())
        self.actionClose.triggered.connect(lambda: exit())
        self.actionSave_As.triggered.connect(lambda: self.saveAs())
        self.actionPrefs.triggered.connect(lambda: self.openPrefs())
        self.actionExport_Raw_JSON.triggered.connect(lambda: self.expJSON())
        self.actionReload_settings.triggered.connect(lambda: self.loadPrefs())

    def loadPrefs(self):
        if os.path.isfile(f"{os.path.expanduser('~')}/.config/weatherGui/preferences.txt"):
            conf = open(
                f"{os.path.expanduser('~')}/.config/weatherGui/preferences.txt", 'r')
            content = conf.readlines()
            theme = content[1].split(" ")[1].strip()
            if not theme == "Default":
                out("debug@theme", f"Setting theme to '{theme}'..")
                if str(list_themes()).__contains__(theme):
                    apply_stylesheet(self, theme=theme)
                else:
                    out("error@theme", "Error: Bad theme config! If you changed the config manually, please check it.")
                    message = QMessageBox()
                    message.setText(
                        "Error:\nBad theme config!\nIf you changed the config manually, please check it.")
                    message.exec_()
        else:
            out('debug@theme', 'Not loading conf, no config file found')

        if os.path.isfile(f"{os.path.expanduser('~')}/.config/weatherGui/preferences.txt"):
            conf = open(
                f"{os.path.expanduser('~')}/.config/weatherGui/preferences.txt", 'r')
            content = conf.readlines()
            self.fmt = content[0].split(" ")[1].strip()
            out("debug@format",  f"Setting format to '{self.fmt}'..")
            if self.fmt == "Imperial":
                self.jsonFmt = "mile"
                self.jsonTemp = "f"
                self.prettyTemp = "F"
                self.prettyWind = "mph"
            elif self.fmt == "Metric":
                self.jsonFmt = "km"
                self.jsonTemp = "c"
                self.prettyTemp = "C"
                self.prettyWind = "km/h"
            else:
                self.jsonFmt = "mile"
                self.jsonTemp = "f"
                self.prettyTemp = "F"
                self.prettyWind = "mph"
                out("error@format", "Error: Bad format config! If you changed the config manually, please check it.")
                message = QMessageBox()
                message.setText(
                    "Error:\nBad format config!\nIf you changed the config manually, please check it.")
                message.exec_()
        else:
            out('debug@format', 'Not loading conf, no config file found')
    def getWeather_(self):
        #loc = Nominatim(user_agent="GetLoc")

        # entering the location name
        #getLoc = loc.geocode(self.local.text())

        # printing latitude and longitude
        #print("Latitude = ", getLoc.latitude)
        #print("Longitude = ", getLoc.longitude)
        local = self.local.text()

        if local == "":
            message = QMessageBox()
            message.setText("Error!\nNo location specified!\nTry again.")
            message.exec_()
        else:

            # Set the tabs to enabled, and say 'Loading...'
            self.tabWidget.setEnabled(True)
            self.weatherInfo.setEnabled(True)
            self.day1.setEnabled(True)
            self.day2.setEnabled(True)
            self.day3.setEnabled(True)
            self.day4.setEnabled(True)
            self.day5.setEnabled(True)
            self.day6.setEnabled(True)
            self.day7.setEnabled(True)
            self.day8.setEnabled(True)
            self.jsonBrowser.setEnabled(True)
            self.weatherInfo.setText("Loading...")
            self.day1.setText("Loading...")
            self.day2.setText("")
            self.day3.setText("")
            self.day4.setText("")
            self.day5.setText("")
            self.day6.setText("")
            self.day7.setText("")
            self.day8.setText("")
            self.jsonBrowser.setText("Loading...")

            # Get weather
            url = "https://weatherdbi.herokuapp.com/data/weather/" + str(local)
            out("debug@apiCaller", f"API request URL: {url}")
            resp = requests.get(url)
            out("debug@apiCaller", f"Server status: {str(resp.status_code)}")
            if not str(resp.content).__contains__("currentConditions"):
                out("error@apiCaller", "Error: Bad API response! Check your location.")
                message = QMessageBox()
                message.setText(
                    "Error!\nBad API response!\nCheck your location.")
                message.exec_()
                return
            self.jsonResp = json.loads(resp.content)
            #self.jsonResp = {'region': 'Logan, UT', 'currentConditions': {'dayhour': 'Tuesday 2:00 PM', 'temp': {'c': 18, 'f': 65}, 'precip': '1%', 'humidity': '23%', 'wind': {'km': 18, 'mile': 11}, 'iconURL': 'https://ssl.gstatic.com/onebox/weather/64/partly_cloudy.png', 'comment': 'Mostly cloudy'}, 'next_days': [{'day': 'Tuesday', 'comment': 'Partly cloudy', 'max_temp': {'c': 18, 'f': 65}, 'min_temp': {'c': 4, 'f': 39}, 'iconURL': 'https://ssl.gstatic.com/onebox/weather/48/partly_cloudy.png'}, {'day': 'Wednesday', 'comment': 'Sunny', 'max_temp': {'c': 24, 'f': 75}, 'min_temp': {'c': 7, 'f': 44}, 'iconURL': 'https://ssl.gstatic.com/onebox/weather/48/sunny.png'}, {'day': 'Thursday', 'comment': 'Partly cloudy', 'max_temp': {'c': 30, 'f': 86}, 'min_temp': {'c': 13, 'f': 55}, 'iconURL': 'https://ssl.gstatic.com/onebox/weather/48/partly_cloudy.png'}, {'day': 'Friday', 'comment': 'Partly cloudy', 'max_temp': {'c': 26, 'f': 79}, 'min_temp': {'c': 12, 'f': 53}, 'iconURL': 'https://ssl.gstatic.com/onebox/weather/48/partly_cloudy.png'}, {'day': 'Saturday', 'comment': 'Showers', 'max_temp': {'c': 18, 'f': 64}, 'min_temp': {'c': 7, 'f': 44}, 'iconURL': 'https://ssl.gstatic.com/onebox/weather/48/rain_light.png'}, {'day': 'Sunday', 'comment': 'Showers', 'max_temp': {'c': 16, 'f': 61}, 'min_temp': {'c': 4, 'f': 39}, 'iconURL': 'https://ssl.gstatic.com/onebox/weather/48/rain_light.png'}, {'day': 'Monday', 'comment': 'Showers', 'max_temp': {'c': 13, 'f': 56}, 'min_temp': {'c': 4, 'f': 39}, 'iconURL': 'https://ssl.gstatic.com/onebox/weather/48/rain_light.png'}, {'day': 'Tuesday', 'comment': 'Scattered showers', 'max_temp': {'c': 16, 'f': 61}, 'min_temp': {'c': 4, 'f': 39}, 'iconURL': 'https://ssl.gstatic.com/onebox/weather/48/rain_s_cloudy.png'}], 'contact_author': {'email': 'communication.with.users@gmail.com', 'auth_note': 'Mail me for feature requests, improvement, bug, help, ect... Please tell me if you want me to provide any other free easy-to-use API services'}, 'data_source': 'https://www.google.com/search?lr=lang_en&q=weather+in+logan,+utah'}
            self.actionExport_Raw_JSON.setEnabled(True)

            # parse json and find the data
            weather = []
            currCond = self.jsonResp["currentConditions"]
            weather.append(self.jsonResp["region"])
            weather.append(currCond["dayhour"])
            weather.append(currCond["temp"][self.jsonTemp])
            weather.append(currCond["comment"])
            weather.append(currCond["precip"])
            weather.append(currCond["wind"][self.jsonFmt])
            statImg = requests.get(currCond["iconURL"], allow_redirects=True)
            icon = Path("/tmp/cwt_status.png")
            icon.write_bytes(statImg.content)
            #print("\nThe current Temperature: " + str(currTemp))

            # show the data
            tab = self.tabWidget
            tab.setEnabled(True)
            label = self.weatherInfo
            #jsonViewer = self.jsonView
            self.fullWeather = "Day and Time: " + str(weather[1]) + "\nLocation: " + str(weather[0]) + "\nTemperature: " + str(
                weather[2]) + f"° {self.prettyTemp}" + "\nPrecipitation: " + str(weather[4]) + "\nWind: " + str(weather[5]) + f" {self.prettyWind}\nCondition: " + str(weather[3])
            label.setText(self.fullWeather)
            self.jsonBrowser.setEnabled(True)
            self.jsonBrowser.setText(str(self.jsonResp))
            self.actionSave_As.setEnabled(True)
            self.forecast = Forecast(self.jsonResp)
            self.day1.setText(self.forecast.mo_forecast)
            self.day2.setText(self.forecast.tu_forecast)
            self.day3.setText(self.forecast.we_forecast)
            self.day4.setText(self.forecast.th_forecast)
            self.day5.setText(self.forecast.fr_forecast)
            self.day6.setText(self.forecast.sa_forecast)
            self.day7.setText(self.forecast.su_forecast)
            self.day8.setText(self.forecast.mo1_forecast)

    def saveAs(self):
        name = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save File", '/weather.txt', '.txt')[0]
        if not name == "":
            file2write = open(name, 'w')
            file2write.write("Weather:\n\n" + self.fullWeather + "\n\nWeek Forecast:\n\n" +
                             f"{self.forecast.mo_forecast}\n{self.forecast.tu_forecast}\n{self.forecast.we_forecast}\n{self.forecast.th_forecast}\n{self.forecast.fr_forecast}\n{self.forecast.sa_forecast}\n{self.forecast.su_forecast}\n{self.forecast.mo1_forecast}\n")
            file2write.close()
        else:
            return

    def expJSON(self):
        name = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save File", '/weather.json', '.json')[0]
        if not name == "":
            file2write = open(name, 'w')
            file2write.write(str(self.jsonResp))
            file2write.close()
        else:
            return

    def openPrefs(self):
        self.prefs = prefs()
        self.loadPrefs()



class prefs(QWidget):
    if os.path.isfile(f"{os.path.expanduser('~')}/.config/weatherGui/preferences.txt"):
        conf = open(
            f"{os.path.expanduser('~')}/.config/weatherGui/preferences.txt", 'r')
        content = conf.readlines()

        fmt = content[0].split(" ")[1].strip()

        output = content[2].split(" ")[1].strip()

    def __init__(self):
        super(prefs, self).__init__()
        out("debug@prefs", "running preferences")
        uic.loadUi("weatherPrefs.ui", self)
        self.setWindowTitle("Preferences")

        self.themeList = list_themes()
        self.themePref.addItem("Default")
        self.themePref.addItems(self.themeList)

        if os.path.isfile(f"{os.path.expanduser('~')}/.config/weatherGui/preferences.txt"):
            conf = open(
                f"{os.path.expanduser('~')}/.config/weatherGui/preferences.txt", 'r')
            content = conf.readlines()

            self.fmt = content[0].split(" ")[1].strip()

            self.selectedFmt = self.fmtPref.currentText()
            self.selectedFmtIndex = self.fmtPref.currentIndex()
            if not self.selectedFmt == self.fmt:
                out("debug@format", "Setting format..")
                # self.fmtPref.setItemData(2, self.fmt) #self.fmtPref.findText(self.fmt), self.fmt)
                if self.fmt == "Imperial":
                    self.fmtPref.setItemText(0, "Imperial")
                    self.fmtPref.setItemText(1, "Metric")
                elif self.fmt == "Metric":
                    self.fmtPref.setItemText(0, "Metric")
                    self.fmtPref.setItemText(1, "Imperial")
                else:
                    print("error, bad value:", self.fmt)
                    print(self.fmt)
                    print(type(self.fmt))
            else:
                out("debug@format", "Continuing..")

            self.theme = content[1].split(" ")[1].strip()
            self.selectedTheme = self.themePref.currentText()
            self.selectedThemeIndex = self.themePref.currentIndex()
            if not self.selectedTheme == self.theme:
                apply_stylesheet(self, theme=self.theme)
            else:
                out("debug@theme", "Continuing..")

            self.output = content[2].split(" ")[1].strip()
            if self.fmt == "Imperial":
                self.jsonFmt = "mile"
                self.jsonTemp = "f"
                self.prettyTemp = "F"
                self.prettyWind = "mph"
            elif self.fmt == "Metric":
                self.jsonFmt = "km"
                self.jsonTemp = "c"
                self.prettyTemp = "C"
                self.prettyWind = "km/h"
            else:
                self.jsonFmt = "mile"
                self.jsonTemp = "f"
                self.prettyTemp = "F"
                self.prettyWind = "mph"
                message = QMessageBox()
                message.setText(
                    "Error:\nBad format config!\nIf you changed the config manually, please check it.")
                message.exec_()
        else:
            out("info@prefs", "No config file, not loading config.")

        self.cancel.clicked.connect(lambda: self.close())
        self.save.clicked.connect(lambda: self.save_())
        self.show()

    def save_(self):
        fmt = self.fmtPref.currentText()
        theme = self.themePref.currentText()
        output = self.outputPref.currentText()
        if not os.path.isdir(f"{os.path.expanduser('~')}/.config/weatherGui/"):
            os.mkdir(f"{os.path.expanduser('~')}/.config/weatherGui/")
        file2write = open(
            f"{os.path.expanduser('~')}/.config/weatherGui/preferences.txt", 'w')
        file2write.write(f"fmt: {fmt}\ntheme: {theme}\noutput: {output}")
        file2write.close()
        self.hide()

    def setPrefs(self):
        if os.path.isfile(f"{os.path.expanduser('~')}/.config/weatherGui/preferences.txt"):
            conf = open(
                f"{os.path.expanduser('~')}/.config/weatherGui/preferences.txt", 'r')
            content = conf.readlines()

            self.fmt = content[0].split(" ")[1].strip()
            self.theme = content[1].split(" ")[1].strip()
            self.output = content[2].split(" ")[1].strip()
            self.selectedTheme = self.themePref.currentText()
            if not self.selectedTheme == self.theme:
                apply_stylesheet(self, theme=self.theme)
        else:
            out("info@prefs", "No config file, not loading config.")

    def exitWindow(self):
        self.close()


def onClose(app):
    out("debug@prefs", "Closing prefs")
    app.aboutToQuit.connect(lambda: prefs.exitWindow())


def main():
    app = QApplication([])
    window = weatherGui()

    out("info@main", "running app..")
    #window.actionPrefs.triggered.connect(lambda: prefs())
    app.exec_()
    #app.aboutToQuit.connect(lambda: QWidgets.close())


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        out("info@main", "Closing...")
        exit()
