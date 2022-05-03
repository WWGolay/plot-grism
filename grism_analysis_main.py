'''
grism_analysis_main

Last Updated 5/2/22
University Of Iowa Astronomy Department
AJ Serck
Will Golay
'''

# Python imports
from datetime import date, timedelta, datetime
import astropy.io.fits as pyfits
import os

# Custom libraries
from bin.grism_analysis_web import grism_web
from bin.grism_tools_lib import grism_tools
from config import setup_config

def main():
    cfg = setup_config.read('grism-gui.cfg')
    default_temp_dir = cfg.get('default', 'default_temp_dir')
    defaultDir = cfg.get('default', 'default_calibration_dir')
    day_iter = int(cfg.get('default', 'find_calib_by_date'))
    take_input = bool(cfg.get('default', 'take_input')=='True')
    default_temp_dir = cfg.get('default', 'default_temp_dir')
    path_to_fits = default_temp_dir
    take_input = False#cfg.get('default', 'take_input')
    web_analyzer = grism_web()
    if take_input:
        fits_image, calibration,path = web_analyzer.get_fits() # Get initial fits image
        print("PATH:" + path)
        if path != "":
            path_to_fits = path
        else:            
            with open(default_temp_dir+'/im.fts', 'wb') as binary_file: # Write fits image to file so it can be analyzed
                binary_file.write(fits_image['content'])
                path_to_fits += '/im.fts'
    
        if calibration == None: # TODO: Add advanced option on first page for entry of custom calibration file, otherwise search for one
            
            # Get date of image to iterate back to latest calibration file, parse header into date object
            hdulist = pyfits.open(path_to_fits)
            fitsDate = hdulist[0].header['DATE-OBS']
            startDate = date(int(fitsDate[0:4]), int(fitsDate[5:7]), int(fitsDate[8:10]))
            
            # Iterate to find latest calib file in last 180 days
            if day_iter > 0:
                for testDate in (startDate - timedelta(n) for n in range(day_iter)):
                    if os.path.isfile(defaultDir+'grism_cal_6_'+testDate.strftime('%Y_%m_%d')+'.csv'):
                        cal_file = defaultDir+'grism_cal_6_'+testDate.strftime('%Y_%m_%d')+'.csv'
                        break
                    else: continue
            else:
                cal_file = default_temp_dir+'/cal.csv'
        else:
            cal_file = default_temp_dir+'/cal.csv'
    else:
        path_to_fits += '/im.fts'
        cal_file = default_temp_dir+'/cal.csv'

    try: os.path.exists(cal_file)
    except: web_analyzer.raise_calibration_error()
    
    grism_analyzer = grism_tools(path_to_fits, cal_file) # instantiate analyzer with fits image and calibration file
    web_analyzer.run_analysis(grism_analyzer)

if __name__ == '__main__':
    main()