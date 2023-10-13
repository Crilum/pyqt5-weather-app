#!/usr/bin/env python3

from re import L, T
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtGui, QtWidgets
import requests
from geopy.geocoders import Nominatim
import json
from pathlib import Path
from time import ctime
import os
from qt_material import apply_stylesheet
from qt_material import list_themes

key = "YOUR_Open_Weather_Map_KEY_HERE"

def getWeatherEmoji(status_code, dt, sunrise, sunset):
    if list(str(status_code))[0] == "2":
        return "⛈️"
    elif list(str(status_code))[0] == "3":
        return "☔"
    elif list(str(status_code))[0] == "5":
        return "🌧️"
    elif list(str(status_code))[0] == "6":
        return "🌨️"
    elif str(status_code) == "741":
        return "🌫️"
    elif str(status_code) == "781":
        return "🌪️"
    elif list(str(status_code))[0] == "7":
        return "🌫️"
    elif str(status_code) == "800" and dt > sunrise:
        return "☀️"
    elif str(status_code) == "800" and dt < sunrise or status_code == "800" and dt > sunset:
        return "☽"
    elif str(status_code) == "801":
        return "🌤️"
    elif str(status_code) == "802":
        return "⛅"
    elif str(status_code) == "803":
        return "🌥️"
    elif str(status_code) == "804":
        return "☁️"
    else:
        out("debug@getWeatherEmoji", "Error: Unmapped status code: " + str(status_code))
        return "❓"
    
def makeFirstUpper(string):
        UpperLetter = list(string)[0].upper()
        theRest = list(string)
        theRest.remove(UpperLetter.lower())
        theRest.insert(0, UpperLetter)
        return ''.join(theRest)
    
class Forecast():
    def __init__(self, json):

        if os.path.isfile(f"{os.path.expanduser('~')}/.config/weatherGui/preferences.txt"):
            conf = open(
                f"{os.path.expanduser('~')}/.config/weatherGui/preferences.txt", 'r')
            content = conf.readlines()
            self.fmt = content[0].split(" ")[1].strip()
            out("debug@format", f"Setting format to '{self.fmt}'..")
            if self.fmt == "Imperial":
                self.jsonFmt = "imperial"
                self.jsonTemp = "f"
                self.prettyTemp = "F"
                self.prettyWind = "mph"
            elif self.fmt == "Metric":
                self.jsonFmt = "metric"
                self.jsonTemp = "c"
                self.prettyTemp = "C"
                self.prettyWind = "km/h"
            elif self.fmt == "Standard":
                self.jsonFmt = "standard"
                self.jsonTemp = "k"
                self.prettyTemp = "K"
                self.prettyWind = "m/sec"
            else:
                self.jsonFmt = "imperial"
                self.jsonTemp = "f"
                self.prettyTemp = "F"
                self.prettyWind = "mph"
                message = QMessageBox()
                message.setText(
                    "Error:\nBad format config!\nIf you changed the config manually, please check it.")
                message.exec_()
        else:
            out('debug@format', 'Not loading conf, conffile not found')
        self.json = json
        self.forecast_days = json["daily"]
        self.currCond = json["current"]
        self.weather = []
        for i in range(0, 8):
            self.weather.append({
                "day": f'{ctime(self.forecast_days[i]["dt"]).split(" ")[0]}, {ctime(self.forecast_days[i]["dt"]).split(" ")[1]} {ctime(self.forecast_days[i]["dt"]).split(" ")[2]}',
                "high": round(self.forecast_days[i]["temp"]["max"]),
                "low": round(self.forecast_days[i]["temp"]["min"]),
                "condition": f'{makeFirstUpper(self.forecast_days[i]["weather"][0]["description"])} {getWeatherEmoji(self.forecast_days[i]["weather"][0]["id"], self.forecast_days[i]["dt"], self.forecast_days[i]["sunrise"], self.forecast_days[i]["sunset"])}'
            })


def out(type, msg):
    if os.path.isfile(f"{os.path.expanduser('~')}/.config/weatherGui/preferences.txt"):
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
    else:
        print(f"{type}| {str(msg)}")


