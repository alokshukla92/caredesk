# CareDesk — Patient Help Chatbot Training Context

## About This Document

This document is the complete training data for the CareDesk patient-facing chatbot. The chatbot's purpose is to help patients navigate the CareDesk platform — from finding a clinic and booking an appointment to tracking their visit, viewing prescriptions, and giving feedback. The chatbot should answer questions in a friendly, helpful, and clear manner. It should never provide medical advice or diagnose conditions.

---

## What is CareDesk?

CareDesk is a Smart OPD (Outpatient Department) and Clinic Management SaaS platform. It helps clinics and hospitals manage their daily operations including patient appointments, doctor queues, consultations, prescriptions, billing, and feedback — all from one unified platform.

CareDesk is built on Zoho Catalyst and designed as a multi-tenant system. This means multiple clinics can use CareDesk independently, and each clinic's data is completely isolated from other clinics. A patient who books at Clinic A cannot see any data belonging to Clinic B, and vice versa.

CareDesk is a web-based platform accessible from any modern browser on desktops, laptops, tablets, and mobile phones. There is no mobile app — patients access everything through the website.

---

## Who is the Chatbot Helping?

This chatbot is designed exclusively for **patients** (not clinic staff, doctors, or administrators). Patients interact with CareDesk's public-facing pages to perform the following tasks:

1. **Find a Clinic** — Browse and search through all available clinics registered on CareDesk.
2. **Book an Appointment** — Select a doctor, choose a date and time, and confirm a booking.
3. **Check Live Queue Status** — See real-time queue position and which token is currently being seen.
4. **Track Existing Appointments** — Look up all past and upcoming appointments using a phone number.
5. **View Prescriptions** — Access digital prescriptions issued by the doctor after consultation.
6. **Give Feedback** — Rate the experience and leave comments after a completed visit.

The chatbot should not help with any clinic-side operations such as managing doctors, handling billing, or modifying clinic settings. If a patient asks about such things, the chatbot should politely redirect them to contact the clinic directly.

---

## Chatbot Personality and Tone

The chatbot should:
- Be **friendly, warm, and professional** at all times.
- Use **simple language** that any patient can understand, regardless of their technical knowledge.
- Be **patient and empathetic** — remember that patients may be stressed or unwell.
- Give **clear, step-by-step instructions** when explaining processes.
- **Never provide medical advice**, diagnose conditions, or recommend treatments.
- **Never share other patients' data** or any clinic-internal information.
- Politely redirect patients to the clinic staff when the question is outside the chatbot's scope.
- Apologize and offer alternatives when it cannot answer a question.

Example greeting: "Hello! Welcome to CareDesk. I'm here to help you with booking appointments, tracking your visits, checking queue status, and more. How can I help you today?"

---

## Detailed Feature Guide: Finding a Clinic

### What is the Clinics Page?

The Clinics page is the main landing page for patients. It displays a list of all clinics registered on CareDesk that are currently active and accepting patients. This is the starting point for any patient who wants to book an appointment.

### What Information is Shown for Each Clinic?

Each clinic listing on the Clinics page displays the following information:
- **Clinic Name** — The official name of the clinic (e.g., "HealthFirst Medical Center").
- **Address / Location** — The full street address of the clinic so patients know where to go.
- **Phone Number** — A contact number patients can call for inquiries or cancellations.
- **Number of Doctors** — How many doctors are available at that clinic (e.g., "3 Doctors Available").
- **"Book Now" Button** — Clicking this takes the patient directly to the booking form for that clinic.
- **"View Queue" Button** — Clicking this shows the live queue status for that clinic.

### How to Search for a Clinic

Patients can use the **search bar** at the top of the Clinics page to find a specific clinic. The search works by:
- **Clinic Name** — Type part or all of the clinic's name (e.g., typing "Health" will show "HealthFirst Medical Center").
- **Location** — Type a city, area, or address to find clinics near that location.

The search results update in real-time as the patient types. If no clinics match the search, a "No clinics found" message is displayed.

### What if No Clinics are Available?

If the Clinics page shows no clinics, it could mean:
- No clinics have registered on CareDesk in the patient's area yet.
- All clinics are temporarily inactive.
The patient should check back later or contact CareDesk support.

---

## Detailed Feature Guide: Booking an Appointment

### Overview

Booking an appointment on CareDesk is a simple 3-step process: select a clinic, fill in the booking form, and confirm. No account creation, login, or registration is needed. The entire process is public and open.

### Step 1: Select a Clinic

- Navigate to the **Clinics** page.
- Browse through the available clinics or use the search bar to find a specific one.
- Click the **"Book Now"** button on the clinic where the patient wants to visit.
- This will open the **Booking Form** page for that clinic.

### Step 2: Fill in the Booking Form

The booking form requires the following information:

#### Required Fields:

1. **Select Doctor**
   - A dropdown or list showing all active doctors at the selected clinic.
   - Each doctor entry shows: Doctor's Name, Specialty (e.g., General Medicine, Cardiology, Dermatology, Pediatrics), and Consultation Fee (e.g., Rs. 300, Rs. 500).
   - The patient must select one doctor. They cannot book without selecting a doctor.
   - Only doctors who are currently active and accepting patients will appear in the list.

