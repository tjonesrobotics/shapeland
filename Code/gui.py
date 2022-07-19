from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys,time, datetime
import numpy as np


FONT="Arial"


class GUI_CLASS(QMainWindow):
	def __init__(self,parkImageFile,park,attractionMetaData,hourlyArrivalPercents,timeSpentPerActivity,peoplePerActivity):
		"""
			Initializes the GUI and it's structure and prepares simulation data for display.

			Inputs:
				parkImageFile: a string with the path to the image of the park map
				park: a park object that has had its simulation run
				attractionMetaData: this contains the attraction data stored in the excel sheet's parameters
				hourlyArrivalPercents: This is the arrival percents defined in teh excel sheet
				timeSpentPerActivity: how many minutes have been spent by all agents in each state at each time step
				peoplePerActivity: how many people are in each state at each time step
		"""
		#Store and initialize data
		self.parkImageFile=parkImageFile
		self.park=park
		self.attractions=park.attractions
		self.attractionMetaData=attractionMetaData
		self.peoplePerActivity=peoplePerActivity
		self.ticks=0
		self.isPlaying=False

		#Use the hourlyArrivalRates to find what time the park opens and closes.
		arrivalTimes=[datetime.datetime.strptime(k,"%I:%M %p") for k in hourlyArrivalPercents]
		arrivalTimes = [t.hour*60+t.minute for t in arrivalTimes]
		self.parkOpen = min([t if t!=0 else 1440 for t in arrivalTimes])
		self.parkClose = park.park_close+self.parkOpen
		self.storeMaxQueues()


		#Create Window
		self.app = QApplication(sys.argv)
		super(GUI_CLASS,self).__init__()
		self.hBox=QHBoxLayout()
		self.hBoxChildren=[]

		#Create the layout
		self.hBoxChildren.append(QVBoxLayout())
		self.hBoxChildren.append(QVBoxLayout())
		for child in self.hBoxChildren:
			self.hBox.addLayout(child)

		#Populate the layout
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
		"""
			Creates self.attrMaxWait, a dict that gives the max wait time for each attraction.
		"""
		self.attrMaxWait={}
		for k,v in self.attractions.items():
			waits = [w for w in v.history["queue_wait_time"].values()]
			self.attrMaxWait[k]=max(waits)

	def getTimeKeys(self):
		"""
			Returns a list containing all of the simulation times for which data has been created.
		"""
		T = []
		for k,v in self.attractions.items():
			t = [tt for tt in v.history["queue_wait_time"].keys() if tt not in T]
			T += t
		T.sort(key=lambda x: int(x))
		return T

	def play(self,updateFunction,period):
		"""
			Plays the animation for the window

			Inputs:
				updateFunction: this is the function that is called for each time step
				period: this is how many miliseconds between frames
		"""

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
		"""
			Pauses the animation
		"""
		self.threadTimer.stop()
		self.isPlaying=False

	def reset(self):
		"""
			Sets the simulation timer to the park's openning
		"""
		self.setTime(self.parkOpen)
		self.times=self.getTimeKeys()
		

	def addControlButtons(self,parent):
		"""
			Creates the row of control buttons with the time window.
			
			Inputs:
				parent: the row that the buttons will be added to.
		"""

		buttonRow = QHBoxLayout()
		parent.addLayout(buttonRow)

		#Play button
		button1=QPushButton("Play",self)
