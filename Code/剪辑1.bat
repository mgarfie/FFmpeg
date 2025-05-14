@echo off
setlocal enabledelayedexpansion

set a=3

for /L %%b in (1,1,20) do (
    set /A a=!a!+1
    ffmpeg -i 1.mp4 -ss 20 -t 10 -c:v copy -c:a copy !a!.mp4
)
