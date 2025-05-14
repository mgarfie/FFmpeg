@echo off
setlocal enabledelayedexpansion

set ss=20

for /L %%i in (1,1,10) do (
    set /A ss=!ss!+10
    ffmpeg -ss !ss! -i 1.mp4 -t 10 -c:v libx264 -c:a aac -strict -2 нд╪Ч%%i.mp4
)
