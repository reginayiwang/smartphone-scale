import matplotlib.pyplot as plt
import scipy.signal as sp
import numpy as np
import pickle
import pandas as pd 
import seaborn as sns
import signals
import os
import matplotlib.animation as animation

from sklearn.manifold import TSNE
plt.style.use('seaborn-colorblind')

import warnings 
warnings.filterwarnings('ignore')

def plot_spectrograms( S, fs):
    f, t, Sax = sp.spectrogram(S[0,:], fs, mode='psd')
    f, t, Say = sp.spectrogram(S[1,:], fs, mode='psd')
    f, t, Saz = sp.spectrogram(S[2,:], fs, mode='psd')
    f, t, Swx = sp.spectrogram(S[3,:], fs, mode='psd')
    f, t, Swy = sp.spectrogram(S[4,:], fs, mode='psd')
    f, t, Swz = sp.spectrogram(S[5,:], fs, mode='psd')

    plt.suptitle("IMU data spectrogram")

    plt.subplot(2,3,1)
    plt.pcolormesh(t, f, Sax)
    plt.ylabel('Accelerometer Frequency [Hz]')

    plt.subplot(2,3,2)
    plt.pcolormesh(t, f, Say)

    plt.subplot(2,3,3)
    plt.pcolormesh(t, f, Saz)

    plt.subplot(2,3,4)
    plt.pcolormesh(t, f, Swx)
    plt.ylabel('Gyro Frequency [Hz]')
    plt.xlabel('X Time [sec]')

    plt.subplot(2,3,5)
    plt.pcolormesh(t, f, Swy)
    plt.xlabel('Y Time [sec]')

    plt.subplot(2,3,6)
    plt.pcolormesh(t, f, Swz)
    plt.xlabel('Z Time [sec]')

    plt.show()

