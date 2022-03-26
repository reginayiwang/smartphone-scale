package com.example.knockoffvibroscale;

import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Environment;
import android.os.IBinder;
import android.os.SystemClock;
import android.util.Log;
import android.widget.Toast;

import de.siegmar.fastcsv.writer.CsvWriter;

import java.io.File;
import java.io.IOException;
import java.text.DecimalFormat;
import java.text.NumberFormat;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public class AccelerometerService extends Service implements SensorEventListener {
    private int counter;
    private String file_prefix;
    private long startTime;
    private SensorManager mSensorManager;
    private Sensor mSensor;
    List<String[]> data = new ArrayList<>();

    public AccelerometerService() {
    }

    @Override
    public void onCreate() {
        super.onCreate();
        mSensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
        mSensor = mSensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        // Start listening for sensor events
        // 5000 us sets a sampling rate of 200 Hz
        counter = intent.getIntExtra("counter", 0);
        file_prefix = intent.getStringExtra("prefix");
        startTime = SystemClock.elapsedRealtimeNanos();
        mSensorManager.registerListener(this, mSensor, 2500); // pixel3 seems to be limited to 400hz sampling rate or so

        Log.d("ACC,","test output");
        Log.d("ACC",String.valueOf(mSensor.getMinDelay()));

        return Service.START_NOT_STICKY;
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        // Stop listening for sensor events and save data to file
        mSensorManager.unregisterListener(this);
        saveToFile();
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        data.add(new String[]{String.valueOf(event.timestamp), String.valueOf(event.values[0]), String.valueOf(event.values[1]), String.valueOf(event.values[2])});
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
        // Required to implement SensorEventListener, but not used here
    }

    @Override
    public IBinder onBind(Intent intent) {
        // Required for subclasses of Service but not used here
        return null;
    }

    /*
    * Saves accelerometer data to file in Downloads folder.
    */
    public void saveToFile() {
        String filename = file_prefix + "accelerometer_" + counter + ".csv";
        File file = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), filename);

        try (CsvWriter csv = CsvWriter.builder().build(file.getAbsoluteFile().toPath())) {
            csv.writeRow("Time (s)", "x", "y", "z");
            for (String[] row : data) {
                csv.writeRow(row);
            }
            Toast.makeText(this, "File saved: " + filename, Toast.LENGTH_LONG).show();
        } catch (final IOException e) {
            Log.e(this.getClass().getName(), e.getMessage());
            Toast.makeText(this, "Could not save file.", Toast.LENGTH_LONG).show();
        }
        data.clear();
    }
}