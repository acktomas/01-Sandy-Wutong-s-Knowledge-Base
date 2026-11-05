# 3_pid_knob.py —— 电位器设定目标角 + PID 闭环控制
#
# 跑之前必须完成：
#   1. 跑过 1_selftest_encoder.py，确认手转一圈 count = 330
#      （330 = 11 PPR x 30 减速比，单相计数。若改成双相计数则填 660）
#   2. 跑过 2_selftest_knob.py，把 RAW_MIN / RAW_MAX 换成实测值
#
# 调参：先只给 Kp（Ki=Kd=0），能到位后再加 Kd 压超调，最后加 Ki 消静差
# 看曲线：Thonny 菜单 View -> Plotter，会画出 target 和 ang 两条线

from machine import Pin, PWM, ADC
import time

PULSE_PER_REV = 330           # 单相计数：11 PPR x 30 减速比（双相则是 660）
MAX_DUTY = 700                # 满量程 1023，限到 70%，防 L298N 过流发烫
RAW_MIN, RAW_MAX = 180, 3950  # ← 换成 2_selftest_knob 量出来的两个数

pwm  = PWM(Pin(4), freq=1000, duty=0)
in1  = Pin(5, Pin.OUT)
in2  = Pin(6, Pin.OUT)
encA = Pin(7, Pin.IN, Pin.PULL_UP)
encB = Pin(8, Pin.IN, Pin.PULL_UP)
knob = ADC(Pin(1))
knob.atten(ADC.ATTN_11DB)

count = 0

def on_a(pin):
    global count
    if encB.value():
        count += 1        # 正转。如果电机猛冲到底不停，把这两行 +1/-1 对调
    else:
        count -= 1

encA.irq(trigger=Pin.IRQ_RISING, handler=on_a)

def set_motor(u):
    if u >= 0:
        in1.value(1); in2.value(0)
    else:
        in1.value(0); in2.value(1); u = -u
    pwm.duty(min(int(u), MAX_DUTY))

Kp, Ki, Kd = 5.0, 0.0, 0.0
integral, err_prev = 0.0, 0.0
target = 0.0
t_next = time.ticks_ms()

while True:
    t = (knob.read() - RAW_MIN) / (RAW_MAX - RAW_MIN) * 360
    t = max(0.0, min(360.0, t))
    if abs(t - target) > 1.0:     # 跳过旋钮抖动，不然电机会一直微颤
        target = t
        integral = 0.0            # 换了目标，积分清零重来

    ang = count * 360.0 / PULSE_PER_REV
    err = target - ang
    if abs(err) < 5:
        integral += err           # 只在快到位时积分，防冲过头
    else:
        integral = 0.0

    u = Kp * err + Ki * integral + Kd * (err - err_prev)
    set_motor(u)
    err_prev = err

    print(target, ang)            # Plotter 看这两条线
    t_next += 20                  # 固定 20ms 一次，别用 sleep
    while time.ticks_diff(t_next, time.ticks_ms()) > 0:
        pass
