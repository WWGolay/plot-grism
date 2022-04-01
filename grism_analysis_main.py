'''
grism_analysis_main

prototype updated last Mar 27th 2022
'''
from bin.grism_analysis_web import grism_web
from bin.grism_analysis_lib import grism_analysis
import os
import matplotlib.pyplot as plt

def main():
    web_analyzer = grism_web()
    fits_image = web_analyzer.get_fits(web_analyzer) #Get initial fits image
    
    cal_file = './calibrations/grism_cal_6_2022_3_25.csv'
    if not os.path.exists(cal_file):
        raise Exception("Calibration file not located!")
    with open("temp.fts", "wb") as binary_file: #Write fits image to file so it can be analyzed
        binary_file.write(fits_image['content'])
    
    grism_analyzer = grism_analysis("temp.fts", cal_file)#instantiate analyzer with fits image and calibration file
    web_analyzer.run_analysis(web_analyzer, grism_analyzer)

if __name__ == '__main__':
    main()
