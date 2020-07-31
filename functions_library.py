# ############################################################################################
# define here the functions that are used across the different pieces of code. 
# we want to be sure something doesnt change in one module and not another
#
# The following functions are defined here (in this order):
#
#       def despike(spikey_panda, thresh, filterlen):                                                        
#       def calculate_metek_ws_wd(data_dates, u, v, hdg_data): # tower heading data is 1s, metek data is 1m  
#       def calc_humidity_ptu300(RHw, temp, press, Td):                                                      
#       def tilt_rotation(ct_phi, ct_theta, ct_psi, ct_up, ct_vp, ct_wp):                                    
#       def decode_licor_diag(raw_diag):                                                                     
#       def get_ct(licor_db):                                                                                
#       def get_dt(licor_db):                                                                                
#       def get_pll(licor_db):                                                                               
#       def take_average(array_like_thing, **kwargs):                                                        
#       def num_missing(series):                                                                             
#       def perc_missing(series):                                                                            
#       def column_is_ints(ser):                                                                             
#       def warn(string):                                                                                    
#       def fatal(string):                                                                                   
#       def grachev_fluxcapacitor(z_level_nominal, z_level_n, sonic_dir, metek, licor, clasp, verbose=False):
#
# ############################################################################################
import pandas as pd
import numpy  as np
import scipy  as sp

from datetime import datetime, timedelta
from scipy    import signal

# despiker
def despike(spikey_panda, thresh, filterlen, medfill):
    # outlier detection from a running median !!!! Replaces outliers with that median !!!!
    tmp                    = spikey_panda.rolling(window=filterlen, center=True, min_periods=1).median()
    spikes_i               = (np.abs(spikey_panda - tmp)) > thresh
    if medfill == 'yes': # fill with median
        spikey_panda[spikes_i] = tmp
    elif medfill == 'no': # fill with nan
        spikey_panda[spikes_i] = nan
    else: # just return bad indices
        spikey_panda = spikes_i
    return spikey_panda


# calculate wind speeds from appropriate metek columns, this code assumes that 'metek_data' is a
# fully indexed entire days worth of '1T' frequency data !! Chris modified this to pass
# u,v,data_dates directly to generalize for other dataframes, thanks Chris
def calculate_metek_ws_wd(data_dates, u, v, hdg_data): # tower heading data is 1s, metek data is 1m
    ws = np.sqrt(u**2+v**2)
    wd = np.mod(90+np.arctan2(v,-u)*180/np.pi,360)

    for time in data_dates[:]: # there has to be a more clever, non-loop, way of doing this
        avg_hdg  = np.nanmean(hdg_data[time:time+timedelta(seconds=60)])
        old_wd   = wd[time]
        wd[time] = np.mod(wd[time]+avg_hdg, 360)

    return ws, wd

# calculate humidity variables following Vaisala
def calc_humidity_ptu300(RHw, temp, press, Td):

    # Calculations based on Appendix B of the PTU/HMT manual to be mathematically consistent with the
    # derivations in the on onboard electronics. Checked against Ola's code and found acceptable
    # agreement (<0.1% in MR). RHi calculation is then made following Hyland & Wexler (1983), which
    # yields slightly higher (<1%) compared a different method of Ola's

    # calculate saturation vapor pressure (Pws) using two equations sets, Wexler (1976) eq 5 & coefficients
    c0    = 0.4931358
    c1    = -0.46094296*1e-2
    c2    = 0.13746454*1e-4
    c3    = -0.12743214*1e-7
    omega = temp - ( c0*temp**0 + c1*temp**1 + c2*temp**2 + c3*temp**3 )

    # eq 6 & coefficients
    bm1 = -0.58002206*1e4
    b0  = 0.13914993*1e1
    b1  = -0.48640239*1e-1
    b2  = 0.41764768*1e-4
    b3  = -0.14452093*1e-7
    b4  = 6.5459673
    Pws = np.exp( ( bm1*omega**-1 + b0*omega**0 + b1*omega**1 + b2*omega**2 + b3*omega**3 ) + b4*np.log(omega) ) # [Pa]

    Pw = RHw*Pws/100 # # actual vapor pressure (Pw), eq. 7, [Pa]

    x = 1000*0.622*Pw/((press*100)-Pw) # mixing ratio by weight (eq 2), [g/kg]

    # if we no dewpoint available (WXT!) then calculate it, else no need to worry about it
    if Td == -1:   # dewpoint (frostpoint), we are assuming T ambient < 0 C, which corresponds to these coefs:
        A = 6.1134
        m = 9.7911
        Tn = 273.47
        Td = Tn / ((m/np.log10((Pw/100)/A)) - 1) # [C] (temperature, not depression!)

    # else: do nothing if arg 4 is any other value and input flag will be returned.
    a = 216.68*(Pw/temp) # # absolute humidity, eq 3, [g/m3]

    h = (temp-273.15)*(1.01+0.00189*x)+2.5*x # ...and enthalpy, eq 4, [kJ/kg]

    # RHi, the saturation vapor pressure over ice, then finally RHI, Hyland & Wexler (1983)
    c0 = -5.6745359*1e3     # coefficients
    c1 = 6.3925247
    c2 = -9.6778430*1e-3
    c3 = 6.2215701*1e-7
    c4 = 2.0747825*1e-9
    c5 = -9.4840240*1e-13
    D  = 4.1635019

    # calculate
    term = (c0*temp**(-1)) + (c1*temp**(0)) + (c2*temp**1) + (c3*temp**2) + (c4*temp**3)+(c5*temp**4)

    # calculate saturation vapor pressure over ice
    Psi = np.exp(term + (D*np.log(temp)))  # Pa

    # convert to rhi
    rhi = 100*(RHw*0.01*Pws)/Psi

    return Td, h, a, x, Pw, Pws, rhi


def calculate_initial_angle(latA,lonA, latB, lonB):

    # Function provided by Martin Radenz, TROPOS
    
    # Calculates the bearing between two points.
    # The formulae used is the following:
    #     ? = atan2(sin(?long).cos(lat2),
    #               cos(lat1).sin(lat2) ? sin(lat1).cos(lat2).cos(?long))

    # source: https://gist.github.com/jeromer/2005586

    # initial_bearing = math.degrees(initial_bearing)
    # compass_bearing = (initial_bearing + 360) % 360

    # :Parameters:
    #   - `pointA: The tuple representing the latitude/longitude for the
    #     first point. Latitude and longitude must be in decimal degrees
    #   - `pointB: The tuple representing the latitude/longitude for the
    #     second point. Latitude and longitude must be in decimal degrees
    # :Returns:
    #   The bearing in degrees
    # :Returns Type:
    #   float

#     if (type(pointA) != tuple) or (type(pointB) != tuple):
#         raise TypeError("Only tuples are supported as arguments")

    lat1 = np.radians(latA)
    lat2 = np.radians(latB)

    diffLong = np.radians(lonB - lonA)

    x = np.sin(diffLong) * np.cos(lat2)
    y = np.cos(lat1) * np.sin(lat2) - (np.sin(lat1)
            * np.cos(lat2) * np.cos(diffLong))

    initial_bearing = np.arctan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180∞ to + 180∞ which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below

    #print((math.degrees(initial_bearing) + 360) % 360)
    initial_bearing = initial_bearing/np.pi*180
    
    compass_bearing = (initial_bearing + 360) % 360
    return compass_bearing


