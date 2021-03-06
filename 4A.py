#!/usr/bin/python
# -*- coding: UTF-8 -*-
import multiprocessing as mp
import bluetooth
import os
import time
try:
	import RPi.GPIO as GPIO
except:
	import Simulate as GPIO

THRESHOLD = 20
#定义状态字段,起始0xFF
state = mp.Value('I',0x0100)

#定义设置字段,起始0xF8
config = mp.Value('I',0x0000)

#定义数据字段,起始0xF0
data = mp.Array('B',[0x00 for i in range(34)])
#data[0]  速度十位
#data[1]  速度个位
#data[2]  速度十分位

#data[3]  踏频百十位
#data[4]  踏频个位

#data[5]  温度正负
#data[6]  温度十位
#data[7]  温度个位
#data[8]  左边速度十位
#data[9]  左边速度个位
#data[10] 左边速度十分位
#data[11] 中间速度十位
#data[12] 中间速度个位
#data[13] 中间速度十分位
#data[14] 右边速度十位
#data[15] 右边速度个位
#data[16] 右边速度十分位
#data[17] 左边距离个位
#data[18] 左边距离十分位
#data[19] 中间距离个位
#data[20] 中间距离十分位
#data[21] 右边距离个位
#data[22] 右边距离十分位

#data[23] 环境光强度

#data[24] 小时十位
#data[25] 小时个位
#data[26] 分钟十位
#data[27] 小时个位
#data[28] 秒十位
#data[29] 秒个位

#data[30] 车轮千位
#data[31] 车轮百位
#data[32] 车轮十位
#data[33] 车轮个位

def set_light():
	type = (config.value&0x000c)>>2
	temp = int((data[23]/15.0)*100) 
	while True:                   #1常亮，2闪烁，3SOS
		if(type == 2)
			global_var.pwm.ChangeDutyCycle(0)
			sleep(0.5)
			global_var.pwm.ChangeDutyCycle(temp)
			sleep(0.5)
		if(type == 3)
			for i in range (3)
				global_var.pwm.ChangeDutyCycle(0)
				sleep(0.5)
				global_var.pwm.ChangeDutyCycle(temp)
				sleep(0.5)
			for i in range (3)
				global_var.pwm.ChangeDutyCycle(0)
				sleep(0.5)
				global_var.pwm.ChangeDutyCycle(temp)
				sleep(1)
			for i in range (3)
				global_var.pwm.ChangeDutyCycle(0)
				sleep(0.5)
				global_var.pwm.ChangeDutyCycle(temp)
				sleep(0.5)


def get_light():
	GPIO.output(12,GPIO.HIGH)
	GPIO.output(25,GPIO.HIGH)
	while True:
		if config.value&0x0010 == 0:
			temp = 0
			
			GPIO.output(25,GPIO.LOW)
			time.sleep(0.2)
			GPIO.output(25,GPIO.HIGH)

			time.sleep(0.2)
			GPIO.output(12,GPIO.LOW)
			time.sleep(0.2)
			
			temp=(temp<<1)+GPIO.input(4)
			temp=(temp<<1)+GPIO.input(17)
			temp=(temp<<1)+GPIO.input(27)
			temp=(temp<<1)+GPIO.input(22)

			data[23] = temp
			GPIO.output(12,GPIO.HIGH)
			time.sleep(0.4)
		else:
			temp = config.value&0x0003
			if temp == 0:
				#关闭手电筒
				data[23] = 0     
			elif temp == 1:
				#亮度低
				data[23] = 5
			elif temp == 2:
				#亮度中
				data[23] = 10
			elif temp == 3:
				#亮度高
				data[23] = 15
			time.sleep(1)
			

def ultra():
	#print "ultra start"
	while True:
		if config.value&0x0200==0:
			temp = os.popen('printf "11.1 22.2 33.3 4.4 5.5 6.6 +77"').read().strip("\n").split(" ")
			data[8] = int(temp[0][0])
			data[9] = int(temp[0][1])
			data[10] = int(temp[0][3])
			data[11] = int(temp[1][0])
			data[12] = int(temp[1][1])
			data[13] = int(temp[1][3])
			data[14] = int(temp[2][0])
			data[15] = int(temp[2][1])
			data[16] = int(temp[2][3])
			data[17] = int(temp[3][0])
			data[18] = int(temp[3][2])
			data[19] = int(temp[4][0])
			data[20] = int(temp[4][2])
			data[21] = int(temp[5][0])
			data[22] = int(temp[5][2])
			data[5] = 1 if temp[6][0] == '+' else 0
			data[6] = int(temp[6][1])
			data[7] = int(temp[6][2])
		
		time.sleep(0.1)

