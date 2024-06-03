package com.example.barber

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import android.widget.EditText
import android.widget.Toast
import com.google.firebase.database.FirebaseDatabase
import java.text.SimpleDateFormat
import java.util.*
import android.app.DatePickerDialog
import android.app.TimePickerDialog
import com.google.firebase.database.DatabaseReference


class SecondActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.second_layout)

        val buttonDetails1 = findViewById<Button>(R.id.button4_1)
        val buttonDetails2 = findViewById<Button>(R.id.button4_2)
        val buttonDetails3 = findViewById<Button>(R.id.button4_3)

        buttonDetails1.setOnClickListener {
            // Показати діалогове вікно з інформацією про першого барбера
            val builder = AlertDialog.Builder(this)
            builder.setTitle("Детальна інформація")
            builder.setMessage("Інформація про першого барбера")


            builder.setPositiveButton(android.R.string.ok) { dialog, _ ->
                dialog.dismiss()
            }

            val dialog = builder.create()
            dialog.show()
        }

        buttonDetails2.setOnClickListener {
            // Показати діалогове вікно з інформацією про другого барбера
            val builder = AlertDialog.Builder(this)
            builder.setTitle("Детальна інформація")
            builder.setMessage("Інформація про другого барбера")

            builder.setPositiveButton(android.R.string.ok) { dialog, _ ->
                dialog.dismiss()
            }

            val dialog = builder.create()
            dialog.show()
        }

        buttonDetails3.setOnClickListener {
            // Показати діалогове вікно з інформацією про третього барбера
            val builder = AlertDialog.Builder(this)
            builder.setTitle("Детальна інформація")
            builder.setMessage("Інформація про третього барбера")


            builder.setPositiveButton(android.R.string.ok) { dialog, _ ->
                dialog.dismiss()
            }

            val dialog = builder.create()
            dialog.show()
        }
    }
}

class ThirdActivity : AppCompatActivity() {

    private lateinit var database: DatabaseReference

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.third_layout)

        database = FirebaseDatabase.getInstance().reference

        val editTextName = findViewById<EditText>(R.id.editTextText)
        val editTextPhone = findViewById<EditText>(R.id.editTextPhone)
        val editTextDateTime = findViewById<EditText>(R.id.editTextDateTime)
        val buttonSubmit = findViewById<Button>(R.id.button6)

        val calendar = Calendar.getInstance()

        editTextDateTime.setOnClickListener {
            DatePickerDialog(this, { _, year, month, dayOfMonth ->
                calendar.set(year, month, dayOfMonth)
                TimePickerDialog(this, { _, hourOfDay, minute ->
                    calendar.set(Calendar.HOUR_OF_DAY, hourOfDay)
                    calendar.set(Calendar.MINUTE, minute)
                    val dateFormat = SimpleDateFormat("dd-MM-yyyy HH:mm", Locale.getDefault())
                    editTextDateTime.setText(dateFormat.format(calendar.time))
                }, calendar.get(Calendar.HOUR_OF_DAY), calendar.get(Calendar.MINUTE), true).show()
            }, calendar.get(Calendar.YEAR), calendar.get(Calendar.MONTH), calendar.get(Calendar.DAY_OF_MONTH)).show()
        }

        buttonSubmit.setOnClickListener {
            val name = editTextName.text.toString()
            val phone = editTextPhone.text.toString()
            val dateTime = editTextDateTime.text.toString()

            if (name.isNotEmpty() && phone.isNotEmpty() && dateTime.isNotEmpty()) {
                val bookingId = database.push().key
                bookingId?.let {
                    val booking = Booking(name, phone, dateTime)
                    database.child("bookings").child(it).setValue(booking)
                }
            } else {
                // Handle the case where some fields are empty
            }
        }
    }

    data class Booking(val name: String, val phone: String, val dateTime: String)
}

class FourthActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.fourth_layout)

    }
}