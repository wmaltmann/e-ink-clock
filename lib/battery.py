from machine import ADC, Pin

SCALING_FACTOR = 1.18

class Battery:
    def __init__(self):
        self._adc_pin = Pin(28, Pin.IN)
        self._adc = ADC(28)
        self.voltage = 0.0
        self.percentage = 50

    def read(self):
        raw = self._adc.read_u16()
        self.voltage = raw * (3.3 / 65535) * (2 * 1.07)
       
        if self.voltage >= 4.2:
            self.percentage = 100
        elif self.voltage <= 3.0:
            self.percentage = 0
        else:
            self.percentage = int(-6168 + 7326 * self.voltage - 3224 * (self.voltage ** 2) + 620 * (self.voltage ** 3) - 43.5 * (self.voltage ** 4))
