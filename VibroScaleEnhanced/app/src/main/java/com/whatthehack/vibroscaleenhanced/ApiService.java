package com.whatthehack.vibroscaleenhanced;

import okhttp3.MultipartBody;
import okhttp3.RequestBody;
import retrofit2.Call;
import retrofit2.http.Multipart;
import retrofit2.http.POST;
import retrofit2.http.Part;

public interface ApiService {
    @Multipart
    @POST("predict")
    Call<Weight> predictWeight(
            @Part("food") RequestBody food,
            @Part MultipartBody.Part acc,
            @Part MultipartBody.Part gyro
            );
}