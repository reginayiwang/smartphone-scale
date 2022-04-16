package com.whatthehack.vibroscaleenhanced;

import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Binder;
import android.os.IBinder;
import android.util.Log;
import android.widget.Toast;

import de.siegmar.fastcsv.writer.CsvWriter;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class SensorService extends Service implements SensorEventListener {
    IBinder binder = new SensorBinder();
    private SensorManager sensorManager;
    private Sensor accSensor;
    private Sensor gyroSensor;
    List<String[]> accData = new ArrayList<>();
    List<String[]> gyroData = new ArrayList<>();

    public SensorService() {
    }

    @Override
    public void onCreate() {
        super.onCreate();
        sensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
        accSensor = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        gyroSensor = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE);
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        if(event.sensor.getType()==Sensor.TYPE_ACCELEROMETER){
            accData.add(new String[]{String.valueOf(event.timestamp), String.valueOf(event.values[0]), String.valueOf(event.values[1]), String.valueOf(event.values[2])});
        } else if (event.sensor.getType()==Sensor.TYPE_GYROSCOPE){
            gyroData.add(new String[]{String.valueOf(event.timestamp), String.valueOf(event.values[0]), String.valueOf(event.values[1]), String.valueOf(event.values[2])});
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
        // Required to implement SensorEventListener, but not used here
    }

    @Override
    public IBinder onBind(Intent intent) {
        // Start listening for sensor events
        // 2500 us sets a sampling rate of 400 Hz
        sensorManager.registerListener(this, accSensor, 2500); // pixel3 seems to be limited to 400hz sampling rate or so
        sensorManager.registerListener(this, gyroSensor, 2500);
        return binder;
    }

    public void stopListener() {
        sensorManager.unregisterListener(this);
    }

    /*
     * Saves sensor data to temporary file.
     */
    public File saveFile(String sensor) throws IOException {
        List<String[]> data;
        File file = File.createTempFile(sensor, ".csv");

        data = sensor.equals(getResources().getString(R.string.acc)) ? accData : gyroData;

        try (CsvWriter csv = CsvWriter.builder().build(file.getAbsoluteFile().toPath())) {
            csv.writeRow("Time (s)", "x", "y", "z");
            for (String[] row : data) {
                csv.writeRow(row);
            }
        } catch (final IOException e) {
            Log.e(this.getClass().getName(), e.getMessage());
            Toast.makeText(this, "Could not create file", Toast.LENGTH_LONG).show();
        }
        data.clear();
        return file;
    }

    public class SensorBinder extends Binder {
        public SensorService getSensorService() {
            return SensorService.this;
        }
    }
}