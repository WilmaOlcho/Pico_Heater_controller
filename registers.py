class RegisterCallbacks:
    reg_set_heater1_power:callable=None
    reg_set_heater2_power:callable=None
    reg_set_heater3_power:callable=None
    reg_set_heater4_power:callable=None
    reg_set_grid_frequency:callable=None
    reg_set_status:callable=None

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

callback = RegisterCallbacks()

register_definitions = {
    "HREGS": {
        "Heater1_power": {
            "register": 0,
            "len": 1,
            "val": 0,
            "on_set_cb": callback.Set_Heater1_power
        },
        "Heater2_power": {
            "register": 1,
            "len": 1,
            "val": 0,
            "on_set_cb": callback.Set_Heater2_power
        },
        "Heater3_power": {
            "register": 2,
            "len": 1,
            "val": 0,
            "on_set_cb": callback.Set_Heater3_power
        },
        "Heater4_power": {
            "register": 3,
            "len": 1,
            "val": 0,
            "on_set_cb": callback.Set_Heater4_power
        },
        "Grid_frequency": {
            "register": 4,
            "len": 1,
            "val": 50,
            "on_set_cb": callback.Set_Grid_frequency
        },
        "Status": {
            "register": 5,
            "len": 1,
            "val": 0,
            "on_set_cb": callback.Set_Status
        },
        "On_chip_temp": {
            "register": 6,
            "len": 1,
            "val": 0
        }
    }
}