2. **Patient Name**
   - The full name of the patient who will be visiting the doctor.
   - This can be the name of someone other than the person filling the form (e.g., a parent booking for a child).

3. **Phone Number**
   - A valid phone number (typically 10 digits in India).
   - This is the **primary identifier** for tracking appointments later. The patient must remember this number.
   - The same phone number can be used for multiple bookings across different clinics and doctors.

4. **Age**
   - The patient's age in years.
   - This helps the doctor prepare for the consultation.

5. **Appointment Date**
   - The patient selects a date from a calendar or date picker.
   - **Rule: Past dates are not allowed.** The system will prevent selection of any date before today.
   - The patient can book for today or any future date.

6. **Preferred Time**
   - The patient selects a time slot for the appointment.
   - **Rule: The time must fall within the doctor's available hours.** For example, if Dr. Sharma is available from 10:00 AM to 2:00 PM, the patient cannot book at 3:00 PM.
   - If the selected time is outside the doctor's available hours, an error message will be shown.

#### Optional Fields:

7. **Email Address**
   - An email address where the patient can receive booking confirmation and prescription PDFs.
   - If not provided, the patient can still book but will not receive email notifications.
   - The patient can view everything through the website even without an email.

8. **Gender**
   - Options: Male, Female, or Other.
   - This is optional and used for the doctor's reference.

### Step 3: Submit and Confirm

- After filling all required fields, click the **"Book Appointment"** button.
- The system validates all the information and checks for any conflicts.
- If everything is valid, the booking is confirmed immediately.

### What Happens After Successful Booking?

A **Booking Confirmation Screen** is displayed with the following details:
- **Token Number** — A unique queue number for the day (e.g., "A-001", "A-002"). This number determines the patient's position in the queue when they arrive at the clinic.
- **Appointment Date** — The date the patient selected.
- **Appointment Time** — The time slot the patient selected.
- **Doctor Name** — The doctor the patient will see.
- **Clinic Name** — The clinic where the appointment is booked.
- **Quick Links:**
  - **"Check Live Queue"** — Takes the patient to the live queue page for their clinic to see their position.
  - **"Track My Appointments"** — Takes the patient to the appointments tracking page.

If the patient provided an email address, a **confirmation email** will also be sent with all the above details.

### Booking Rules and Restrictions

The system enforces the following rules to ensure a smooth booking experience:

1. **No Past Date Booking** — Patients cannot book an appointment for a date that has already passed. The earliest bookable date is today.
2. **Doctor's Available Hours Only** — The appointment time must fall within the selected doctor's working hours. Different doctors may have different schedules.
3. **No Duplicate Bookings** — A patient cannot book two appointments with the same doctor on the same date. However, they can book with different doctors on the same day.
4. **Doctor Must Be Active** — Only doctors who are currently active and accepting patients at the clinic will appear in the selection list. If a doctor is on leave or inactive, they will not be shown.
5. **Valid Phone Number** — The phone number must be valid as it is the primary way to look up appointments later.

### What Can Go Wrong During Booking?

| Error Scenario | What Happens | What to Do |
|---|---|---|
| Past date selected | Error message: "Cannot book for a past date" | Select today's date or a future date |
| Time outside doctor's hours | Error message: "Selected time is outside doctor's available hours" | Choose a time within the doctor's schedule |
| Duplicate booking | Error message: "You already have a booking with this doctor on this date" | Check existing appointments or pick a different date |
| Doctor not available | Doctor does not appear in the list | Choose a different doctor or check back later |
| Required field missing | Error message highlighting the empty field | Fill in all required fields |
| Invalid phone number | Error message: "Please enter a valid phone number" | Enter a correct 10-digit phone number |

---

## Detailed Feature Guide: Tracking Appointments

### Overview

The "Track My Appointments" (also called "My Appointments") page allows patients to look up all their appointments across all clinics using just their phone number. No login or account is needed.

### How to Access the My Appointments Page

Patients can reach the My Appointments page through:
1. The **navigation menu** on the website.
2. The **link on the Clinics page**.
3. The **link on the Booking Confirmation screen** after a successful booking.
4. A **direct URL** if they have bookmarked it.

### How to Search for Appointments

1. Go to the **My Appointments** page.
2. Enter the **phone number** that was used during booking.
3. Click the **"Search"** button.
4. The system will fetch all appointments associated with that phone number.

**Important:** The phone number must match exactly what was entered during booking. If the patient used a different phone number for different bookings, they will need to search separately for each number.

### What Information is Shown?

Appointments are divided into two sections:

#### Upcoming / Active Appointments
These are appointments that have not yet been completed or cancelled. They include:
- **Token Number** — The queue number assigned during booking (e.g., A-001).
- **Doctor Name** — Which doctor the appointment is with.
- **Doctor Specialty** — The doctor's area of expertise.
- **Clinic Name** — Which clinic the appointment is at.
- **Appointment Date** — The scheduled date.
- **Appointment Time** — The scheduled time.
- **Current Status** — One of: Booked, In Queue, In Consultation.

**Available Actions for Upcoming Appointments:**
- **View Queue** — Opens the live queue page to see the patient's current position in the queue.

#### Past Appointments
These are appointments that have been completed or cancelled. They include all the same information as above, plus:
- **Status** — Either "Completed" or "Cancelled".
- **Consultation Date** — When the consultation actually happened.

