# 🎬 Movie Reservation System (OTP Based)

## 📌 Project Overview
The **Movie Reservation System** is a simple and user-friendly web application that allows users to book movie tickets **without online payment**.

This system is specially designed for users who **do not trust online payments** or feel insecure about payment failures.  
Instead of payment, bookings are confirmed using an **OTP (One Time Password)** system.

---

## ⭐ Key Features

### 🔐 Login & Signup
- User authentication system
- Secure login and signup
- Only logged-in users can book seats

---

### 🎥 Movie Dashboard
- List of available movies
- Movie details (show time, venue, seats)
- Real-time seat availability

---

### ⏳ Seat Hold System (5 Minutes)
- When a user selects a seat:
  - The seat is **held for 5 minutes**
  - During this time, **no other user can book that seat**
- If the user does not complete the booking within 5 minutes:
  - The seat is **automatically released**

✅ Prevents unfair blocking of seats

---

### 🔑 OTP-Based Booking (No Payment Required)
- ❌ No online payment required
- ✅ Booking is confirmed using OTP
- OTP is used as booking verification

This system is ideal for users who:
- Avoid online payments
- Are worried about payment failures

---

### 📖 My Bookings
- Users can view their **previous bookings**
- Shows movie name, venue, time, and seat details
- Booking history is securely stored

---

### ⏰ Venue Reporting Rule (30 Minutes)
- Users must arrive at the venue **30 minutes before the movie start time**
- If the user does not arrive on time:
  - The seat is **automatically released**
  - This prevents loss for the theatre owner

---

## 💡 Why This System Is Unique?
- No online payment system
- OTP-based seat booking
- Smart 5-minute seat hold timer
- Automatic seat release
- Trust-based booking experience

---

## 🛠 Tech Stack (Example)
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python (Flask / Django)
- **Database:** SQLite / MySQL
- **Authentication:** Login + OTP system

---

## 🚀 Future Enhancements
- Admin dashboard
- SMS / Email OTP support
- Improved seat selection UI
- Multiple theatre / venue support

---

## 📄 License
This project is created for **educational, hackathon, and learning purposes**.

---

## 👨‍💻 Developed By
**Yatharth Chouhan**  
Hackathon Project 2025
