'''
grism_analysis_main

prototype edited Mar 27th 2022 - AS
last updated 2 Apr 2022 - WG

'''
from bin.grism_analysis_web import grism_web
from bin.grism_tools_lib import grism_tools
import os,glob
from datetime import date, timedelta, datetime
import astropy.io.fits as pyfits

def main():
    web_analyzer = grism_web()
    take_input = True
    if take_input:
        fits_image, calibration = web_analyzer.get_fits(web_analyzer) # Get initial fits image

        with open('temp/im.fts', 'wb') as binary_file: # Write fits image to file so it can be analyzed
            binary_file.write(fits_image['content'])
    
        if calibration == None: # TODO: Add advanced option on first page for entry of custom calibration file, otherwise search for one
            defaultDir = 'calibrations/'
            
            # Get date of image to iterate back to latest calibration file, parse header into date object
            hdulist = pyfits.open('temp/im.fts')
            fitsDate = hdulist[0].header['DATE-OBS']
            startDate = date(int(fitsDate[0:4]), int(fitsDate[5:7]), int(fitsDate[8:10]))
            
            # Iterate to find latest calib file in last 180 days
            for testDate in (startDate - timedelta(n) for n in range(180)):
                if os.path.isfile(defaultDir+'grism_cal_6_'+testDate.strftime('%Y_%m_%d')+'.csv'):
                    cal_file = defaultDir+'grism_cal_6_'+testDate.strftime('%Y_%m_%d')+'.csv'
                    break
                else: continue
        else:
            with open('temp/cal.csv', 'wb') as binary_file: # Write fits image to file so it can be analyzed
                binary_file.write(calibration['content'])
            cal_file = 'temp/cal.csv'
    else:
        cal_file = 'temp/cal.csv'

    if not os.path.exists(cal_file):
        web_analyzer.raise_calibration_error()
    
    grism_analyzer = grism_tools('temp/im.fts', cal_file) # instantiate analyzer with fits image and calibration file
    web_analyzer.run_analysis(web_analyzer, grism_analyzer)

if __name__ == '__main__':
    main()