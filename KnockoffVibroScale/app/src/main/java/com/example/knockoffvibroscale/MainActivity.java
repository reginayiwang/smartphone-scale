package com.example.knockoffvibroscale;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Context;
import android.content.Intent;
import android.hardware.SensorEventListener;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.util.Log;
import android.view.View;
import android.widget.TextView;

public class MainActivity extends AppCompatActivity {
    private TextView directions;
    private int counter = 0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        directions = (TextView) findViewById(R.id.directions);
    }

    public void onClickWeigh(View view) {
        directions.setText("WAIT");

        // Start services
        Intent intent = new Intent(getApplicationContext(), AccelerometerService.class);
        Intent gyroIntent = new Intent(getApplicationContext(), GyroscopeService.class);
        Intent noGravityIntent = new Intent(getApplicationContext(), LinearAccelerometerService.class);
        intent.putExtra("counter", counter);
        startService(intent);
        startService(gyroIntent);
        startService(noGravityIntent);

        // Tell user to place item after 3 seconds
        final Handler handler = new Handler(Looper.getMainLooper());
        handler.postDelayed(() -> directions.setText("Place item"), 3000);

        // Stop services after 8.5 seconds
        // This leaves time for the user to place the item
        handler.postDelayed(() -> {
            stopService(new Intent(getApplicationContext(), AccelerometerService.class));
            stopService(new Intent(getApplicationContext(), LinearAccelerometerService.class));
            stopService(new Intent(getApplicationContext(), GyroscopeService.class));
            directions.setText("");
        }, 8500);

        // Vibrate phone for 8.5 seconds
        Vibrator vibrator = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);
        VibrationEffect effect = VibrationEffect.createOneShot(8500, VibrationEffect.DEFAULT_AMPLITUDE);
        vibrator.vibrate(effect);

        counter++;
    }
}