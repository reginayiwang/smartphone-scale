import scipy.signal as sp
import scipy.interpolate as ip
import csv
import numpy as np
import harminv

def make_feats(acc_file, gyro_file, OG=False):
    if OG:
        feats = generate_features_from_file(acc_file, gyro_file, mode='sub', OG=True)
        cin = feats['classic_intensity'][1]
        return np.array(cin)
    else:
        xz_indices = [0, 2]
        feats = generate_features_from_file(acc_file, gyro_file, mode='per', OG=False)
        fin = feats['filtered_intensity'][xz_indices]
        hmag = feats['h_peak_magnitude'][xz_indices]
        return np.concatenate((fin, hmag), axis=0)
    
def resample_and_sync(at,a,wt,w,period=1.0/396.4):
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

def load_data(acc_file, gyro_file, OG=False):
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

    if OG:
        at, wt = np.array(at[::2]), np.array(wt[::2])
        a = np.vstack((np.array(ax[::2]),np.array(ay[::2]),np.array(az[::2])))
        w = np.vstack((np.array(wx[::2]),np.array(wy[::2]),np.array(wz[::2])))

    dt_a = (at[1:] - at[:-1])
    
    return resample_and_sync(at, a, wt, w, np.median(dt_a))

def filter_data(S, fs, fc_low=128, fc_high=192, plot_freq_response=False):
    if fc_high is not None:
        sos = sp.butter(1, [2*fc_low/fs,2*fc_high/fs], 'bandpass', analog=False,output='sos')
    else:
        sos = sp.butter(1, 2*fc_low/fs, 'highpass', analog=False,output='sos')

    return sp.sosfilt(sos, S, axis=1)

def segment_signal(t, S, ref_bounds, obj_bounds):
    ref_start, ref_stop = np.argwhere(t<=ref_bounds[0])[-1][0] if ref_bounds[0] > 0 else 0, np.argwhere(t<=ref_bounds[1])[-1][0]
    obj_start, obj_stop = np.argwhere(t<=obj_bounds[0])[-1][0], np.argwhere(t<=obj_bounds[1])[-1][0]
    
    ref_len = ref_stop-ref_start
    obj_len = obj_stop-obj_start
    if ref_len > obj_len:
        ref_stop = ref_start + obj_len
    elif ref_len < obj_len:
        obj_stop = obj_start + ref_len

    return S[:, ref_start:ref_stop], S[:, obj_start:obj_stop]

def harminv_peaks(fs, S):
    h_peak_mags = np.empty(6)
    for i in range(6):
        inversion = harminv.invert(S[i,:], fmin=fs*5./16., fmax=fs*7./16., dt=1.0/fs, nf=64)
        best = np.argmax([inversion[j][1] for j in range(inversion.shape[0])])
        h_peak_mags[i] = inversion[best][1]

    return h_peak_mags

def classic_intensity(S):
    offset = S - np.expand_dims(np.mean(S, axis=1), axis=-1)
    intensity = np.sum(np.abs(offset), axis=1)/S.shape[1]

    return intensity

def compare_refs(ref, obj, mode):
    if mode == 'div':
        return obj/ref
    elif mode == 'sub':
        return obj-ref
    elif mode == 'per':
        return (obj-ref)/ref

    return (ref, obj)

def generate_features(t,fs,S,ref_bounds,obj_bounds, mode, OG=False):
    feature_dict = {}
    
    ref_S, obj_S = segment_signal(t, S, ref_bounds,obj_bounds)

    filtered_S = filter_data(S, fs, fs/4., None)
    filtered_ref_S, filtered_obj_S  = segment_signal(t, filtered_S, ref_bounds,obj_bounds)

    if OG:     
        feature_dict['classic_intensity'] = compare_refs(classic_intensity(ref_S), classic_intensity(obj_S), 'sub') # ignore in favor of filtered_classic?
        return feature_dict

    feature_dict['filtered_intensity'] = compare_refs(classic_intensity(filtered_ref_S), classic_intensity(filtered_obj_S), mode)

    ref_h_peak_mags = harminv_peaks(fs, ref_S)
    obj_h_peak_mags = harminv_peaks(fs, obj_S)

    feature_dict['h_peak_magnitude'] = compare_refs(ref_h_peak_mags, obj_h_peak_mags, mode)
    
    return feature_dict

def generate_features_from_file(acc_file, gyro_file, ref_bounds= (0.1,2.9), obj_bounds = (5.1,7.9), mode='sub', OG=False):
    t, fs, S = load_data(acc_file, gyro_file, OG=OG)
    
    feature_dict = generate_features(t,fs,S,ref_bounds,obj_bounds, mode, OG=OG)
    return feature_dict