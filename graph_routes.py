from pyx import *
import glob
import csv
import os
import math

for root, dirs, files in os.walk("."):
  for dir in dirs:
    c=canvas.canvas()
    print '----------------------------------' + dir
    for filename in glob.glob(dir + '/*.csv'):
      f=open(filename, 'rb')
      datareader=csv.reader(f, delimiter=',')
      old_x=0
      old_y=0
      for row in datareader:
        if row[0] == 'x':
          continue
        x=int(float(row[0]))
        y=int(float(row[1]))
        mag = ((x-old_x) ** 2 + (y - old_y) ** 2) ** 0.5
        print(mag)
        if (mag < 1):
            color_line = color.gradient.Rainbow.getcolor(0)
        else:
            color_line = color.gradient.Rainbow.getcolor(math.log10(mag)/3)
        c.stroke(path.line(old_x,old_y,x,y),[style.linewidth(0.1),style.linecap.round, color_line])
        old_x = x
        old_y = y
    c.writePDFfile(dir)
