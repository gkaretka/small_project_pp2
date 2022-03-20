'''
  __ _ _ __  ___ 
 / _` | '_ \/ __|
| (_| | |_) \__ \
 \__, | .__/|___/
  __/ | |        
 |___/|_|       
           _       _ _ _ _            
          | |     | | (_) |           
 ___  __ _| |_ ___| | |_| |_ ___  ___ 
/ __|/ _` | __/ _ \ | | | __/ _ \/ __|
\__ \ (_| | ||  __/ | | | ||  __/\__ \
|___/\__,_|\__\___|_|_|_|\__\___||___/

 In our devices file there are used 5 NMEA codes 
'$GPGSA' - GPS DOP and active satellites (don't care)
'$GPGSV' - GPS Satellites in view        (SNR)
'$GPRMC' - Recommended minimum specific GPS/Transit data (location)
'$GPVTG' - Track Made Good and Ground Speed (speed)
'$GPGGA' - Global Positioning System Fix Data (location)

$GPRMC and $GPGGA should contain the same data, 
'''

from processing import nmea_parser
import folium
import math


def main(file):
    raw_data = file.readlines()
    pos_entries = nmea_parser.parse(raw_data)
    return calculate_results_and_maps(pos_entries)


def generate_colormap():
    colors = []
    val = 0x00ff00
    for i in range(0, 255):
        val = val + (1 << 16)
        colors.append(val)

    for i in range(255, 0, -1):
        val = val - (1 << 8)
        colors.append(val)

    return colors


def min_max_speed_altitude(entries):
    min_altitude = 80000
    max_altitude = -80000
    min_speed = 80000
    max_speed = -80000
    average_long = 0
    average_lat = 0

    for i in range(0, len(entries)):
        alt = float(entries[i].get_altitude())
        speed = float(entries[i].get_speed_kmph())

        average_lat += entries[i].get_lat()
        average_long += entries[i].get_long()

        if alt < min_altitude:
            min_altitude = alt
        if alt > max_altitude:
            max_altitude = alt

        if speed < min_speed:
            min_speed = speed
        if speed > max_speed:
            max_speed = speed

    average_long /= len(entries)
    average_lat /= len(entries)

    return min_altitude, max_altitude, min_speed, max_speed, average_lat, average_long


'''
    a = sin²(Δφ / 2) + cos
    φ1 ⋅ cos
    φ2 ⋅ sin²(Δλ / 2)
    c = 2 ⋅ atan2( √a, √(1−a) )
    d = R ⋅ c
    
    where φ is latitude, λ is longitude, R is earth’s radius (mean radius = 6,371km);
    note that angles need to be in radians to pass to trig functions!
'''


def calculate_length_of_track_km(entries):
    r = 6371000
    track_length = 0
    delta_length = []
    for i in range(0, len(entries) - 1):
        loc1_rad_lat = math.radians(float(entries[i].get_lat()))
        loc2_rad_lat = math.radians(float(entries[i + 1].get_lat()))

        delta_rad_lat = math.radians(float(entries[i + 1].get_lat()) - float(entries[i].get_lat()))
        delta_rad_long = math.radians(float(entries[i + 1].get_long()) - float(entries[i].get_long()))

        a = math.sin(delta_rad_lat / 2) ** 2 + math.cos(loc1_rad_lat) \
            * math.cos(loc2_rad_lat) * math.sin(delta_rad_long / 2) ** 2

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        segment_length = r * c
        track_length += segment_length
        delta_length.append(segment_length)

    return track_length, delta_length


def calculate_results_and_maps(entries):
    min_altitude, max_altitude, min_speed, max_speed, average_lat, average_long = min_max_speed_altitude(entries)
    max_snr = 99 #dB according to provided information max snr is 99dB
    
    coordinates = []
    for i in range(0, len(entries)):
        coordinates.append([entries[i].get_lat(), entries[i].get_long()])

    # color segments according to speed
    altitude_colormap = []
    speed_colormap = []
    snr_colormap = []
    colors = generate_colormap()
    for i in range(0, len(entries)):
        speed_colormap.append(math.floor((float(entries[i].get_speed_kmph())- min_speed) * (len(colors)-1) / (max_speed-min_speed)))
        
        altitude_colormap.append(\
            math.floor((float(entries[i].get_altitude())-min_altitude) * (len(colors)-1) / (max_altitude-min_altitude)))
        
        snr_colormap.append(math.floor(float(entries[i].get_snr_average()) * (len(colors)-1) / max_snr))

    altitude_map = folium.Map(location=[average_lat, average_long], zoom_start=13)
    speed_map = folium.Map(location=[average_lat, average_long], zoom_start=13)
    snr_map = folium.Map(location=[average_lat, average_long], zoom_start=13)

    # add start and end
    folium.Marker(coordinates[0], popup='<i>Start</i>').add_to(altitude_map)
    folium.Marker(coordinates[len(coordinates) - 1], popup='<i>End</i>').add_to(altitude_map)

    folium.Marker(coordinates[0], popup='<i>Start</i>').add_to(speed_map)
    folium.Marker(coordinates[len(coordinates) - 1], popup='<i>End</i>').add_to(speed_map)

    folium.Marker(coordinates[0], popup='<i>Start</i>').add_to(snr_map)
    folium.Marker(coordinates[len(coordinates) - 1], popup='<i>End</i>').add_to(snr_map)

    # convert numbers to hex colors
    hex_format_colors = list(map(lambda color: "#"+(6-len(hex(color)[2:]))*"0"+str(hex(color)[2:]), colors))

    for i in range(0, len(coordinates)-2):
        folium.PolyLine(locations=(coordinates[i], coordinates[i+1]),
                        tooltip=str(entries[i].get_altitude()),
                        opacity=1,
                        color=hex_format_colors[altitude_colormap[i]],
                        weigth=6).add_to(altitude_map)

        folium.PolyLine(locations=(coordinates[i], coordinates[i + 1]),
                        tooltip=str(entries[i].get_speed_kmph()),
                        opacity=1,
                        color=hex_format_colors[speed_colormap[i]],
                        weigth=6).add_to(speed_map)

        folium.PolyLine(locations=(coordinates[i], coordinates[i + 1]),
                        tooltip=str(entries[i].get_snr_average()),
                        opacity=1,
                        color=hex_format_colors[snr_colormap[i]],
                        weigth=6).add_to(snr_map)

    results = {
               "altitude_map": altitude_map,
               "speed_map": speed_map,
               'snr_map': snr_map,
               "altitudes": list(map(lambda ents: ents.get_altitude(), entries)),
               "speeds": list(map(lambda ents: ents.get_speed_kmph(), entries)),
               "datetimes": list(map(lambda ents: ents.get_timestamp(), entries)),
               "track_length": calculate_length_of_track_km(entries),
               }

    return results
