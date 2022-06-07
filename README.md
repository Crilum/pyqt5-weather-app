# pyqt5-weather-app
A simple weather app written in PyQt5

<br>

![](https://github.com/Crilum/pyqt5-weather-app/raw/main/res/weather-app-showoff.gif)

## To run
```bash
git clone https://github.com/Crilum/pyqt5-weather-app
cd pyqt5-weather-app
python3 weatherUi.py
```
Note: `weatherUi.py` must be run in the same directory as the ui files.

## Issues
Because the API used in this app is free, sometimes, near the end of the month, it runs out of free Heroku Dynos. If you get an error about a bad API response, you can check if it legitimate by going to https://weatherdbi.herokuapp.com.
If you get a page that says `Application Error`, chances are the API ran out of free Dynos.

##### Solution
The number of available Heroku Dynos resets at the beginning of each month, so you might just have to wait.. Sorry.


## Credits
- [weatherDB](https://weatherdbi.herokuapp.com) - Awesome API!