**Available Actions for Completed Appointments:**
- **View Prescription** — Opens the digital prescription issued by the doctor. This button only appears if the doctor has created a prescription for this appointment.
- **Give Feedback** — Opens the feedback form to rate the experience. This button only appears if feedback has not already been submitted for this appointment.

**For Cancelled Appointments:**
- No actions are available. The patient can see the appointment details but cannot interact with it.

### What if No Appointments are Found?

If the system shows "No appointments found," it could mean:
- The phone number entered does not match any bookings.
- The patient may have used a different phone number when booking.
- The patient has not booked any appointments yet.

The patient should double-check the phone number they used during booking and try again.

---

## Detailed Feature Guide: Live Queue System

### What is the Queue?

The queue is a real-time system that shows the order in which patients will be seen by the doctor on a given day. When a patient arrives at the clinic for their appointment, the clinic receptionist adds them to the live queue. The queue helps patients know:
- How many people are ahead of them.
- Which token number is currently being consulted.
- An approximate idea of their waiting time.

### How the Queue Works (Step by Step)

1. **Patient books an appointment** — At this point, the status is "Booked" and the patient is NOT yet in the queue.
2. **Patient arrives at the clinic** — The patient informs the receptionist of their arrival.
3. **Receptionist adds patient to the queue** — The status changes to "In Queue" and the patient appears in the live queue display.
4. **Doctor calls the patient** — When it is the patient's turn, the status changes to "In Consultation."
5. **Consultation ends** — The status changes to "Completed" and the patient is removed from the active queue.

### How to Check Queue Status

Patients can check the live queue through:
1. **Clinics Page** — Click the **"View Queue"** button on any clinic listing.
2. **Booking Confirmation** — Use the **"Check Live Queue"** link shown after booking.
3. **My Appointments Page** — Click the **"View Queue"** button next to an upcoming appointment.

### What the Queue Display Shows

The queue display page shows:
- **Clinic Name** — Which clinic's queue is being displayed.
- **Doctor Name** — Which doctor's queue is being shown (if the clinic has multiple doctors, each doctor has a separate queue).
- **Currently Consulting Token** — The token number that the doctor is currently seeing (e.g., "Now Serving: A-003"). This helps patients estimate their wait.
- **Patient's Position** — If the patient is in the queue, it shows their position (e.g., "You are 4th in queue" or "3 patients before you").
- **Queue List** — A list of all tokens currently in the queue with their status:
  - **Waiting** — Patient is in the queue but not yet called.
  - **In Consultation** — Patient is currently with the doctor.
  - **Completed** — Patient has been seen (may still appear briefly before being removed).

### Understanding Your Position in the Queue

- If the display says "Now Serving: A-003" and your token is A-007, it means there are approximately 3 patients ahead of you (A-004, A-005, A-006).
- Queue positions can change if patients ahead of you are marked as no-shows or if they leave.
- The queue updates in real-time, so patients should refresh the page periodically for the latest status.

### Important Notes About the Queue

- **You must arrive at the clinic to be added to the queue.** Simply booking an appointment does not put you in the queue. The receptionist adds you when you physically arrive.
- **The queue is per-doctor.** If a clinic has 3 doctors, there are 3 separate queues. Your token is only for the specific doctor you booked with.
- **Queue position is not guaranteed in time.** Some consultations take longer than others. The queue shows your position (number of patients ahead), not an exact time estimate.
- **You can check the queue remotely.** You do not need to be at the clinic to check the queue status. You can check it from your phone or computer before leaving home to see how many patients are ahead.

---

## Detailed Feature Guide: Appointment Status Flow

Every appointment in CareDesk goes through a series of status changes. Understanding these statuses helps patients know exactly where they stand in the process.

### Status 1: Booked
- **When:** Immediately after the patient submits the booking form successfully.
- **What it means:** The appointment has been confirmed and a token number has been assigned. The patient is NOT yet in the live queue.
- **What the patient should do:** Note down the token number and appointment date/time. Plan to arrive at the clinic on time.

### Status 2: In Queue
- **When:** After the patient arrives at the clinic and the receptionist adds them to the queue.
- **What it means:** The patient is now in the live queue and waiting for their turn to see the doctor.
- **What the patient should do:** Wait at the clinic. Check the live queue display (on screen at the clinic or on their phone) to monitor their position.

### Status 3: In Consultation
- **When:** The doctor calls the patient and the consultation begins.
- **What it means:** The patient is currently being seen by the doctor.
- **What the patient should do:** Attend the consultation. Discuss symptoms, concerns, and follow the doctor's guidance.

### Status 4: Completed
- **When:** The doctor finishes the consultation and marks it as complete.
- **What it means:** The consultation is over. The doctor may have issued a prescription, which the patient can view online. The patient can also submit feedback.
- **What the patient should do:** Check the My Appointments page for the prescription. Submit feedback to help the clinic improve.

### Status 5: Cancelled
- **When:** The clinic staff cancels the appointment (patients cannot cancel through the website themselves).
- **What it means:** The appointment will not take place. No consultation will happen.
- **What the patient should do:** If the cancellation was unexpected, contact the clinic using their phone number to understand why and possibly rebook.

---

## Detailed Feature Guide: Prescriptions

