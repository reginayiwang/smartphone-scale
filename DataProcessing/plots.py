import matplotlib.pyplot as plt
import scipy.signal as sp
import numpy as np

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

  plt.subplot(2,3,1)
  plt.plot(f,psd_ref_ax[:psd_ref_ax.shape[0]//2], label='ref')
  plt.plot(f,psd_obj_ax[:psd_ref_ax.shape[0]//2], label='obj')
  plt.yscale('log')

  plt.subplot(2,3,2)
  plt.plot(f,psd_ref_ay[:psd_ref_ax.shape[0]//2], label='ref')
  plt.plot(f,psd_obj_ay[:psd_ref_ax.shape[0]//2], label='obj')
  plt.yscale('log')

  plt.subplot(2,3,3)
  plt.plot(f,psd_ref_az[:psd_ref_ax.shape[0]//2], label='ref')
  plt.plot(f,psd_obj_az[:psd_ref_ax.shape[0]//2], label='obj')
  plt.yscale('log')

  plt.subplot(2,3,4)
  plt.plot(f,psd_ref_wx[:psd_ref_ax.shape[0]//2], label='ref')
  plt.plot(f,psd_obj_wx[:psd_ref_ax.shape[0]//2], label='obj')
  plt.yscale('log')

  plt.subplot(2,3,5)
  plt.plot(f,psd_ref_wy[:psd_ref_ax.shape[0]//2], label='ref')
  plt.plot(f,psd_obj_wy[:psd_ref_ax.shape[0]//2], label='obj')
  plt.yscale('log')

  plt.subplot(2,3,6)
  plt.plot(f,psd_ref_wz[:psd_ref_ax.shape[0]//2], label='ref')
  plt.plot(f,psd_obj_wz[:psd_ref_ax.shape[0]//2], label='obj')
  plt.yscale('log')

  plt.show()



def plot_transfer_comparisons(ref_S,obj_S,fs):
  win = sp.get_window('hann',ref_S.shape[1])

  psd_ref_ax = np.fft.fft(win*ref_S[0,:])
  psd_obj_ax = np.fft.fft(win*obj_S[0,:])
  psd_ref_ay = np.fft.fft(win*ref_S[1,:])
  psd_obj_ay = np.fft.fft(win*obj_S[1,:])
  psd_ref_az = np.fft.fft(win*ref_S[2,:])
  psd_obj_az = np.fft.fft(win*obj_S[2,:])
  psd_ref_wx = np.fft.fft(win*ref_S[3,:])
  psd_obj_wx = np.fft.fft(win*obj_S[3,:])
  psd_ref_wy = np.fft.fft(win*ref_S[4,:])
  psd_obj_wy = np.fft.fft(win*obj_S[4,:])
  psd_ref_wz = np.fft.fft(win*ref_S[5,:])
  psd_obj_wz = np.fft.fft(win*obj_S[5,:])

  f = np.linspace(0,fs/2,psd_ref_ax.shape[0]//2)

  plt.subplot(2,3,1)
  plt.plot(f,np.abs(psd_obj_ax[:psd_ref_ax.shape[0]//2]/psd_ref_ax[:psd_ref_ax.shape[0]//2])**2)
  plt.yscale('log')

  plt.subplot(2,3,2)
  plt.plot(f,np.abs(psd_obj_ay[:psd_ref_ax.shape[0]//2]/psd_ref_ay[:psd_ref_ax.shape[0]//2])**2)
  plt.yscale('log')

  plt.subplot(2,3,3)
  plt.plot(f,np.abs(psd_obj_az[:psd_ref_ax.shape[0]//2]/psd_ref_az[:psd_ref_ax.shape[0]//2])**2)
  plt.yscale('log')

  plt.subplot(2,3,4)
  plt.plot(f,np.abs(psd_obj_wx[:psd_ref_ax.shape[0]//2]/psd_ref_wx[:psd_ref_ax.shape[0]//2])**2)
  plt.yscale('log')

  plt.subplot(2,3,5)
  plt.plot(f,np.abs(psd_obj_wy[:psd_ref_ax.shape[0]//2]/psd_ref_wy[:psd_ref_ax.shape[0]//2])**2)
  plt.yscale('log')

  plt.subplot(2,3,6)
  plt.plot(f,np.abs(psd_obj_wz[:psd_ref_ax.shape[0]//2]/psd_ref_wz[:psd_ref_ax.shape[0]//2])**2)
  plt.yscale('log')

  plt.show()