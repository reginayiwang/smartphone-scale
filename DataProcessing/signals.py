from re import X
import scipy.signal as sp
import scipy.interpolate as ip
import matplotlib.pyplot as plt
import csv
import numpy as np
import sys



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

def get_gyroscope_filename(filename):
    split = filename.split('_')
    split[-2] = 'gyroscope'
    
    return '_'.join(split)

def load_data(filename, plot_t_stats=False):
    at,ax,ay,az = [],[],[],[]
    wt,wx,wy,wz = [],[],[],[]

    with open(filename, newline='') as csvfile:
        accdata = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(accdata) # first line is labels, this skips
        for row in accdata:
            at.append(int(row[0]))
            ax.append(float(row[1]))
            ay.append(float(row[2]))
            az.append(float(row[3]))

    with open(get_gyroscope_filename(filename), newline='') as csvfile:
        accdata = csv.reader(csvfile, delimiter=',', quotechar='|')
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

    if plot_t_stats:
        # dt statistics: how stable is our timestamp, how large?
        print("accelerometer mean, median, std: ", np.mean(dt_a),np.median(dt_a),np.std(dt_a))
        plt.subplot(1,2,1)
        plt.title("dt/median(dt), Accelerometer")
        plt.hist(dt_a/np.median(dt_a))
        plt.show()

        print("gyro mean, median, std: ", np.mean(dt_w),np.median(dt_w),np.std(dt_w))
        plt.subplot(1,2,2)
        plt.title("dt/median(dt), gyro")
        plt.hist(dt_w/np.median(dt_w))
        plt.show()

    t, fs, S = resample_and_sync(at, a, wt, w, np.median(dt_a))
    return t, fs, S


def plot_spectrograms( S, fs):
    f, t, Sax = sp.spectrogram(S[0,:], fs, mode='psd')
    f, t, Say = sp.spectrogram(S[1,:], fs, mode='psd')
    f, t, Saz = sp.spectrogram(S[2,:], fs, mode='psd')
    f, t, Swx = sp.spectrogram(S[3,:], fs, mode='psd')
    f, t, Swy = sp.spectrogram(S[4,:], fs, mode='psd')
    f, t, Swz = sp.spectrogram(S[5,:], fs, mode='psd')


    plt.subplot(2,3,1)
    plt.pcolormesh(t, f, Sax, shading='gouraud')
    plt.ylabel('Frequency [Hz]')

    plt.subplot(2,3,2)
    plt.pcolormesh(t, f, Say, shading='gouraud')

    plt.subplot(2,3,3)
    plt.pcolormesh(t, f, Saz, shading='gouraud')

    plt.subplot(2,3,4)
    plt.pcolormesh(t, f, Swx, shading='gouraud')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')

    plt.subplot(2,3,5)
    plt.pcolormesh(t, f, Swy, shading='gouraud')
    plt.xlabel('Time [sec]')

    plt.subplot(2,3,6)
    plt.pcolormesh(t, f, Swz, shading='gouraud')
    plt.xlabel('Time [sec]')

    plt.show()

