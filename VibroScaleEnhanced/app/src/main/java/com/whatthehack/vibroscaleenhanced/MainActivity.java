package com.whatthehack.vibroscaleenhanced;

import androidx.appcompat.app.AppCompatActivity;

import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.os.Bundle;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.view.View;
import android.view.inputmethod.InputMethodManager;
import android.widget.ArrayAdapter;
import android.widget.AutoCompleteTextView;
import android.widget.Toast;

import com.whatthehack.vibroscaleenhanced.databinding.ActivityMainBinding;

import java.io.File;

import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.RequestBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class MainActivity extends AppCompatActivity {
    ActivityMainBinding binding;
    AutoCompleteTextView itemDropdown;
    private String item;
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

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityMainBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        binding.loading.hide();
        // Populate dropdown menus
        ArrayAdapter<CharSequence> itemAdapter = ArrayAdapter.createFromResource(this,
                R.array.item_array, android.R.layout.simple_spinner_dropdown_item);
        itemDropdown = (AutoCompleteTextView) binding.item.getEditText();
        itemDropdown.setAdapter(itemAdapter);
    }

    public void reset(View view) {
        binding.weight.setText("");
        binding.weighButton.setEnabled(true);
        binding.reset.setVisibility(View.GONE);
    }

    public void onClickWeigh(View view) {
        if (isValid()) {
            // Move keyboard out of the way
            InputMethodManager imm = (InputMethodManager) getSystemService(Context.INPUT_METHOD_SERVICE);
            imm.hideSoftInputFromWindow(view.getWindowToken(), 0);

            binding.weighButton.setEnabled(false);

            item = String.valueOf(itemDropdown.getText()).trim();

            binding.directions.setText("Wait");

            // Start services
            Vibrator vibrator = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);
            Intent intent = new Intent(getApplicationContext(), SensorService.class);
            bindService(intent, connection, BIND_AUTO_CREATE);

            // Tell user to place item after 3 seconds
            final Handler handler = new Handler(Looper.getMainLooper());
            handler.postDelayed(() -> binding.directions.setText("Place item"), 3000);

            // Stop vibration and sensor collection after 8.1 seconds
            // This leaves time for the user to place the item
            handler.postDelayed(() -> {
                binding.directions.setText("");
                vibrator.cancel();
                sensorService.stopListener();
                try {
                    File accData = sensorService.saveFile(getString(R.string.acc));
                    File gyroData = sensorService.saveFile(getString(R.string.gyro));
                    getWeight(accData, gyroData);
                } catch (Exception e) {
                    Toast.makeText(this, "Could not get weight", Toast.LENGTH_LONG).show();
                }
                unbindService(connection);
            }, 8100);

            // Vibrate phone for 8.5 seconds
            VibrationEffect effect = VibrationEffect.createOneShot(8100, 255);
            vibrator.vibrate(effect);
        }
    }

    public void getWeight(File accData, File gyroData) {
        binding.loading.show();
        ApiService service = ServiceGenerator.createService(ApiService.class);
        RequestBody food = RequestBody.create(okhttp3.MultipartBody.FORM, item);
        MultipartBody.Part accBody = prepFileBody(getString(R.string.acc_key), accData);
        MultipartBody.Part gyroBody = prepFileBody(getString(R.string.gyro_key), gyroData);
        Call<Weight> call = service.predictWeight(food, accBody, gyroBody);
        call.enqueue(new Callback<Weight>() {
            @Override
            public void onResponse(Call<Weight> call,
                                   Response<Weight> response) {
                String res = response.body().weight;
                int weight = (int) Double.parseDouble(res.substring(1, res.length()-1));
                binding.weight.setText(weight + " g");
                binding.loading.hide();
                binding.reset.setVisibility(View.VISIBLE);
            }

            @Override
            public void onFailure(Call<Weight> call, Throwable t) {
                Toast.makeText(getApplicationContext(), "Request Error: " + t.getMessage(), Toast.LENGTH_LONG).show();
                binding.loading.hide();
                reset(binding.reset);
            }
        });
    }

    private MultipartBody.Part prepFileBody(String name, File file) {
        RequestBody requestFile = RequestBody.create(MediaType.parse(getString(R.string.csv_type)), file);
        return MultipartBody.Part.createFormData(name, file.getName(), requestFile);
    }

    private boolean isValid() {
        boolean valid = true;

        if (itemDropdown.length() == 0) {
            itemDropdown.setError("Item required");
            valid = false;
        } else {
            itemDropdown.setError(null);
        }
        return valid;
    }
}