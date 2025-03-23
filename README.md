# e-ink-clock

## e-ink display docs
- https://www.waveshare.com/wiki/Pico-ePaper-2.9

## sync from local to device
```powershell
robocopy C:\repos\e-ink-clock\src D:\src /E /XD .git
```

## sync from device to local (use only if changes were made directly on device)
```powershell
robocopy D:\ C:\repos\e-ink-clock /E /XD .git
```