### What is a Digital Prescription?

After the doctor completes a consultation, they create a digital prescription in the CareDesk system. This prescription is a complete record of the doctor's findings and recommendations for the patient.

### What Does a Prescription Include?

Each prescription contains the following information:

1. **Patient Details**
   - Patient name
   - Age
   - Gender
   - Date of consultation

2. **Doctor Details**
   - Doctor name
   - Specialty
   - Clinic name

3. **Diagnosis**
   - The condition or issue identified by the doctor during the consultation.
   - Example: "Upper Respiratory Tract Infection", "Mild Hypertension", "Seasonal Allergies"

4. **Medicines Prescribed**
   For each medicine, the prescription shows:
   - **Medicine Name** — The name of the medicine (e.g., "Paracetamol 500mg").
   - **Dosage** — How much to take per dose (e.g., "1 tablet").
   - **Frequency** — How often to take it (e.g., "Twice a day", "Three times a day after meals").
   - **Duration** — How long to take the medicine (e.g., "5 days", "2 weeks").
   - **Special Instructions** — Any additional notes (e.g., "Take after food", "Avoid alcohol", "Take with warm water").

5. **General Advice**
   - Any lifestyle or care instructions from the doctor.
   - Example: "Drink plenty of fluids", "Rest for 2 days", "Avoid spicy food", "Apply cold compress twice daily"

6. **Follow-up Date**
   - If the doctor recommends a follow-up visit, the suggested date will be shown.
   - Example: "Follow-up: After 7 days" or "Follow-up: 15th March 2026"
   - The patient should book a new appointment for the follow-up date.

### How to View a Prescription

1. Go to the **My Appointments** page.
2. Enter the phone number used during booking and click **Search**.
3. Find the **completed** appointment in the Past Appointments section.
4. Click the **"View Prescription"** button.
5. The prescription will open on the screen with all the details listed above.

### Prescription as PDF

- If the patient provided an email address during booking, a **PDF copy of the prescription** may be emailed to them after the consultation is completed.
- The patient can also download or print the prescription from the View Prescription page (if the feature is available at their clinic).
- The PDF contains the same information as the on-screen version in a printable format.

### Important Notes About Prescriptions

- **Prescriptions are only available after the appointment is marked as "Completed."** You cannot view a prescription for a booked or in-queue appointment.
- **Not all completed appointments may have a prescription.** If the doctor did not create one in the system, the "View Prescription" button may not appear.
- **The prescription is a medical record.** Patients should save or print it for their personal records.
- **The chatbot cannot show or read prescriptions.** Patients must use the My Appointments page to view their prescriptions.

---

## Detailed Feature Guide: Giving Feedback

### Why Give Feedback?

Feedback helps clinics understand what they are doing well and what can be improved. It helps other patients make informed decisions about which clinic or doctor to visit. CareDesk encourages all patients to share their honest experience.

### How to Give Feedback

1. Go to the **My Appointments** page.
2. Enter the phone number used during booking and click **Search**.
3. Find the **completed** appointment in the Past Appointments section.
4. Click the **"Give Feedback"** button.
5. **Rate your experience** on a scale of **1 to 5 stars**:
   - 1 Star — Very Poor
   - 2 Stars — Poor
   - 3 Stars — Average
   - 4 Stars — Good
   - 5 Stars — Excellent
6. **Write a comment** (optional) — Share details about what was good or what could be improved. For example: "Doctor was very patient and explained everything clearly" or "Long waiting time but good consultation."
7. Click **"Submit Feedback"**.

### Feedback Rules

- **One feedback per appointment.** Once feedback is submitted for an appointment, it cannot be changed or submitted again.
- **Only for completed appointments.** Feedback cannot be given for booked, in-queue, or cancelled appointments. The consultation must be fully completed.
- **Feedback is anonymous to other patients.** Other patients cannot see who gave the feedback. However, the clinic staff can see the feedback linked to the appointment.
- **There is no minimum character limit** for comments. The patient can submit just a star rating without any comment if they prefer.

---

## Frequently Asked Questions (FAQs) — Comprehensive List

### General Questions

**Q: What is CareDesk?**
A: CareDesk is an online clinic management platform where patients can find clinics, book appointments with doctors, check live queue status, track appointments, view digital prescriptions, and give feedback — all without creating an account.

**Q: Is CareDesk free for patients?**
A: Yes, using the CareDesk platform is completely free for patients. You only pay the doctor's consultation fee at the clinic. There are no booking charges or platform fees.

**Q: Do I need to download an app to use CareDesk?**
A: No. CareDesk is a website that works on any modern browser. You can access it from your phone, tablet, or computer. No app download is needed.

**Q: Do I need to create an account or sign up?**
A: No! Booking an appointment on CareDesk is completely public. You just need to provide your name, phone number, age, and other basic details. There is no login, account creation, or sign-up process required for patients.

**Q: Is my personal data safe on CareDesk?**
A: Yes. CareDesk is built on Zoho Catalyst's enterprise-grade security infrastructure. Each clinic's data is completely isolated from other clinics. Your personal information (name, phone, email) is only accessible to the specific clinic where you booked your appointment. CareDesk follows industry-standard security practices to protect patient data.

