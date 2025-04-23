# e-ink-clock
 
## sync from device to local
```powershell
robocopy D:\ C:\repos\e-ink-clock /E /XD .git
```

## sync from local to device
```powershell
robocopy C:\repos\e-ink-clock\src D:\src /E /XD .git
```