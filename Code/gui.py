from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys,time, datetime

import threading

#import tkinter as tk
#from PIL import Image, ImageTk

FONT="Arial"


class GUI_CLASS(QMainWindow):
	def __init__(self,parkImageFile,parkDataDefaults,park,attractionMetaData,hourlyArrivalPercents,timeSpentPerActivity,peoplePerActivity):
		self.parkImageFile=parkImageFile
		self.park=park
		self.attractions=park.attractions
		self.attractionMetaData=attractionMetaData
		self.ticks=0
		self.isPlaying=False
		self.peoplePerActivity=peoplePerActivity

		arrivalTimes=[datetime.datetime.strptime(k,"%I:%M %p") for k in hourlyArrivalPercents]
		arrivalTimes = [t.hour*60+t.minute for t in arrivalTimes]
		self.parkOpen = min([t if t!=0 else 1440 for t in arrivalTimes])
		self.parkClose = park.park_close+self.parkOpen


		self.storeMaxQueues()

		self.app = QApplication(sys.argv)

		#Create Window
		super(GUI_CLASS,self).__init__()
		self.hBox=QHBoxLayout()
		self.hBoxChildren=[]

		self.hBoxChildren.append(QVBoxLayout())
		self.hBoxChildren.append(QVBoxLayout())
		for child in self.hBoxChildren:
			self.hBox.addLayout(child)

		self.loadParkMap(parkImageFile,self.hBoxChildren[0])
		self.createAttractionCallouts()
		self.createParkSummaries(self.hBoxChildren[1])
		self.addControlButtons(self.hBoxChildren[0])


		#Add the layout to the window
		widget=QWidget()
		widget.setLayout(self.hBox)
		self.setCentralWidget(widget)
		#Resize the window
		self.setFixedSize(self.sizeHint())


		self.show()
		sys.exit(self.app.exec_())

	def storeMaxQueues(self):
		self.attrMaxWait={}
		for k,v in self.attractions.items():
			waits = [w for w in v.history["queue_wait_time"].values()]
			self.attrMaxWait[k]=max(waits)

	def getTimeKeys(self):
		T = []
		for k,v in self.attractions.items():
			t = [tt for tt in v.history["queue_wait_time"].keys() if tt not in T]
			T += t
		T.sort(key=lambda x: int(x))
		return T

	def play(self,updateFunction,period):
		self.times=self.getTimeKeys()
		if self.getTime()>=self.parkClose:
			self.setTime(self.parkOpen)
		self.isPlaying=True

		#Period should be specified in ms

		self.threadTimer=QTimer(self)
		self.threadTimer.setInterval(period)
		self.threadTimer.timeout.connect(updateFunction)
		self.threadTimer.start()

	def pause(self):
		self.threadTimer.stop()
		self.isPlaying=False

	def reset(self):
		#Period should be specified in ms
		self.setTime(self.parkOpen)
		self.times=self.getTimeKeys()
		

	def addControlButtons(self,parent):
		buttonRow = QHBoxLayout()
		parent.addLayout(buttonRow)

		button1=QPushButton("Play",self)
#		button1.setToolTip("Example button")
		def f():
			if not self.isPlaying:
				return self.play(self.animateSimulation,100)
		button1.clicked.connect(f)
		buttonRow.addWidget(button1)

		button2=QPushButton("Pause",self)
		def f(): return self.pause()
		button2.clicked.connect(f)
		buttonRow.addWidget(button2)

		button3=QPushButton("Reset",self)
		def f(): return self.reset()
		button3.clicked.connect(f)
		buttonRow.addWidget(button3)

		self.timeEdit = QTimeEdit()
		print(dir(self.timeEdit))
		self.timeEdit.userTimeChanged.connect(self.updateDisplay)
		buttonRow.addWidget(self.timeEdit)

		buttonRow.addWidget(QLabel(),1)
		self.setTime(self.parkOpen)


	def getTime(self):
		t=self.timeEdit.time()
		return t.hour()*60+t.minute()

	def setTime(self,t):
		t=t%1440
		h=t//60
		m=t%60
		self.timeEdit.setTime(QTime(h,m))

	def storeSimResults(self,queueLength,queueWaitTime,expQueueWaitTime):
		self.queueLength=queueLength
		self.queueWaitTime=queueWaitTime
		self.expQueueWaitTime=expQueueWaitTime

	def animateSimulation(self):
		if self.getTime()>=self.parkClose:
			self.threadTimer.stop()
			self.isPlaying=False
			return
		self.updateDisplay()
		self.setTime(self.getTime()+1)


	def createParkSummaries(self, parent):
		data = [["Attendance","Attendance",0]]
		data+= [["People "+k.capitalize(),k,v] for k,v in self.peoplePerActivity[0].items()]

		parent.addWidget(QLabel(),1)
		self.summaryWidgets = {}
		for label, key, value in data:
			l1=QLabel()
			l1.setAlignment(Qt.AlignCenter)
			l1.setText(label)
			l1.setFont(QFont("Arial",16))
			parent.addWidget(l1)

			l2=QLabel()
			l2.setAlignment(Qt.AlignCenter)
			l2.setText(str(value))
			parent.addWidget(l2)

			self.summaryWidgets[key]=l2

