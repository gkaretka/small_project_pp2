from datetime import datetime, date
from math import floor


class GPRMC:

    def __init__(self, row_data):
        slitted_data = str(row_data).split(",")
        self.name = slitted_data[0]

        # create datetime object based
        date_year = "19" + str(slitted_data[9])[4:6] \
            if int(str(slitted_data[9])[4:6]) > int(str(date.today().year)[-2:]) \
            else "20" + str(slitted_data[9])[4:6]
        self.time_stamp = datetime(int(date_year),
                                   int(str(slitted_data[9])[2:4]),
                                   int(str(slitted_data[9])[0:2]),
                                   int(str(slitted_data[1])[0:2]),
                                   int(str(slitted_data[1])[2:4]),
                                   int(str(slitted_data[1])[4:6]))

        self.validity = slitted_data[2]
        self.north_south = slitted_data[4]
        self.east_west = slitted_data[6]
        self.speed_knots = slitted_data[7]
        self.course = slitted_data[8]
        self.date_stamp = slitted_data[9]
        self.variation = slitted_data[10]

        self.snr_list = []

        lat_sign = -1 if self.north_south == "S" else 1
        long_sign = -1 if self.east_west == "W" else 1

        self.current_latitude = floor(float(slitted_data[3]) * lat_sign / 100) \
                              + float(slitted_data[3]) * lat_sign % 100 / 60
        self.current_longitude = floor(float(slitted_data[5]) * long_sign / 100) \
                               + float(slitted_data[5]) * long_sign % 100 / 60

    def add_snr(self, snr):
        self.snr_list.append(snr)

    def __repr__(self):
        return "Timestamp: " + str(self.time_stamp) \
               + ", lat: " + str(self.current_latitude) \
               + " , long:" + str(self.current_longitude) + "\n"

    def __str__(self):
        return "Timestamp: " + str(self.time_stamp) \
               + ", lat: " + str(self.current_latitude) \
               + " , long:" + str(self.current_longitude)


class GPGGA:

    def __init__(self, row_data):
        slitted_data = str(row_data).split(",")
        self.name = slitted_data[0]
        self.time_stamp = slitted_data[1]
        self.altitude = slitted_data[9]

    def __repr__(self):
        return "Timestamp: " + str(self.time_stamp) \
               + ", alt: " + str(self.altitude) + "\n"

    def __str__(self):
        return "Timestamp: " + str(self.time_stamp) \
               + ", alt: " + str(self.altitude)


class GPGSV:
    def __init__(self, row_data):
        slitted_data = str(row_data).split(",")
        self.name = slitted_data[0]
        self.snr = slitted_data[7]

    def __str__(self):
        return "SNR: " + str(self.snr)


class GPVTG:

    def __init__(self, row_data):
        slitted_data = str(row_data).split(",")
        self.name = slitted_data[0]
        self.speed_knots = slitted_data[5]
        self.speed_kmph = slitted_data[7]

    def __repr__(self):
        return "Speed knots: " + str(self.speed_knots) \
               + ", speed kmph: " + str(self.speed_kmph) + "\n"

    def __str__(self):
        return "Speed knots: " + str(self.speed_knots) \
               + ", speed kmph: " + str(self.speed_kmph)