def distance(lat1, lon1, lat2, lon2):
    
    # Function provided by Martin Radenz, TROPOS
        
    #     lat1, lon1 = origin
    #     lat2, lon2 = destination
    radius = 6361 # km

    dlat = np.radians(lat2-lat1)
    dlon = np.radians(lon2-lon1)
    a = np.sin(dlat/2) * np.sin(dlat/2) + np.cos(np.radians(lat1))         * np.cos(np.radians(lat2)) * np.sin(dlon/2) * np.sin(dlon/2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    d = radius * c

    return d


def tilt_rotation(ct_phi, ct_theta, ct_psi, ct_up, ct_vp, ct_wp):

    # This subroutine rotates a vector from one cartesian basis to another, based upon the
    # three Euler angles, defined as rotations around the reference axes, xyz.

    # Rotates the sonic winds from body coordinates to earth coordinates.  This is the tild
    # rotation that corrects for heading and the tilt of the sonic reltive to plum.

    # y,x,z in -> u,v,w out

    # This differs from the double rotation into the plane of the wind streamline that is
    # needed for the flux calculations and is performed in the grachev_fluxcapacitor. The
    # output from this rotation is the best estimate of the actual wind direction, having
    # corrected for both heading and contributions to the horizontal wind by z

    # Adapted from coord_trans.m (6/27/96) from Chris Fairall's group by C. Cox 2/22/20
    #
    #  phi   = about inclinometer y/u axis (anti-clockwise about Metek north-south) (roll)
    #  theta = about inclinometer x/v axis (anti-clockwise about Metek east-west) (pitch)
    #  psi   = about z/w axis (yaw, "heading")

    # calculations are in radians, but inputs are in degrees
    ct_phi   = np.radians(ct_phi)
    ct_theta = np.radians(ct_theta)
    ct_psi   = np.radians(ct_psi)

    ct_u = ct_up*np.cos(ct_theta)*np.cos(ct_psi)\
           + ct_vp*(np.sin(ct_phi)*np.sin(ct_theta)*np.cos(ct_psi)-np.cos(ct_phi)*np.sin(ct_psi))\
           + ct_wp*(np.cos(ct_phi)*np.sin(ct_theta)*np.cos(ct_psi)+np.sin(ct_phi)*np.sin(ct_psi))

    ct_v = ct_up*np.cos(ct_theta)*np.sin(ct_psi)\
           + ct_vp*(np.sin(ct_phi)*np.sin(ct_theta)*np.sin(ct_psi)+np.cos(ct_phi)*np.cos(ct_psi))\
           + ct_wp*(np.cos(ct_phi)*np.sin(ct_theta)*np.sin(ct_psi)-np.sin(ct_phi)*np.cos(ct_psi))

    ct_w = ct_up*(-np.sin(ct_theta))\
           + ct_vp*(np.cos(ct_theta)*np.sin(ct_phi))\
           + ct_wp*(np.cos(ct_theta)*np.cos(ct_phi))

    return ct_u, ct_v, ct_w

def decode_licor_diag(raw_diag):

    # speed things up so we dont wait forever
    bin_v     = np.vectorize(bin)
    get_ct_v  = np.vectorize(get_ct)
    get_dt_v  = np.vectorize(get_dt)
    get_pll_v = np.vectorize(get_pll)

    # licor diagnostics are encoded in the binary of an integer reported by the sensor. the coding is described
    # in Licor Technical Document, 7200_TechTip_Diagnostic_Values_TTP29 and unpacked here.
    licor_diag     = np.int16(raw_diag)
    pll            = licor_diag*np.nan
    detector_temp  = licor_diag*np.nan
    chopper_temp   = licor_diag*np.nan
    # __"why the %$@$)* can't this be vectorized? This loop is slow"__
    # well, chris, you asked for vectorization.. now you got it! now to get rid of the list comprehension
    non_nan_inds  = ~np.isnan(raw_diag) 
    #if not np.isnan(raw_diag).all():
    if non_nan_inds.any():

        licor_diag_bin = bin_v(licor_diag[non_nan_inds])
        chopper_temp_bin = licor_diag_bin[:][2]

        # try to use vectorized functions?
        # chopper_temp[non_nan_inds]  = get_ct_v(licor_diag_bin)
        # detector_temp[non_nan_inds] = get_dt_v(licor_diag_bin)
        # pll[non_nan_inds]           = get_pll_v(licor_diag_bin)
        
        # or just use list comprehension? vectorize is doing weird things, and not much faster... maybe this is better
        chopper_temp[non_nan_inds]  = [np.int(x[2]) if len(x)==10 and x[2]!='b' else np.nan for x in licor_diag_bin]
        detector_temp[non_nan_inds] = [np.int(x[3]) if len(x)==10 and x[2]!='b' else np.nan for x in licor_diag_bin]
        pll[non_nan_inds]           = [np.int(x[4]) if len(x)==10 and x[2]!='b' else np.nan for x in licor_diag_bin]

    return pll, detector_temp, chopper_temp

# these functions are for vectorization by numpy to 
def get_ct(licor_db):
    if len(licor_db)>4 and licor_db[2]!='b':
        if licor_db[2] != np.nan:
            return np.int(licor_db[2])
    else: return np.nan
def get_dt(licor_db):
    if len(licor_db)>4 and licor_db[2]!='b': 
        if licor_db[3] != np.nan:
            return np.int(licor_db[3])
    else: return np.nan
def get_pll(licor_db):
    if len(licor_db)>4 and licor_db[2]!='b':
        if licor_db[4] != np.nan:
            return np.int(licor_db[4])
    else: return np.nan

# this is the function that averages for the 1m and 10m averages
# perc_allowed_missing defines how many data points are required to be non-nan before returning nan
# i.e. if 10 out of 100 data points are non-nan and you specify 80, this returns nan
#
# can be called like:     DataFrame.apply(take_average, perc_allowed_missing=80)
def take_average(array_like_thing, **kwargs):

    perc_allowed_missing = kwargs.get('perc_allowed_missing')
    if perc_allowed_missing is None:
        perc_allowed_missing = 100.0
    
    if array_like_thing.size == 0:
        return nan
    perc_miss = np.round((np.count_nonzero(np.isnan(array_like_thing))/float(array_like_thing.size))*100.0, decimals=4)
    if perc_allowed_missing < perc_miss:
        return nan
    else:
        return np.nanmean(array_like_thing)

# functions to make grepping lines easier, differentiating between normal output, warnings, and fatal errors
def warn(string):
    max_line = len(max(string.splitlines(), key=len))
    print('')
    print("!! Warning: {} !!".format("!"*(max_line)))
    for line in string.splitlines():
        print("!! Warning: {} {}!! ".format(line," "*(max_line-len(line))))
    print("!! Warning: {} !!".format("!"*(max_line)))
    print('')

def fatal(string):
    max_line = len(max(string.splitlines(), key=len))
    print('')
    print("!! FATAL {} !!".format("!"*(max_line)))
    for line in string.splitlines():
        print("!! FATAL {} {}!! ".format(line," "*(max_line-len(line))))
    center_off = int((max_line-48)/2.)
    if center_off+center_off != (max_line-len(line)):
        print("!! FATAL {} I'm sorry, but this forces an exit... goodbye! {} !!".format(" "*center_off," "*(center_off)))
    else:
        print("!! FATAL {} I'm sorry, but this forces an exit... goodbye! {} !!".format(" "*center_off," "*center_off))
    print("!! FATAL {} !!".format("!"*(max_line)))
    exit()

def num_missing(series):
    return np.count_nonzero(series==np.NaN)

def perc_missing(series):
    if series.size == 0: return 100.0
    return np.round((np.count_nonzero(np.isnan(series))/float(series.size))*100.0, decimals=4)

# checks a column/series in a dataframe to see if it can be stored as ints 
def column_is_ints(ser): 

    if ser.dtype == object:
        warn("your pandas series for {} contains objects, that shouldn't happen".format(ser.name))
        return False

    elif ser.empty or ser.isnull().all():
        return False
    else:
        mx = ser.max()
        mn = ser.min()

        ser_comp = ser.fillna(mn-1)  
        ser_zero = ser.fillna(0)

        # test if column can be converted to an integer
        try: asint  = ser_zero.astype(np.int32)
        except Exception as e:
            return False
        result = (ser_comp - asint)
        result = result.sum()
        if result > -0.01 and result < 0.01:

            # could probably support compression to smaller dtypes but not yet,
            # for now everything is int32... because simple

            # if mn >= 0:
            #     if mx < 255:
            #         return np.uint8
            #     elif mx < 65535:
            #         return np.uint16
            #     elif mx < 4294967295:
            #         return np.uint32
            #     else:
            #         print("our netcdf files dont support int64")
            # else:
            #     if mn > np.iinfo(np.int8).min and mx < np.iinfo(np.int8).max:
            #         return np.int8
            #     elif mn > np.iinfo(np.int16).min and mx < np.iinfo(np.int16).max:
            #         return np.int16
            #     elif mn > np.iinfo(np.int32).min and mx < np.iinfo(np.int32).max:
            #         return np.int32
            #     elif mn > np.iinfo(np.int64).min and mx < np.iinfo(np.int64).max:
            #         print("our netcdf files dont support int64")

            return True
        else:
            return False

# despik.m
def despik(uraw):
    uz = np.array(uraw)
    on=np.array(range(0, len(uz)))
    uz=np.column_stack([on,uz])
    
    npt=np.size(uz,0)
    
    uu2=uz[uz[:,1].argsort(),]
    uu=uu2[0:npt,1]
    mp=np.floor(npt/2)
    mu=uu[int(mp)]
    sp=np.floor(0.84*npt)
    sm=np.floor(0.16*npt)
    sig=(uu[int(sp)]-uu[int(sm)])/2
    dsig=max(4*sig,0.5)
    im=1
    while abs(mu-uu[im])>dsig:
       im=im+1
    
    ip=npt-1
    while abs(uu[ip]-mu)>dsig:
       ip=ip-1
    
    pct=(im+npt-ip)/npt*100
    uu2[0:im,1]=mu
    uu2[ip:npt,1]=mu
    uy=uu2[uu2[:,0].argsort(),]
    uu=uy[0:npt,1]
    
    return uu

# maybe this goes in a different file?
def grachev_fluxcapacitor(z_level_n, sonic_dir, metek, licor, clasp, verbose=False):

    # define the verbose print option
    v_print      = print if verbose else lambda *a, **k: None
    verboseprint = v_print
    nan          = np.NaN  # make using nans look better

    # some setup
    samp_freq = 10             # sonic sampling rate in Hz
    npos      = 1800*samp_freq # highest possible number of data points (36000)
    sfreq     = 1/samp_freq
    nx        = samp_freq*(1800-1)

    # this should subset to 30 min and loop. get to it later.
    U   = metek['u']
    V   = metek['v']
    W   = metek['w']
    T   = metek['T']
    npt = len(U)

    # Goodness, there are going to be a lot of things to save. Lets package it up.
    turbulence_data = pd.DataFrame(columns=[\
    'Hs', # sensible heat flux (W/m2) - Based on the sonic temperature!!!
    'Hs_hi',   # sensible heat flux (sonic temperature!) based on the high-frequency part of the cospectrum(W/m2)
    'Cd', # Drag coefficient, Cd
    'Cd_hi', # Drag coefficient based on the high-frequency part of the momentum flux, Cd_hi:
    'ustar',  # the friction velocity based only on the downstream, uw,  stress components (m/s)
    'ustar_hi', # friction velocity based on the high-frequency part of downstream, uw_hi,  stress components (m/s)
    'Tstar', # the temperature scale
    'Tstar_hi', # the temperature scale based on the high-frequency part of the turbulent fluxes
    'zeta_level_n', # Monin-Obukhov stability parameter, z/L
    'zeta_level_n_hi', # Monin-Obukhov stability parameter based on the high-frequency part of the turbulent fluxes, z/L_hi
    'wu_csp', # wu-covariance based on the wu-cospectra integration
    'wv_csp', # wv-covariance based on the wv-cospectra integration
    'uv_csp', # uv-covariance based on the uv-cospectra integration
    'wT_csp', # wt-covariance, vertical flux of the sonic temperature  [deg m/s]
    'uT_csp', # ut-covariance, horizontal flux of the sonic temperature (along-wind component) [deg m/s]
    'vT_csp', # vt-covariance, horizontal flux of the sonic temperature (cross-wind component) [deg m/s]
    'phi_u',  # MO universal functions for the standard deviations
    'phi_v',  # MO universal functions for the standard deviations
    'phi_w',  # MO universal functions for the standard deviations
    'phi_T',  # MO universal functions for the standard deviations
    'phi_uT', # MO universal function for the horizontal heat flux
    'phi_u_hi', # MO universal functions for the standard deviations based on the high-frequency part of the turbulent fluxes
    'phi_v_hi', # MO universal functions for the standard deviations based on the high-frequency part of the turbulent fluxes
    'phi_w_hi', # MO universal functions for the standard deviations based on the high-frequency part of the turbulent fluxes
    'phi_T_hi', # MO universal functions for the standard deviations based on the high-frequency part of the turbulent fluxes
    'phi_uT_hi', # MO universal function for the horizontal heat flux based on the high-frequency part of the turbulent fluxes
    'epsilon_u',  # Dissipation rate of the turbulent kinetic energy based on the energy spectra of the longitudinal velocity component in the inertial subrange [m^2/s^3]:
    'epsilon_v', # Dissipation rate of the turbulent kinetic energy based on the energy spectra of the lateral velocity component in the inertial subrange [m^2/s^3]:
    'epsilon_w', # Dissipation rate of the turbulent kinetic energy based on the energy spectra of the vertical velocity component in the inertial subrange [m^2/s^3]:
    'epsilon',  # Dissipation rate of the turbulent kinetic energy = median of the values derived from Su, Sv, & Sw [m^2/s^3]:
    'Phi_epsilon',  # Monin-Obukhov universal function Phi_epsilon based on the median epsilon:
    'Phi_epsilon_hi', # Monin-Obukhov universal function Phi_epsilon based on the median epsilon based on the high-frequency part of the momentum flux:
    'Nt', # The dissipation (destruction) rate for half the temperature variance [deg^2/s]
    'Phi_Nt', # Monin-Obukhov universal function Phi_Nt
    'Phi_Nt_hi', # Monin-Obukhov universal function Phi_Nt based on the high-frequency part of the turbulent fluxes
    'Phix',     # QC: Angle of attack
    'DeltaU',   # QC: Non-Stationarity
    'DeltaV',   # QC: Non-Stationarity
    'DeltaT',   # QC: Non-Stationarity
    'Kurt_u',   # QC: Kurtosis
    'Kurt_v',   # QC: Kurtosis
    'Kurt_w',   # QC: Kurtosis
    'Kurt_T',   # QC: Kurtosis
    'Kurt_uw',  # QC: Kurtosis
    'Kurt_vw',  # QC: Kurtosis
    'Kurt_wT',  # QC: Kurtosis
    'Kurt_uT',  # QC: Kurtosis
    'Skew_u',   # QC: Skewness
    'Skew_v',   # QC: Skewness
    'Skew_w',   # QC: Skewness
    'Skew_T',   # QC: Skewness
    'Skew_uw',  # QC: Skewness
    'Skew_vw',  # QC: Skewness
    'Skew_wT',  # QC: Skewness
    'Skew_uT']) # QC: Skewness
    
    # Sanity check: Reject the half hour series if it is too short, less than 2^13 = 8192 points = 13.6 min @ 10 Hz
    if npt < 8192:
        verboseprint('  No valid data for sonic at height (np<8192) '+np.str(z_level_n))
        # give the cols unique names (for netcdf later), give it a row of nans, and kick it back to the main
        # !! what is the difference betwee dataframe keys and columns? baffled. just change them both.
        turbulence_data.keys    = turbulence_data.keys()#+'_'+z_level_nominal
        #print(turbulence_data)
        turbulence_data.columns = turbulence_data.keys
        turbulence_data         = turbulence_data.append([{turbulence_data.keys[0]: nan}]) 
        return turbulence_data

    # Reject the series of more than 50% of u- or v- or w-wind speed component are nan
    if sum(U.isna()) > npt/2 or sum(V.isna()) > npt/2 or sum(W.isna()) > npt/2 or sum(T.isna()) > npt/2:
        # give the cols unique names (for netcdf later), give it a row of nans, and kick it back to the main
        # !! what is the difference betwee dataframe keys and columns? baffled. just change them both.
        turbulence_data.keys    = turbulence_data.keys()#+'_'+z_level_nominal
        turbulence_data.columns = turbulence_data.keys
        turbulence_data         = turbulence_data.append([{turbulence_data.keys[0]: nan}])
        return turbulence_data
        verboseprint('  No valid data for sonic at height (>50% missing)  '+np.str(z_level_n))


    #verboseprint('  Calculating sonic at height '+np.str(z_level_n)+' m and heading '+np.str(np.round(sonic_dir,decimals=1))+' deg...')

    # Replace missing values (NaN) or inf using mean values:
    # This method is preferable in the case if there are too many NaNs or long gaps
    U[np.isinf(U)] = nan
    V[np.isinf(V)] = nan
    W[np.isinf(W)] = nan
    T[np.isinf(T)] = nan

    U = U.fillna(U.mean())
    V = V.fillna(V.mean())
    W = W.fillna(W.mean())
    T = T.fillna(T.mean())

    # Computes means for entire time block (1 hr or less)
    um = U.mean()
    vm = V.mean()
    wm = W.mean()
    Tm = T.mean()

    # there was one day for asfs30 (10/06/2019) where this was true and so wsp divisions were undefined
    if um == 0 and vm ==0 and wm ==0: #half hour of _zero_ wind? has to be bad data
        turbulence_data.keys    = turbulence_data.keys()#+'_'+z_level_nominal
        turbulence_data.columns = turbulence_data.keys
        turbulence_data         = turbulence_data.append([{turbulence_data.keys[0]: nan}])
        verboseprint('  Bad data for sonic at height {}'.format(np.str(z_level_n)))
        return turbulence_data

    # Rotate!

    # We used the most common method, which is a double rotation of the anemometer coordinate system, to
    # compute the longitudinal, lateral, and vertical velocity components in real time (Kaimal and Finnigan
    # 1994, Sect. 6.6).
    ss = (um**2+vm**2)**0.5
    # working in radians in this block
    thet     = np.arctan2(vm,um)
    phi      = np.arctan2(wm,ss)
    rot      = np.array([[1.,1.,1.],[1.,1.,1.],[1.,1.,1.]])
    rot[0,0] = np.cos(phi)*np.cos(thet)
    rot[0,1] = np.cos(phi)*np.sin(thet)
    rot[0,2] = np.sin(phi)
    rot[1,0] = -np.sin(thet)
    rot[1,1] = np.cos(thet)
    rot[1,2] = 0
    rot[2,0] = -1*np.sin(phi)*np.cos(thet)
    rot[2,1] = -1*np.sin(phi)*np.sin(thet)
    rot[2,2] = np.cos(phi)

    # the original matlab code is written in a loop like so, but this can be
    # very slow so I've vectorized it below. The differences in the approach
    # agree to exactly
    # for i in range(npt):
    #     x=np.array([U[i],V[i],W[i]])
    #     xr=np.dot(rot,np.transpose(x))
    #     U[i]=xr[0]
    #     V[i]=xr[1]
    #     W[i]=xr[2]
    x=np.array([U,V,W])
    xr=np.dot(rot,x)
    U = xr[0,:]
    V = xr[1,:]
    W = xr[2,:]

    # Mean rotated wind speed components:
    # vrm and wrm can be used for QC purposes (theoretically vrm = 0 and wrm = 0)
    urm = U.mean()
    vrm = V.mean()
    wrm = W.mean()
    
    #
    # Compute the spectra and cospectra
    #

    # Define 'nf', the length in gridpoints of the FFT windowing segment
    # Here np = length(T) = length(Traw) = length(w) = length(wraw) = ... - length of a raw data file
    if npt < 8192:
       nf=npt           # condition to avoid different matrix dimensions for short raw data series;
    #  nf=2^12          # 2^12 = 4096 points  (or = 4096/10 sec  =  6.82667 min for samp_freq = 10 Hz)
    elif npt < 16384:
       nf=2**13         # 2^13 = 8192 points  (or = 8192/10 sec  = 13.65333 min for samp_freq = 10 Hz)
    elif npt < 32768:   # For half hour data we expect to be here, a 27.3 min flux, the closest po2 for the FFT to 30 min.
       nf=2**14         # 2^14 = 16384 points (or = 16384/10 sec = 27.30667 min for samp_freq = 10 Hz)
    else:
       nf=2**15         # 2^15 = 32768 points (or = 32768/10 sec = 54.61333 min for samp_freq = 10 Hz)

    nf_min = nf/600     # nf in minutes

    # Instantaneous relative direction of the wind speed vector in the rotated coordinate system:
    wdirr = np.arctan2(-1*V,U)*180/np.pi          # Instantaneous relative direction of the wind speed vector (deg)

    us = U[0:nf]
    vs = V[0:nf]
    ws = W[0:nf]
    Ts = T[0:nf]
    wdirs = wdirr[0:nf]
         
    # Means for FFT segment (Note that they differ from hourly means, see above):
    usm = us.mean()
    vsm = vs.mean()
    wsm = ws.mean()
    Tsm = Ts.mean()
    wdirsm = wdirs.mean()

    # >>> Perform Fast Fourier Transform (FFT) to compute power spectra and cospectra:
    # In the following version linear detrend is used (no overlaping)

    F,su = signal.welch(us-usm,10,signal.windows.hamming(nf),detrend='linear') # (psd = Power Spectral Density)
    F,sv = signal.welch(vs-vsm,10,signal.windows.hamming(nf),detrend='linear')
    F,sw = signal.welch(ws-wsm,10,signal.windows.hamming(nf),detrend='linear')
    F,sT = signal.welch(Ts-Tsm,10,signal.windows.hamming(nf),detrend='linear')
           
    F,swu = signal.csd(ws-wsm,us-usm,10,signal.windows.hamming(nf),detrend='linear')   # (csd = Cross Spectral Density)
    F,swv = signal.csd(ws-wsm,vs-vsm,10,signal.windows.hamming(nf),detrend='linear')
    F,swT = signal.csd(ws-wsm,Ts-Tsm,10,signal.windows.hamming(nf),detrend='linear')
            
    # In addition to Chris' original code, computation of CuT, CvT, and Cuv are added by AG
    # Cospectra CuT & CvT are associated with the horizontal heat flux
    F,suT = signal.csd(us-usm,Ts-Tsm,10,signal.windows.hamming(nf),detrend='linear')
    F,svT = signal.csd(vs-vsm,Ts-Tsm,10,signal.windows.hamming(nf),detrend='linear')
    F,suv = signal.csd(us-usm,vs-vsm,10,signal.windows.hamming(nf),detrend='linear')

    # Also spectrum of wind speed direction is added (AG)
    F,swdir = signal.welch(wdirs-wdirsm,10,signal.windows.hamming(nf),detrend='linear')



    # Spectra smoothing

    nfd2 = nf/2
    c1   = 0.1
    jx   = 0
    dx   = 1
    ix   = 0
    inx  = 0
           
    sus    = np.zeros(int(nfd2), dtype=complex)
    svs    = np.zeros(int(nfd2), dtype=complex)
    sws    = np.zeros(int(nfd2), dtype=complex)
    sTs    = np.zeros(int(nfd2), dtype=complex)
    cwus   = np.zeros(int(nfd2), dtype=complex)
    cwvs   = np.zeros(int(nfd2), dtype=complex)
    cwTs   = np.zeros(int(nfd2), dtype=complex)
    cuTs   = np.zeros(int(nfd2), dtype=complex)
    cvTs   = np.zeros(int(nfd2), dtype=complex)
    cuvs   = np.zeros(int(nfd2), dtype=complex)
    swdirs = np.zeros(int(nfd2), dtype=complex)
    fs     = np.zeros(int(nfd2), dtype=complex)
    dfs    = np.zeros(int(nfd2), dtype=complex)

    while jx<nfd2:
        dx     = (dx*np.exp(c1))
        d1     = np.int32(np.floor(dx))
        acu    = 0
        acv    = 0
        acw    = 0
        acT    = 0
        acwu   = 0
        acwv   = 0
        acwT   = 0
        acuT   = 0
        acvT   = 0
        acuv   = 0
        acwdir = 0
        ac2    = 0
        k=0
        for jx in range(ix,ix+d1):
            if (jx==nfd2):
                break
            acu    = acu+su[jx]
            acv    = acv+sv[jx]
            acw    = acw+sw[jx]
            acT    = acT+sT[jx]
            acwu   = acwu+swu[jx]
            acwv   = acwv+swv[jx]
            acwT   = acwT+swT[jx]
            acuT   = acuT+suT[jx]
            acvT   = acvT+svT[jx]
            acuv   = acuv+suv[jx]
            acwdir = acwdir+swdir[jx]
            ac2    = ac2+F[jx]
            k=k+1    

        sus[inx] = acu/k   
        svs[inx] = acv/k   
        sws[inx] = acw/k   
        sTs[inx] = acT/k   
        cwus[inx] = acwu/k 
        cwvs[inx] = acwv/k
        cwTs[inx] = acwT/k
        cuTs[inx] = acuT/k
        cvTs[inx] = acvT/k
        cuvs[inx] = acuv/k
        swdirs[inx]=acwdir/k
        fs[inx]=ac2/k
        dfs[inx]=F[jx]-F[ix]+F[1]
        ix=jx+1
        inx=inx+1
    
    sus = sus[0:inx]
    svs = svs[0:inx]
    sws = sws[0:inx]
    sTs = sTs[0:inx]
    cwus = cwus[0:inx]
    cwvs = cwvs[0:inx]
    cwTs = cwTs[0:inx]
    cuTs = cuTs[0:inx]
    cvTs = cvTs[0:inx]
    cuvs = cuvs[0:inx]
    swdirs = swdirs[0:inx]
    fs = fs[0:inx]
    dfs = dfs[0:inx]
    
    # take the real part
    sus    = np.real(sus)
    svs    = np.real(svs)
    sws    = np.real(sws)
    sTs    = np.real(sTs)
    cwus   = np.real(cwus)
    cwvs   = np.real(cwvs)
    cwTs   = np.real(cwTs)
    cuTs   = np.real(cuTs)
    cvTs   = np.real(cvTs)
    cuvs   = np.real(cuvs)
    swdirs = np.real(swdirs)
    fs     = np.real(fs)
    dfs    = np.real(dfs)

    #++++++++++++++++++++++++ Important constants and equations ++++++++++++++++++++++++++++++++
    # !!! Tsm - temperature in deg C
    tdk   = 273.15                                 # absolute zero
    Rgas  = 287.1                                  # universal gas constant, J/(kg K)
    sigma = 5.67e-8                                # Stefan-Boltzman constant, W/(m^2 K^4)
    pr    = 1013                                   # air pressure (mb) when no pressure measurements
    qo    = 0                                      # air humidity when no humidity measurements
    rho   = pr*100/(Rgas*(Tsm+tdk)*(1+0.61e-3*qo)) # density of air derived from ideal gas equation, kg/m^3
    cp    = 1005.6+0.017211*Tsm+0.000392*Tsm*Tsm   # isobaric specific heat of air (median), J/(kg K), (from Ed Andreas)
    Le    = (2.501-.00237*Tsm)*1e6                 # latent heat of vaporization, J/kg
    visa  = 1.326e-5*(1+6.542e-3*Tsm+8.301e-6*Tsm*Tsm-4.84e-9*Tsm*Tsm*Tsm) # m^2/s, molecular viscosity from TOGA CORE bulk algorithm
    kt = (0.02411*(1+0.003309*Tsm-1.441e-6*Tsm*Tsm))/(rho*cp) # m^2/s, koefficient of molecular thermal diffusivity (from Ed Andreas)

    #+++++++++++++++++++++++++++++ Wind speed and direction ++++++++++++++++++++++++++++++++++++
    wsp = (um**2 + vm**2 + wm**2)**0.5       # hour averaged wind speed (m/s)
    wdir = np.arctan2(-vm,um)*180/np.pi      # averaged relative wind direction (deg)

    # Convert wind direction range to [0 360] segment:
    if (wdir < 0):
        wdir = wdir + 360

    # All directions for wind and stress here are calculated using the meteorological convention ('from').
    # All directions are relatively true (Geographic) North, not magnetic North!

    # For true wind direction add a true orientation of a sonic anemometer:
    truewdir = wdir + sonic_dir                 # 1-hr averaged true wind direction (deg)
    # Here orientation of the sonic anemoneter (sonic_9m_dir = 180 + 17 deg) is provided by Irina Repina
    # Convert wind direction range to [0 360] segment:
    if (truewdir > 360):
        truewdir = truewdir - 360

    #++++++++++++++++++++++++++++ Fluxes Based on the Cospectra +++++++++++++++++++++++++++++++
    # >>> Compute covariances ("fluxes") based on the appropriate cospectra integration (the
    # total flux is the sum of cospectra frequency components) The turbulent fluxes and
    # variances are derived through frequency integration of the appropriate cospectra and spectra
    cwux = np.sum(cwus*dfs)
    cwvx = np.sum(cwvs*dfs)
    cuvx = np.sum(cuvs*dfs)
    cwTx = np.sum(cwTs*dfs)
    cuTx = np.sum(cuTs*dfs)
    cvTx = np.sum(cvTs*dfs)
    # >>> Compute standard deviations based on the appropriate spectra integration:
    sigu_spc = (np.sum(sus*dfs))**0.5       # based on the Su-spectra integration
    sigv_spc = (np.sum(svs*dfs))**0.5       # based on the Sv-spectra integration
    sigw_spc = (np.sum(sws*dfs))**0.5       # based on the Sw-spectra integration
    sigT_spc = (np.sum(sTs*dfs))**0.5       # based on the St-spectra integration
    sigwdir_spc = (np.sum(swdirs*dfs))**0.5 # based on the Sdir-spectra integration
    ssm = (usm*usm+vsm*vsm)**0.5

    # !! Note that sigwdir_spc may be used for quality control (or QC for short) of the data
    # For example sigwdir_spc > 15 deg may be considered as "bad" data (non-stationary)
    # However this QC is not applicable for free convection limit (light winds)

    # >>> Wind stress components and the friction velocity:
    wu_csp = cwux   # wu-covariance based on the wu-cospectra integration
    wv_csp = cwvx   # wv-covariance based on the wv-cospectra integration
    uv_csp = cuvx   # uv-covariance based on the uv-cospectra integration
    ustar = -np.sign(wu_csp)*(np.abs(wu_csp))**0.5 # the friction velocity based only on the downstream, uw,  stress components (m/s)
    # ustar = - sign(wu_csp)*((abs(wu_csp))^2 + (abs(wv_csp))^2)^(1/4);  # ustar is based on both stress components (m/s)

    # >>> Sensible heat flux:
    # Note that a sonic anemometer/thermometer measures the so-called 'sonic' temperature which is close to the virtual temperature
    # Thus <w't'> here is a buoyancy flux
    # Moisture correction is necessary to obtain the correct sensible heat flux (e.g., Kaimal and Finnigan, 1994)
    # However, in Arctic and Antarctic this value very close to the temperature flux (i.e. the sensible heat flux)
    wT_csp = cwTx   # wt-covariance, vertical flux of the sonic temperature  [deg m/s]
    uT_csp = cuTx   # ut-covariance, horizontal flux of the sonic temperature (along-wind component) [deg m/s]
    vT_csp = cvTx   # vt-covariance, horizontal flux of the sonic temperature (cross-wind component) [deg m/s]
    Hs = wT_csp*rho*cp    # sensible heat flux (W/m2) - Based on the sonic temperature!!!
    Tstar = -wT_csp/np.abs(ustar) # the temperature scale

    # The loop below is added for cases when number of points < 32768 (54.61333 min) or < 16384 (27.30667 min)
    # It defines frequencies for fluxes in the high-frequency subrange and defines the inertial subrange
    # !! -1 to get to 0 based (python) but preserving the original values for reference.
    if npt < 8192:  # 2^12 = 4096 points  (or = 4096/10 sec  =  6.82667 min for samp_freq = 10 Hz)
       fsl = 4-1
       fsn = 53-1
       fsi01 = 34-1
       fsi02 = 35-1
       fsi03 = 36-1
       fsi04 = 37-1
       fsi05 = 38-1
       fsi06 = 39-1
       fsi07 = 40-1
       fsi08 = 41-1
       fsi09 = 42-1
       fsi10 = 43-1
       fsi11 = 44-1
       fsi12 = 45-1

    elif npt < 16384: # 2^13 = 8192 points  (or =  8192/10 sec = 13.65333 min for samp_freq = 10 Hz)
       fsl = 6-1
       fsn = 60-1
       fsi01 = 40-1
       fsi02 = 41-1
       fsi03 = 42-1
       fsi04 = 43-1
       fsi05 = 44-1
       fsi06 = 45-1
       fsi07 = 46-1
       fsi08 = 47-1
       fsi09 = 48-1
       fsi10 = 49-1
       fsi11 = 50-1
       fsi12 = 51-1

    elif npt < 32768: # 2^14 = 16384 points (or = 16384/10 sec = 27.30667 min for samp_freq = 10 Hz)
       fsl = 9-1
       fsn = 67-1
       fsi01 = 47-1
       fsi02 = 48-1
       fsi03 = 49-1
       fsi04 = 50-1
       fsi05 = 51-1
       fsi06 = 52-1
       fsi07 = 53-1
       fsi08 = 54-1
       fsi09 = 55-1
       fsi10 = 56-1
       fsi11 = 57-1
       fsi12 = 58-1

    else: # 2^15 = 32768 points (or = 32768/10 sec = 54.61333 min for samp_freq = 10 Hz)
       fsl = 13-1
       fsn = 74-1
       fsi01 = 54-1
       fsi02 = 55-1
       fsi03 = 56-1
       fsi04 = 57-1
       fsi05 = 58-1
       fsi06 = 59-1
       fsi07 = 60-1
       fsi08 = 61-1
       fsi09 = 62-1
       fsi10 = 63-1
       fsi11 = 64-1
       fsi12 = 65-1

    # >>> Compute covariances ("fluxes") in the high-frequency part of the appropriate cospectra
    # To separate the small-scale turbulence from mesoscale motions (mostly in SBL), a low-frequency
    # cut-off was applied on the spectra/cospectra as a lower limit of integration.
    # low-freq cut-off fsn = fs(13) = 0.0064 Hz (the 13-th spectral value) for 2^15 = 32768 data points = 54.61333 min,
    # low-freq cut-off fsn = fs(9)  = 0.0064 Hz (the  9-th spectral value) for 2^14 = 16384 data points = 27.30667 min,
    # low-freq cut-off fsn = fs(6)  = 0.0061 Hz (the  6-th spectral value) for 2^13 =  8192 data points = 13.65333 min
    # These cut-off values are consistent with the low-frequency cut-off at 0.0061 Hz for
    # SHEBA data (Grachev et al. 2013, BLM, 147(1), 51-82, doi 10.1007/s10546-012-9771-0)
    # The upper limit of integration is 5 Hz (the Nyquist frequency)
    wu_csp_hi = np.sum(cwus[fsl:fsn]*dfs[fsl:fsn])
    wv_csp_hi = np.sum(cwvs[fsl:fsn]*dfs[fsl:fsn])
    uv_csp_hi = np.sum(cuvs[fsl:fsn]*dfs[fsl:fsn])
    wT_csp_hi = np.sum(cwTs[fsl:fsn]*dfs[fsl:fsn])
    uT_csp_hi = np.sum(cuTs[fsl:fsn]*dfs[fsl:fsn])
    vT_csp_hi = np.sum(cvTs[fsl:fsn]*dfs[fsl:fsn])
    ustar_hi = -np.sign(wu_csp_hi)*(np.abs(wu_csp_hi))**0.5 # friction velocity based on the high-frequency part of downstream, uw_hi,  stress components (m/s)
    Tstar_hi = -wT_csp_hi/np.abs(ustar_hi) # the temperature scale based on the high-frequency part of the turbulent fluxes
    Hs_hi = wT_csp_hi*rho*cp    # sensible heat flux (sonic temperature!) based on the high-frequency part of the cospectrum(W/m2)

    # >>> Compute standard deviations in the high-frequency part of the appropriate spectra
    #
    # real conversions here needed because parent variables defined as complex under spectra smoothing section
    #
    sigu_spc_hi    = (np.sum(sus[fsl:fsn]*dfs[fsl:fsn]))**0.5
    sigv_spc_hi    = (np.sum(svs[fsl:fsn]*dfs[fsl:fsn]))**0.5
    sigw_spc_hi    = (np.sum(sws[fsl:fsn]*dfs[fsl:fsn]))**0.5
    sigT_spc_hi    = (np.sum(sTs[fsl:fsn]*dfs[fsl:fsn]))**0.5
    sigwdir_spc_hi = (np.sum(swdirs[fsl:fsn]*dfs[fsl:fsn]))**0.5

    # >>> Some Monin-Obukhov (MO) parameters based on the local turbulent measurements:
    # Monin-Obukhov stability parameter, z/L:
    zeta_level_n = - ((0.4*9.81)/(Tsm+tdk))*(z_level_n*wT_csp/(ustar**3))
    # Drag coefficient, Cd:
    Cd = - wu_csp/(wsp**2)
    # MO universal functions for the standard deviations:
    phi_u = sigu_spc/ustar
    phi_v = sigv_spc/ustar
    phi_w = sigw_spc/ustar
    phi_T = sigT_spc/np.abs(Tstar)
    # MO universal function for the horizontal heat flux:
    phi_uT = uT_csp/wT_csp

    # >>> Some Monin-Obukhov (MO) parameters based on the local turbulent measurements (same as above but based on the high-frequency part of the turbulent fluxes):
    # Monin-Obukhov stability parameter based on the high-frequency part of the turbulent fluxes, z/L_hi:
    zeta_level_n_hi = - ((0.4*9.81)/(Tsm+tdk))*(z_level_n*wT_csp_hi/(ustar_hi**3))
    # Drag coefficient , Cd_hi:
    Cd_hi = - wu_csp_hi/(wsp**2)
    # MO universal functions for the standard deviations based on the high-frequency part of the turbulent fluxes:
    phi_u_hi = sigu_spc_hi/ustar_hi
    phi_v_hi = sigv_spc_hi/ustar_hi
    phi_w_hi = sigw_spc_hi/ustar_hi
    phi_T_hi = sigT_spc_hi/np.abs(Tstar_hi)

    # MO universal function for the horizontal heat flux based on the high-frequency part of the turbulent fluxes:
    phi_uT_hi = uT_csp_hi/wT_csp_hi

    #+++++++++++++++++++ Compute structure parameters in the inertial subrange +++++++++++++++++
    #+++++++++++++++++++++++++++++ 5/3 Kolmogorov power law +++++++++++++++++++++++++++++++++++

    # Structure parameters are used to derive dissipation rate of the turbulent kinetic energy ('epsilon') and half the temperature variance (Nt)
    # The inertial subrange is considered in the frequency subrange ~ 0.6-2 Hz
    # Generally this subrange depends on a height of measurements and may be different for w-component
    # For 2^15 = 32768 data points = 54.61333 min, the structure parameters are computed in the frequency domain between the 54th and 65th spectral values:
    #    fs(fsi01:fsi12) = fs(54:65) = [0.6662 0.7372 0.8156 0.9023 0.9981 1.1041 1.2213 1.3507 1.4937 1.6518 1.8265 2.0197]
    # For 2^14 = 16384 data points = 27.30667 min, the structure parameters are computed in the frequency domain between the 47th and 58th spectral values:
    #    fs(fsi01:fsi12) = fs(47:58) = [0.6531 0.7233 0.8011 0.8871 0.9824 1.0876 1.2039 1.3324 1.4743 1.6312 1.8045 1.9962]
    # For 2^13 =  8192 data points = 13.65333 min, the structure parameters are computed in the frequency domain between the 40th and 51st spectral values:
    #    fs(fsi01:fsi12) = fs(40:51) = [0.6342 0.7037 0.7806 0.8655 0.9595 1.0638 1.1792 1.3062 1.4465 1.6022 1.7743 1.9647]
    # For 2^12 =  4096 data points =  6.82667 min, the structure parameters are computed in the frequency domain between the 34th and 45th spectral values:
    #    fs(fsi01:fsi12) = fs(34:45) = [0.6738 0.7495 0.8337 0.9265 1.0291 1.1426 1.2683 1.4075 1.5613 1.7310 1.9189 2.1277]

    # Structure parameters definition:
    # Cu^2 = 4*alpha*epsilon^{2/3} (alpha=0.55); Ct^2 = 4*beta*Nt*epsilon^{-1/3} (beta=0.8)
    # Relationships between the structure parameters and the frequency spectra:
    # Cu^2 = 4*(2pi/U)^{2/3}*Su(f)*f^{-5/3}; Ct^2 = 4*(2pi/U)^{2/3}*St(f)*f^{-5/3};
    # Dimensions: [Cu^2] = [Ustar^2/z^{2/3}]; [Ct^2] = [Tstar^2/z^{2/3}];
    # Local isotropy in the inertial subrange assumes:
    # Fv(k)=Fw(k)=(4/3)Fu(k), or Sv(f)=Sw(f)=(4/3)Su(f), or Cv^2=Cw^2=(4/3)Cu^2.
    # Conversion from wavenumber to frequency scales: k*Fu(k)=f*Su(f).
    # See details in the textbook by J.C. Kaimal & J.J. Finnigan "Atmospheric Boundary Layer Flows" (1994)

    gfac = 4*(2*np.pi/wsp)**0.667
    cu2 = gfac*np.median(sus[fsi01:fsi12]*fs[fsi01:fsi12]**1.667)              # Cu^2, U structure parameter [x^2/m^2/3 = m^1.33/s^2]
    cv2 = gfac*np.median(svs[fsi01:fsi12]*fs[fsi01:fsi12]**1.667)              # Cv^2, V structure parameter [x^2/m^2/3 = m^1.33/s^2]
    cw2 = gfac*np.median(sws[fsi01:fsi12]*fs[fsi01:fsi12]**1.667)              # Cw^2, W structure parameter [x^2/m^2/3 = m^1.33/s^2]
    cT2 = gfac*np.median((sTs[fsi01:fsi12]-np.min(sTs))*fs[fsi01:fsi12]**1.667)   # Ct^2, T structure parameter [x^2/m^2/3 = deg^2/m^2/3]; (term -min(sTs) reduces some noise - proposed by Chris F.)
    # cT2 = gfac*numpy.median((sTs[fsi01:fsi12])*fs[fsi01:fsi12]**1.667)            # Ct^2, T structure parameter [x^2/m^2/3 = deg^2/m^2/3]


    #+++++++++++++++++ Compute dissipation rate of the turbulent kinetic energy ++++++++++++++++

    # Non-dimensional dissipation rate of the turbulent kinetic energy (TKE):
    # Phi_epsilon = kappa*z*epsilon/Ustar^3 - see Eq. (1.30) in Kaimal & Finnigan (1994)
    # Substitution of epsilon = (Cu^2/4*alpha)^(3/2) leads to
    # Phi_epsilon = kappa*[(z^2/3)*Cu^2/4*alpha*Ustar^2] = kappa*(Cu^2n/4*alpha)^3/2, where

    alphaK = 0.55 # - the Kolmogorov constant (alpha=0.55 - see above)
    # Note that Cu^2=(3/4)Cv^2=(3/4)Cw^2

    # >>> For epsilon_u (Based on Su) ++++++++++++++++++++++++++++++++++++++
    # Dissipation rate of the turbulent kinetic energy based on the energy spectra of the longitudinal velocity component in the inertial subrange [m^2/s^3]:
    epsilon_u = (cu2/(4*alphaK))**(3/2)
    # >>> For epsilon_v (Based on Sv) ++++++++++++++++++++++++++++++++++++++
    # Dissipation rate of the turbulent kinetic energy based on the energy spectra of the lateral velocity component in the inertial subrange [m^2/s^3]:
    epsilon_v = (3/4)*(cv2/(4*alphaK))**(3/2)
    # >>> For epsilon_w (Based on Sw) ++++++++++++++++++++++++++++++++++++++
    # Dissipation rate of the turbulent kinetic energy based on the energy spectra of the vertical velocity component in the inertial subrange [m^2/s^3]:
    epsilon_w = (3/4)*(cw2/(4*alphaK))**(3/2)
    # >>> Median epsilon (median of epsilon_u, epsilon_v, & epsilon_w) ++++++++++++++++++++++++++++++++++++++
    # Dissipation rate of the turbulent kinetic energy = median of the values derived from Su, Sv, & Sw [m^2/s^3]:
    epsilon = np.median([epsilon_u,epsilon_v,epsilon_w])
    # Monin-Obukhov universal function Phi_epsilon based on the median epsilon:
    Phi_epsilon = (0.4*z_level_n*epsilon)/(ustar**3)
    # Monin-Obukhov universal function Phi_epsilon based on the median epsilon based on the high-frequency part of the momentum flux:
    Phi_epsilon_hi = (0.4*z_level_n*epsilon)/(ustar_hi**3)

    #+++++ Compute the dissipation (destruction) rate for half the temperature variance +++++++
    #++++++++++++++++++ 5/3 Obukhov-Corrsin power law for the passive scalar ++++++++++++++++++

    #  Temperature Structure Parameter: Ct^2 = 4*beta*Nt*epsilon^{-1/3} (beta=0.8)
    betaK = 0.8 # - the Kolmogorov (Obukhov-Corrsin) constant for the passive scalar (beta=0.8 - see above)

    # >>> Nt (Based on Ct^2 derived from St) ++++++++++++++++++++++++++++++++++++++
    # The dissipation (destruction) rate for half the temperature variance [deg^2/s]:
    Nt = (cT2*(epsilon**(1/3)))/(4*betaK)
    # Monin-Obukhov universal function Phi_Nt:
    Phi_Nt = (0.4*z_level_n*Nt)/(ustar*Tstar**2)
    # Monin-Obukhov universal function Phi_Nt based on the high-frequency part of the turbulent fluxes:
    Phi_Nt_hi = (0.4*z_level_n*Nt)/(ustar_hi*Tstar_hi**2)

    #++++++++++++++++++++++ Compute spectral slopes in the inertial subrange +++++++++++++++++++

    # >>> Spectral slopes are computed in the frequency domain defined above
    # Compute a spectral slope in the inertial subrange for Su. Individual slopes:
    nSu_1 = np.log(sus[fsi07]/sus[fsi01])/np.log(fs[fsi07]/fs[fsi01])
    nSu_2 = np.log(sus[fsi08]/sus[fsi02])/np.log(fs[fsi08]/fs[fsi02])
    nSu_3 = np.log(sus[fsi09]/sus[fsi03])/np.log(fs[fsi09]/fs[fsi03])
    nSu_4 = np.log(sus[fsi10]/sus[fsi04])/np.log(fs[fsi10]/fs[fsi04])
    nSu_5 = np.log(sus[fsi11]/sus[fsi05])/np.log(fs[fsi11]/fs[fsi05])
    nSu_6 = np.log(sus[fsi12]/sus[fsi06])/np.log(fs[fsi12]/fs[fsi06])
    # Median spectral slope in the inertial subrange:
    nSu = np.median([nSu_1,nSu_2,nSu_3,nSu_4,nSu_5,nSu_6])

    # Compute a spectral slope in the inertial subrange for Sv.
    # Individual slopes:
    nSv_1 = np.log(svs[fsi07]/svs[fsi01])/np.log(fs[fsi07]/fs[fsi01])
    nSv_2 = np.log(svs[fsi08]/svs[fsi02])/np.log(fs[fsi08]/fs[fsi02])
    nSv_3 = np.log(svs[fsi09]/svs[fsi03])/np.log(fs[fsi09]/fs[fsi03])
    nSv_4 = np.log(svs[fsi10]/svs[fsi04])/np.log(fs[fsi10]/fs[fsi04])
    nSv_5 = np.log(svs[fsi11]/svs[fsi05])/np.log(fs[fsi11]/fs[fsi05])
    nSv_6 = np.log(svs[fsi12]/svs[fsi06])/np.log(fs[fsi12]/fs[fsi06])
    # Median spectral slope in the inertial subrange:
    nSv = np.median([nSv_1,nSv_2,nSv_3,nSv_4,nSv_5,nSv_6])

    # Compute a spectral slope in the inertial subrange for Sw. Individual slopes:
    nSw_1 = np.log(sws[fsi07]/sws[fsi01])/np.log(fs[fsi07]/fs[fsi01])
    nSw_2 = np.log(sws[fsi08]/sws[fsi02])/np.log(fs[fsi08]/fs[fsi02])
    nSw_3 = np.log(sws[fsi09]/sws[fsi03])/np.log(fs[fsi09]/fs[fsi03])
    nSw_4 = np.log(sws[fsi10]/sws[fsi04])/np.log(fs[fsi10]/fs[fsi04])
    nSw_5 = np.log(sws[fsi11]/sws[fsi05])/np.log(fs[fsi11]/fs[fsi05])
    nSw_6 = np.log(sws[fsi12]/sws[fsi06])/np.log(fs[fsi12]/fs[fsi06])
    # Median spectral slope in the inertial subrange:
    nSw = np.median([nSw_1,nSw_2,nSw_3,nSw_4,nSw_5,nSw_6])


    # Compute a spectral slope in the inertial subrange for St.
    # Individual slopes:
    nSt_1 = np.log(sTs[fsi07]/sTs[fsi01])/np.log(fs[fsi07]/fs[fsi01])
    nSt_2 = np.log(sTs[fsi08]/sTs[fsi02])/np.log(fs[fsi08]/fs[fsi02])
    nSt_3 = np.log(sTs[fsi09]/sTs[fsi03])/np.log(fs[fsi09]/fs[fsi03])
    nSt_4 = np.log(sTs[fsi10]/sTs[fsi04])/np.log(fs[fsi10]/fs[fsi04])
    nSt_5 = np.log(sTs[fsi11]/sTs[fsi05])/np.log(fs[fsi11]/fs[fsi05])
    nSt_6 = np.log(sTs[fsi12]/sTs[fsi06])/np.log(fs[fsi12]/fs[fsi06])
    # Median spectral slope in the inertial subrange:
    nSt = np.median([nSt_1,nSt_2,nSt_3,nSt_4,nSt_5,nSt_6])


    # Compute a spectral slope in the inertial subrange for Swdirs (wind direction spectrum).
    # Individual slopes:
    nSwdir_1 = np.log(swdirs[fsi07]/swdirs[fsi01])/np.log(fs[fsi07]/fs[fsi01])
    nSwdir_2 = np.log(swdirs[fsi08]/swdirs[fsi02])/np.log(fs[fsi08]/fs[fsi02])
    nSwdir_3 = np.log(swdirs[fsi09]/swdirs[fsi03])/np.log(fs[fsi09]/fs[fsi03])
    nSwdir_4 = np.log(swdirs[fsi10]/swdirs[fsi04])/np.log(fs[fsi10]/fs[fsi04])
    nSwdir_5 = np.log(swdirs[fsi11]/swdirs[fsi05])/np.log(fs[fsi11]/fs[fsi05])
    nSwdir_6 = np.log(swdirs[fsi12]/swdirs[fsi06])/np.log(fs[fsi12]/fs[fsi06])
    # Median spectral slope in the inertial subrange:
    nSwdir = np.median([nSwdir_1,nSwdir_2,nSwdir_3,nSwdir_4,nSwdir_5,nSwdir_6])


    # Note that the spectral slopes can be used as QC parameters, e.g. as indicator of resolution limit of a sonic anemometer
    # This resolution leads to a step ladder appearance in the data time series, and the turbulent fluxes cannot be reliably calculated
    # See Fig. 1b in Vickers & Mahrt (1997)J. Atmos. Oc. Tech. 14(3): 512�526
    # Eventually, in the very stable regime, the spectral slope levels off asymptotically at zero which corresponds to 'white noise' in the sensor
    # See spectra at level 5 in Fig. 3 in Grachev et al. (2008) Acta Geophysica. 56(1): 142�166.
    # For example, conditions nSu, nSv, nSu, and nSt > - 0.5 (or even > - 1) can be used as QC thresholds

    #+++++++++++++++Second-order moments of atmospheric turbulence (including fluxes)+++++++++++
    #+++++++++++++++ (Direct variances and covariances based on Reynolds averaging) ++++++++++++

    # Removing linear trends from the data (detrending the data):
    us_dtr = signal.detrend(us)
    vs_dtr = signal.detrend(vs)
    ws_dtr = signal.detrend(ws)
    Ts_dtr = signal.detrend(Ts)

    # Trend lines:
    us_trend = us - us_dtr
    vs_trend = vs - vs_dtr
    ws_trend = ws - ws_dtr
    Ts_trend = Ts - Ts_dtr

    # Mean of the detrended data (should be very close to zero)
    us_dtr_m = us_dtr.mean()
    vs_dtr_m = vs_dtr.mean()
    ws_dtr_m = ws_dtr.mean()
    Ts_dtr_m = Ts_dtr.mean()

    # >>> Covariances and Variances of the detrending data:
    cov_wu   = np.cov(ws_dtr,us_dtr)
    cov_wv   = np.cov(ws_dtr,vs_dtr)
    cov_uv   = np.cov(us_dtr,vs_dtr)
    cov_wT   = np.cov(ws_dtr,Ts_dtr)
    cov_uT   = np.cov(us_dtr,Ts_dtr)
    cov_vT   = np.cov(vs_dtr,Ts_dtr)
    wu_cov   = cov_wu[0,1]
    wv_cov   = cov_wv[0,1]
    uv_cov   = cov_uv[0,1]
    wT_cov   = cov_wT[0,1]
    uT_cov   = cov_uT[0,1]
    vT_cov   = cov_vT[0,1]
    sigu_cov = cov_wu[1,1]    # Standard deviation of the u-wind component
    sigv_cov = cov_wv[1,1]    # Standard deviation of the v-wind component
    sigw_cov = cov_wu[0,0]    # Standard deviation of the w-wind component
    sigT_cov = cov_wT[1,1]    # Standard deviation of the the air temperature (sonic temperature)
    sigu_std = np.std(us_dtr) # Standard deviation of the u-wind component
    sigv_std = np.std(vs_dtr) # Standard deviation of the v-wind component
    sigw_std = np.std(ws_dtr) # Standard deviation of the w-wind component
    sigT_std = np.std(Ts_dtr) # Standard deviation of the the air temperature (sonic temperature)

    # >>> Second-order moments (directly or by definition)
    # Linear detrending but no block-averaging of the data!
    # >>> Note that this is the same as 'cov' MatLab command above
    # nf = 32768 (54.6133 min averaged data)
    uu_dtr   = (np.sum(us_dtr*us_dtr))/nf
    uv_dtr   = (np.sum(us_dtr*vs_dtr))/nf
    uw_dtr   = (np.sum(us_dtr*ws_dtr))/nf
    vv_dtr   = (np.sum(vs_dtr*vs_dtr))/nf
    vw_dtr   = (np.sum(vs_dtr*ws_dtr))/nf
    ww_dtr   = (np.sum(ws_dtr*ws_dtr))/nf
    uT_dtr   = (np.sum(us_dtr*Ts_dtr))/nf
    vT_dtr   = (np.sum(vs_dtr*Ts_dtr))/nf
    wT_dtr   = (np.sum(ws_dtr*Ts_dtr))/nf
    TT_dtr   = (np.sum(Ts_dtr*Ts_dtr))/nf
    sigu_dtr = (uu_dtr)**0.5 # Standard deviation of the u-wind component
    sigv_dtr = (vv_dtr)**0.5 # Standard deviation of the v-wind component
    sigw_dtr = (ww_dtr)**0.5 # Standard deviation of the w-wind component
    sigT_dtr = (TT_dtr)**0.5 # Standard deviation of the the air temperature (sonic temperature)

    # Note that sigu_cov = sigu_std = sigu_dtr (the same for 'v', 'w', and 'T') - different methods of computation

    # >>> Standard deviations of the detrending second-order moments (fluxes and variances):
    sig_uv_dtr = np.std(us_dtr*vs_dtr)
    sig_uw_dtr = np.std(us_dtr*ws_dtr)
    sig_vw_dtr = np.std(vs_dtr*ws_dtr)
    sig_uT_dtr = np.std(us_dtr*Ts_dtr)
    sig_vT_dtr = np.std(vs_dtr*Ts_dtr)
    sig_wT_dtr = np.std(ws_dtr*Ts_dtr)
    sig_uu_dtr = np.std(us_dtr*us_dtr)
    sig_vv_dtr = np.std(vs_dtr*vs_dtr)
    sig_ww_dtr = np.std(ws_dtr*ws_dtr)
    sig_TT_dtr = np.std(Ts_dtr*Ts_dtr)

    # >>> Second-order moments (directly or by definition)
    # Same as above, but no detrending and no block-averaging of the data!
    # nf = 32768 (54.6133 min averaged data)
    uu_direct   = (np.sum((us-usm)*(us-usm)))/nf
    uv_direct   = (np.sum((us-usm)*(vs-vsm)))/nf
    uw_direct   = (np.sum((us-usm)*(ws-wsm)))/nf
    vv_direct   = (np.sum((vs-vsm)*(vs-vsm)))/nf
    vw_direct   = (np.sum((vs-vsm)*(ws-wsm)))/nf
    ww_direct   = (np.sum((ws-wsm)*(ws-wsm)))/nf
    uT_direct   = (np.sum((us-usm)*(Ts-Tsm)))/nf
    vT_direct   = (np.sum((vs-vsm)*(Ts-Tsm)))/nf
    wT_direct   = (np.sum((ws-wsm)*(Ts-Tsm)))/nf
    TT_direct   = (np.sum((Ts-Tsm)*(Ts-Tsm)))/nf
    sigu_direct = (uu_direct)**0.5
    sigv_direct = (vv_direct)**0.5
    sigw_direct = (ww_direct)**0.5
    sigT_direct = (TT_direct)**0.5

    # Ratio of the fluxes (standard deviations) derived from covariances to the appropriate values derived from cospectra (spectra):
    wu_ratio   = wu_cov/wu_csp
    wv_ratio   = wv_cov/wv_csp
    wT_ratio   = wT_cov/wT_csp
    sigu_ratio = sigu_cov/sigu_spc
    sigv_ratio = sigv_cov/sigv_spc
    sigw_ratio = sigw_cov/sigw_spc
    sigT_ratio = sigT_cov/sigT_spc

    # See details of the linear detrending in:
    # Gash, J. H. C. and A. D. Culf. 1996. Applying linear de-trend to eddy correlation data in real time. Boundary-Layer Meteorology, 79: 301-306.

    #++++++++++++++++++++ Third-order moments of atmospheric turbulence ++++++++++++++++++++++++
    # Linear detrending but no block-averaging of the data!
    # nf = 32768 (54.6133 min averaged data)

    uuu_dtr = (np.sum(us_dtr*us_dtr*us_dtr))/nf
    uuv_dtr = (np.sum(us_dtr*us_dtr*vs_dtr))/nf
    uuw_dtr = (np.sum(us_dtr*us_dtr*ws_dtr))/nf
    uvv_dtr = (np.sum(us_dtr*vs_dtr*vs_dtr))/nf
    uvw_dtr = (np.sum(us_dtr*vs_dtr*ws_dtr))/nf
    uww_dtr = (np.sum(us_dtr*ws_dtr*ws_dtr))/nf
    vvv_dtr = (np.sum(vs_dtr*vs_dtr*vs_dtr))/nf
    vvw_dtr = (np.sum(vs_dtr*vs_dtr*ws_dtr))/nf
    vww_dtr = (np.sum(vs_dtr*ws_dtr*ws_dtr))/nf
    www_dtr = (np.sum(ws_dtr*ws_dtr*ws_dtr))/nf

    uuT_dtr = (np.sum(us_dtr*us_dtr*Ts_dtr))/nf
    uvT_dtr = (np.sum(us_dtr*vs_dtr*Ts_dtr))/nf
    uwT_dtr = (np.sum(us_dtr*ws_dtr*Ts_dtr))/nf
    vvT_dtr = (np.sum(vs_dtr*vs_dtr*Ts_dtr))/nf
    vwT_dtr = (np.sum(vs_dtr*ws_dtr*Ts_dtr))/nf
    wwT_dtr = (np.sum(ws_dtr*ws_dtr*Ts_dtr))/nf
    uTT_dtr = (np.sum(us_dtr*Ts_dtr*Ts_dtr))/nf
    vTT_dtr = (np.sum(vs_dtr*Ts_dtr*Ts_dtr))/nf
    wTT_dtr = (np.sum(ws_dtr*Ts_dtr*Ts_dtr))/nf
    TTT_dtr = (np.sum(Ts_dtr*Ts_dtr*Ts_dtr))/nf

    #+++++++++++++++++++++++++++++++ Skewness & Kurtosis +++++++++++++++++++++++++++++++++++++++
    # >>> Skewness is a measure of symmetry, or more precisely, the lack of symmetry.  The
    # skewness for a normal distribution is zero, and any symmetric data should have a
    # skewness near zero.  Negative values for the skewness indicate data that are skewed left
    # and positive values for the skewness indicate data that are skewed right.

    # Skewness of the linear detrended data:
    Skew_u = sp.stats.skew(us_dtr)
    Skew_v = sp.stats.skew(vs_dtr)
    Skew_w = sp.stats.skew(ws_dtr)
    Skew_T = sp.stats.skew(Ts_dtr)
    Skew_uw = sp.stats.skew(us_dtr*ws_dtr)
    Skew_vw = sp.stats.skew(vs_dtr*ws_dtr)
    Skew_wT = sp.stats.skew(ws_dtr*Ts_dtr)
    Skew_uT = sp.stats.skew(us_dtr*Ts_dtr)

    # Direct definition of skewness (note that this is the same as 'skewness' MatLab command above):
    Skew_u0=uuu_dtr/sigu_dtr**3
    Skew_v0=vvv_dtr/sigv_dtr**3
    Skew_w0=www_dtr/sigw_dtr**3
    Skew_T0=TTT_dtr/sigT_dtr**3
    # Use this definition in the case if MatLab Statistics Toolbox is not available

    # >>> Kurtosis is a measure of whether the data are peaked or flat relative to a normal distribution.
    # Data sets with low kurtosis tend to have a flat top near the mean rather than a sharp peak.
    # The kurtosis for a standard normal distribution is three.

    # Kurtosis of the linear detrended data:
    Kurt_u  = sp.stats.kurtosis(us_dtr)
    Kurt_v  = sp.stats.kurtosis(vs_dtr)
    Kurt_w  = sp.stats.kurtosis(ws_dtr)
    Kurt_T  = sp.stats.kurtosis(Ts_dtr)
    Kurt_uw = sp.stats.kurtosis(us_dtr*ws_dtr)
    Kurt_vw = sp.stats.kurtosis(vs_dtr*ws_dtr)
    Kurt_wT = sp.stats.kurtosis(ws_dtr*Ts_dtr)
    Kurt_uT = sp.stats.kurtosis(us_dtr*Ts_dtr)

    # Some forth-order moments (for kurtosis calculations):
    uuuu_dtr = (np.sum(us_dtr*us_dtr*us_dtr*us_dtr))/nf
    vvvv_dtr = (np.sum(vs_dtr*vs_dtr*vs_dtr*vs_dtr))/nf
    wwww_dtr = (np.sum(ws_dtr*ws_dtr*ws_dtr*ws_dtr))/nf
    TTTT_dtr = (np.sum(Ts_dtr*Ts_dtr*Ts_dtr*Ts_dtr))/nf
    # Direct definition of kurtosis (note that this is the same as 'kurtosis' MatLab command above):
    Kurt_u0 = uuuu_dtr/sigu_dtr**4
    Kurt_v0 = vvvv_dtr/sigv_dtr**4
    Kurt_w0 = wwww_dtr/sigw_dtr**4
    Kurt_T0 = TTTT_dtr/sigT_dtr**4

    # Different examples of skewness/kurtosis and PDFs in CBL and SBL can be found in:
    # Chu et al (1996) WRR v32(6) 1681-1688; Graf et al (2010) BLM v134(3) 459-486; Mahrt et al (2012) JPO v42(7) 1134-1142

    # +++++++ Quality Control (QC) parameters derived from sonic anemometer for the 1-hr time series +++++++++++

    # Flagged if the values of different variables exceed user-defined (user-selected) thresholds
    # Angle of attack:
    Phix = phi*180/np.pi

    # If angle of attack is large (say > 15 deg) data should be filtered out or a correction to
    # compensate for the angle of attack error should be applied, e.g. see:

    # van der Molen, M. K. J. H. C. Gash, and J. A. Elbers (2004) Sonic anemometer (co)sine response and flux
    # measurement: II. The effect of introducing an angle of attack dependent calibration. Agricultural and
    # Forest Meterology, 122: 95-109.

    # Nakai, Taro; van der Molen, M. K.; Gash, J. H. C.; Kodama, Yuji (2006) Correction of sonic
    # anemometer angle of attack errors. Agricultural and Forest Meteorology, 136. 19-30.

    # Non-Stationarity of the data in the 1-hr time series, if sigwdir_spc is large (e.g. > 15 deg) data may
    # be considered as "bad" data (non-stationary). However this QC is not applicable for free convection
    # limit (light winds). Another QC parameters: Steadiness of horizontal wind and sonic temperature
    # (non-stationary data)
    DeltaU = us_trend[nf-1] - us_trend[0]
    DeltaV = vs_trend[nf-1] - vs_trend[0]
    DeltaT = Ts_trend[nf-1] - Ts_trend[0]
    # For example, |DeltaU| > 2 m/s, |DeltaV| > 2 m/s, |DeltaT| > 2 deg C can be used as QC thresholds

    # Recall that spectral slopes and rotated mean wind components, vrm & wrm, can also be used as QC
    # parameters (see earlier)

    # Different issues of QC are discussed in:

    # Foken, T. and B. Wichura. (1996) Tools for quality assessment of surface-based flux
    # measurements. Agricultural and Forest Meteorology, 78: 83-105.

    # Vickers D., Mahrt L. (1997) Quality control and flux sampling problems for tower and aircraft
    # data. J. Atmos. Oc. Tech. 14(3): 512�526

    # Foken et al. (2004) Edited by X. Lee, et al. Post-field quality control, in Handbook of
    # micrometeorology: A guide for surface flux measurements, 81-108.

    # Burba, G., and D. Anderson, (2010) A Brief Practical Guide to Eddy Covariance Flux Measurements:
    # Principles and Workflow Examples for Scientific and Industrial Applications. LI-COR, Lincoln, USA,
    # Hard and Softbound, 211 pp.

    #
    # End of calculations. Now output something
    #

    turbulence_data = turbulence_data.append([{'wu_csp': wu_csp,'wv_csp': wv_csp,'uv_csp': uv_csp,'ustar': ustar,\
        'wT_csp': wT_csp,'uT_csp': uT_csp,'vT_csp': vT_csp,'Hs': Hs,'Tstar': Tstar,'ustar_hi': ustar_hi,\
        'Tstar_hi': Tstar_hi,'Hs_hi': Hs_hi,'zeta_level_n': zeta_level_n,'Cd': Cd,'phi_u': phi_u,'phi_v': phi_v,\
        'phi_w': phi_w,'phi_T': phi_T,'phi_uT': phi_uT,'zeta_level_n_hi': zeta_level_n_hi,'Cd_hi': Cd_hi,\
        'phi_u_hi': phi_u_hi,'phi_v_hi': phi_v_hi,'phi_w_hi': phi_w_hi,'phi_T_hi': phi_T_hi,'phi_uT_hi': phi_uT_hi,\
        'epsilon_u': epsilon_u,'epsilon_v': epsilon_v,'epsilon_w': epsilon_w,'epsilon': epsilon,'Phi_epsilon': Phi_epsilon,\
        'Phi_epsilon_hi': Phi_epsilon_hi,'Nt': Nt,'Phi_Nt': Phi_Nt,'Phi_Nt_hi': Phi_Nt_hi,'Phix': Phix,\
        'DeltaU': DeltaU,'DeltaV': DeltaV,'DeltaT': DeltaT,'Kurt_u': Kurt_u,'Kurt_v': Kurt_v,'Kurt_w': Kurt_w,\
        'Kurt_T': Kurt_T,'Kurt_uw': Kurt_uw,'Kurt_vw': Kurt_vw,'Kurt_wT': Kurt_wT,'Kurt_uT': Kurt_uT,\
        'Skew_u': Skew_u,'Skew_v': Skew_v,'Skew_w': Skew_w,'Skew_T': Skew_T,'Skew_uw': Skew_uw,'Skew_vw': Skew_vw,\
        'Skew_wT': Skew_wT,'Skew_uT': Skew_uT}])

    # we need to give the columns unique names for the netcdf build later...
    # !! what is the difference betwee dataframe keys and columns? baffled. just change them both.
    # this needs to be done in code to make this more modular

    turbulence_data.keys = turbulence_data.keys()#+'_'+z_level_nominal
    turbulence_data.columns = turbulence_data.keys

    return turbulence_data

# takes datetime object, returns string YYYY-mm-dd
def dstr(date):
    return date.strftime("%Y-%m-%d")

# Bulk fluxes
def cor_ice_A10(bulk_input):
# ############################################################################################
# AUTHORS:
#
#   Ola Persson  ola.persson@noaa.gov
#   Python conversion and integration by Christopher Cox (NOAA) christopher.j.cox@noaa.gov
#
# PURPOSE:
#
# Bulk flux calculations for sea ice written by O. Persson and based on the 
# calculations made for SHEBA by Andreas et al. (2004) and the COARE algorithm
# (Fairall et al. 1996) minimization approach to solve for the needed 
# coefficients.
# Python version converted from Matlab cor_ice_A10.m
#
# References:
#   Andreas (1987) https://erdc-library.erdc.dren.mil/jspui/bitstream/11681/9435/1/CR-86-9.pdf
#   Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm
#   Andreas et al. (2004) https://doi.org/10.1175/1525-7541(2004)005<0611:SOSIAN>2.0.CO;2
#   Fairall et al. (1996) https://doi.org/10.1029/95JC03205                                 
#   Fairall et al. (2003) https://doi.org/10.1175/1520-0442(2003)016<0571:BPOASF>2.0.CO;2
#   Holtslag and De Bruin (1988) https://doi.org/10.1175/1520-0450(1988)027<0689:AMOTNS>2.0.CO;2
#   Grachev and Fairall (1997) https://doi.org/10.1175/1520-0450(1997)036<0406:DOTMOS>2.0.CO;2
#   Paulson (1970) https://doi.org/10.1175/1520-0450(1970)009<0857:TMROWS>2.0.CO;2
#   Smith (1988) https://doi.org/10.1029/JC093iC12p15467
#   Webb et al. (1980) https://doi.org/10.1002/qj.49710644707
# 
# Notes:
#   - prior to mods (see updates): x=[4.5,0,-10,-5,1,2,203,250,0,600,1010,15,15,15] test data compares to matlab version < 10^-15 error (Cox)
#   - modified for ice or water (Persson)
#   - this version has a shortened iteration (Persson) [max iters in stable conditions = 3]
#   - the 5th variable is a switch, x(5)<3 means ice, >3 means water (Persson)
#   - uses LKB Rt and Rq for seawater and Andreas 1987 for ice (Persson)
#   - presently has fixed zo=3e-4 for ice and Smith (1988) for water (Persson)    
#   - First guess Qs from Buck (qice.m, qwat.m by O. Persson) but hard-coded here. These estimates will
#     differ slightly from Hyland and Wexler humidity calculations reported at the tower (Cox)
#  
# Updates:
#   - additional documentation (Cox)
#   - instead of passing LWD, SWD and estimating nets, code now expects netLW and netSW (Cox)
#   - included rr, rt, rq as outputs
#   - took nominal zot and zoq out of the loop
#   - calculating zot, zoq and zo inside the loop now, but not allowing zoq or zot to be smaller than nominal 10^-4 Andreas value
#   - removed rain rate
#   - removed cool skin and hardcoded iceconcentration to be 1
# 
# Outputs:
#   hsb: sensible heat flux (Wm-2)
#   hlb: latent heat flux (Wm-2)
#   tau: stress                             (Pa)
#   zo: roughness length, veolicity              (m)
#   zot:roughness length, temperature (m)
#   zoq: roughness length, humidity (m)
#   L: Obukhov length (m)
#   usr: friction velocity (sqrt(momentum flux)), ustar (m/s)
#   tsr: temperature scale, tstar (K)
#   qsr: specific humidity scale, qstar (kg/kg?)
#   dter:
#   dqer: 
#   hl_webb: Webb density-corrected Hl (Wm-2)
#   Cd: transfer coefficient for stress
#   Ch: transfer coefficient for Hs
#   Ce: transfer coefficient for Hl
#   Cdn_10: 10 m neutral transfer coefficient for stress
#   Chn_10: 10 m neutral transfer coefficient for Hs
#   Cen_10: 10 m neutral transfer coefficient for Hl
#   rr: Reynolds number
#   rt: 
#   rq:
    

    import math
     
    u=bulk_input[0]         # wind speed                         (m/s)
    ts=bulk_input[1]        # bulk water/ice surface tempetature (degC)
    t=bulk_input[2]         # air temperature                    (degC) 
    Q=bulk_input[3]         # air moisture mixing ratio          (fraction)
    zi=bulk_input[4]        # inversion height                   (m)
    P=bulk_input[5]         # surface pressure                   (mb)
    zu=bulk_input[6]        # height of anemometer               (m)
    zt=bulk_input[7]        # height of thermometer              (m)
    zq=bulk_input[8]        # height of hygrometer               (m)
    
    
    
    ################################# Constants ################################## 
    # Set
    Beta=1.25 # gustiness coeff
    von=0.4 # von Karman constant
    fdg=1.00 # ratio of thermal to wind von Karman
    tdk=273.15 
    grav=9.82 # gravity
    CDn10=1.5e-3 # guestimated 10-m neutral drag coefficient

    # Air
    Rgas=287.1
    Le=(2.501-.00237*ts)*1e6
    cpa=1004.67 
    rhoa=P*100/(Rgas*(t+tdk)*(1+0.61*Q)) # density of air
    visa=1.325e-5*(1+6.542e-3*t+8.301e-6*t*t-4.8e-9*t*t*t) # kinematic viscosity
    
    
    ##############################################################################
    
    
    
    ############################### Subfunctions ################################# 
    
    # psi_m and psi_h are the stability functions that correct the neutral 
    # stability calculations for drag and tranfer, respectively, for deviations
    # from that assumption. They are "known" parameters and are borrowed here
    # from Paulson (1970) for the unstable state and Holtslag and De Bruin 
    # (1988) for the stable case, as wad done for SHEBA (Andreas et al. 2004).
    
    # for drag
    def psih_sheba(zet):
        if zet<0: # instability, Paulson (1970)
            x=(1-15*zet)**.5
            psik=2*math.log((1+x)/2)
            x=(1-34.15*zet)**.3333
            psic=1.5*math.log((1+x+x*x)/3)-math.sqrt(3)*math.atan((1+2*x)/math.sqrt(3))+4*math.atan(1)/math.sqrt(3)
            f=zet*zet/(1+zet*zet)
            psi=(1-f)*psik+f*psic                                              
        else: # stability, Holtslag and De Bruin (1988)
            ah = 5 
            bh = 5 
            ch = 3
            BH = math.sqrt(ch**2 - 4)
            psi = - (bh/2)*math.log(1+ch*zet+zet**2) + (((bh*ch)/(2*BH)) - (ah/BH))*(math.log((2*zet+ch-BH)/(2*zet+ch+BH)) - math.log((ch-BH)/(ch+BH)))
        return psi
    
    # for transfer
    def psim_sheba(zet):
        if zet<0: # instability, Paulson (1970)
            x=(1-15*zet)**.25;
            psik=2*math.log((1+x)/2)+math.log((1+x*x)/2)-2*math.atan(x)+2*math.atan(1)
            x=(1-10.15*zet)**.333
            psic=1.5*math.log((1+x+x*x)/3)-math.sqrt(3)*math.atan((1+2*x)/math.sqrt(3))+4*math.atan(1)/math.sqrt(3)
            f=zet*zet/(1+zet*zet)
            psi=(1-f)*psik+f*psic                                             
        else: # stability, Holtslag and De Bruin (1988)
            am = 5 
            bm = am/6.5
            BM = ((1-bm)/bm)**(1/3)
            y = (1+zet)**(1/3)
            psi = - (3*am/bm)*(y-1)+((am*BM)/(2*bm))*(2*math.log((BM+y)/(BM+1))-math.log((BM**2-BM*y+y**2)/(BM**2-BM+1))+2*math.sqrt(3)*math.atan((2*y-BM)/(BM*math.sqrt(3)))-2*math.sqrt(3)*math.atan((2-BM)/(BM*math.sqrt(3))))
        return psi
    
    

    ########################### COARE BULK LOOP ##############################
         
    # First guesses 
    
    if ts<=0:
        es=(1.0003+4.18e-6*P)*6.1115*math.exp(22.452*ts/(ts+272.55))
        Qs=es*622/(1010.0-.378*es)/1000    
    else:
        es=6.112*math.exp(17.502*ts/(ts+241.0))*(1.0007+3.46e-6*P)
        Qs=es*622/(1010.0-.378*es)/1000
               
          
    wetc=0.622*Le*Qs/(Rgas*(ts+tdk)**2)
            
    du=u
    dt=ts-t-0.0098*zt
    dq=Qs-Q
    ta=t+tdk
    ug=0.5
    dter=0
    
    ut=math.sqrt(du*du+ug*ug)
    zogs=10/(math.exp(von*(CDn10)**-0.5)) # drag coefficient estimate
    
    
    # Neutral coefficient
    u10=ut*math.log(10/zogs)/math.log(zu/zogs)
    cdhg=von/math.log(10/zogs)    
    usr=cdhg*u10
    zo10=zogs
    
    Cd10=(von/math.log(10/zo10))**2
    Ch10=0.0015
    
    Ct10=Ch10/math.sqrt(Cd10)
    zot10=10/math.exp(von/Ct10)
    Cd=(von/math.log(zu/zo10))**2
    
    # Grachev and Fairall (1997)    
    Ct=von/math.log(zt/zot10) # temp transfer coeff
    CC=von*Ct/Cd # z/L vs Rib linear coefficient
    Ribcu=-zu/zi/.004/Beta**3 # Saturation Rib
    Ribu=-grav*zu/ta*((dt-dter)+.61*ta*dq)/ut**2
    nits=7 # Number of iterations
    
    if Ribu<0:
    	zetu=CC*Ribu/(1+Ribu/Ribcu) # Unstable, G&F
    else:
    	zetu=CC*Ribu*(1+27/9*Ribu/CC) # Stable, I forget where I got this	
        
    L10=zu/zetu # MO length
    
    if zetu>150:
    	nits=3 # cutoff iteration if too stable
    
    # Figure guess stability dependent scaling params 
    usr=ut*von/(math.log(zu/zo10)-psim_sheba(zu/L10))
    tsr=-(dt-dter)*von*fdg/(math.log(zt/zot10)-psih_sheba(zt/L10))
    qsr=-(dq-wetc*dter)*von*fdg/(math.log(zq/zot10)-psih_sheba(zq/L10))
  
    zot=1e-4
    zoq=1e-4 # approximate values found by Andreas et al. (2004)  		    
    
    # Bulk Loop
    for i in range(nits): 
     

        zet=von*grav*zu/ta*(tsr+0.61*ta*qsr)/(usr**2) # Eq. (7), Fairall et al. (1996)
        zo=zogs
        
        # Fairall et al. (2003)
        rr=zo*usr/visa # Reynolds
        
        # Andreas (1987) for snow/ice
        if rr<=0.135: # areodynamically smooth
            rt=rr*math.exp(1.250)
            rq=rr*math.exp(1.610)
        elif rr<=2.5: # transition
            rt=rr*math.exp(0.149-.55*math.log(rr))
            rq=rr*math.exp(0.351-0.628*math.log(rr))
        elif rr<=1000: # aerodynamically rough
            rt=rr*math.exp(0.317-0.565*math.log(rr)-0.183*math.log(rr)*math.log(rr))
            rq=rr*math.exp(0.396-0.512*math.log(rr)-0.180*math.log(rr)*math.log(rr))
    

        L=zu/zet
        usr=ut*von/(math.log(zu/zo)-psim_sheba(zu/L))
        tsr=-(dt-dter)*von*fdg/(math.log(zt/zot)-psih_sheba(zt/L))
        qsr=-(dq-wetc*dter)*von*fdg/(math.log(zq/zoq)-psih_sheba(zq/L))
        Bf=-grav/ta*usr*(tsr+0.61*ta*qsr)
       
        if Bf>0:
            ug=Beta*(Bf*zi)**0.333
        else:
            ug=0.2
            
                
        #########    
        # added by Cox...
        # this allows zo to be calculated in the loop, which I think it needs to be
        # zot as well, but not allowing it to go to 0 and brek things.
        tau=rhoa*usr*usr*du/ut # stress
        Cd=tau/rhoa/du**2
        Ch=-usr*tsr/du/(dt-dter)
        zogs=zu*math.exp( -(von*Cd**-0.5 + psim_sheba(zq/L)) ) # Andreas (2004) eq. 3A
        zot=zu* math.exp( -(von*Cd**-0.5*Ch**-1 + psih_sheba(zq/L)) ) # Andreas (2004) eq. 3B
        if zot < 1e-4: zot = 1e-4
        ##########
        
        
        ut=math.sqrt(du*du+ug*ug)
        hsb=-rhoa*cpa*usr*tsr
        hlb=-rhoa*Le*usr*qsr
    
        dter=0
       
        dqer=wetc*dter
        

    # end bulk iter loop
    
    tau=rhoa*usr*usr*du/ut # stress

    ##############################################################################
    
    # Webb et al. correction
    wbar=1.61*hlb/rhoa/Le+(1+1.61*Q)*hsb/rhoa/cpa/ta
    hl_webb=wbar*Q*Le
    # compute transfer coeffs relative to du @meas. ht
    Cd=tau/rhoa/du**2
    Ch=-usr*tsr/du/(dt-dter)
    Ce=-usr*qsr/(dq-dqer)/du
    # 10-m neutral coeff realtive to ut
    Cdn_10=von**2/math.log(10/zo)/math.log(10/zo)
    Chn_10=von**2*fdg/math.log(10/zo)/math.log(10/zot)
    Cen_10=von**2*fdg/math.log(10/zo)/math.log(10/zoq)
    
    bulk_return=[hsb,hlb,tau,zo,zot,zoq,L,usr,tsr,qsr,dter,dqer,hl_webb,Cd,Ch,Ce,Cdn_10,Chn_10,Cen_10,rr,rt,rq]
    
    return bulk_return