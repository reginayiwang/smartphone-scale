from re import X
import scipy.signal as sp
import scipy.interpolate as ip
from sklearn.preprocessing import PolynomialFeatures
import csv
import numpy as np
import pandas as pd
import harminv

def make_feats(acc_file, gyro_file):
    df = pd.DataFrame.from_dict(generate_features_from_file(acc_file, gyro_file))
    cin = df['classic_intensity']
    fin = df['filtered_intensity']
    lips = df['left_ips']
    rips = df['right_ips']
    pmag = df['peak_magnitude']
    pfre = df['peak_frequency']
    hmag = df['h_peak_magnitude']
    hfre = df['h_peak_frequency']
    poly = PolynomialFeatures(degree=3)
    feats = poly.fit_transform(np.array(hmag).reshape(1, -1))
    
    return np.array(feats)
    # return np.concatenate((cin,fin,lips,rips,pmag,pfre),axis=0)

def resample_and_sync(at,a,wt,w,period=1.0/396.4):
#   period_adjusted = period * 1e9 # in microseconds

  start_point = max(at[0],wt[0])
  end_point = min(at[-1],wt[-1])

  kind='cubic' # 'quadratic'
  a_f = ip.interp1d(at,a,kind=kind)
  w_f = ip.interp1d(wt,w,kind=kind)

  new_t = [start_point + i * period for i in range(0,1+int((end_point - start_point)/period))]
  new_t_seconds = (new_t - start_point)*1e-9

  new_a_stack = a_f(new_t)
  new_w_stack = w_f(new_t)
  S = np.vstack((new_a_stack[0,:],new_a_stack[1,:],new_a_stack[2,:],new_w_stack[0,:],new_w_stack[1,:],new_w_stack[2,:]))

  return new_t_seconds, 1.0/(period*1e-9), S

def load_data(acc_file, gyro_file):
    at,ax,ay,az = [],[],[],[]
    wt,wx,wy,wz = [],[],[],[]

    accdata = csv.reader(acc_file, delimiter=',', quotechar='|')
    next(accdata) # first line is labels, this skips
    for row in accdata:
        at.append(int(row[0]))
        ax.append(float(row[1]))
        ay.append(float(row[2]))
        az.append(float(row[3]))


    accdata = csv.reader(gyro_file, delimiter=',', quotechar='|')
    next(accdata) # first line is labels, this skips
    for row in accdata:
        wt.append(int(row[0]))
        wx.append(float(row[1]))
        wy.append(float(row[2]))
        wz.append(float(row[3]))

    at, wt = np.array(at), np.array(wt)
    a = np.vstack((np.array(ax),np.array(ay),np.array(az)))
    w = np.vstack((np.array(wx),np.array(wy),np.array(wz)))

    dt_a = (at[1:] - at[:-1])
    dt_w = (wt[1:] - wt[:-1])

    t, fs, S = resample_and_sync(at, a, wt, w, np.median(dt_a))
    return t, fs, S

def filter_data(S, fs, fc_low=128, fc_high=192, plot_freq_response=False):
    # filters data w/ highpass or bandpass filter (if fc_high is not None)  
    if fc_high is not None:
        sos = sp.butter(1, [2*fc_low/fs,2*fc_high/fs], 'bandpass', analog=False,output='sos')
    else:
        sos = sp.butter(1, 2*fc_low/fs, 'highpass', analog=False,output='sos')

    return sp.sosfilt(sos, S, axis=1)

def segment_signal(t, S, ref_bounds, obj_bounds):
    # bounds format: (start, stop) in seconds
    ref_start, ref_stop = np.argwhere(t<=ref_bounds[0])[-1][0] if ref_bounds[0] > 0 else 0, np.argwhere(t<=ref_bounds[1])[-1][0]
    obj_start, obj_stop = np.argwhere(t<=obj_bounds[0])[-1][0], np.argwhere(t<=obj_bounds[1])[-1][0]
    
    ref_len = ref_stop-ref_start
    obj_len = obj_stop-obj_start
    if ref_len > obj_len:
        ref_stop = ref_start + obj_len
    elif ref_len < obj_len:
        obj_stop = obj_start + ref_len
    # we should probably enforce the same size if we want to output this raw or if we want to output the full fft to the ml algs

    return t[ref_start:ref_stop], t[obj_start:obj_stop], S[:, ref_start:ref_stop], S[:, obj_start:obj_stop]

