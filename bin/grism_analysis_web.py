'''
grism_analysis_web

prototype updated last Mar 30th 2022
'''

import io
#from turtle import width
from pywebio.input import file_upload, input_group, NUMBER
from pywebio.output import put_text, put_image, use_scope, put_button, popup, clear, put_button,put_html,put_collapse
from pywebio.pin import *
from pywebio import config,start_server,session
import pywebio.input as pywebio_input
import pywebio.pin as pywebio_pin
import io
import matplotlib.pyplot as plt
from bin.grism_tools_lib import grism_tools
"""
Notes:
-Class uses the PywebIO persistent-input(PIN) functionality. Every input that alters graphs first sets the attribute, then
calls for the linked graphs to be updated.
-The use_scope method is used to place the graphs, this allows the webpage to keep all graphs in the same place when clearing
the sections and re-making the graphs. When calling these functions from the PIN module, it automatically passes the altered value
as a parameter, but this isn't useful (some plots use multiple parameters) so a dummy parameter is used
"""
class grism_web:
    def __init__(self):
        config(theme='minty', title="Iowa Grism Analysis")
        self.lines_checkbox_dict=[
            {'label':'Hydrogen (Balmer)', 'value':'H', 'selected':True},
            {'label':'Helium', 'value':'He'},
            {'label':'Carbon', 'value':'C'},
            {'label':'Nitrogen', 'value':'N'},
            {'label':'Oxygen', 'value':'O'},
            {'label':'Calcium', 'value':'Ca'}]
        #Set default parameters for graphs.
        self.lines=['H']
        self.minWL = 380
        self.maxWL = 750
        self.medavg = 3
        self.temperature = 10000
        self.stripHeight = -1
        self.stripCenter = -1
        self.gaussMinWl = 651
        self.gaussMaxWl = 661
        self.emission_check_box_dict = [{'label':'Emission', 'value':1, 'selected':False}]
        self.emission = 0

        #saved images
        self.grism_buff = None
        self.spectrum_buff = None
        self.strip_buff = None
        self.gauss_buff = None
        self.twoxtwo_buff = None
        self.rectified_buff = None

    def raise_calibration_error(self):
        popup("ERROR, CALIBRATION FILE NOT FOUND. MANUALLY UPLOAD OR CONTACT SOFTWARE MANAGER")

    """Removed 4/6/2022 to simplify program and remove anchored dropdown
    def resubmit_grism_image(self, img):
        with open('temp/temp.fts', 'wb') as binary_file: # Write fits image to file so it can be analyzed
            binary_file.write(img['content'])
        grism_analyzer = grism_tools('temp/temp.fts', self.analyzer.get_calib())
        self.run_analysis(self, grism_analyzer)
    """

    def update_med_avg(self, med_avg):
        m = med_avg
        if(m is None):
            m=3
        if(med_avg%2 == 0):
            m -= 1
            #pin.medavg = m 
        self.medavg = m

    def update_lower_wl(self, lower):
        if lower > self.maxWL:
            lower = self.maxWL - 1
            pin.minWL = self.maxWL - 1
        self.minWL = lower
    
    def update_upper_wl(self, upper):
        if upper < self.minWL:
            upper = self.minWL + 1
            pin.maxWL = self.minWL + 1        
        self.maxWL = upper
        
    def update_lines(self, lines):
        self.lines = lines

    def update_mode(self, mode):
        self.mode = mode

    def update_strip_height(self, height):
        self.stripHeight = height

    def update_strip_center(self, center):
        self.stripCenter = center

    def update_temperature(self, temperature):
        self.temperature = temperature

    def update_gauss_min(self, min):
        if min > self.gaussMaxWl:
            min = self.gaussMaxWl - 1
            pin.minGauss = self.gaussMaxWl - 1
        self.gaussMinWl = min
    
    def update_gauss_max(self,max):
        if max < self.gaussMinWl:
            max = self.gaussMinWl + 1
            pin.maxGauss = self.gaussMinWl + 1
        self.gaussMaxWl = max
    
    def update_emission(self, emission):
        self.emission = emission

    @use_scope('fits_section')
    def update_fits(self, dummy="dummy"):
        self.grism_buff = self.analyzer.plot_image(figsize=(10,10), cmap='gray')    
        clear(scope='fits_section')
        put_image(self.grism_buff.getvalue())

    @use_scope('strip_section')
    def update_strip(self, dummy=None):
        if self.stripHeight != -1 and self.stripCenter != -1:
            self.analyzer.apply_calibration("test", self.stripHeight, self.stripCenter)        
        self.strip_buff = self.analyzer.plot_strip(cmap='jet')
        clear(scope='strip_section')
        put_image(self.strip_buff.getvalue())

    @use_scope('2b2_section')
    def update_two_by_two(self, dummy=None):#TODO needs to be updated to comply with other ways of saving    
        self.twoxtwo_buff = self.analyzer.plot_2x2(ref_file='', medavg=self.medavg, xlims =[self.minWL,self.maxWL])
        clear(scope='2b2_section')
        put_image(self.twoxtwo_buff.getvalue())                   

    @use_scope('spectrum_section')
    def update_spectrum(self, dummy=None):   
        self.spectrum_buff = self.analyzer.plot_spectrum(calibrated = True, plot_lines = self.lines,title='', medavg = self.medavg, xlims = [self.minWL, self.maxWL])
        clear(scope='spectrum_section')
        put_image(self.spectrum_buff.getvalue())

    @use_scope('gauss_section')
    def update_gauss(self, dummy=None):
        self.gauss_buff = self.analyzer.fit_gaussian(self.gaussMinWl,self.gaussMaxWl, emission = self.emission)
        clear(scope='gauss_section')
        put_image(self.gauss_buff.getvalue())

    @use_scope('rectified_section')
    def update_rectified(self, dummy = None):#TODO needs to be updated to comply with other ways of saving
        self.rectified_buff = self.analyzer.plot_rectified_spectrum(self.temperature,wavemin=self.minWL,wavemax=self.maxWL)         
        clear(scope='rectified_section')
        put_image(self.rectified_buff.getvalue())     

    def dowload_pdf(self):
        self.analyzer.get_pdf(self.lines,self.medavg,self.minWL,self.maxWL,self.gaussMinWl, self.gaussMaxWl,self.emission)
        content = open('./temp/Grism.pdf', 'rb').read()  
        session.download("Grism.pdf",content)

    def download_grism(self):
        session.download("grism.png", self.grism_buff.getvalue())

    def download_strip(self):
        session.download("strip.png", self.strip_buff.getvalue())      

    def download_spectrum(self):
        session.download("spectrum.png", self.spectrum_buff.getvalue())

    def download_gauss(self):
        session.download("gauss.png", self.gauss_buff.getvalue())

    def download_rectified(self):
        session.download("rectified.png", self.rectified_buff.getvalue())

    def download_2b2(self):
        session.download("2b2.png", self.twoxtwo_buff.getvalue())

    def dowload_pngs(self):            
        self.download_grism()
        self.download_strip()
        self.download_spectrum()
        self.download_gauss()
        self.download_rectified()
        self.download_2b2()

    def get_fits(self):
        fits_input = [
        pywebio_input.file_upload("Select a .fts file to analyze",name="fits", accept=[".fts",".fits",".fit"], required=True),#Fits image file select
        #pywebio_input.file_upload("(Advanced) Select a manual .csv calibration file (optional)", name="cal", accept=".csv", required=False)
        ]
        form_ans=input_group("Select a Fits image to analyze", fits_input)
        fits = form_ans['fits']
        #cal = form_ans['cal']
        return fits,None

    def run_analysis(self, grism_analyzer):
        self.analyzer = grism_analyzer #Copy analyzer from constructor
        
        #Updated defaults from calibration
        minwave, maxwave = grism_analyzer.wave_range()
        self.update_lower_wl(minwave)
        self.update_upper_wl(maxwave)


        logo = open('./images/UILogoTransparent.png', 'rb').read()  
        put_image(logo, height="20%", width="50%")     
        put_html("<h1>Grism Analysis Results</h1>")
        put_html("<h3>Image</h3>")
        put_collapse("Help","This is the grism image. Placing more text here would not be that hard")
        self.update_fits()#put fits image
        put_button("Download Grism PNG", onclick=self.download_grism)#grism Image PNG Download

        """4/6/2022 Removed for initial draft to simplify 
        pywebio_pin.put_input(label="Manual Strip Height", name = "stripHeight", type=NUMBER)
        pywebio_pin.pin_on_change(name="stripHeight", onchange=self.update_strip_height)
        pywebio_pin.put_input(label="Manual Strip Center", name = "stripCenter", type=NUMBER)
        pywebio_pin.pin_on_change(name="stripCenter", onchange=self.update_strip_center)
        put_button("Execute Manual Strip Calibration", onclick=self.update_strip)
        """        
        self.update_strip()
        put_button("Download Strip PNG", onclick=self.download_strip)#Strip Image PNG Download

        put_html("<h3>Spectrum</h3>")   
        pywebio_pin.put_checkbox(label="Plot Lines", name="plotLines", options=self.lines_checkbox_dict)#pin spectrum options
        pywebio_pin.pin_on_change(name="plotLines", onchange=self.update_lines)
        pywebio_pin.pin_on_change(name="plotLines", onchange=self.update_spectrum)

        #pywebio_pin.put_input(label="Median Average", name = "medavg", type=NUMBER, placeholder=3)
        pywebio_pin.put_slider(label="Minimum Average", name="medavg", value= self.medavg, min_value= 1, max_value = 21, step = 2)
        pywebio_pin.pin_on_change(name="medavg", onchange=self.update_med_avg)
        pywebio_pin.pin_on_change(name="medavg", onchange=self.update_spectrum)

        pywebio_pin.put_slider(label="Minimum Wavelength", name="minWL", value= self.minWL, min_value= self.minWL, max_value = self.maxWL, step = 5)#pin gauss options
        pywebio_pin.pin_on_change(name="minWL", onchange=self.update_lower_wl)
        pywebio_pin.pin_on_change(name="minWL", onchange=self.update_spectrum)

        pywebio_pin.put_slider(label="Maximum Wavelength", name="maxWL", value= self.maxWL, min_value= self.minWL, max_value = self.maxWL, step = 5)
        pywebio_pin.pin_on_change(name="maxWL", onchange=self.update_upper_wl)
        pywebio_pin.pin_on_change(name="maxWL", onchange=self.update_spectrum)        

        self.update_spectrum(self.lines)#put spectrum

        put_button("Download Spectrum PNG", onclick=self.download_spectrum)#Spectrum Image PNG Download

        put_html("<h3>Gaussian Filter</h3>")        
        pywebio_pin.put_slider(label="Minimum Gauss Wavelength", name="minGauss", value= self.gaussMinWl, min_value= self.minWL, max_value = self.maxWL, step = 1)#pin gauss options
        pywebio_pin.pin_on_change(name="minGauss", onchange=self.update_gauss_min)
        pywebio_pin.pin_on_change(name="minGauss", onchange=self.update_gauss)

        pywebio_pin.put_slider(label="Maximum Gauss Wavelength", name="maxGauss", value= self.gaussMaxWl, min_value= self.minWL, max_value = self.maxWL, step = 1)
        pywebio_pin.pin_on_change(name="maxGauss", onchange=self.update_gauss_max)
        pywebio_pin.pin_on_change(name="maxGauss", onchange=self.update_gauss)

        pywebio_pin.put_checkbox(label="Emission Line", name="emission", options=self.emission_check_box_dict)
        pywebio_pin.pin_on_change(name="emission", onchange=self.update_emission)
        pywebio_pin.pin_on_change(name="emission", onchange=self.update_gauss)
        
        self.update_gauss()#put gauss
        put_button("Download Gauss PNG", onclick=self.download_gauss)#Gauss Image PNG Download
        
        self.update_two_by_two()

        put_button("Download 2x2 PNG", onclick=self.download_2b2)#Gauss Image PNG Download

        pywebio_pin.put_input(label="Temperature (K)", name = "temper", type=NUMBER, placeholder=10000)
        pywebio_pin.pin_on_change(name="temper", onchange=self.update_temperature)
        pywebio_pin.pin_on_change(name="temper", onchange=self.update_rectified)

        self.update_rectified()

        put_button("Download Rectified PNG", onclick=self.download_rectified)#Gauss Image PNG Download

        
        put_html("</hr><h4>Dowload All Images</h4>")
        put_button("Dowload PDF", onclick=self.dowload_pdf);
        put_button("Dowload PNGs of All Plots", onclick=self.dowload_pngs)

        session.hold()               