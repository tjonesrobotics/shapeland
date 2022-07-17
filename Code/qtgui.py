from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import sys

'''
class MainWindow(QMainWindow):
	def __init__(self, parent=None, *args, **kwargs):
		super(MainWindow,self).__init__(*args,**kwargs)

		self.setWindowTitle("This is the window I made")
		label = QLabel("This is the text that I typed")
		label.setAlignment(Qt.AlignCenter)

		self.setCentralWidget(label)

		button = QPushButton("Press Me!")
		button.setCheckable(True)
		button.clicked.connect(self.the_button_was_clicked)
		button.released.connect(self.the_button_was_released)
		button.clicked.connect(self.the_button_was_toggled)

		self.setCentralWidget(button)
		self.button_is_checked=True
		self.button = button

		self.windowTitleChanged.connect(self.the_window_changed)
'''

class Window(QWidget):
	def __init__(self, parent=None):
		super(Window, self).__init__(parent)
		
		p=QPixmap("ep_map_2021.png")
		p=p.scaledToHeight(500)
		pixmap_label = QLabel(
			pixmap=p
		)
		
		text_label = QLabel(text="delete")
		print("XX")
		lay = QVBoxLayout(self)
		print("YY")
		lay.addWidget(pixmap_label, alignment=Qt.AlignCenter)
		lay.addWidget(text_label, alignment=Qt.AlignCenter)

	def the_window_changed(self):
		print("The window title has been changed")

	def the_button_was_clicked(self):
		self.button.setText("It's been clicked.")
		self.button.setEnabled(False)
		self.setWindowTitle("Changed title")
		print("Clicked!")
	def the_button_was_released(self):
		print("Release!",self.button.isChecked())
	def the_button_was_toggled(self,checked):
		self.button_is_checked=checked
		print("Clicked?",checked)
'''
app = QApplication(sys.argv)
window=Window()
window.show()
#app.exec_()
app.exec_()
'''



class DemoApp(QMainWindow):
	def __init__(self, parent=None):

		super(DemoApp, self).__init__()

		# set up the layout for the MainWindow. 
		grid_layout = QGridLayout()
		self.graphicsView = QGraphicsView()
		self.graphicsView.setRenderHint(QPainter.Antialiasing)
		self.graphicsView.setRenderHint(QPainter.HighQualityAntialiasing)
		grid_layout.addWidget(self.graphicsView)

		widget = QWidget()
		widget.setLayout(grid_layout)

		self.setCentralWidget(widget)

		scene = QGraphicsScene()
		self.graphicsView.setScene(scene)

		p=QPixmap("ep_map_2021.png")
		p=p.scaledToHeight(800)
		pixmap_label = QLabel(
			pixmap=p
		)
		scene.addPixmap(p)


		mytext1 = QGraphicsSimpleTextItem('the first label')
		scene.addItem(mytext1)

		mytext2 = QGraphicsSimpleTextItem('the second label')
		scene.addItem(mytext2)
		mytext2.setPos(100,350)
		mytext2.setText("changed to this")



		xy=[[0,0],[100,0],[100,100],[50,125],[0,100]]
		x = [x[0] for x in xy]
		y = [x[1] for x in xy]

		print(x,y)

		r = 3

		import numpy as np
		pointsX,pointsY=[],[]
		for i in range(len(x)):
			x0, x1, x2 = x[i-1],x[i],x[(i+1)%len(x)]
			y0, y1, y2 = y[i-1],y[i],y[(i+1)%len(x)]

			theta2=np.arctan2(y2-y1,x2-x1)
			if y2-y1==0 and x2-x1<0:
				theta2=-np.pi
			theta1=np.arctan2(y1-y0,x1-x0)
			if y1-y0==0 and x1-x0<0:
				theta1=-np.pi

			xb=x1-r*np.cos(theta1)+r*np.cos(theta1+np.pi/2)
			yb=y1-r*np.sin(theta1)+r*np.sin(theta1+np.pi/2)
			print("XY",xb,yb,[y1-y0,x1-x0])

			#See if (xb,yb) is inside the polygon. Travel up from the point to count crossings
			segmentsCrossed=0
			for j in range(len(x)):
				if (xb<x[j] and xb<x[j-1]) or (xb<x[j] and xb<x[j-1]):
					continue
				if (yb<y[j] and yb<y[j-1]) or (yb<y[j] and yb<y[j-1]):
					continue
				if x[j]-x[j-1]==0 and xb!=x[j]:
					continue
				else:
					m=(y[j]-y[j-1])/(x[j]-x[j-1])
					b=y[j]-m*x[j]

					yProjection=m*xb*b
					if yProjection>yb:
						segmentsCrossed+=1
			if segmentsCrossed%2==0:
#				xb=x1-r*np.cos(theta1)-r*np.cos(theta1+np.pi/2)
#				yb=y1-r*np.sin(theta1)-r*np.sin(theta1+np.pi/2)
				print("CROSSING")
				input()


			for theta in np.linspace(theta1,theta2,20):
				print(theta,theta1,theta2)
				theta-=np.pi/2

				pointsX.append(xb+r*np.cos(theta))
				pointsY.append(yb+r*np.sin(theta))

			'''
			pointsX.append(xb+r*np.cos(theta1+90))
			pointsY.append(yb+r*np.sin(theta1+90))
			pointsX.append(xb-r*np.cos(thetaM))
			pointsY.append(yb-r*np.sin(thetaM))
			pointsX.append(xb+r*np.cos(theta2+90))
			pointsY.append(yb+r*np.sin(theta2+90))

			pointsX.append(x1+r*np.cos(theta1-90))
			pointsX.append(x1+r*np.sin(theta1-90))
			'''

		print(pointsX)
		print(pointsY)
		points = [QPointF(x,y) for x,y in zip(pointsX,pointsY)]
		polygon=QPolygonF()
		for p in points:
			polygon.append(p)

		item = QGraphicsPolygonItem(polygon)
		item.setPen(QPen(Qt.red))
		item.setBrush(QBrush(Qt.red))
		scene.addItem(item)


	def paint(self):
		painter = QPainter(self)
		painter.setPen(QPen(Qt.black, 5, Qt.SolidLine))


		painter.drawPolygon(points)




app = QApplication(sys.argv)
demo_app = DemoApp(None)

demo_app.show()

sys.exit(app.exec_())
