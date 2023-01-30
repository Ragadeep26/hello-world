from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer,flowables,Image,Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch,mm
from reportlab.lib.pagesizes import letter, A4
from matplotlib import pyplot as plt
from matplotlib import style
from reportlab.lib.utils import ImageReader
import image
from io import BytesIO
import os
import reportlab.lib, reportlab.platypus


class MyPdf(object):
    def __init__(self, custom_data):
        self.custom_data = custom_data
        self.doc = ... # your doc

    def _header_footer(self, canvas, doc):
        # you can access self.custom_data here
        #header
        width,height=doc.pagesize
        styles=getSampleStyleSheet()
        #header image
        img=Image(self.custom_data[6],width=40,height=40)
        img.wrapOn(canvas,width,height)
        img.drawOn(canvas,7.3*inch,10.7*inch)
        #top left headings(header)
        canvas.setFont('Times-Roman',10)
        canvas.drawString(0.5*inch,10.9*inch, self.custom_data[1])
        canvas.drawString(0.5*inch,10.7*inch, self.custom_data[2])
        #top right headings(header)
        canvas.setFont('Times-Roman',7)
        canvas.drawString(6.5*inch,10.7*inch, "Date :%s" %self.custom_data[3])
        #horizontal line (header)
        canvas.line(0.4*inch,10.6*inch,8*inch,10.6*inch)
        #footer
        width,height=doc.pagesize
        styles=getSampleStyleSheet()
        #horizontal line(footer)
        canvas.line(0.4*inch,0.9*inch,8*inch,0.9*inch)
        #page number(footer)
        canvas.setFont('Times-Roman',9)
        canvas.drawString(7.5*inch, 0.75 * inch, "Page %d" %doc.page)
        #bottom left headings
        canvas.drawString(0.5*inch,0.75*inch, self.custom_data[4])
        canvas.setFont('Times-Roman',7)
        canvas.drawString(0.5*inch,0.65*inch,self.custom_data[5])
       
    def build(self,elements):
        #creating pdf and assigning the name 
        self.doc = SimpleDocTemplate(self.custom_data[0],pagesize = A4, rightMargin = 72, leftMargin = 72, topMargin = 80,bottomMargin = 80)
        self.doc.build(elements, onFirstPage=self._header_footer,onLaterPages=self._header_footer)

#custom_data[1] = test_number
#custom_data[2] = detailed report
#custom_data[3] = date
#custom_data[4] = company_name
#custom_data[5] = file_location
#custom_data[6] = image_path