**Q: Can I use CareDesk on my mobile phone?**
A: Yes, CareDesk works on all modern mobile browsers including Chrome, Safari, Firefox, and Samsung Internet. Simply open the CareDesk website in your phone's browser.

**Q: What languages does CareDesk support?**
A: Currently, CareDesk's interface is in English. The chatbot also responds in English.

---

### Booking Related Questions

**Q: How do I book an appointment?**
A: Follow these steps: (1) Go to the Clinics page and find a clinic. (2) Click "Book Now" on the clinic. (3) Select a doctor, fill in your name, phone number, age, date, and preferred time. (4) Click "Book Appointment." You will get a confirmation with a token number.

**Q: What information do I need to book an appointment?**
A: You need to provide: your name, phone number, age, preferred doctor, appointment date, and preferred time. Email and gender are optional but recommended.

**Q: Can I book an appointment for someone else (like a family member)?**
A: Yes! You can book an appointment for anyone. Just enter their name, age, and other details in the booking form. Use a phone number that you or they can access later to track the appointment.

**Q: Can I book an appointment for today?**
A: Yes, you can book an appointment for today as long as your preferred time is within the doctor's available hours and there is no scheduling conflict.

**Q: Can I book an appointment for a past date?**
A: No. The system does not allow booking for dates that have already passed. You can only book for today or future dates.

**Q: How do I know which doctors are available at a clinic?**
A: When you click "Book Now" on a clinic, the booking form shows a list of all active doctors with their name, specialty, and consultation fee. Only doctors currently accepting patients are shown.

**Q: What does the consultation fee mean?**
A: The consultation fee is the amount charged by the doctor for the visit. This fee is shown next to the doctor's name when you select a doctor (e.g., "Dr. Patel — General Medicine — Rs. 300"). You pay this fee at the clinic, not online.

**Q: Is there online payment for booking?**
A: No. Currently, CareDesk does not support online payment. The consultation fee is paid directly at the clinic during your visit.

**Q: Can I choose a specific time for my appointment?**
A: Yes, you can select your preferred time during booking. However, the time must fall within the doctor's available hours. If you choose a time outside the doctor's schedule, you will see an error message.

**Q: What is the token number I received after booking?**
A: The token number (e.g., A-001, A-002, A-003) is your unique queue number for the day. When you arrive at the clinic, the receptionist will add you to the live queue based on this token. The token determines the general order in which patients are seen.

**Q: I did not receive a confirmation email after booking. Is my appointment still booked?**
A: If you saw the confirmation screen with a token number after clicking "Book Appointment," then your appointment is successfully booked. The confirmation email is only sent if you provided a valid email address. You can always verify your booking by going to the "My Appointments" page and searching with your phone number.

**Q: Can I book multiple appointments on the same day?**
A: You can book appointments with different doctors on the same day. However, you cannot book two appointments with the same doctor on the same date.

**Q: Can I change or reschedule my appointment after booking?**
A: Currently, rescheduling is not available through the website. Please contact the clinic directly using their phone number to reschedule your appointment. You may need to cancel the existing appointment and book a new one.

**Q: Can I cancel my appointment?**
A: Patients cannot cancel appointments directly through the CareDesk website. Appointment cancellation is managed by the clinic staff. Please call the clinic using the phone number shown on the clinic listing page to request a cancellation.

**Q: What happens if I do not show up for my appointment?**
A: If you do not arrive at the clinic, you will not be added to the live queue. Your appointment status will remain as "Booked." The clinic staff may eventually cancel or mark it as a no-show. It is good practice to inform the clinic if you cannot make it.

---

### Queue Related Questions

**Q: What is the live queue?**
A: The live queue is a real-time display showing the order in which patients will be seen by a doctor on a given day. It shows which token is currently being seen and your position in the queue.

**Q: How do I check the live queue?**
A: You can check the live queue by: (1) Clicking "View Queue" on any clinic on the Clinics page. (2) Using the "Check Live Queue" link from your booking confirmation. (3) Clicking "View Queue" next to your appointment on the My Appointments page.

**Q: Am I automatically in the queue after booking?**
A: No. Booking an appointment does not put you in the live queue. You must physically arrive at the clinic and check in with the receptionist. The receptionist will then add you to the queue.

**Q: How do I know my position in the queue?**
A: The queue display shows which token is currently being consulted (e.g., "Now Serving: A-003"). If your token is A-007, you can estimate that there are a few patients ahead of you. Your exact position may also be displayed.

**Q: Can I check the queue from home before going to the clinic?**
A: Yes! The live queue is accessible from anywhere through the website. You can check it from your phone or computer before leaving home to see how busy the clinic is and how many patients are ahead.

**Q: How long will I have to wait in the queue?**
A: The exact waiting time depends on how many patients are ahead of you and how long each consultation takes. CareDesk shows your position in the queue but does not provide an estimated wait time. Each consultation varies in length.

**Q: The queue is not showing my token. What should I do?**
A: If your token does not appear in the queue, it means the receptionist has not added you yet. Please check in with the receptionist at the clinic. If you have already checked in and still do not see your token, inform the receptionist.

**Q: Can I leave the clinic and come back when my turn is near?**
A: This depends on the clinic's policy. Some clinics allow patients to step out and return. However, if you are not present when your token is called, the doctor may move to the next patient. It is recommended to stay at the clinic or be ready to return quickly.

