# 1_selftest_encoder.py —— 编码器自检
# 用途：电机完全不动，手转输出轴看计数对不对
# 接线：只需 4 根（编码器 VCC->3V3, GND->GND, A->GPIO7, B->GPIO8）
#       12V 和 L298N 可以先不接，只插 USB 就能跑
#
# 判断：转一整圈 count 应该到 330（反转是 -330）
#       明显低于 330 = 转太快丢脉冲，把 MAX_DUTY 降低
#       一直是 0 = 编码器没接上
#
# 为什么是 330：
#   编码器 A 相每转（电机轴）输出 11 个脉冲，减速比 30
#   本程序只在 A 相上升沿计数（B 相只用来判方向），属于单相计数
#   输出轴一圈 = 11 x 30 = 330，分辨率 360/330 ≈ 1.09°
#   ★ 若以后改成 A、B 两相都触发计数（双相），这里要改成 660

from machine import Pin
import time

PULSE_PER_REV = 330          # 单相计数：11 PPR x 30 减速比

encA = Pin(7, Pin.IN, Pin.PULL_UP)
encB = Pin(8, Pin.IN, Pin.PULL_UP)

count = 0

def on_a(pin):
    global count
    if encB.value():
        count += 1
    else:
        count -= 1

encA.irq(trigger=Pin.IRQ_RISING, handler=on_a)

print("慢慢手转输出轴一整圈，看 count 最后是多少（应该是 330）")

while True:
    print("count =", count, " 角度 =", round(count * 360 / PULSE_PER_REV, 1))
    time.sleep_ms(300)
