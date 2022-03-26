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

public class SensorService extends Service implements SensorEventListener {
    private int counter;
    private String filePrefix;
    private long startTime;
    private SensorManager sensorManager;
    private Sensor accSensor;
    private Sensor gyroSensor;
    private Sensor noGravSensor;
    List<String[]> accData = new ArrayList<>();
    List<String[]> gyroData = new ArrayList<>();
    List<String[]> noGravData = new ArrayList<>();

    public SensorService() {
    }

    @Override
    public void onCreate() {
        super.onCreate();
        sensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
        accSensor = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        gyroSensor = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE);
        noGravSensor = sensorManager.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION);
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        // Start listening for sensor events
        // 2500 us sets a sampling rate of 400 Hz
        counter = intent.getIntExtra("counter", 0);
        filePrefix = intent.getStringExtra("prefix");
        startTime = SystemClock.elapsedRealtimeNanos();
        sensorManager.registerListener(this, accSensor, 2500); // pixel3 seems to be limited to 400hz sampling rate or so
        sensorManager.registerListener(this, gyroSensor, 2500);
        sensorManager.registerListener(this, noGravSensor, 2500);
        return Service.START_NOT_STICKY;
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        // Stop listening for sensor events and save data to file
        sensorManager.unregisterListener(this);
        saveToFile(getResources().getString(R.string.acc));
        saveToFile(getResources().getString(R.string.gyro));
        saveToFile(getResources().getString(R.string.noGrav));
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        // Calculate elapsed time
        double time = (event.timestamp - startTime) * 1e-9;
        DecimalFormat format = (DecimalFormat) NumberFormat.getInstance(Locale.ENGLISH);
        format.applyPattern("0.000000000E0");

        // Add new sensor values to list
        if(event.sensor.getType()==Sensor.TYPE_ACCELEROMETER){
            accData.add(new String[]{format.format(time), String.valueOf(event.values[0]), String.valueOf(event.values[1]), String.valueOf(event.values[2])});
        } else if (event.sensor.getType()==Sensor.TYPE_GYROSCOPE){
            gyroData.add(new String[]{format.format(time), String.valueOf(event.values[0]), String.valueOf(event.values[1]), String.valueOf(event.values[2])});
        } else if(event.sensor.getType()==Sensor.TYPE_LINEAR_ACCELERATION){
            noGravData.add(new String[]{format.format(time), String.valueOf(event.values[0]), String.valueOf(event.values[1]), String.valueOf(event.values[2])});
        }

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
    public void saveToFile(String sensor) {
        if (sensor.equals("accelerometer")) {
            Log.d("acc data", String.valueOf(accData.size()));
            Log.d("Gyro data", String.valueOf(gyroData.size()));
            Log.d("grav data", String.valueOf(noGravData.size()));
        }
        List<String[]> data;
        String filename = filePrefix + sensor + "_" + counter + ".csv";
        File file = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), filename);

        if (sensor.equals(getResources().getString(R.string.acc))) {
            data = accData;
        } else if (sensor.equals(getResources().getString(R.string.gyro))) {
            data = gyroData;
        } else {
            data = noGravData;
        }

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