#			l1.setStyleSheet("background-color: lightgreen")
			#Adding a widget with non zero stretch allows this to fill all the other space
			#so the others stay compressed
			parent.addWidget(QLabel(),2)
  

	def loadParkMap(self,imFile,parent):
		self.graphicsView=QGraphicsView()
		self.graphicsView.setRenderHint(QPainter.Antialiasing)
		self.graphicsView.setRenderHint(QPainter.HighQualityAntialiasing)
		parent.addWidget(self.graphicsView)

		self.scene = QGraphicsScene()
		self.graphicsView.setScene(self.scene)

		image=QPixmap(imFile)
		image=image.scaledToHeight(800)
		self.scene.addPixmap(image)



	def createAttractionCallouts(self):
		if "attrCallouts" not in dir(self):
			self.attrCallouts={}

		bbox=15
		alpha=220
		self.borderColor=[0,0,0,alpha]
		self.calloutColorBase=[200,200,200,alpha]
		self.calloutColorHigh=[201,32,76,alpha]
		self.calloutBackgrounds={}

		for meta in self.attractionMetaData:
			name=meta["name"]
			obj=self.attractions[name]
			x, y, q = meta["x_pos"], meta["y_pos"], "--"
			text=QGraphicsSimpleTextItem(q)
			text.setPos(x,y)

			xyBase=[[-1,-1],[1,-1],[1,1],[0,1.5],[-1,1]]
			xy=[[xx*bbox+x,yy*bbox+y] for xx,yy in xyBase]
			item=self.addRoundedPolygon(xy,self.borderColor,self.calloutColorBase)
			self.calloutBackgrounds[name]=item

			height=text.boundingRect().height()
			width=text.boundingRect().width()
			text.setPos(int(x-width/2),int(y-height/2))

			self.attrCallouts[name]=text
			self.scene.addItem(text)

	def updateDisplay(self):
		self.updateAttractionCallouts()
		self.updateParkSummaries()
			

	def updateParkSummaries(self):
		time = self.getTime()-self.parkOpen

		count = self.park.history["total_active_agents"][time]
		self.summaryWidgets["Attendance"].setText(str(count))

		for k,v in self.peoplePerActivity[time].items(): 
			self.summaryWidgets[k].setText(str(v))


	def updateAttractionCallouts(self):
		time = self.getTime()-self.parkOpen
		for meta in self.attractionMetaData:
			name=meta["name"]
			obj=self.attractions[name]
			x, y = meta["x_pos"], meta["y_pos"]
			q=obj.history["queue_wait_time"][time]
			percentOfHigh=q/self.attrMaxWait[name]
			q=str(q)

			color=[int(c1*(1-percentOfHigh)+c2*percentOfHigh) for c1,c2 in zip(self.calloutColorBase,self.calloutColorHigh)]
			self.setPolygonColor(self.calloutBackgrounds[name],self.borderColor,color)

			obj = self.attrCallouts[name]
			obj.setText(q)
			height=obj.boundingRect().height()
			width=obj.boundingRect().width()
			obj.setPos(int(x-width/2),int(y-height/2))


	def addRoundedPolygon(self,xy,borderColor,bgColor):
		x = [x[0] for x in xy]
		y = [x[1] for x in xy]

		R = 2

		import numpy as np
		pointsX,pointsY=[],[]
		for i in range(len(x)):
			x0, x1, x2 = x[i-1],x[i],x[(i+1)%len(x)]
			y0, y1, y2 = y[i-1],y[i],y[(i+1)%len(x)]

			theta2=np.arctan2(y1-y2,x1-x2)
			if y1-y2==0 and x1-x2<0:
				theta2=-np.pi
			theta1=np.arctan2(y1-y0,x1-x0)
			if y1-y0==0 and x1-x0<0:
				theta1=-np.pi

			thetaA=(theta2-theta1)/2

			r = R/np.cos(thetaA)
			s = (r**2-R**2)**0.5

			xb=x1+r*np.cos(theta1+thetaA)
			yb=y1+r*np.sin(theta1+thetaA)

			#See if (xb,yb) is inside the polygon. Travel up from the point to count crossings
			segmentsCrossed=0
			yValCrossed=[]
			for j in range(len(x)):
				if (xb<x[j] and xb<x[j-1]) or (xb>x[j] and xb>x[j-1]):
					continue
				elif x[j]-x[j-1]==0 and xb!=x[j]:
					continue
				else:
					m=(y[j]-y[j-1])/(x[j]-x[j-1])
					b=y[j]-m*x[j]

					yProjection=m*xb+b
					if yProjection>yb and yProjection not in yValCrossed:
						segmentsCrossed+=1
						yValCrossed.append(yProjection)
			if segmentsCrossed%2==0:
				thetaA+=np.pi
				xb=x1+r*np.cos(theta1+thetaA)
				yb=y1+r*np.sin(theta1+thetaA)
			t1,t2=theta1-np.pi/2,theta2+np.pi/2

			if t2-t1>2*np.pi:
				t1+=2*np.pi

			for theta in np.linspace(t1,t2,20):

				pointsX.append(xb+s*np.cos(theta))
				pointsY.append(yb+s*np.sin(theta))

		points = [QPointF(x,y) for x,y in zip(pointsX,pointsY)]
		polygon=QPolygonF()
		for p in points:
			polygon.append(p)

		item = QGraphicsPolygonItem(polygon)
		self.setPolygonColor(item,borderColor,bgColor)

		self.scene.addItem(item)
		self.scene.update()

		return item

	def setPolygonColor(self,item,borderColor,bgColor):
		pen=QPen(QColor(*tuple(borderColor)),1.5)
		item.setPen(pen)

		brush=QBrush(QColor(*tuple(bgColor)))
		item.setBrush(brush)
		item.update()
#		self.scene.addItem(item)
		self.scene.update()
		return item


	def updateParkSummary(self,entries):
		for label, value in entries:
			if label in self.parkValues:
				self.parkValues[label]=value
				self.parkValueContainers[label].configure(text=value)




