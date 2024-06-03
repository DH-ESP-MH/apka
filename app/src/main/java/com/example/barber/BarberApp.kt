package com.example.barber

import android.app.Application
import com.google.firebase.database.FirebaseDatabase

class BarberApp : Application() {
    override fun onCreate() {
        super.onCreate()
        FirebaseDatabase.getInstance().setPersistenceEnabled(true)
    }
}