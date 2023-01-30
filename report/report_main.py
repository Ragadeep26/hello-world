from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer,flowables,Image,Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch,mm
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import letter, A4
import image
import datetime
from io import BytesIO
import os
import reportlab.lib, reportlab.platypus
from report_class import MyPdf


PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0]
styles = getSampleStyleSheet()

def go():

    #creating date
    tday = datetime.date.today()
    date = tday.strftime("%d/%m/%y")

    Story = [Spacer(1,0.2*inch)]
    Heading1 = "Details ::"
    styles.add(ParagraphStyle(name='Justify', fontName = 'Times-Bold', fontSize = 10))
    Story.append(Paragraph(Heading1, styles["Justify"]))
    Story.append(Spacer(1, 12))

    #creating manual data in the report
    styles.add(ParagraphStyle(name='Normal1', fontName = 'Times-Roman', fontSize = 9))
    ptext = '<font size=8>Borehole Name : BH 1</font>'
   
    Story.append(Paragraph(ptext, styles["Normal1"]))
    ptext = "Casing Diameter :3.0 .m/ 2.92 m"
    Story.append(Paragraph(ptext, styles["Normal1"]))
    ptext = "ATM Pressurew : 10.0 kPa"
    Story.append(Paragraph(ptext, styles["Normal1"]))
    ptext = "Penetration Depth : 15.0 .m"
    Story.append(Paragraph(ptext, styles["Normal1"]))
    ptext = "Installation Days : 1.0 days"
    Story.append(Paragraph(ptext, styles["Normal1"]))

    #spacer gaurantees the defined limit space between the paragraphs

    Story.append(Spacer(1, 12))

    Heading2 = "Results ::"
    styles.add(ParagraphStyle(name='Justify1', fontName = 'Times-Bold', fontSize = 10))
    Story.append(Paragraph(Heading2, styles["Justify1"]))
    Story.append(Spacer(1, 26))
    
    #creating table 

    def read_m(path):
        with open(path) as file:
            lines = []
            for line in file:
                #changing string in to float for rounding up
                line = float(line)
                x = (round(line,3))
                #changing float element to string for strip
                x = str(x)
                lines.append(x.rstrip())
        return lines
    #these variables depend on the number of 'm' files(moniman)
    a = read_m(r"C:\Users\vli\Desktop\m")
    b = read_m(r"C:\Users\vli\Desktop\m1")
    rows = [["swx","sxs","sxcd","azxs","tyhgf"],a,b,a,b,a,b,a,b,a,b,a,b,a,b,a,b,a,b,a,b,a,b,a,b,a,b,a,b,a,b,a,b,a,b,a,b,a,b]
    #length_rows is used for font formatting
    Length_rows = len(rows)
    table = Table(rows,colWidths=None,rowHeights=None,style = None,repeatRows=1,repeatCols=0)
    table.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-Length_rows),'Times-Bold'),('FONTNAME',(0,1),(-1,-1),'Times-Roman'),('ALIGN',(0,0),(-1,-1),'CENTER'),('INNERGRID',(0,0),(-1,-1),0.25,colors.black),
                               ('BOX',(0,0),(-1,-1),0.25,colors.black)]))
    Story.append(table)
    
    Story.append(Spacer(1,30))
    
    #matplotlib picture
    P=Image(r"C:\Users\vli\Desktop\matty.png",width=5*inch,height=4*inch)
    

    Story.append(P)

    Story.append(Spacer(1, 10))
    
    #giving the custom data in the report...see the class for the order
    custom_data = ["Reportlab.pdf","Test 01","Detailed Report",date,"BAUER Spezialtiefbau GmbH","C:1/2_casing + Program/tobe/Casing Simulator/TEST_Project.ba",
                    r"C:\Users\vli\Desktop\BAUER.png"]
    my_pdf = MyPdf(custom_data)
    my_pdf.build(Story)
go()

#for opening the created pdf
xx = "Reportlab.pdf"
print("writing")
os.startfile(xx)
 