def peak_data(fs, S):
    PSD = np.abs(np.fft.fft(S,axis=1))**2
    PSD = PSD[:,:PSD.shape[1]//2] # np.log(1+PSD[:,:PSD.shape[1]//2]) #work in log?
    peak_freqs, peak_mags, left_ips, right_ips = np.empty(6), np.empty(6), np.empty(6), np.empty(6), 

    f = np.linspace(0,fs/2,PSD.shape[1])

    for i in range(6):
        peaks, peaks_dict = sp.find_peaks(PSD[i,:],height=(0,None),width=(None,None),plateau_size=(None,None))
        peak_arg = np.argmax(peaks_dict['peak_heights'])
        peak_freqs[i] = f[peaks[peak_arg]]
        peak_mags[i] = peaks_dict['peak_heights'][peak_arg]
        left_ips[i] = peaks_dict['left_ips'][peak_arg]
        right_ips[i] = peaks_dict['right_ips'][peak_arg]


    return peak_freqs, peak_mags, left_ips, right_ips
    
def harminv_peaks(fs, S):
    h_peak_freqs, h_peak_mags, h_decay, h_Q, h_error = np.empty(6), np.empty(6), np.empty(6), np.empty(6), np.empty(6)
    for i in range(6):
        inversion = harminv.invert(S[i,:], fmin=fs*5./16., fmax=fs*7./16., dt=1.0/fs, nf=64)
        best = np.argmax([inversion[j][1] for j in range(inversion.shape[0])])
        h_peak_freqs[i] = inversion[best][0]
        h_peak_mags[i] = inversion[best][1]
        h_decay[i] = inversion[best][3]
        h_Q[i] = inversion[best][4]
        h_error[i] = inversion[best][5]

    return h_peak_freqs, h_peak_mags, h_decay, h_Q, h_error

def classic_intensity(S):
    #original vibroscale feature
    offset = S - np.expand_dims(np.mean(S, axis=1), axis=-1)
    intensity = np.sum(np.abs(offset), axis=1)/S.shape[1]

    return intensity

def classic_power(S):
    offset = S - np.expand_dims(np.mean(S, axis=1), axis=-1)
    return np.sum(np.abs(offset)**2, axis=1)/S.shape[1]

def compare_refs(ref, obj, mode):
    if mode == 'div':
        return obj/ref
    elif mode == 'sub':
        return obj-ref
    elif mode == 'per':
        return (obj-ref)/ref

    return (ref, obj)

def generate_features(t,fs,S,ref_bounds,obj_bounds, mode='div', Harminv=True):
    feature_dict = {}
    
    ref_t, obj_t, ref_S, obj_S = segment_signal(t, S, ref_bounds,obj_bounds)

    filtered_S = filter_data(S, fs, fs/4., None)
    ref_t, obj_t, filtered_ref_S, filtered_obj_S  = segment_signal(t, filtered_S, ref_bounds,obj_bounds)

    feature_dict['classic_intensity'] = compare_refs(classic_intensity(ref_S), classic_intensity(obj_S), mode) # ignore in favor of filtered_classic?
    feature_dict['filtered_intensity'] = compare_refs(classic_intensity(filtered_ref_S), classic_intensity(filtered_obj_S), mode)

    #Shouldn't need to filter peak-finder data because we're in frequency space anyways\    
    ref_peak_freqs, ref_peak_mags, ref_left_ips, ref_right_ips = peak_data(fs, ref_S)
    obj_peak_freqs, obj_peak_mags, obj_left_ips, obj_right_ips = peak_data(fs, obj_S)

    feature_dict['peak_frequency'] = compare_refs(ref_peak_freqs, obj_peak_freqs, mode)
    feature_dict['peak_magnitude'] = compare_refs(ref_peak_mags, obj_peak_mags, mode)
    feature_dict['left_ips'] = compare_refs(ref_left_ips, obj_left_ips, mode)
    feature_dict['right_ips'] = compare_refs(ref_right_ips, obj_right_ips, mode)

    if Harminv:
        ref_h_peak_freqs, ref_h_peak_mags, ref_h_decay, ref_h_Q, ref_h_error = harminv_peaks(fs, ref_S)
        obj_h_peak_freqs, obj_h_peak_mags, obj_h_decay, obj_h_Q, obj_h_error = harminv_peaks(fs, obj_S)

        feature_dict['h_peak_frequency'] = compare_refs(ref_h_peak_freqs, obj_h_peak_freqs, mode)
        feature_dict['h_peak_magnitude'] = compare_refs(ref_h_peak_mags, obj_h_peak_mags, mode)
        feature_dict['h_decay'] = compare_refs(ref_h_decay, obj_h_decay, mode)
        feature_dict['h_Q'] = compare_refs(ref_h_Q, obj_h_Q, mode)
        feature_dict['h_error'] = compare_refs(ref_h_error, obj_h_error, mode)
    
    return feature_dict

def generate_features_from_file(acc_file, gyro_file, ref_bounds= (0.1,2.9), obj_bounds = (5.1,7.9), mode='sub'):
    """
    main feature generator function for vibroscale
        inputs:
            filename: name of accelerometer csv (matching gyroscope data will be accessed automatically)
            ref bounds = ( start time in seconds, stop time in seconds) of no-object-on-phone-vibration
            obj bounds = ( start time in seconds, stop time in seconds) of object-on-phone-vibration
            mode = 'div', 'sub', 'per', or None :
                'div' -> object_feature/ref_feature
                'sub' -> object_feature-ref_feature
                'per' -> (object_featur-ref_feature)/ref_feature
                None -> return object features only (only data from vibration with object on phone)
            
            outputs: 
            feature_dict:
                6-dimensional vectors referring to the xyz axis of the accelerometer and then the gyroscope:
                    feature_dict['classic_intensity'] : original vibroscale calculation, no filtering
                    feature_dict['filtered_intensity'] : original vibroscale calculation, filtered around signal
                    feature_dict['peak_frequency'] : frequency of largest peak in fft
                    feature_dict['peak_magnitude'] : magnitude of largest peak in fft
                    feature_dict['left_ips] : left kurtosis, ish (intersection of interpolated peak w/ base)
                    feature_dict['right_ips] : right kurtosis, ish (intersection of interpolated peak w/ base)
                1-dim vectors/descriptors
                    feature_dict['weight'] : int, weight in grams, from filename
                    feature_dict['class'] : str, type of fruit, from filename
            
            all features are 6-dimensional vectors referring to the xyz axis of the accelerometer and then the gyroscope
    """
    t, fs, S = load_data(acc_file, gyro_file)

    feature_dict = generate_features(t,fs,S,ref_bounds,obj_bounds, mode)

    return feature_dict