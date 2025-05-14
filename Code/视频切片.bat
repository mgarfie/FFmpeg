@echo off
setlocal enabledelayedexpansion

rem 设置每段视频的截取长度（单位：秒）
set segment_duration=10

rem 用 ffprobe 获取总时长（秒），输出为浮点数
for /f "delims=" %%a in ('ffprobe -v error -select_streams v:0 -show_entries format^=duration -of default^=noprint_wrappers^=1:nokey^=1 1.mp4') do (
    set duration=%%a
)

rem 截取整数部分（避免小数计算问题）
for /f "delims=." %%b in ("!duration!") do (
    set /A total_seconds=%%b
)

rem 计算循环次数（总时长 ÷ 每段时长）
set /A loops=total_seconds / segment_duration

echo 视频总时长：!total_seconds! 秒，需要循环：!loops! 次

set ss=0

for /L %%i in (1,1,!loops!) do (
    ffmpeg -ss !ss! -i 1.mp4 -t %segment_duration% -c:v libx264 -c:a aac -strict -2 文件%%i.mp4
    set /A ss=!ss!+segment_duration
)

echo 完成！