def hall():
	#print "hall start"
	halltime1 = [0,0,0]
	timen1 = 0
	state1 = 0
	halltime2 = [0,0,0]
	timen2 = 0
	state2 = 0
	while True:
		temp1 = GPIO.input(16)
		if state1==0:
			if temp1==1:
				state1 = 1
		elif state1==1:
			if temp1==0:
				state1 = 0
				halltime1[timen1] = time.time()
				timen1 = timen1+1
				if timen1==3:
					timen1=0
					temp = (data[30]+data[31]/10.0+data[32]/100.0+data[33]/1000.0)/((halltime1[2]-halltime1[0])/2.0)
					print "m/s:",temp
					temp = int(temp*10)
					data[2] = temp%10
					temp = temp/10
					data[1] = temp%10
					temp = temp/10
					data[0] = temp
		temp2 = GPIO.input(20)
		if state2==0:
			if temp2==1:
				state2 = 1
		elif state2==1:
			if temp2==0:
				state2 = 0
				halltime2[timen2] = time.time()
				timen2 = timen2+1
				if timen2==3:
					timen2=0
					temp = int(60/((halltime2[2]-halltime2[0])/2.0))
					print "kph:",temp
					data[3] = (temp/10)%100
					data[4] = temp%10
		time.sleep(0.01)

def RF():
	port = 1
	addr = '00:21:13:00:B5:F2'
	sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
	
	flag = 1
	while flag:
		try:
			sock.connect((addr,port))
			flag = 0
		except:
			print "connect error"
			time.sleep(1)
		
	while True:
		send = ''
		send = send + chr(0xff)
		send = send + chr((state.value&0xff00)>>8)
		send = send + chr((state.value&0x00ff))
		send = send + chr(0xf8)
		send = send + chr((config.value&0xff00)>>8)
		send = send + chr((config.value&0x00ff))
		send = send + chr(0xf0)
		send = send + ''.join([chr(d) for d in data])
		#print send
		sock.send(send)
		time.sleep(0.5)
	sock.close()
		
class state_flag():
	#BCM no. of state machine GPIO
	UP_B = 5
	DOWN_B = 26
	LEFT_B = 13
	RIGHT_B = 19
	MIDDLE_B = 6
	SHUT_B = 21
	
	#botton flags
	u_pre_flag = 0
	u_cur_flag = 0
	u_in_flag = 0
	d_pre_flag = 0
	d_cur_flag = 0
	d_in_flag = 0
	l_pre_flag = 0
	l_cur_flag = 0
	l_in_flag = 0
	r_pre_flag = 0
	r_cur_flag = 0
	r_in_flag = 0
	m_pre_flag = 0
	m_cur_flag = 0
	m_in_flag = 0
	s_pre_flag = 0
	s_cur_flag = 0
	s_in_flag = 0
	
	#botton holding counts
	u_count = 0
	d_count = 0
	s_count = 0
	
	
class global_var():
	pwm = ''