def plot_PSD_comparisons(lb_ref,ub_ref,lb_obj,ub_obj,S,fs):
  #TODO this function needs updating away from "lb_ref" to taking in segmented data 
  #TODO we can fft along axis too so that needs cleaned

  win = sp.get_window('hann',ub_ref-lb_ref)
  psd_ref_ax = abs(np.fft.fft(win*S[lb_ref:ub_ref,0]))**2
  psd_obj_ax = abs(np.fft.fft(win*S[lb_obj:ub_obj,0]))**2
  psd_ref_ay = abs(np.fft.fft(win*S[lb_ref:ub_ref,1]))**2
  psd_obj_ay = abs(np.fft.fft(win*S[lb_obj:ub_obj,1]))**2
  psd_ref_az = abs(np.fft.fft(win*S[lb_ref:ub_ref,2]))**2
  psd_obj_az = abs(np.fft.fft(win*S[lb_obj:ub_obj,2]))**2
  psd_ref_wx = abs(np.fft.fft(win*S[lb_ref:ub_ref,3]))**2
  psd_obj_wx = abs(np.fft.fft(win*S[lb_obj:ub_obj,3]))**2
  psd_ref_wy = abs(np.fft.fft(win*S[lb_ref:ub_ref,4]))**2
  psd_obj_wy = abs(np.fft.fft(win*S[lb_obj:ub_obj,4]))**2
  psd_ref_wz = abs(np.fft.fft(win*S[lb_ref:ub_ref,5]))**2
  psd_obj_wz = abs(np.fft.fft(win*S[lb_obj:ub_obj,5]))**2

  f = np.linspace(0,fs/2,psd_ref_ax.shape[0]//2)

  plt.subplot(2,3,1)
  plt.plot(f,psd_ref_ax[0:512], label='ref')
  plt.plot(f,psd_obj_ax[0:512], label='obj')
  plt.yscale('log')

  plt.subplot(2,3,2)
  plt.plot(f,psd_ref_ay[0:512], label='ref')
  plt.plot(f,psd_obj_ay[0:512], label='obj')
  plt.yscale('log')

  plt.subplot(2,3,3)
  plt.plot(f,psd_ref_az[0:512], label='ref')
  plt.plot(f,psd_obj_az[0:512], label='obj')
  plt.yscale('log')

  plt.subplot(2,3,4)
  plt.plot(f,psd_ref_wx[0:512], label='ref')
  plt.plot(f,psd_obj_wx[0:512], label='obj')
  plt.yscale('log')

  plt.subplot(2,3,5)
  plt.plot(f,psd_ref_wy[0:512], label='ref')
  plt.plot(f,psd_obj_wy[0:512], label='obj')
  plt.yscale('log')

  plt.subplot(2,3,6)
  plt.plot(f,psd_ref_wz[0:512], label='ref')
  plt.plot(f,psd_obj_wz[0:512], label='obj')
  plt.yscale('log')

  plt.show()

def filter_data(S, fs, fc_low=128, fc_high=192, plot_freq_response=False):
    # filters data w/ highpass or bandpass filter (if fc_high is not None)  
    if fc_high is not None:
        sos = sp.butter(2, [2*fc_low/fs,2*fc_high/fs], 'bandpass', analog=False,output='sos')
    else:
        sos = sp.butter(2, 2*fc_low/fs, 'lowpass', analog=False,output='sos')

    if plot_freq_response:    
        w, h = sp.sosfreqz(sos) # different w here

        plt.semilogx(w, 20 * np.log10(abs(h)))
        plt.title('Butterworth filter frequency response')
        plt.xlabel('Frequency [radians / second]')
        plt.ylabel('Amplitude [dB]')
        plt.margins(0, 0.1)
        plt.grid(which='both', axis='both')
        plt.axvline(100, color='green') # cutoff frequency
        plt.show()

    return sp.sosfilt(sos, S, axis=1)

def segment_signal(t, S, ref_bounds,obj_bounds):
    # bounds format: (start, stop) in seconds
    ref_start, ref_stop = np.argwhere(t<=ref_bounds[0])[-1][0] if ref_bounds[0] > 0 else 0, np.argwhere(t<=ref_bounds[1])[-1][0]
    obj_start, obj_stop = np.argwhere(t<=obj_bounds[0])[-1][0], np.argwhere(t<=obj_bounds[1])[-1][0]
    
    # we should probably enforce the same size if we want to output this raw or if we want to output the full fft to the ml algs

    return t[ref_start:ref_stop], t[obj_start:obj_stop], S[:, ref_start:ref_stop], S[:, obj_start:obj_stop]

def peak_data(fs, S):
    #TODO figure out left/right kurtosis stuff/otherwise add more FFT data here 

    PSD = np.abs(np.fft.fft(S,axis=1))**2
    PSD = PSD[:,:PSD.shape[1]//2]
    peak_freqs, peak_mags, peak_widths = np.empty(6),np.empty(6), np.empty(6), 

    f = np.linspace(0,fs/2,PSD.shape[1])

    for i in range(6):
        peaks, peaks_dict = sp.find_peaks(PSD[i,:],height=(1,None),width=(None,None),plateau_size=(None,None))
        peak_arg = np.argmax(peaks_dict['peak_heights'])
        peak_freqs[i] = f[peaks[peak_arg]]
        peak_mags[i] = peaks_dict['peak_heights'][peak_arg]
        peak_widths[i] = peaks_dict['widths'][peak_arg]

    return peak_freqs, peak_mags, peak_widths
    
def harminv_peaks(S):
    # TODO (secret weapon, like peakfinder but more accurate)
    pass

def classic_intensity(S):
    #original vibroscale feature
    offset = S - np.expand_dims(np.mean(S, axis=1), axis=-1)
    intensity = np.sum(np.abs(offset), axis=1)/S.shape[1]

    return intensity


def generate_features(t,fs,S,ref_bounds,obj_bounds):
    feature_dict = {}
    
    ref_t, obj_t, ref_S, obj_S = segment_signal(t, S, ref_bounds,obj_bounds)

    filtered_S = filter_data(S, fs, 128, 192)
    ref_t, obj_t, filtered_ref_S, filtered_obj_S  = segment_signal(t, filtered_S, ref_bounds,obj_bounds)

    feature_dict['classic_intensity'] = (classic_intensity(ref_S), classic_intensity(obj_S)) # ignore in favor of filtered_classic?
    feature_dict['filtered_intensity'] = (classic_intensity(filtered_ref_S), classic_intensity(filtered_obj_S))

    #Shouldn't need to filter peak-finder data because we're in frequency space anyways\    
    ref_peak_freqs, ref_peak_mags, ref_peak_widths = peak_data(fs, ref_S)
    obj_peak_freqs, obj_peak_mags, obj_peak_widths = peak_data(fs, obj_S)

    feature_dict['peak_frequency'] = ref_peak_freqs, obj_peak_freqs
    feature_dict['peak_magnitude'] = ref_peak_mags, obj_peak_mags
    feature_dict['peak_width'] = ref_peak_widths, obj_peak_widths

    # output raw FFT?
    
    return feature_dict

def generate_features_from_file(filename, ref_bounds= (0,3), obj_bounds = (5,8)):
    """
    main feature generator function for vibroscale
        inputs:
            filename: name of accelerometer csv
            ref bounds = ( start time in seconds, stop time in seconds) of no-object-on-phone-vibration
            obj bounds = ( start time in seconds, stop time in seconds) of object-on-phone-vibration
            
            outputs: 
            feature_dict:
                feature_dict['classic_intensity'] : original vibroscale calculation, no filtering
                feature_dict['filtered_intensity'] : original vibroscale calculation, filtered around signal
                feature_dict['peak_frequency'] : frequency of largest peak in fft
                feature_dict['peak_magnitude'] : magnitude of largest peak in fft
                feature_dict['peak_width] : width of largest peak in fft
            
            all features are tuples of (ref_data, obj_data) and all sub-features are 6-dimensional vectors referring to the xyz axis of the accelerometer and then the gyroscope
    """

    t, fs, S = load_data(filename)
    feature_dict = generate_features(t,fs,S,ref_bounds,obj_bounds)

    return feature_dict

if __name__ == "__main__":
    features_dict = generate_features_from_file('test_accelerometer_1.csv')

    for key in features_dict.keys():
        print(key, features_dict[key][0], features_dict[key][1])