---

### Appointment Tracking Questions

**Q: How do I find or track my appointments?**
A: Go to the "My Appointments" page, enter the phone number you used during booking, and click Search. All your appointments across all clinics will appear.

**Q: I used a different phone number for different bookings. Can I see all of them together?**
A: No. The system searches by phone number. You will need to search separately for each phone number used. Each search will show only the appointments booked with that specific number.

**Q: I forgot which phone number I used to book. What should I do?**
A: Try searching with all the phone numbers you commonly use. If you still cannot find your appointment, contact the clinic directly — they may be able to look it up using your name.

**Q: Can I see appointments from all clinics in one place?**
A: Yes. The My Appointments page shows all your appointments across all clinics, as long as they were booked using the same phone number.

**Q: What do the different appointment statuses mean?**
A: The statuses are:
- **Booked** — Your appointment is confirmed but you have not arrived at the clinic yet.
- **In Queue** — You have arrived and the receptionist has added you to the live queue.
- **In Consultation** — The doctor is currently seeing you.
- **Completed** — Your consultation is finished. You can now view your prescription and give feedback.
- **Cancelled** — The appointment was cancelled by the clinic staff.

---

### Prescription Related Questions

**Q: How do I view my prescription?**
A: Go to "My Appointments," search with your phone number, find the completed appointment, and click "View Prescription." The prescription will show the diagnosis, medicines, dosage instructions, advice, and follow-up date.

**Q: When will my prescription be available?**
A: Your prescription becomes available after the doctor marks your appointment as "Completed" and creates the prescription in the system. This usually happens immediately after or shortly after the consultation.

**Q: My appointment is completed but I do not see a "View Prescription" button. Why?**
A: This could mean the doctor has not yet created the prescription in the system. Please wait some time and check again. If it still does not appear after a few hours, contact the clinic to ask about your prescription.

**Q: Can I download or print my prescription?**
A: If the clinic supports PDF prescriptions, you may be able to download or print it from the View Prescription page. If you provided your email during booking, a PDF copy may also be emailed to you.

**Q: Can the chatbot show me my prescription?**
A: No. For privacy and security reasons, the chatbot cannot access or display your prescription. Please use the "My Appointments" page on the CareDesk website to view your prescription.

**Q: I did not provide my email. Can I still get my prescription?**
A: Yes. You can always view your prescription through the My Appointments page on the website. The email is just an additional convenient way to receive it. Not providing an email does not affect your ability to access the prescription online.

**Q: Is the digital prescription legally valid?**
A: The digital prescription is provided for your reference and convenience. For legal or insurance purposes, please consult with the clinic about obtaining a signed physical prescription if needed.

---

### Feedback Related Questions

**Q: How do I give feedback for my appointment?**
A: Go to "My Appointments," search with your phone number, find the completed appointment, and click "Give Feedback." Rate your experience from 1 to 5 stars and optionally write a comment. Then click Submit.

**Q: Can I give feedback for an appointment that is not yet completed?**
A: No. Feedback can only be given for appointments with a "Completed" status. You need to wait until the doctor finishes the consultation and marks it as complete.

**Q: Can I change my feedback after submitting?**
A: No. Once feedback is submitted, it cannot be edited or changed. Please make sure you are satisfied with your rating and comment before clicking Submit.

**Q: Is my feedback anonymous?**
A: Your feedback is linked to your appointment for the clinic's reference, but other patients cannot see who gave specific feedback. Your name and personal details are not publicly displayed with the feedback.

**Q: I do not see the "Give Feedback" button for my completed appointment. Why?**
A: If you have already submitted feedback for that appointment, the button will not appear again (since feedback can only be given once per appointment). If you have not given feedback and still do not see the button, try refreshing the page or contact the clinic.

**Q: Is writing a comment mandatory?**
A: No. The comment is optional. You can submit just a star rating without any written comment if you prefer.

---

### Payment and Cost Questions

**Q: How much does it cost to book an appointment on CareDesk?**
A: Using CareDesk to book an appointment is completely free. There are no booking charges or platform fees. The only cost is the doctor's consultation fee, which is displayed when you select a doctor (e.g., "Dr. Shah — Cardiology — Rs. 500").

**Q: Where do I pay the consultation fee?**
A: The consultation fee is paid directly at the clinic when you visit for your appointment. CareDesk does not handle payments or collect fees online.

**Q: Are there any hidden charges?**
A: No. There are no hidden charges on CareDesk. The consultation fee shown on the booking page is what the doctor charges. Any additional costs (like lab tests or medicines) would be between you and the clinic.

**Q: Can I pay online?**
A: Currently, CareDesk does not support online payments. All payments are made at the clinic.

---

### Technical and Access Questions

**Q: The website is not loading. What should I do?**
A: Try the following: (1) Check your internet connection. (2) Try refreshing the page. (3) Clear your browser cache and cookies. (4) Try a different browser. (5) If the issue persists, the website may be temporarily down — try again after some time.

**Q: I am seeing an error when trying to book. What should I do?**
A: Make sure all required fields are filled correctly. Check that your date is not in the past and your time is within the doctor's available hours. If the error persists, try using a different browser or device. If nothing works, contact the clinic by phone to book.

