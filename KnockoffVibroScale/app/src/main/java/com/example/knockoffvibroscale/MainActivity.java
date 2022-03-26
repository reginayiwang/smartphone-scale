package com.example.knockoffvibroscale;

import androidx.appcompat.app.AppCompatActivity;

import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.util.Log;
import android.view.View;
import android.view.inputmethod.InputMethodManager;
import android.widget.ArrayAdapter;
import android.widget.AutoCompleteTextView;

import com.example.knockoffvibroscale.databinding.ActivityMainBinding;

public class MainActivity extends AppCompatActivity implements SaveDialog.ISaveDialog {
    boolean serviceBounded;
    SensorService sensorService;
    ServiceConnection connection = new ServiceConnection() {
        @Override
        public void onServiceDisconnected(ComponentName name) {
            serviceBounded = false;
            sensorService = null;
        }

        @Override
        public void onServiceConnected(ComponentName name, IBinder service) {
            serviceBounded = true;
            SensorService.SensorBinder binder = (SensorService.SensorBinder) service;
            sensorService = binder.getSensorService();
        }
    };

    ActivityMainBinding binding;
    AutoCompleteTextView itemDropdown;
    AutoCompleteTextView amplitudeDropdown;
    SharedPreferences pref;
    SaveDialog dialog;
    private String model;
    private String filePrefix;
    private int counter;
    private String item;
    private String weight;
    private String amplitude;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityMainBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());
        model = Build.MODEL.replace(" ", "");
        dialog = new SaveDialog();

        // Populate dropdown menus
        ArrayAdapter<CharSequence> itemAdapter = ArrayAdapter.createFromResource(this,
                R.array.item_array, android.R.layout.simple_spinner_dropdown_item);
        itemDropdown = (AutoCompleteTextView) binding.item.getEditText();
        itemDropdown.setAdapter(itemAdapter);
        ArrayAdapter<CharSequence> amplitudeAdapter = ArrayAdapter.createFromResource(this,
                R.array.amplitude_array, android.R.layout.simple_spinner_dropdown_item);
        amplitudeDropdown = (AutoCompleteTextView) binding.amplitude.getEditText();
        amplitudeDropdown.setAdapter(amplitudeAdapter);

        // Retrieve previous counter value if it exists
        pref = getPreferences(Context.MODE_PRIVATE);
        counter = pref.getInt(getString(R.string.counter_key), 0);
        binding.counter.getEditText().setText(String.valueOf(counter + 1));
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        SharedPreferences.Editor editor = pref.edit();
        editor.putInt(getString(R.string.counter_key), counter);
        editor.apply();
    }

    public void decrementCounter(View view) {
        int current = Integer.parseInt(binding.counter.getEditText().getText().toString().trim());
        binding.counter.getEditText().setText(String.valueOf(current-1));
    }

    public void incrementCounter(View view) {
        int current = Integer.parseInt(binding.counter.getEditText().getText().toString().trim());
        binding.counter.getEditText().setText(String.valueOf(current+1));
    }

    public void onClickWeigh(View view) {
        if (isValid()) {
            // Move keyboard out of the way
            InputMethodManager imm = (InputMethodManager)getSystemService(Context.INPUT_METHOD_SERVICE);
            imm.hideSoftInputFromWindow(view.getWindowToken(), 0);

            item = String.valueOf(itemDropdown.getText()).trim();
            weight = String.valueOf(binding.weight.getEditText().getText()).trim();
            amplitude = String.valueOf(amplitudeDropdown.getText());
            counter = Integer.parseInt(binding.counter.getEditText().getText().toString().trim());
            filePrefix = model + "_" + item + "_" + weight + "_" + amplitude + "_";

            binding.directions.setText("Wait");

            // Start services
            Vibrator vibrator = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);
            Intent intent = new Intent(getApplicationContext(), SensorService.class);
            intent.putExtra(getResources().getString(R.string.counter), counter);
            intent.putExtra(getResources().getString(R.string.prefix), filePrefix);
            bindService(intent, connection, BIND_AUTO_CREATE);

            // Tell user to place item after 3 seconds
            final Handler handler = new Handler(Looper.getMainLooper());
            handler.postDelayed(() -> binding.directions.setText("Place item"), 3000);

            // Stop vibration and sensor collection after 8.5 seconds
            // This leaves time for the user to place the item
            handler.postDelayed(() -> {
                binding.directions.setText("");
                vibrator.cancel();
                sensorService.stopListener();
                openDialog();
            }, 8500);

            // Vibrate phone for 8.5 seconds
            vibrate(vibrator, amplitude);
        }
    }

    /**
     * Open save dialog
     */
    public void openDialog() {
        SaveDialog saveDialog = new SaveDialog();
        saveDialog.show(getSupportFragmentManager(), "Save Dialog");
    }

    /**
     * Increment counter and save data
     */
    @Override
    public void saveData() {
        sensorService.saveToFile(getResources().getString(R.string.acc));
        sensorService.saveToFile(getResources().getString(R.string.gyro));
        sensorService.saveToFile(getResources().getString(R.string.noGrav));
        binding.counter.getEditText().setText(String.valueOf(counter + 1));
    }

    /**
     * Unbind sensor service
     */
    @Override
    public void stopService() {
        unbindService(connection);
    }

    private void vibrate(Vibrator vibrator, String amplitude) {
        VibrationEffect effect;
        if (amplitude.equals(getResources().getString(R.string.increasing_amp))) {
            effect = VibrationEffect.createWaveform(VibrationSettings.increaseTimes,
                    VibrationSettings.increaseAmps, 0);
        } else if (amplitude.equals(getResources().getString(R.string.high_low))) {
            effect = VibrationEffect.createWaveform(VibrationSettings.highLowTimes,
                    VibrationSettings.highLowAmps, 0);
        } else {
            effect = VibrationEffect.createOneShot(8500, amplitude.equals(getResources()
                    .getString(R.string.high_amp)) ? VibrationSettings.highAmp : VibrationSettings.lowAmp);
        }
        vibrator.vibrate(effect);
    }

    private boolean isValid() {
        boolean valid = true;

        if (itemDropdown.length() == 0) {
            itemDropdown.setError("Item required");
            valid = false;
        } else {
            itemDropdown.setError(null);
        }

        if (binding.weight.getEditText().length() == 0) {
            binding.weight.getEditText().setError("Weight required");
            valid = false;
        } else {
            binding.weight.getEditText().setError(null);
        }

        if (amplitudeDropdown.length() == 0) {
            amplitudeDropdown.setError("Amplitude required");
            valid = false;
        } else {
            amplitudeDropdown.setError(null);
        }

        if (binding.counter.getEditText().length() == 0) {
            binding.counter.getEditText().setError("Counter required");
            valid = false;
        } else {
            binding.counter.getEditText().setError(null);
        }
        return valid;
    }

    private static class VibrationSettings {
        private static int highAmp = 255;
        private static int lowAmp= 100;
        private static long[] increaseTimes = {103, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11,
                11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11,
                11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11,
                11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11,
                11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11,
                11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11,
                11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11,
                11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11,
                11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11,
                11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11,
                11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11,
                11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11,
                11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 103, 2000};
        private static int[] increaseAmps = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36,
                37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57,
                58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78,
                79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99,
                100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116,
                117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133,
                134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,
                151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167,
                168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184,
                185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201,
                202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218,
                219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235,
                236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252,
                253, 254, 255, 0};
        private static long[] highLowTimes = {1500, 3500};
        private static int[] highLowAmps = {highAmp, lowAmp};
    }
 }