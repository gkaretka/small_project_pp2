from processing.nmea_time_entries import GPRMC, GPGGA, GPVTG, GPGSV

nmea_codes_length = 7


class PositioningData:

    def get_lat(self):
        return self.gprmc_obj.current_latitude

    def get_all_snr_samples(self):
        return self.gprmc_obj.snr_list

    def get_snr_average(self):
        return sum(map(lambda obj: float(obj.snr), self.gprmc_obj.snr_list)) / len(self.gprmc_obj.snr_list)

    def get_long(self):
        return self.gprmc_obj.current_longitude

    def get_timestamp(self):
        return self.gprmc_obj.time_stamp

    def get_datestamp(self):
        return self.gprmc_obj.date_stamp

    def get_altitude(self):
        return self.gpgga_obj.altitude

    def get_speed_knots(self):
        return self.gprmc_obj.speed_knots

    def get_speed_kmph(self):
        return self.gpvtg_obj.speed_kmph

    def get_speed_knots_gpgvt(self):
        return self.gpvtg_obj.speed_knots

    def __init__(self, gprmc, gpgga, gpvtg):
        self.gprmc_obj = gprmc
        self.gpgga_obj = gpgga
        self.gpvtg_obj = gpvtg


def resolve_snr_sentences(sentences_to_resolve, lat, long):
    for i in range(0, len(sentences_to_resolve)-1):
        sentences_to_resolve[i].parent_location_lat = lat
        sentences_to_resolve[i].parent_location_long = long


def parse(raw_data):
    nmea_sentences = []
    unresolved_snr_sentences = []
    for i in range(0, len(raw_data)):
        code = raw_data[i][0:nmea_codes_length - 1]
        if code == "$GPRMC":
            cur_gprmc_obj = GPRMC(raw_data[i])

            if len(unresolved_snr_sentences) > 0:
                for usnrs in unresolved_snr_sentences:
                    cur_gprmc_obj.add_snr(usnrs)
                unresolved_snr_sentences.clear()
            nmea_sentences.append(cur_gprmc_obj)
        elif code == "$GPGGA":
            nmea_sentences.append(GPGGA(raw_data[i]))
        elif code == "$GPVTG":
            nmea_sentences.append(GPVTG(raw_data[i]))
        elif code == "$GPGSV":
            unresolved_snr_sentences.append(GPGSV(raw_data[i]))

    position_data = []
    for i in range(0, len(nmea_sentences)-2):
        if nmea_sentences[i].name == "$GPRMC":
            position_data.append(
                PositioningData(gprmc=nmea_sentences[i], gpvtg=nmea_sentences[i+1], gpgga=nmea_sentences[i+2])
            )

    return position_data