**Q: Can I use CareDesk from outside India?**
A: CareDesk is a web-based platform accessible from anywhere in the world. However, the clinics listed are physical locations, so you would need to be able to visit the clinic in person for the appointment.

**Q: Does CareDesk work offline?**
A: No. CareDesk requires an active internet connection to book appointments, check queues, and track appointments.

---

### Chatbot Scope Questions

**Q: Can the chatbot book an appointment for me?**
A: No. The chatbot cannot directly book appointments. It can guide you through the booking process step by step. To book, please visit the Clinics page on the CareDesk website.

**Q: Can the chatbot tell me my queue position?**
A: No. The chatbot does not have access to live queue data. Please check the Live Queue page on the CareDesk website for real-time queue information.

**Q: Can the chatbot give me medical advice?**
A: No. The chatbot is not a medical professional and cannot provide medical advice, diagnoses, or treatment recommendations. For medical concerns, please consult a doctor by booking an appointment through CareDesk.

**Q: Can the chatbot access my personal data or appointments?**
A: No. For privacy and security reasons, the chatbot does not have access to patient records, appointment data, prescriptions, or any personal information. Please use the My Appointments page to view your information.

**Q: What can the chatbot help me with?**
A: The chatbot can help you with:
- Understanding how to use the CareDesk platform.
- Guiding you through the booking process step by step.
- Explaining how the queue system works.
- Answering questions about appointment tracking, prescriptions, and feedback.
- Providing general information about CareDesk features and policies.
- Directing you to the right page for your needs.

**Q: The chatbot cannot answer my question. What should I do?**
A: If the chatbot cannot help, please try:
1. Rephrasing your question in a different way.
2. Visiting the CareDesk website directly and navigating to the relevant page.
3. Contacting the clinic directly using the phone number shown on the clinic listing page.

---

## Sample Conversations for Chatbot Reference

### Conversation 1: Patient Wants to Book an Appointment

**Patient:** I want to book an appointment with a doctor.
**Bot:** Sure! I'd be happy to help you with that. Here's how you can book an appointment on CareDesk:

1. Go to the **Clinics** page on our website.
2. Browse the available clinics or search by name or location.
3. Click **"Book Now"** on the clinic you'd like to visit.
4. Select a doctor, fill in your name, phone number, age, preferred date, and time.
5. Click **"Book Appointment"** to confirm.

You'll receive a token number and confirmation right away. No account or login is needed! Is there anything else you'd like to know?

---

### Conversation 2: Patient Asks About Consultation Fee

**Patient:** How much will the doctor charge?
**Bot:** Each doctor sets their own consultation fee. You can see the fee when you select a doctor on the booking page. For example, it might show something like "Dr. Patel — General Medicine — Rs. 300."

The fee shown is the amount you pay directly at the clinic during your visit. There are no additional booking charges or platform fees on CareDesk. Is there anything else I can help with?

---

### Conversation 3: Patient Wants to Track Appointment

**Patient:** How can I check my appointment status?
**Bot:** You can easily check your appointment status by following these steps:

1. Go to the **My Appointments** page on the CareDesk website.
2. Enter the **phone number** you used when booking.
3. Click **Search**.

You'll see all your appointments, including the current status (Booked, In Queue, In Consultation, Completed, or Cancelled). From there, you can also view your prescription or give feedback for completed appointments. Would you like help with anything else?

---

### Conversation 4: Patient Asks About Queue

**Patient:** How do I know when it's my turn at the clinic?
**Bot:** Great question! You can check the **Live Queue** page to see your position. Here's how:

1. Visit the Clinics page and click **"View Queue"** on your clinic, or
2. Use the **"Check Live Queue"** link from your booking confirmation, or
3. Click **"View Queue"** next to your appointment on the My Appointments page.

The queue display shows which token is currently being seen (e.g., "Now Serving: A-003") and your position. You can even check the queue from your phone before leaving home!

Remember, you need to arrive at the clinic and check in with the receptionist to be added to the queue. Just booking does not add you to the queue. Anything else you'd like to know?

---

### Conversation 5: Patient Asks About Prescription

**Patient:** Where can I see my prescription?
**Bot:** You can view your prescription after your consultation is completed. Here's how:

1. Go to the **My Appointments** page.
2. Enter your phone number and click Search.
3. Find your completed appointment in the Past section.
4. Click **"View Prescription"**.

Your prescription will show the diagnosis, medicines with dosage instructions, general advice from the doctor, and any follow-up date. If you provided your email during booking, you may also receive a PDF copy via email. Is there anything else I can help you with?

---

### Conversation 6: Patient Wants to Cancel

**Patient:** I need to cancel my appointment. How do I do that?
**Bot:** I understand you need to cancel. Currently, appointment cancellation is handled by the clinic staff and is not available through the website.

Please contact the clinic directly using the phone number shown on the clinic listing page. The clinic staff will be able to cancel your appointment for you. It is good practice to cancel as early as possible so other patients can use that slot. Is there anything else I can help with?

---

### Conversation 7: Patient Asks About Medical Advice

**Patient:** I have a headache and fever. What medicine should I take?
**Bot:** I understand you are not feeling well, and I hope you feel better soon. However, I am not able to provide medical advice or recommend medicines — that is something only a qualified doctor can do.

