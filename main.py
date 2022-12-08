'''
main

Last Updated 12/07/22
University Of Iowa Department of Physics and Astronomy
Robert Mutel
Will Golay
AJ Serck
Jack Kelley
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
    home_path = os.path.dirname(os.path.abspath(__file__))+'/'
    cfg = setup_config.read(home_path+'config/plot-grism.cfg')
    default_temp_dir = home_path + cfg.get('default', 'default_temp_dir')
    defaultDir = home_path + cfg.get('default', 'default_calibration_dir')
    day_iter = int(cfg.get('default', 'find_calib_by_date'))
    take_input = bool(cfg.get('default', 'take_input')=='True')
    path_to_fits = default_temp_dir
    web_analyzer = grism_web()
    if take_input:
        fits_image, calibration, path = web_analyzer.get_fits() # Get initial fits image
        print("PATH:" + path)
        if path != "":
            path_to_fits = path
        else:            
            with open(default_temp_dir+'im.fts', 'wb') as binary_file: # Write fits image to file so it can be analyzed
                binary_file.write(fits_image['content'])
                path_to_fits += 'im.fts'
    
        if calibration == None: 
            
            # Get date of image to iterate back to latest calibration file, parse header into date object
            hdulist = pyfits.open(path_to_fits)
            fitsDate = hdulist[0].header['DATE-OBS']
            startDate = date(int(fitsDate[0:4]), int(fitsDate[5:7]), int(fitsDate[8:10]))
            
            # Iterate to find latest calib file in last n days
            if day_iter > 0:
                for testDate in (startDate - timedelta(n) for n in range(day_iter)):
                    if os.path.isfile(defaultDir+'grism_cal_6_'+testDate.strftime('%Y_%m_%d')+'.csv'):
                        cal_file = defaultDir+'grism_cal_6_'+testDate.strftime('%Y_%m_%d')+'.csv'
                        break
                    else: continue
                else:
                    cal_file = default_temp_dir+'cal.csv'
            else:
                cal_file = default_temp_dir+'cal.csv'
        else:
            cal_file = default_temp_dir+'cal.csv'
    else:
        path_to_fits += 'im.fts'
        cal_file = default_temp_dir+'cal.csv'

    try:
        grism_analyzer = grism_tools(path_to_fits, cal_file) # instantiate analyzer with fits image and calibration file
        web_analyzer.run_analysis(grism_analyzer)
    except:
        web_analyzer.raise_calibration_error()

if __name__ == '__main__':
    main()