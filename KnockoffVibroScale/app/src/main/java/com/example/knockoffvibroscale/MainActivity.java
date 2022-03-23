package com.example.knockoffvibroscale;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Context;
import android.content.Intent;
import android.hardware.SensorEventListener;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.util.Log;
import android.view.View;
import android.view.inputmethod.InputMethodManager;
import android.widget.ArrayAdapter;
import android.widget.AutoCompleteTextView;
import android.widget.EditText;
import android.widget.TextView;

import com.example.knockoffvibroscale.databinding.ActivityMainBinding;

public class MainActivity extends AppCompatActivity {
    ActivityMainBinding binding;
    AutoCompleteTextView itemDropdown;
    AutoCompleteTextView amplitudeDropdown;
    EditText counterInput;
    private String model;
    private String file_prefix;
    private int counter = 0;
    private String item;
    private String weight;
    private String amplitude;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityMainBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());
        model = Build.MODEL.replace(" ", "");

        // Populate dropdown menus
        ArrayAdapter<CharSequence> itemAdapter = ArrayAdapter.createFromResource(this,
                R.array.item_array, android.R.layout.simple_spinner_dropdown_item);
        itemDropdown = (AutoCompleteTextView) binding.item.getEditText();
        itemDropdown.setAdapter(itemAdapter);
        ArrayAdapter<CharSequence> amplitudeAdapter = ArrayAdapter.createFromResource(this,
                R.array.amplitude_array, android.R.layout.simple_spinner_dropdown_item);
        amplitudeDropdown = (AutoCompleteTextView) binding.amplitude.getEditText();
        amplitudeDropdown.setAdapter(amplitudeAdapter);

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
            file_prefix = model + "_" + item + "_" + weight + "_" + amplitude + "_";

            binding.directions.setText("Wait");

            // Start services
            Intent accIntent = new Intent(getApplicationContext(), AccelerometerService.class);
            Intent gyroIntent = new Intent(getApplicationContext(), GyroscopeService.class);
            Intent noGravityIntent = new Intent(getApplicationContext(), LinearAccelerometerService.class);
            accIntent.putExtra("counter", counter);
            gyroIntent.putExtra("counter", counter);
            noGravityIntent.putExtra("counter", counter);
            accIntent.putExtra("prefix", file_prefix);
            gyroIntent.putExtra("prefix", file_prefix);
            noGravityIntent.putExtra("prefix", file_prefix);
            startService(accIntent);
            startService(gyroIntent);
            startService(noGravityIntent);

            // Tell user to place item after 3 seconds
            final Handler handler = new Handler(Looper.getMainLooper());
            handler.postDelayed(() -> binding.directions.setText("Place item"), 3000);

            // Stop services after 8.5 seconds
            // This leaves time for the user to place the item
            handler.postDelayed(() -> {
                stopService(new Intent(getApplicationContext(), AccelerometerService.class));
                stopService(new Intent(getApplicationContext(), LinearAccelerometerService.class));
                stopService(new Intent(getApplicationContext(), GyroscopeService.class));
                binding.directions.setText("");
                binding.counter.getEditText().setText(String.valueOf(counter + 1));
            }, 8500);

            // Vibrate phone for 8.5 seconds
            Vibrator vibrator = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);
            VibrationEffect effect = VibrationEffect.createOneShot(8500, amplitude.equals("High") ? 255 : 100);
            vibrator.vibrate(effect);

        }
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
 }