#		button1.setToolTip("Example button")
		def f():
			if not self.isPlaying:
				return self.play(self.animateSimulation,100)
		button1.clicked.connect(f)
		buttonRow.addWidget(button1)

		#Pause button
		button2=QPushButton("Pause",self)
		def f(): return self.pause()
		button2.clicked.connect(f)
		buttonRow.addWidget(button2)

		#Reset Button
		button3=QPushButton("Reset",self)
		def f(): return self.reset()
		button3.clicked.connect(f)
		buttonRow.addWidget(button3)

		#Add the time window
		self.timeEdit = QTimeEdit()
		print(dir(self.timeEdit))
		self.timeEdit.userTimeChanged.connect(self.updateDisplay)
		buttonRow.addWidget(self.timeEdit)
		self.setTime(self.parkOpen)

		#Add space to the bottom of the column
		buttonRow.addWidget(QLabel(),1)


	def getTime(self):
		"""
			Returns the time in the time window as the number of minutes since midnight.
		"""
		t=self.timeEdit.time()
		return t.hour()*60+t.minute()

	def setTime(self,t):
		"""
			Sets the time window based on the requested time.
			
			Inputs:
				t: the number of minutes since midnight.
		"""
		t=t%1440
		h=t//60
		m=t%60
		self.timeEdit.setTime(QTime(h,m))

	def animateSimulation(self):
		"""
			Stops the animation if the end is reached. Otherwise, updates the display and continues.
		"""
		if self.getTime()>=self.parkClose:
			self.threadTimer.stop()
			self.isPlaying=False
			return
		self.updateDisplay()
		self.setTime(self.getTime()+1)


	def createParkSummaries(self, parent):
		"""
			Initializes the column of park-centric stats.
			
			Inputs:
				parent: the column that the data views will be added to.
		"""

		#Each data entry is a label, key, and value
		data = [["Attendance","Attendance",0]]
		data+= [["People "+k.capitalize(),k,v] for k,v in self.peoplePerActivity[0].items()]

		parent.addWidget(QLabel(),1)
		self.summaryWidgets = {}
		for label, key, value in data:
			#Create the data label
			l1=QLabel()
			l1.setAlignment(Qt.AlignCenter)
			l1.setText(label)
			l1.setFont(QFont(FONT,16))
			parent.addWidget(l1)

			#Create the data window
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
		"""
			Adds the park map to the GUI
			
			Inputs:
				imFile: path to the image file for the park map.
				parent: the column that the image will be loaded to.
		"""
		#Create a GraphicsView for the Map
		self.graphicsView=QGraphicsView()
		self.graphicsView.setRenderHint(QPainter.Antialiasing)
		self.graphicsView.setRenderHint(QPainter.HighQualityAntialiasing)
		parent.addWidget(self.graphicsView)
		self.scene = QGraphicsScene()
		self.graphicsView.setScene(self.scene)

		#Add the map
		image=QPixmap(imFile)
		image=image.scaledToHeight(800)
		self.scene.addPixmap(image)



	def createAttractionCallouts(self):
		"""
			Create the callouts for the attraction wait times
		"""
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
		"""
			Update the attraction and park data displayed at each frame by calling a function for each
		"""

		self.updateAttractionCallouts()
		self.updateParkSummaries()
			

	def updateParkSummaries(self):
		"""
			Update the park data displayed for the current time step.
		"""
		time = self.getTime()-self.parkOpen

		count = self.park.history["total_active_agents"][time]
		self.summaryWidgets["Attendance"].setText(str(count))

		for k,v in self.peoplePerActivity[time].items(): 
			self.summaryWidgets[k].setText(str(v))


	def updateAttractionCallouts(self):
		"""
			Update the attraction data displayed for the current time step.
		"""
		time = self.getTime()-self.parkOpen
		#For each attraction with meta data
		for meta in self.attractionMetaData:
			#Get the meta data and the object
			name=meta["name"]
			obj=self.attractions[name]
			x, y = meta["x_pos"], meta["y_pos"]

			#Find the current wait time and the color for the background
			q=obj.history["queue_wait_time"][time]
			percentOfHigh=q/self.attrMaxWait[name]
			q=str(q)

			color=[int(c1*(1-percentOfHigh)+c2*percentOfHigh) for c1,c2 in zip(self.calloutColorBase,self.calloutColorHigh)]

			#Update the callout
			self.setPolygonColor(self.calloutBackgrounds[name],self.borderColor,color)
			obj = self.attrCallouts[name]
			obj.setText(q)

			#Reposition the box in case the width changed
			height=obj.boundingRect().height()
			width=obj.boundingRect().width()
			obj.setPos(int(x-width/2),int(y-height/2))


	def addRoundedPolygon(self,xy,borderColor,bgColor):
		"""
			Draw a polygon with a specified list of vertices, but round the corners.
			
			Inputs:
				xy: A list of (x,y) pairs for the polygon corners.
				borderColor: The color to draw the polygon border.
				bgColor: The color to fill the polygon
		"""
		x = [x[0] for x in xy]
		y = [x[1] for x in xy]

		#The radius for the corner curve
		R = 2
	

		pointsX,pointsY=[],[]
		#For each vertex
		for i in range(len(x)):
			#Calculate the angles of the sides that meet at that vertex
			x0, x1, x2 = x[i-1],x[i],x[(i+1)%len(x)]
			y0, y1, y2 = y[i-1],y[i],y[(i+1)%len(x)]

			theta2=np.arctan2(y1-y2,x1-x2)
			if y1-y2==0 and x1-x2<0:
				theta2=-np.pi
			theta1=np.arctan2(y1-y0,x1-x0)
			if y1-y0==0 and x1-x0<0:
				theta1=-np.pi

			#Get the "halfway" angle
			thetaA=(theta2-theta1)/2

			#DO some trig to find the distance from the center of the curve.
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

			#Find the angles purpendicular to the sides, going through that center
			t1,t2=theta1-np.pi/2,theta2+np.pi/2

			if t2-t1>2*np.pi:
				t1+=2*np.pi

			#Going create a point for each angle
			for theta in np.linspace(t1,t2,20):

				pointsX.append(xb+s*np.cos(theta))
				pointsY.append(yb+s*np.sin(theta))

		#Convert the ordered pair points into QPoints and create the polygon
		points = [QPointF(x,y) for x,y in zip(pointsX,pointsY)]
		polygon=QPolygonF()
		for p in points:
			polygon.append(p)

		#Add graphics properties and return the polgyon
		item = QGraphicsPolygonItem(polygon)
		self.setPolygonColor(item,borderColor,bgColor)

		self.scene.addItem(item)
		self.scene.update()

		return item


	def setPolygonColor(self,item,borderColor,bgColor):
		"""
			Set the colors of a polygon or other drawn shape
			
			Inputs:
				item: The polygon to be colored
				borderColor: The color to draw the polygon border.
				bgColor: The color to fill the polygon
		"""
		#Set the border color and width (1.5)
		pen=QPen(QColor(*tuple(borderColor)),1.5)
		item.setPen(pen)

		#Set the fill
		brush=QBrush(QColor(*tuple(bgColor)))
		item.setBrush(brush)

		#Apply the color
		item.update()
		self.scene.update()

		return item





