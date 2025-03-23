# e-ink-clock

## Docs
- Circuit Python: https://circuitpython.org/board/raspberry_pi_pico2_w/
- Circuit Python Lib: https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases
- E-Ink: https://www.waveshare.com/wiki/Pico-ePaper-2.9

## sync from local to device
```powershell
robocopy C:\repos\e-ink-clock\src D:\src /E /XD .git
```

## sync from device to local (use only if changes were made directly on device)
```powershell
robocopy D:\ C:\repos\e-ink-clock /E /XD .git
```