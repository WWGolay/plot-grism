'''
grism_analysis_main

prototype edited Mar 27th 2022 - AS
last updated 7 Apr 2022 - WG

'''

# Python imports
from datetime import date, timedelta, datetime
import astropy.io.fits as pyfits
import os,glob

# Custom libraries
from bin.grism_analysis_web import grism_web
from bin.grism_tools_lib import grism_tools
from config import setup_config

def main():
    cfg = setup_config.read('grism-gui.cfg')

    web_analyzer = grism_web()
    default_temp_dir = cfg.get('default', 'default_temp_dir')
    take_input = True #cfg.get('default', 'take_input')
    if take_input:
        #fits_image, calibration = web_analyzer.get_fits(web_analyzer) # Get initial fits image
        fits_image, calibration = web_analyzer.get_fits() # Get initial fits image

        with open(default_temp_dir+'/im.fts', 'wb') as binary_file: # Write fits image to file so it can be analyzed
            binary_file.write(fits_image['content'])
    
        if calibration == None: # TODO: Add advanced option on first page for entry of custom calibration file, otherwise search for one
            defaultDir = cfg.get('default', 'default_calibration_dir')
            
            # Get date of image to iterate back to latest calibration file, parse header into date object
            hdulist = pyfits.open(default_temp_dir+'/im.fts')
            fitsDate = hdulist[0].header['DATE-OBS']
            startDate = date(int(fitsDate[0:4]), int(fitsDate[5:7]), int(fitsDate[8:10]))
            
            # Iterate to find latest calib file in last 180 days
            day_iter = int(cfg.get('default', 'find_calib_by_date'))
            if day_iter > 0:
                for testDate in (startDate - timedelta(n) for n in range(day_iter)):
                    if os.path.isfile(defaultDir+'grism_cal_6_'+testDate.strftime('%Y_%m_%d')+'.csv'):
                        cal_file = defaultDir+'grism_cal_6_'+testDate.strftime('%Y_%m_%d')+'.csv'
                        break
                    else: continue
            else:
                cal_file = default_temp_dir+'/cal.csv'
        else:
            with open(default_temp_dir+'/cal.csv', 'wb') as binary_file: # Write fits image to file so it can be analyzed
                binary_file.write(calibration['content'])
            cal_file = default_temp_dir+'/cal.csv'
    else:
        cal_file = default_temp_dir+'/cal.csv'

    if not os.path.exists(cal_file):
        web_analyzer.raise_calibration_error()
    
    grism_analyzer = grism_tools(default_temp_dir+'/im.fts', cal_file) # instantiate analyzer with fits image and calibration file
    web_analyzer.run_analysis(grism_analyzer)

if __name__ == '__main__':
    main()