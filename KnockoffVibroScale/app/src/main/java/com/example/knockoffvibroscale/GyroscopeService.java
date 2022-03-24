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

public class GyroscopeService extends Service implements SensorEventListener {
    private int counter;
    private String file_prefix;
    private long startTime;
    private SensorManager sensorManager;
    private Sensor sensor;
    List<String[]> data = new ArrayList<>();

    public GyroscopeService() {
    }

    @Override
    public void onCreate() {
        super.onCreate();
        sensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
        sensor = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE);
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {

        counter = intent.getIntExtra("counter", 0);
        file_prefix = intent.getStringExtra("prefix");
        startTime = SystemClock.elapsedRealtimeNanos();
        sensorManager.registerListener(this, sensor, 2500); // What sampling period here?

        return Service.START_NOT_STICKY;
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        sensorManager.unregisterListener(this);
        saveToFile();
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        // Calculate elapsed time
        double time = (event.timestamp - startTime) * 1e-9;
        DecimalFormat format = (DecimalFormat) NumberFormat.getInstance(Locale.ENGLISH);
        format.applyPattern("0.000000000E0");

        // Add new sensor values to list
        data.add(new String[]{format.format(time), String.valueOf(event.values[0]), String.valueOf(event.values[1]), String.valueOf(event.values[2])});
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    /*
     * Saves gyroscope data to file in Downloads folder.
     */
    public void saveToFile() {
        String filename = file_prefix + "gyroscope_" + counter + ".csv";
        File file = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), filename);

        try (CsvWriter csv = CsvWriter.builder().build(file.getAbsoluteFile().toPath())) {
            csv.writeRow("Time (s)", "x", "y", "z");
            for (String[] row : data) {
                csv.writeRow(row);
            }
            Toast.makeText(this, "File saved: " + filename, Toast.LENGTH_LONG).show();
        } catch (final IOException e) {
            Toast.makeText(this, "Could not save file.", Toast.LENGTH_LONG).show();
        }
        data.clear();
    }
}