from skyfield.api import Topos, load, utc, EarthSatellite
from datetime import timedelta
import datetime
import math
import pytz
import ephem

def FIND_SATE(line1, line2, satellite_name):
    ts = load.timescale()
    line1 = line1
    line2 = line2
    satellite = EarthSatellite(line1, line2, satellite_name, ts)
    return satellite, 1


def find_lines_after_string(filename, search_string):
    line1 = None
    line2 = None
    with open(filename, 'r') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if search_string in line:
                if i+1 < len(lines):
                    line1 = lines[i+1].strip()
                if i+2 < len(lines):
                    line2 = lines[i+2].strip()
                break
    return line1, line2
def CAL_PASS_TIME(target_satellite, observer_lat, observer_lon, observer_elevation, tz="Asia/Shanghai"):
    topos = Topos(latitude_degrees=observer_lat, longitude_degrees=observer_lon,
                  elevation_m=observer_elevation)
    # 获取当前时间并创建Skyfield的时间对象
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    ts = load.timescale()
    t0 = ts.utc(now)
    t1 = t0 + timedelta(days=2)  # 查找2天内过境时间
    passes = target_satellite.find_events(topos, t0, t1)
    # 获取当地时区
    local_tz = pytz.timezone(tz)

    pass_times = []
    departure_times = []
    if not passes[0]:
        return None, None
    # 打印下一次过境的当地时间和离境时间
    for time, event in zip(passes[0], passes[1]):
        if event == 0:  # 0表示升，1表示降
            # 将UTC时间转换为当地时间
            local_time = time.utc_datetime().replace(tzinfo=pytz.utc).astimezone(local_tz)
            pass_times.append(local_time.strftime('%Y-%m-%d %H:%M:%S'))
        elif event == 2:
            departure_time_utc = time.utc_datetime().replace(tzinfo=pytz.utc).astimezone(local_tz)
            departure_times.append(departure_time_utc.strftime('%Y-%m-%d %H:%M:%S'))

    return pass_times, departure_times

def CAL_DATA(satellite,line1,line2,observer_lon,observer_lat,observer_elevation,data,UP_HZ,DOWN_HZ):


    # 创建观测者对象并设置位置和时间
    observer = ephem.Observer()
    observer.lon = str(observer_lon)
    observer.lat =str( observer_lat)
    observer.elevation = observer_elevation
    observer.date = data  # 设置为当前UTC时间

    satellite.compute(observer)
    # 获取卫星的速度（单位：km/s）
    range_rate = satellite.range_velocity / 1000
    # print("速度:", range_rate, "km/s")
    UP_SHIFT = range_rate / 299792.458 * UP_HZ  # 单位：Hz
    DOWN_SHIFT = -range_rate / 299792.458 * DOWN_HZ  # 单位：Hz
    DIS = satellite.range / 1000  # 单位从m转换为km
    return round(math.degrees(float(satellite.az)),2),   round(math.degrees(float(satellite.alt)),2),round(UP_SHIFT,0),round(DOWN_SHIFT,0),round(DIS,2)
