class Timezones:
    _timezones = {
        "BIT": {"name": "Baker Island Time", "offset": -43200},
        "SST": {"name": "Samoa Standard Time", "offset": -39600},
        "HAST": {"name": "Hawaii-Aleutian Standard Time", "offset": -36000},
        "MIT": {"name": "Marquesas Islands Time", "offset": -34200},
        "AKST": {"name": "Alaska Standard Time", "offset": -32400},
        "PST": {"name": "Pacific Standard Time", "offset": -28800},
        "MST": {"name": "Mountain Standard Time", "offset": -25200},
        "CST": {"name": "Central Standard Time", "offset": -21600},
        "EST": {"name": "Eastern Standard Time", "offset": -18000},
        "AST": {"name": "Atlantic Standard Time", "offset": -14400},
        "NST": {"name": "Newfoundland Standard Time", "offset": -12600},
        "ART": {"name": "Argentina Time", "offset": -10800},
        "GST": {"name": "South Georgia Time", "offset": -7200},
        "AZOT": {"name": "Azores Standard Time", "offset": -3600},
        "GMT": {"name": "Greenwich Mean Time", "offset": 0},
        "CET": {"name": "Central European Time", "offset": 3600},
        "EET": {"name": "Eastern European Time", "offset": 7200},
        "MSK": {"name": "Moscow Standard Time", "offset": 10800},
        "IRST": {"name": "Iran Standard Time", "offset": 12600},
        "GST+4": {"name": "Gulf Standard Time", "offset": 14400},
        "AFT": {"name": "Afghanistan Time", "offset": 16200},
        "PKT": {"name": "Pakistan Standard Time", "offset": 18000},
        "IST": {"name": "Indian Standard Time", "offset": 19800},
        "NPT": {"name": "Nepal Time", "offset": 20700},
        "BST": {"name": "Bangladesh Standard Time", "offset": 21600},
        "MMT": {"name": "Myanmar Time", "offset": 23400},
        "ICT": {"name": "Indochina Time", "offset": 25200},
        "CST+8": {"name": "China Standard Time", "offset": 28800},
        "ACWST": {"name": "Australian Central Western Standard Time", "offset": 31500},
        "JST": {"name": "Japan Standard Time", "offset": 32400},
        "ACST": {"name": "Australian Central Standard Time", "offset": 34200},
        "AEST": {"name": "Australian Eastern Standard Time", "offset": 36000},
        "LHST": {"name": "Lord Howe Standard Time", "offset": 37800},
        "SBT": {"name": "Solomon Islands Time", "offset": 39600},
        "NZST": {"name": "New Zealand Standard Time", "offset": 43200},
        "CHAST": {"name": "Chatham Islands Time", "offset": 45900},
        "TKT": {"name": "Tokelau Time", "offset": 46800},
        "LINT": {"name": "Line Islands Time", "offset": 50400},
    }

    @staticmethod
    def all():
        return Timezones._timezones

    @staticmethod
    def key_from_name(name):
        for key, value in Timezones._timezones.items():
            if value["name"].lower() == name.lower():
                return key
        return "CST"

    @staticmethod
    def offset_from_name(name: str):
        for value in Timezones._timezones.values():
            if value["name"].lower() == name.lower():
                return int(value["offset"])
        return -21600

    @staticmethod
    def offset_from_key(key: str):
        data = Timezones._timezones.get(key.upper())
        if data:
            return int(data["offset"])
        return -21600
