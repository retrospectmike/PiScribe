import random
import time
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper	
import RPi.GPIO as GPIO

## Sound functions ##
# MakeNoise is the basic noise function.  Almost all higher functions just
  # call MakeNoise with different parameters
  # MakeNoise always starts and ends the motor at the same position so
  # that you don't end up running against a drive's head stop HOWEVER since
  # motors can sometimes slip, skip, or stall, there is **NO GUARANTEE** that 
  # this will forever keep the motor from making its way to a different spot.
def MakeNoise(targIters=5,styles=[stepper.INTERLEAVE],step_sleep=0.01):
	kit = MotorKit()
	steps=0
	iters = 0
	targFwdI = 0
	targFwd = 100
	#targIters = 5
	#styles=[stepper.MICROSTEP, stepper.INTERLEAVE, stepper.DOUBLE]

	targBwd = -1*targFwd#1900
	targFinal = 0
	#step_sleep = 0.4
	thisStyle = random.choice(styles)
	if thisStyle is stepper.INTERLEAVE:
		step_sleep = max([step_sleep,0.00001])
	elif thisStyle is stepper.SINGLE:
		step_sleep = max([step_sleep,0.05])

	if(targIters>0):
		while iters<targIters: #steps<targFwd:
			steps=kit.stepper2.onestep(
				direction=stepper.FORWARD,
				style = thisStyle
			)
			#print(iters)
			time.sleep(step_sleep)
			iters+=1

		thisStyle = random.choice(styles)
		while iters>-1*targIters: #steps>targBwd*0:
			steps=kit.stepper2.onestep(
				direction=stepper.BACKWARD,
				style = thisStyle
			)
			#print(iters)
			time.sleep(step_sleep)
			iters-=1

		if iters<0:
			home_direction = stepper.FORWARD
			inc = 1
		else:
			home_direction = stepper.BACKWARD
			inc = -1
		# One more to bring back to zero
		thisStyle = random.choice(styles)
		while iters!=0:#steps<targFinal:
			steps=kit.stepper2.onestep(
				direction=home_direction,
				style = thisStyle
			)
			time.sleep(step_sleep)
			#print(iters)
			iters+=inc
	else:
		kit.stepper2.onestep(
			direction=stepper.FORWARD,
			style=thisStyle)
		time.sleep(step_sleep)
		kit.stepper2.onestep(
			direction=stepper.BACKWARD,
			style=thisStyle)
	kit.stepper2.release()
# FloppyReadByBeeps sounds like an old Macintosh floppy drive reading, unused.
def FloppyReadByBeeps(numBeeps=1):
	MakeNoise(targIters=numBeeps/2,styles=[stepper.INTERLEAVE],step_sleep=0.4)
# FloppyWriteByBeeps sounds like an old Macintosh floppy drive writing, unused.
def FloppyWriteByBeeps(numBeeps=1):
	MakeNoise(targIters=numBeeps/2,styles=[stepper.INTERLEAVE],step_sleep=0.01)

#Unused, but provides an interface to command a # of beeps
def HDReadByBeeps(numBeeps=1):
	sleepTimes=[0.025,0.01,0.05,.1]
	#MakeNoise(targIters=numBeeps/2,styles=[stepper.INTERLEAVE],step_sleep=0.3)
	MakeNoise(targIters=numBeeps/2,styles=[stepper.INTERLEAVE],
		step_sleep=random.choice(sleepTimes))
#HDSeek mimics hard drive seeking noises.  
#  targIters determines how many seek noises it makes (i.e. how long the sounds last)
def HDSeek(targIters=13):
	MakeNoise(targIters=targIters,styles=[stepper.MICROSTEP],step_sleep=0.00001)
#HDRead mimics hard drive reading noises.
#  numReads dictates how many read noises it makes (i.e. how long the sounds last)
def HDRead(numReads=1):
	seekTimes=[1,4,8,8,8,20,20,20,20,8,20,20,20,20]
	readBeeps=[1,1,2,4,2,4,2,4,2,4]
	sleepTimes=[0,0,0,0.1,0.2,0.3,0.4,0.5]
	for i in range(numReads):
		seeks=random.choice(seekTimes)
		beeps=random.choice(readBeeps)
		sleeps=random.choice(sleepTimes)
		print(f"{seeks} seeks, {beeps} beeps, {sleeps} sleeps")
		HDSeek(targIters=seeks)
		HDReadByBeeps(beeps)
		time.sleep(sleeps)
		
#HDStartup mimics the MiniScribe's startup noises
def HDStartup():
	kit = MotorKit()
	i=0
	targFwdI = 450
	styles=[stepper.INTERLEAVE]#stepper.MICROSTEP, stepper.INTERLEAVE, stepper.DOUBLE]

	targFinal = 0
	STEP_SLEEP = 0.0001

	while i<targFwdI:
		i=kit.stepper2.onestep(
			direction=stepper.FORWARD,
			style = stepper.MICROSTEP
		)
		#print(i)
		time.sleep(STEP_SLEEP)

	
	time.sleep(0.1)
	while i>-targFwdI*3/4: #i>targBwd*0:
		i=kit.stepper2.onestep(
			direction=stepper.BACKWARD,
			style = stepper.MICROSTEP)
		#print(i)
		time.sleep(STEP_SLEEP)
		
	time.sleep(0.1)
	while i<targFwdI*2:
		i=kit.stepper2.onestep(
			direction=stepper.FORWARD,
			style = stepper.MICROSTEP
		)
		#print(i)
		time.sleep(STEP_SLEEP)


	if i<0:
		home_direction = stepper.FORWARD
	else:
		home_direction = stepper.BACKWARD
	# One more to bring back to zero

	time.sleep(0.1)
	while i!=0:#i<targFinal:
		i=kit.stepper2.onestep(
			direction=home_direction,
			style = stepper.INTERLEAVE
		)
		time.sleep(STEP_SLEEP/10)
		
	kit.stepper2.release()

## Main initializes the GPIO and loops listening to the activity input pin
def main():
	GPIO.setwarnings(True)
	GPIO.setmode(GPIO.BCM)
	GPIO_to_BlueSCSI_Pin = 4
	GPIO_testLED = 17
	GPIO.setup(GPIO_to_BlueSCSI_Pin,GPIO.IN)
	GPIO.setup(GPIO_testLED,GPIO.OUT)
	
	kit = MotorKit()
	kit.stepper2.release()
	 
	
	ActivityState = GPIO.input(GPIO_to_BlueSCSI_Pin)
	
	print("Hard drive startup sounds...")
	time.sleep(1)
	HDStartup()
	time.sleep(4)
	print("Welcome to PiScribe")

	while True: #Track state and only print statements when there's a change
		if ActivityState != GPIO.input(GPIO_to_BlueSCSI_Pin):
			ActivityState = GPIO.input(GPIO_to_BlueSCSI_Pin)
			if ActivityState:
				print("... inactive.")
				print(ActivityState)
			else:
				print("Activity!...")
				print(ActivityState)
		if 0==ActivityState: #(active low)
			GPIO.output(GPIO_testLED,0)
			HDRead(1)
			GPIO.output(GPIO_testLED,1)
		else:
			GPIO.output(GPIO_testLED,1)
		time.sleep(.0000002)

	
#Run main if called directly
if __name__=="__main__":
	main()