def plot_PSD_comparisons(ref_S,obj_S,fs):
  win = sp.get_window('hann',ref_S.shape[1])
  psd_ref_ax = 1+abs(np.fft.fft(win*ref_S[0,:]))**2
  psd_obj_ax = 1+abs(np.fft.fft(win*obj_S[0,:]))**2
  psd_ref_ay = 1+abs(np.fft.fft(win*ref_S[1,:]))**2
  psd_obj_ay = 1+abs(np.fft.fft(win*obj_S[1,:]))**2
  psd_ref_az = 1+abs(np.fft.fft(win*ref_S[2,:]))**2
  psd_obj_az = 1+abs(np.fft.fft(win*obj_S[2,:]))**2
  psd_ref_wx = 1+abs(np.fft.fft(win*ref_S[3,:]))**2
  psd_obj_wx = 1+abs(np.fft.fft(win*obj_S[3,:]))**2
  psd_ref_wy = 1+abs(np.fft.fft(win*ref_S[4,:]))**2
  psd_obj_wy = 1+abs(np.fft.fft(win*obj_S[4,:]))**2
  psd_ref_wz = 1+abs(np.fft.fft(win*ref_S[5,:]))**2
  psd_obj_wz = 1+abs(np.fft.fft(win*obj_S[5,:]))**2

  f = np.linspace(0,fs/2,psd_ref_ax.shape[0]//2)


  fig, axs = plt.subplots(2, 3)
  fig.suptitle('Power Spectral Density Comparison')


  axs[0,0].plot(f,psd_ref_ax[:psd_ref_ax.shape[0]//2], label='ref')
  axs[0,0].plot(f,psd_obj_ax[:psd_ref_ax.shape[0]//2], label='obj')
  axs[0,0].set_yscale('log')

  axs[0,1].plot(f,psd_ref_ay[:psd_ref_ax.shape[0]//2], label='ref')
  axs[0,1].plot(f,psd_obj_ay[:psd_ref_ax.shape[0]//2], label='obj')
  axs[0,1].set_yscale('log')

  axs[0,2].plot(f,psd_ref_az[:psd_ref_ax.shape[0]//2], label='ref')
  axs[0,2].plot(f,psd_obj_az[:psd_ref_ax.shape[0]//2], label='obj')
  axs[0,2].set_yscale('log')

  axs[1,0].plot(f,psd_ref_wx[:psd_ref_ax.shape[0]//2], label='ref')
  axs[1,0].plot(f,psd_obj_wx[:psd_ref_ax.shape[0]//2], label='obj')
  axs[1,0].set_yscale('log')

  axs[1,1].plot(f,psd_ref_wy[:psd_ref_ax.shape[0]//2], label='ref')
  axs[1,1].plot(f,psd_obj_wy[:psd_ref_ax.shape[0]//2], label='obj')
  axs[1,1].set_yscale('log')

  axs[1,2].plot(f,psd_ref_wz[:psd_ref_ax.shape[0]//2], label='ref')
  axs[1,2].plot(f,psd_obj_wz[:psd_ref_ax.shape[0]//2], label='obj')
  axs[1,2].set_yscale('log')

  plt.show()

def ts_detail(ref_t, obj_t, ref_S, obj_S):
  plt.title("Time series, detail view.  Accelerometer Y axis.")
  plt.plot(ref_t[0:25], ref_S[1,0:25], label='reference')
  plt.plot(ref_t[0:25], obj_S[1,0:25], label='measurement')
  plt.show()

def ts_overall(ref_t, obj_t, ref_S, obj_S):
  plt.title("Time series, detail view.  Accelerometer Y axis. Apple")
  
  plt.plot(ref_t, ref_S[1], label='reference')
  plt.plot(ref_t, obj_S[1], label='measurement')
  plt.show()

if __name__=='__main__':

  inspection_list = ['Pixel3_Apple_146_High_accelerometer_30.csv']

  for file in os.scandir('DataProcessing/data/test'):
    if file.name in inspection_list:
      t, fs, S = signals.load_data(file, OG=False)
      plot_spectrograms(S,fs)

      ref_t, obj_t, ref_S, obj_S  = signals.segment_signal(t, S, ref_bounds= (0.1,2.9), obj_bounds = (5.1,7.9))

      ts_detail(ref_t, obj_t, ref_S, obj_S)
      ts_overall(ref_t, obj_t, ref_S, obj_S)
      plot_PSD_comparisons(ref_S,obj_S, fs)

  # iter = os.scandir('DataProcessing/data/all_data/')
  # file = iter.__next__()
  # t, fs, S = signals.load_data(file, OG=False)
  # ref_t, obj_t, ref_S, obj_S  = signals.segment_signal(t, S, ref_bounds= (0.1,2.9), obj_bounds = (5.1,7.9))


  # fig, ax = plt.subplots()

  # lines = []

  # line1,  = ax.plot(ref_t, ref_S[1], label='reference', linewidth=1.5)
  # line2,  = ax.plot(ref_t, obj_S[1], label='measurement', linewidth=0.5)

  # lines.append(line1)
  # lines.append(line2)

  # def update(*args):
  #   file = iter.__next__()

  #   if str(file).split('_')[-2] == 'accelerometer':
  #     t, fs, S = signals.load_data(file, OG=False)
  #     ref_t, obj_t, ref_S, obj_S  = signals.segment_signal(t, S, ref_bounds= (0.1,2.9), obj_bounds = (5.1,7.9))
  #     lines[0].set_ydata(ref_S[1])
  #     lines[0].set_xdata(ref_t)
  #     lines[1].set_ydata(obj_S[1])
  #     lines[1].set_xdata(ref_t)
  #   return lines

  # anim = animation.FuncAnimation(fig, update, frames = os.scandir('DataProcessing/data/all_data/'), interval=10)
  
  # f = r"animation.gif" 
  # writergif = animation.PillowWriter(fps=30) 
  # anim.save(f, writer=writergif)
  # plt.show()

  # file.name = 'DataProcessing/data/test/Pixel3_Apple_146_High_accelerometer_30.csv'