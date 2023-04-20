class RegisterCallbacks:
    reg_set_heater1_power:callable=None
    reg_set_heater2_power:callable=None
    reg_set_heater3_power:callable=None
    reg_set_heater4_power:callable=None
    reg_set_grid_frequency:callable=None
    reg_set_status:callable=None
    reg_set_stop_processing:callable=None

    def Set_Heater1_power(self, reg_type:str, address:int, val:int):
        if self.reg_set_heater1_power:
            self.reg_set_heater1_power(reg_type, address, val)

    def Set_Heater2_power(self, reg_type:str, address:int, val:int):
        if self.reg_set_heater2_power:
            self.reg_set_heater2_power(reg_type, address, val)

    def Set_Heater3_power(self, reg_type:str, address:int, val:int):
        if self.reg_set_heater3_power:
            self.reg_set_heater3_power(reg_type, address, val)

    def Set_Heater4_power(self, reg_type:str, address:int, val:int):
        if self.reg_set_heater4_power:
            self.reg_set_heater4_power(reg_type, address, val)

    def Set_Grid_frequency(self, reg_type:str, address:int, val:int):
        if self.reg_set_grid_frequency:
            self.reg_set_grid_frequency(reg_type, address, val)

    def Set_Status(self, reg_type:str, address:int, val:int):
        if self.reg_set_status:
            self.reg_set_status(reg_type, address, val)

    def Set_Stop_processing(self, reg_type:str, address:int, val:int):
        if self.reg_set_stop_processing:
            self.reg_set_stop_processing(reg_type, address, val)

callback = RegisterCallbacks()

register_definitions = {
    "HREGS": {
        "Heater1_power": {
            "register": 0,
            "len": 1,
            "val": 0,
            "on_set_cb": callback.Set_Heater1_power,
            "value_range_min": 0,
            "value_range_max": 100
        },
        "Heater2_power": {
            "register": 1,
            "len": 1,
            "val": 0,
            "on_set_cb": callback.Set_Heater2_power,
            "value_range_min": 0,
            "value_range_max": 100
        },
        "Heater3_power": {
            "register": 2,
            "len": 1,
            "val": 0,
            "on_set_cb": callback.Set_Heater3_power,
            "value_range_min": 0,
            "value_range_max": 100
        },
        "Heater4_power": {
            "register": 3,
            "len": 1,
            "val": 0,
            "on_set_cb": callback.Set_Heater4_power,
            "value_range_min": 0,
            "value_range_max": 100
        },
        "Grid_frequency": {
            "register": 4,
            "len": 1,
            "val": 50,
            "on_set_cb": callback.Set_Grid_frequency,
            "values_specified": [50,60]
        },
        "Status": {
            "register": 5,
            "len": 1,
            "val": 0,
            "on_set_cb": callback.Set_Status,
            "value_range_min": 0x00,
            "value_range_max": 0x0F
        },
        "On_chip_temp": {
            "register": 6,
            "len": 1,
            "val": 0
        },
        "Logfile_size": {
            "register": 10,
            "len": 1,
            "val": 0
        },
        "Logfile_readline": {
            "register": 11,
            "len": 40,
            "val": 0
        },
        "Logfile_readline_index": {
            "register": 12,
            "len": 1,
            "val": 0
        },
        "Stop_processing": {
            "register": 2137,
            "len": 1,
            "val": 0,
            "on_set_cb": callback.Set_Stop_processing
        }
    }
}