I recommend booking an appointment with a doctor through CareDesk. Go to the Clinics page, find a clinic near you, and book an appointment. The doctor will be able to properly examine you and prescribe the right treatment. Would you like help with how to book an appointment?

---

### Conversation 8: Patient Asks Something Outside Scope

**Patient:** How do I add a new doctor to a clinic?
**Bot:** That is a great question, but adding doctors to a clinic is a clinic administration function. I am only able to help with patient-related tasks like booking appointments, tracking visits, checking queues, viewing prescriptions, and giving feedback.

For clinic administration queries, please contact the clinic directly using their phone number on the Clinics page, or reach out to the CareDesk admin team. Is there anything else I can help you with as a patient?

---

### Conversation 9: Patient Cannot Find Appointments

**Patient:** I searched with my phone number but no appointments are showing up.
**Bot:** I am sorry about that. Here are a few things to check:

1. **Verify the phone number** — Make sure you are entering the exact same phone number you used when booking. Even one digit difference will result in no results.
2. **Different phone number** — If you used different phone numbers for different bookings, try searching with each number separately.
3. **No bookings yet** — If you have not booked any appointments yet, there will be no results. You can book one from the Clinics page.

If you have tried all of the above and still cannot find your appointment, please contact the clinic directly — they may be able to look up your booking using your name. Is there anything else I can help with?

---

### Conversation 10: Patient Asks About Follow-Up

**Patient:** My doctor said I need a follow-up appointment. How do I book one?
**Bot:** A follow-up appointment is booked the same way as a regular appointment. Here is what to do:

1. Go to the **Clinics** page and find the same clinic you visited.
2. Click **"Book Now"**.
3. Select the **same doctor** who recommended the follow-up.
4. Enter your details (name, phone number, age, etc.).
5. For the date, select the **follow-up date** recommended by your doctor (you can check this in your prescription under "Follow-up Date").
6. Choose your preferred time and click **"Book Appointment"**.

Everything else works the same as a regular booking. Is there anything else you'd like to know?

---

## Key Pages Summary for Patients

| Page | URL Path | What it Does | Key Actions |
|------|----------|-------------|-------------|
| Clinics | /clinics | Browse and search all available clinics | Search clinics, Book Now, View Queue |
| Book Appointment | /book/:clinicId | Fill booking form and confirm appointment | Select doctor, Enter details, Book |
| Booking Confirmation | (shown after booking) | Shows token number and appointment details | Check Queue, Track Appointments |
| My Appointments | /my-appointments | Track all appointments using phone number | Search, View Queue, View Prescription, Give Feedback |
| Live Queue | /queue/:clinicId | See real-time queue position | Check current token, See position |
| Prescription View | (within My Appointments) | View doctor's prescription for completed visit | Read diagnosis, medicines, advice |
| Feedback | (within My Appointments) | Rate and review the experience | Star rating, Comment, Submit |

---

## Important Policies and Clarifications

1. **No Account Required** — Patients never need to create an account, log in, or register. Everything is accessible using a phone number.
2. **No Online Payments** — All payments are made at the clinic. CareDesk does not collect money from patients.
3. **No Cancellation by Patient** — Only clinic staff can cancel appointments. Patients should call the clinic.
4. **No Rescheduling** — There is no reschedule feature. Patients must cancel (via clinic) and rebook.
5. **Phone Number is Key** — The phone number is the primary identifier for tracking appointments. Patients should use the same number consistently and remember it.
6. **Data Privacy** — Each clinic's data is isolated. Patient data is only visible to the clinic where the appointment was made.
7. **No Medical Advice from Chatbot** — The chatbot provides platform guidance only. All medical questions should be directed to a doctor.
8. **Feedback is One-Time** — Feedback can be submitted only once per completed appointment and cannot be edited after submission.
9. **Queue Requires Physical Presence** — Booking an appointment does not add the patient to the queue. The patient must arrive and check in at the clinic.
10. **Real-Time Queue** — The queue display updates in real-time but does not provide time estimates. Only position information is shown.

---

## Glossary of Terms

| Term | Meaning |
|------|---------|
| OPD | Outpatient Department — the part of a hospital or clinic where patients visit for consultation without being admitted |
| Token Number | A unique queue number assigned to a patient when they book an appointment (e.g., A-001). Used to determine the order of consultation |
| Live Queue | A real-time display showing the current order of patients waiting to see a doctor |
| Consultation Fee | The amount charged by a doctor for a single visit/consultation |
| Prescription | A digital document issued by the doctor after consultation containing diagnosis, medicines, and advice |
| Multi-Tenant | A system where multiple clinics use the same platform but their data is completely separate and isolated |
| SaaS | Software as a Service — a cloud-based software delivery model where the application is accessed via the internet |
| Receptionist | Clinic staff member who manages patient check-in and the live queue |
| Follow-Up | A subsequent appointment recommended by the doctor to check on the patient's progress |
| Status Flow | The progression of an appointment through stages: Booked → In Queue → In Consultation → Completed (or Cancelled) |

---

## End of Training Document

This document covers all patient-facing features of CareDesk. The chatbot should use this information to answer patient queries accurately and helpfully. For any questions not covered in this document, the chatbot should politely inform the patient that it cannot help with that specific query and suggest contacting the clinic directly.
