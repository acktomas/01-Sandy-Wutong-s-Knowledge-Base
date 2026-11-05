# 2_selftest_knob.py —— 电位器自检
# 用途：量出电位器两端的真实读数，填进 3_pid_knob.py 的 RAW_MIN / RAW_MAX
# 接线：电位器左端->GND, 中间->GPIO1, 右端->3V3
# 判断：拧到最左记最小值，拧到最右记最大值
#       常见结果像 180 / 3950，跟 0 / 4095 差很远，这是正常的

from machine import ADC, Pin
import time

knob = ADC(Pin(1))
knob.atten(ADC.ATTN_11DB)     # 量程 0~3.3V

print("拧到最左，记下最小值；拧到最右，记下最大值")

while True:
    print(knob.read())
    time.sleep_ms(300)