def state_machine():
		
	def state_set_flag():
		#systick_freq
		systick_freq = 2

		#up
		state_flag.u_pre_flag = state_flag.u_cur_flag
		state_flag.u_cur_flag = GPIO.input(state_flag.UP_B)
		if state_flag.u_cur_flag == 1:
			#state_flag.u_count = state_flag.u_count + 1
			#hold for 0.5s
			#if state_flag.u_count >= (systick_freq/2):
			#	state_flag.u_count = 0
			#	state_flag.u_in_flag = 1
			#	print "up input"
			#rising edge
			if state_flag.u_pre_flag == 0:
				state_flag.u_in_flag = 1
				print "up input"
		
		#down
		state_flag.d_pre_flag = state_flag.d_cur_flag
		state_flag.d_cur_flag = GPIO.input(state_flag.DOWN_B)
		if state_flag.d_cur_flag == 1:
			#state_flag.d_count = state_flag.d_count + 1
			#hold for 0.5s
			#if state_flag.d_count >= (systick_freq/2):
			#	state_flag.d_count = 0
			#	state_flag.d_in_flag = 1
			#	print "down input"
			#rising edge
			if state_flag.d_pre_flag == 0:
				state_flag.d_in_flag = 1
				print "down input"

		#left
		state_flag.l_pre_flag = state_flag.l_cur_flag
		state_flag.l_cur_flag = GPIO.input(state_flag.LEFT_B)
		#rising edge
		if state_flag.l_pre_flag == 0 and state_flag.l_cur_flag == 1:
			state_flag.l_in_flag = 1
			print "left input"

		#right
		state_flag.r_pre_flag = state_flag.r_cur_flag
		state_flag.r_cur_flag = GPIO.input(state_flag.RIGHT_B)
		#rising edge
		if state_flag.r_pre_flag == 0 and state_flag.r_cur_flag == 1:
			state_flag.r_in_flag = 1
			print "right input"

		#middle
		state_flag.m_pre_flag = state_flag.m_cur_flag
		state_flag.m_cur_flag = GPIO.input(state_flag.MIDDLE_B)
		#rising edge
		if state_flag.m_pre_flag == 0 and state_flag.m_cur_flag == 1:
			state_flag.m_in_flag = 1
			print "middle input"

		#shut
		state_flag.s_pre_flag = state_flag.s_cur_flag
		state_flag.s_cur_flag = GPIO.input(state_flag.SHUT_B)
		if state_flag.s_cur_flag == 1:
			if state_flag.s_pre_flag == 1:
				state_flag.s_count = state_flag.s_count + 1
				if state_flag.s_count >= 20:
					state_flag.s_count = 0
					print "shutdown"
					#os.popen("sudo halt")
			else:
				state_flag.s_in_flag = 1
				state_flag.s_count = 0
				print "shut input"
			
	def state_trans():
		state_set_flag()

		#shut screen
		if state_flag.s_in_flag == 1:
			state_flag.s_in_flag = 0
			#设置屏幕开关
			config.value = (config.value&~0x4000)|(config.value^0x4000)

		#run
		elif (state.value | 0x0FFF) == 0x1FFF:
			light_lumi = config.value&0x0003
			if state_flag.u_in_flag == 1:
				state_flag.u_in_flag = 0
				if light_lumi == 3:
					light_lumi = 0
				else:
					light_lumi = light_lumi + 1
			if state_flag.d_in_flag == 1:
				state_flag.d_in_flag = 0
				if light_lumi == 0:
					light_lumi = 3
				else:
					light_lumi = light_lumi - 1
			if state_flag.l_in_flag == 1:
				state_flag.l_in_flag = 0
			if state_flag.r_in_flag == 1:
				state_flag.r_in_flag = 0
				state.value = 0x2100
			if state_flag.m_in_flag == 1:
				state_flag.m_in_flag = 0
				state.value = 0x2100
			config.value = (config.value&~0x0003)|light_lumi
		#setting 1st order
		elif (state.value | 0x0FFF) == 0x2FFF:
			if state_flag.u_in_flag == 1:
				state_flag.u_in_flag = 0
				if state.value == 0x2100:
					state.value = 0x2700
				else:
					state.value = state.value - 0x0100
			if state_flag.d_in_flag == 1:
				state_flag.d_in_flag = 0
				if state.value == 0x2700:
					state.value = 0x2100
				else:
					state.value = state.value + 0x0100
			if state_flag.l_in_flag == 1:
				state_flag.l_in_flag = 0
				state.value = 0x1000
			if state_flag.r_in_flag == 1:
				state_flag.r_in_flag = 0
				if state.value == 0x2700:
					state.value = 0x1000
				else:
					state.value = state.value + 0x1010
			if state_flag.m_in_flag == 1:
				state_flag.m_in_flag = 0
				if state.value == 0x2700:
					state.value = 0x1000
				else:
					state.value = state.value + 0x1010

		#ultra 2nd order
		elif (state.value | 0x00FF) == 0x31FF:
			if state_flag.u_in_flag == 1:
				state_flag.u_in_flag = 0
				if state.value == 0x3110:
					state.value = 0x3140
				else:
					state.value = state.value - 0x0010
			if state_flag.d_in_flag == 1:
				state_flag.d_in_flag = 0
				if state.value == 0x3140:
					state.value = 0x3110
				else:
					state.value = state.value + 0x0010
			if state_flag.l_in_flag == 1:
				state_flag.l_in_flag = 0
				state.value = 0x2100
			if state_flag.r_in_flag == 1:
				state_flag.r_in_flag = 0
				if state.value == 0x3110:
					#超声波开关
					config.value = (config.value&~0x2000)|(config.value^0x2000)
				elif state.value == 0x3120:
					#设置超声波灵敏度
					config.value = (config.value&~0x1800)|((config.value&0x1800+1)%3)
				elif state.value == 0x3130:
					#超声波报警开关
					config.value = (config.value&~0x0400)|(config.value^0x0400)
				elif state.value == 0x3140:
					state.value = 0x1000
			if state_flag.m_in_flag == 1:
				state_flag.m_in_flag = 0
				if state.value == 0x3110:
					#超声波开关
					config.value = (config.value&~0x2000)|(config.value^0x2000)
				elif state.value == 0x3120:
					#设置超声波灵敏度
					config.value = (config.value&~0x1800)|((config.value&0x1800+1)%3)
				elif state.value == 0x3130:
					#超声波报警开关
					config.value = (config.value&~0x0400)|(config.value^0x0400)
				elif state.value == 0x3140:
					state.value = 0x1000

		#light 2nd order
		elif (state.value | 0x00FF) == 0x32FF:
			if state_flag.u_in_flag == 1:
				state_flag.u_in_flag = 0
				if state.value == 0x3210:
					state.value = 0x3230
				else:
					state.value = state.value - 0x0010
			if state_flag.d_in_flag == 1:
				state_flag.d_in_flag = 0
				if state.value == 0x3230:
					state.value = 0x3210
				else:
					state.value = state.value + 0x0010
			if state_flag.l_in_flag == 1:
				state_flag.l_in_flag = 0
				state.value = 0x2200
			if state_flag.r_in_flag == 1:
				state_flag.r_in_flag = 0
				if state.value == 0x3210:
					#设置手电筒自动开关
					config.value = (config.value&~0x0010)|(config.value^0x0010)
				elif state.value == 0x3220:
					#设置手电筒模式
					config.value = (config.value&~0x000c)|((config.value&0x000c+1)%3)
				elif state.value == 0x3230:
					state.value = 0x1000
			if state_flag.m_in_flag == 1:
				state_flag.m_in_flag = 0
				if state.value == 0x3210:
					#设置手电筒自动开关
					config.value = (config.value&~0x0010)|(config.value^0x0010)
				elif state.value == 0x3220:
					#设置手电筒模式
					config.value = (config.value&~0x000c)|((config.value&0x000c+1)%3)
				elif state.value == 0x3230:
					state.value = 0x1000

		#phone 2nd order
		elif (state.value | 0x00FF) == 0x33FF:
			if state_flag.u_in_flag == 1:
				state_flag.u_in_flag = 0
				if state.value == 0x3310:
					state.value = 0x3330
				else:
					state.value = state.value - 0x0010
			if state_flag.d_in_flag == 1:
				state_flag.d_in_flag = 0
				if state.value == 0x3330:
					state.value = 0x3310
				else:
					state.value = state.value + 0x0010
			if state_flag.l_in_flag == 1:
				state_flag.l_in_flag = 0
				state.value = 0x2300
			if state_flag.r_in_flag == 1:
				state_flag.r_in_flag = 0
				if state.value == 0x3310:
					#设置来电开关
					config.value = (config.value&~0x0200)|(config.value^0x0200)
				elif state.value == 0x3320:
					#设置短信开关
					config.value = (config.value&~0x0100)|(config.value^0x0100)
				elif state.value == 0x3330:
					state.value = 0x1000
			if state_flag.m_in_flag == 1:
				state_flag.m_in_flag = 0
				if state.value == 0x3310:
					#设置来电开关
					config.value = (config.value&~0x0200)|(config.value^0x0200)
				elif state.value == 0x3320:
					#设置短信开关
					config.value = (config.value&~0x0100)|(config.value^0x0100)
				elif state.value == 0x3330:
					state.value = 0x1000

		#time 2nd order
		elif (state.value | 0x00FF) == 0x34FF:
			if state_flag.u_in_flag == 1:
				state_flag.u_in_flag = 0
				if state.value == 0x3410:
					state.value = 0x3420
				else:
					state.value = state.value - 0x0010
			if state_flag.d_in_flag == 1:
				state_flag.d_in_flag = 0
				if state.value == 0x3420:
					state.value = 0x3410
				else:
					state.value = state.value + 0x0010
			if state_flag.l_in_flag == 1:
				state_flag.l_in_flag = 0
				state.value = 0x2400
			if state_flag.r_in_flag == 1:
				state_flag.r_in_flag = 0
				if state.value == 0x3410:
					state.value = 0x4411
				elif state.value == 0x3420:
					state.value = 0x1000
			if state_flag.m_in_flag == 1:
				state_flag.m_in_flag = 0
				if state.value == 0x3410:
					state.value = 0x4411
				elif state.value == 0x3420:
					state.value = 0x1000

		#circumference 2nd order
		elif (state.value | 0x00FF) == 0x35FF:
			if state_flag.u_in_flag == 1:
				state_flag.u_in_flag = 0
				if state.value == 0x3510:
					state.value = 0x3520
				else:
					state.value = state.value - 0x0010
			if state_flag.d_in_flag == 1:
				state_flag.d_in_flag = 0
				if state.value == 0x3520:
					state.value = 0x3510
				else:
					state.value = state.value + 0x0010
			if state_flag.l_in_flag == 1:
				state_flag.l_in_flag = 0
				state.value = 0x2500
			if state_flag.r_in_flag == 1:
				state_flag.r_in_flag = 0
				if state.value == 0x3510:
					state.value = 0x4511
				elif state.value == 0x3520:
					state.value = 0x1000
			if state_flag.m_in_flag == 1:
				state_flag.m_in_flag = 0
				if state.value == 0x3510:
					state.value = 0x4511
				elif state.value == 0x3520:
					state.value = 0x1000

		#OLED 2nd order
		elif (state.value | 0x00FF) == 0x36FF:
			if state_flag.u_in_flag == 1:
				state_flag.u_in_flag = 0
				if state.value == 0x3610:
					state.value = 0x3630
				else:
					state.value = state.value - 0x0010
			if state_flag.d_in_flag == 1:
				state_flag.d_in_flag = 0
				if state.value == 0x3630:
					state.value = 0x3610
				else:
					state.value = state.value + 0x0010
			if state_flag.l_in_flag == 1:
				state_flag.l_in_flag = 0
				state.value = 0x2600
			if state_flag.r_in_flag == 1:
				state_flag.r_in_flag = 0
				if state.value == 0x3610:
					#设置OLED开关
					config.value = (config.value&~0x0080)|(config.value^0x0080)
				elif state.value == 0x3620:
					#设置OLED亮度
					config.value = (config.value&~0x0060)|((config.value&0x0060+1)%3)
				elif state.value == 0x3630:
					state.value = 0x1000
			if state_flag.m_in_flag == 1:
				state_flag.m_in_flag = 0
				if state.value == 0x3610:
					#设置OLED开关
					config.value = (config.value&~0x0080)|(config.value^0x0080)
				elif state.value == 0x3620:
					#设置OLED亮度
					config.value = (config.value&~0x0060)|((config.value&0x0060+1)%3)
				elif state.value == 0x3630:
					state.value = 0x1000

		#time 3rd order
		elif (state.value | 0x00FF) == 0x44FF:
			time_h = data[24]*10+data[25]
			time_m = data[26]*10+data[27]
			if state_flag.u_in_flag == 1:
				state_flag.u_in_flag = 0
				if state.value == 0x4411:
					if time_h == 23:
						time_h = 0
					else:
						time_h = time_h + 1
				elif state.value == 0x4412:
					if time_m == 59:
						time_m = 0
					else:
						time_m = time_m + 1
			if state_flag.d_in_flag == 1:
				state_flag.d_in_flag = 0
				if state.value == 0x4411:
					if time_h == 0:
						time_h = 23
					else:
						time_h = time_h - 1
				elif state.value == 0x4412:
					if time_m == 0:
						time_m = 59
					else:
						time_m = time_m - 1
			if state_flag.l_in_flag == 1:
				state_flag.l_in_flag = 0
				if state.value == 0x4411:
					state.value = 0x4412
				elif state.value == 0x4412:
					state.value = 0x4411     
			if state_flag.r_in_flag == 1:
				state_flag.r_in_flag = 0
				if state.value == 0x4411:
					state.value = 0x4412
				elif state.value == 0x4412:
					state.value = 0x4411 
			if state_flag.m_in_flag == 1:
				state_flag.m_in_flag = 0
				state.value = 0x3410
			data[24] = time_h/10
			data[25] = time_h%10
			data[26] = time_m/10
			data[27] = time_m%10

		#circumference 3rd order
		elif (state.value | 0x00FF) == 0x45FF:
			if state_flag.u_in_flag == 1:
				state_flag.u_in_flag = 0
				if state.value == 0x4511:
					if data[30] == 9:
						data[30] = 0
					else:
						data[30] = data[30] + 1
				elif state.value == 0x4512:
					if data[31] == 9:
						data[31] = 0
					else:
						data[31] = data[31] + 1
				elif state.value == 0x4513:
					if data[32] == 9:
						data[32] = 0
					else:
						data[32] = data[32] + 1
				elif state.value == 0x4514:
					if data[33] == 9:
						data[33] = 0
					else:
						data[33] = data[33] + 1
			if state_flag.d_in_flag == 1:
				state_flag.d_in_flag = 0
				if state.value == 0x4511:
					if data[30] == 0:
						data[30] = 9
					else:
						data[30] = data[30] - 1
				elif state.value == 0x4512:
					if data[31] == 0:
						data[31] = 9
					else:
						data[31] = data[31] - 1
				elif state.value == 0x4513:
					if data[32] == 0:
						data[32] = 9
					else:
						data[32] = data[32] - 1
				elif state.value == 0x4514:
					if data[33] == 0:
						data[33] = 9
					else:
						data[33] = data[33] - 1
			if state_flag.l_in_flag == 1:
				state_flag.l_in_flag = 0
				if state.value == 0x4511:
					state.value = 0x4514
				else:
					state.value = state.value - 0x0001
			if state_flag.r_in_flag == 1:
				state_flag.r_in_flag = 0
				if state.value == 0x4514:
					state.value = 0x4511
				else:
					state.value = state.value + 0x0001
			if state_flag.m_in_flag == 1:
				state_flag.m_in_flag = 0
				state.value = 0x3510

	print "state machine start"
	state.value = 0x1000
	while True:
		#print "%04x"%state.value
		state_trans()
		time.sleep(0.1)
		