class weatherGui(QMainWindow):
    def __init__(self):
        super(weatherGui, self).__init__()
        out("info@weatherGui", "loading ui file...")
        uic.loadUi("weather.ui", self)
        self.setWindowTitle("Weather")
        self.loadPrefs()
        
        self.show()

        self.getWeather.clicked.connect(lambda: self.getWeather_())
        self.actionClose.triggered.connect(lambda: exit())
        self.actionSave_As.triggered.connect(lambda: self.saveAs())
        self.actionPrefs.triggered.connect(lambda: self.openPrefs())
        self.actionExport_Raw_JSON.triggered.connect(lambda: self.expJSON())
        self.actionReload_settings.triggered.connect(lambda: self.loadPrefs())

    def getGeoLocal(city, self):
        url = f"https://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={key}"
        out("debug@apiCaller", f"location API request URL: {url}")
        resp = requests.get(url)
        out("debug@apiCaller", f"Server status: {str(resp.status_code)}")
        if not str(resp.content).__contains__("current"):
            out("error@apiCaller", "Error: Bad Location API response! Check your location.")
            out("debug@apiCaller", str(resp.content))
            message = QMessageBox()
            message.setText(
                "Error!\nBad Location API response!\nCheck your location.")
            message.exec_()
            return
        self.jsonResp = json.loads(resp.content)
        return self.jsonResp[0]

    def getPrecipHourly(self, json):
        if "rain" in json["current"]:
            return json["current"]["rain"]["1h"]
        else:
            return "No rain."

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
                self.jsonFmt = "imperial"
                self.jsonTemp = "f"
                self.prettyTemp = "F"
                self.prettyWind = "mph"
            elif self.fmt == "Metric":
                self.jsonFmt = "metric"
                self.jsonTemp = "c"
                self.prettyTemp = "C"
                self.prettyWind = "km/h"
            elif self.fmt == "Standard":
                self.jsonFmt = "standard"
                self.jsonTemp = "k"
                self.prettyTemp = "K"
                self.prettyWind = "m/sec"
            else:
                self.jsonFmt = "imperial"
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
        localInput = self.local.text()

        if localInput == "":
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

            # Get Location

            loc = Nominatim(user_agent="Crilum-PyQt5-Weather-App")

            getLoc = loc.geocode(self.local.text(), addressdetails=True)

            print(getLoc.raw)

            # printing latitude and longitude
            #print("Latitude = ", getLoc.latitude)
            #print("Longitude = ", getLoc.longitude)

            """url = f"https://api.openweathermap.org/geo/1.0/direct?q={str(localInput)}&limit=1&appid={key}"
            resp = requests.get(url)
            out("debug@apiCaller", f"Server status: {str(resp.status_code)}")
            if not str(resp.content).__contains__("lat"):
                out("error@apiCaller", f"Error: Bad Location API response! Check your location.\n\nServer response: {resp.status_code}\n{resp.content}")
                message = QMessageBox()
                message.setText(
                    "Error!\nBad Location API response!\nCheck your location.")
                message.exec_()
                return
            out("debug@apiCaller", f"Geolocation Response: {json.loads(resp.content)}\nAPI request URL: {url}")
            self.localJSON = json.loads(resp.content)[0]"""
  
            # Get weather
            url = f"https://api.openweathermap.org/data/3.0/onecall?lat={getLoc.latitude}&lon={getLoc.longitude}&units={self.fmt}&appid={key}"
            out("debug@apiCaller", f"API request URL: {url}")
            resp = requests.get(url)
            out("debug@apiCaller", f"Server status: {str(resp.status_code)}")
            if not str(resp.content).__contains__("current"):
                out("error@apiCaller", f"Error: Bad API response! Check your location.\n\nServer response: {resp.status_code}\n{resp.content}")
                message = QMessageBox()
                message.setText(
                    "Error!\nBad API response!\nCheck your location.")
                message.exec_()
                return
            self.jsonResp = json.loads(resp.content)
            # Sample response for testing
            # self.jsonResp = {}
            self.actionExport_Raw_JSON.setEnabled(True)

            # parse json and find the data
            weather = []
            currCond = self.jsonResp["current"]
            weather.append(f'{getLoc.raw["address"]["city"]}, {getLoc.raw["address"]["state"]}, {getLoc.raw["address"]["country_code"]}')    # self.localJSON["name"] + ", " + self.localJSON["state"])
            weather.append(ctime(currCond["dt"]))
            weather.append(round(currCond["temp"]))
            weather.append(f'{makeFirstUpper(currCond["weather"][0]["description"])} {getWeatherEmoji(currCond["weather"][0]["id"], currCond["dt"], currCond["sunrise"], currCond["sunset"])}')
            weather.append(f'{self.getPrecipHourly(self.jsonResp)}')
            weather.append(round(currCond["wind_speed"]))
            statImg = requests.get(f"https://openweathermap.org/img/wn/{currCond['weather'][0]['icon']}d@2x.png", allow_redirects=True)
            icon = Path("/tmp/cwt_status.png")
            icon.write_bytes(statImg.content)

            # show the data
            tab = self.tabWidget
            tab.setEnabled(True)
            label = self.weatherInfo
            self.fullWeather = "Day and Time: " + str(weather[1]) + "\nLocation: " + str(weather[0]) + "\nTemperature: " + str(
                weather[2]) + f"° {self.prettyTemp}" + "\nPrecipitation: " + str(weather[4]) + "\nWind: " + str(weather[5]) + f" {self.prettyWind}\nCondition: " + str(weather[3])
            label.setText(self.fullWeather)
            self.jsonBrowser.setEnabled(True)
            self.jsonBrowser.setText(str(self.jsonResp))
            self.actionSave_As.setEnabled(True)
            self.forecast = Forecast(self.jsonResp)
            day_list = ["day1", "day2", "day3", "day4", "day5", "day6", "day7", "day8"]
            for i in range(0, 8):
                getattr(self, day_list[i]).setText(self.forecast.weather[i]["day"])
                getattr(self, f'{day_list[i]}_high').setText(f'High:  {self.forecast.weather[i]["high"]}°')
                getattr(self, f'{day_list[i]}_low').setText(f'Low:  {self.forecast.weather[i]["low"]}°')
                getattr(self, f'{day_list[i]}_condition').setText(self.forecast.weather[i]["condition"])

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
                    self.fmtPref.setItemText(2, "Standard (Kelvin)")
                elif self.fmt == "Metric":
                    self.fmtPref.setItemText(0, "Metric")
                    self.fmtPref.setItemText(1, "Imperial")
                    self.fmtPref.setItemText(2, "Standard (Kelvin)")
                elif self.fmt == "Standard (Kelvin)":
                    self.fmtPref.setItemText(2, "Standard (Kelvin)")
                    self.fmtPref.setItemText(0, "Metric")
                    self.fmtPref.setItemText(1, "Imperial")
                else:
                    out("error@format", "error, bad value:" + self.fmt)
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
            elif self.fmt == "Standard":
                self.jsonFmt = "standard"
                self.jsonTemp = "k"
                self.prettyTemp = "K"
                self.prettyWind = "m/sec"
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