def GPIO_init():
	GPIO.setmode(GPIO.BCM)
	
	#霍尔传感器GPIO
	GPIO.setup(16,GPIO.IN)
	GPIO.setup(20,GPIO.IN)
		
	#状态机GPIO
	GPIO.setup(state_flag.UP_B,GPIO.IN)
	GPIO.setup(state_flag.DOWN_B,GPIO.IN)
	GPIO.setup(state_flag.LEFT_B,GPIO.IN)
	GPIO.setup(state_flag.RIGHT_B,GPIO.IN)
	GPIO.setup(state_flag.MIDDLE_B,GPIO.IN)
	GPIO.setup(state_flag.SHUT_B,GPIO.IN)
	
	#光线传感器GPIO
	GPIO.setup(4,GPIO.IN)       #DB7           
	GPIO.setup(17,GPIO.IN)      #DB6
	GPIO.setup(27,GPIO.IN)		#DB5
	GPIO.setup(22,GPIO.IN)		#DB4
	GPIO.setup(25,GPIO.OUT)     #WR
	GPIO.setup(12,GPIO.OUT)     #RD
	
	#PWM
	GPIO.setup(18,GPIO.OUT)
	global_var.pwm = GPIO.PWM(18,1000)
	global_var.pwm.start(0)
	

def main():
	print "start"
	GPIO_init()
	phall = mp.Process(target=hall)
	#pultra = mp.Process(target=ultra)
	plight = mp.Process(target=get_light)
	#pRF = mp.Process(target=RF)
	pstate = mp.Process(target=state_machine)
	psetlight = mp.Process(target=set_light)
	data[30] = 1
	data[31] = 5
	data[32] = 0
	data[33] = 0
	phall.start()
	psetlight.start()
	#pultra.start()
	plight.start()
	#pRF.start()
	pstate.start()

if __name__=="__main__":
	main()
