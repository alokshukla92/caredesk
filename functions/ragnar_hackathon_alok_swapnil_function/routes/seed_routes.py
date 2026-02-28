import logging
import json
from utils.constants import (
    TABLE_CLINICS, TABLE_DOCTORS, TABLE_PATIENTS,
    TABLE_APPOINTMENTS, TABLE_PRESCRIPTIONS,
    ist_today, ist_now,
)
from utils.response import success, error, server_error
from services.auth_service import require_clinic
from datetime import timedelta

logger = logging.getLogger(__name__)


def _delete_all_rows(app, table_name, clinic_id):
    """Delete all rows for a clinic from a table."""
    zcql = app.zcql()
    rows = zcql.execute_query(
        f"SELECT ROWID FROM {table_name} WHERE clinic_id = '{clinic_id}'"
    )
    if rows:
        table = app.datastore().table(table_name)
        for row in rows:
            try:
                table.delete_row(row[table_name]["ROWID"])
            except Exception as e:
                logger.warning(f"Delete failed for {table_name} row: {e}")


def _delete_all_rows_no_clinic(app, table_name):
    """Delete all rows from a table (no clinic_id filter)."""
    zcql = app.zcql()
    rows = zcql.execute_query(f"SELECT ROWID FROM {table_name}")
    if rows:
        table = app.datastore().table(table_name)
        for row in rows:
            try:
                table.delete_row(row[table_name]["ROWID"])
            except Exception as e:
                logger.warning(f"Delete failed for {table_name} row: {e}")


def seed_demo(app, request):
    """POST /api/seed-demo — Clear all data and insert demo data for hackathon."""
    try:
        clinic_id, user = require_clinic(app, request)
        if not clinic_id:
            return error("No clinic found", 403)

        # ── Step 1: Clear existing data for THIS clinic ──
        logger.info("Clearing existing data...")
        _delete_all_rows(app, TABLE_PRESCRIPTIONS, clinic_id)
        _delete_all_rows(app, TABLE_APPOINTMENTS, clinic_id)
        _delete_all_rows(app, TABLE_PATIENTS, clinic_id)
        _delete_all_rows(app, TABLE_DOCTORS, clinic_id)
        logger.info("All existing data cleared.")

        today = ist_now().date()
        today_str = today.isoformat()

        # ── Step 2: Insert Doctors ──
        doctors_data = [
            {
                "name": "Alok Shukla",
                "specialty": "General Medicine",
                "email": "dr.alok@sanjeevani.com",
                "phone": "9876543210",
                "available_from": "09:00",
                "available_to": "17:00",
                "consultation_fee": "500",
                "status": "active",
            },
            {
                "name": "Priya Sharma",
                "specialty": "Cardiology",
                "email": "dr.priya@sanjeevani.com",
                "phone": "9876543211",
                "available_from": "10:00",
                "available_to": "18:00",
                "consultation_fee": "800",
                "status": "active",
            },
            {
                "name": "Rajesh Patel",
                "specialty": "Pediatrics",
                "email": "dr.rajesh@sanjeevani.com",
                "phone": "9876543212",
                "available_from": "09:00",
                "available_to": "14:00",
                "consultation_fee": "600",
                "status": "active",
            },
            {
                "name": "Sneha Gupta",
                "specialty": "Dermatology",
                "email": "dr.sneha@sanjeevani.com",
                "phone": "9876543213",
                "available_from": "11:00",
                "available_to": "19:00",
                "consultation_fee": "700",
                "status": "active",
            },
        ]

        doc_table = app.datastore().table(TABLE_DOCTORS)
        doctor_ids = []
        for doc in doctors_data:
            doc["clinic_id"] = clinic_id
            row = doc_table.insert_row(doc)
            doctor_ids.append(row["ROWID"])
            logger.info(f"Doctor created: {doc['name']} -> ID {row['ROWID']}")

        # ── Step 3: Insert Patients ──
        patients_data = [
            {"name": "Amit Kumar", "phone": "9111111101", "email": "amit.kumar@gmail.com", "age": "32", "gender": "Male", "blood_group": "B+", "medical_history": "Mild hypertension"},
            {"name": "Sunita Devi", "phone": "9111111102", "email": "sunita.devi@gmail.com", "age": "45", "gender": "Female", "blood_group": "O+", "medical_history": "Diabetes Type 2"},
            {"name": "Rahul Verma", "phone": "9111111103", "email": "rahul.verma@gmail.com", "age": "28", "gender": "Male", "blood_group": "A+", "medical_history": "No known allergies"},
            {"name": "Pooja Singh", "phone": "9111111104", "email": "pooja.singh@gmail.com", "age": "35", "gender": "Female", "blood_group": "AB+", "medical_history": "Asthma"},
            {"name": "Vikram Joshi", "phone": "9111111105", "email": "vikram.joshi@gmail.com", "age": "52", "gender": "Male", "blood_group": "O-", "medical_history": "Cholesterol, BP medication"},
            {"name": "Meera Nair", "phone": "9111111106", "email": "meera.nair@gmail.com", "age": "25", "gender": "Female", "blood_group": "B-", "medical_history": "None"},
            {"name": "Arjun Reddy", "phone": "9111111107", "email": "arjun.reddy@gmail.com", "age": "40", "gender": "Male", "blood_group": "A-", "medical_history": "Previous knee surgery"},
            {"name": "Kavita Rao", "phone": "9111111108", "email": "kavita.rao@gmail.com", "age": "60", "gender": "Female", "blood_group": "O+", "medical_history": "Heart condition, diabetes"},
            {"name": "Rohan Mehta", "phone": "9111111109", "email": "rohan.mehta@gmail.com", "age": "8", "gender": "Male", "blood_group": "B+", "medical_history": "Childhood vaccinations up to date"},
            {"name": "Ananya Pillai", "phone": "9111111110", "email": "ananya.pillai@gmail.com", "age": "22", "gender": "Female", "blood_group": "A+", "medical_history": "Skin allergies"},
            {"name": "Deepak Chauhan", "phone": "9111111111", "email": "deepak.c@gmail.com", "age": "55", "gender": "Male", "blood_group": "AB-", "medical_history": "Chronic back pain, slip disc"},
            {"name": "Neha Agarwal", "phone": "9111111112", "email": "neha.a@gmail.com", "age": "30", "gender": "Female", "blood_group": "O+", "medical_history": "Thyroid (hypothyroid)"},
            {"name": "Sanjay Tiwari", "phone": "9111111113", "email": "sanjay.t@gmail.com", "age": "65", "gender": "Male", "blood_group": "B+", "medical_history": "Diabetes, cataract surgery 2024"},
            {"name": "Ritu Saxena", "phone": "9111111114", "email": "ritu.s@gmail.com", "age": "38", "gender": "Female", "blood_group": "A+", "medical_history": "PCOD, migraine"},
            {"name": "Kartik Bhatt", "phone": "9111111115", "email": "kartik.b@gmail.com", "age": "12", "gender": "Male", "blood_group": "O+", "medical_history": "Tonsillitis (recurring)"},
        ]

        pat_table = app.datastore().table(TABLE_PATIENTS)
        patient_ids = []
        for pat in patients_data:
            pat["clinic_id"] = clinic_id
            row = pat_table.insert_row(pat)
            patient_ids.append(row["ROWID"])
            logger.info(f"Patient created: {pat['name']} -> ID {row['ROWID']}")

        # ── Step 4: Insert Appointments ──
        from routes.appointment_routes import _generate_token
        appt_table = app.datastore().table(TABLE_APPOINTMENTS)
        rx_table = app.datastore().table(TABLE_PRESCRIPTIONS)

        def make_appt(doc_idx, pat_idx, date_str, time, status, feedback=None):
            doc_name = doctors_data[doc_idx]["name"]
            token = _generate_token(app, clinic_id, date_str, doc_name)
            row_data = {
                "clinic_id": clinic_id,
                "doctor_id": doctor_ids[doc_idx],
                "patient_id": patient_ids[pat_idx],
                "appointment_date": date_str,
                "appointment_time": time,
                "status": status,
                "token_number": token,
                "notes": "",
                "feedback_score": "",
                "feedback_text": "",
                "feedback_sentiment": "",
                "feedback_keywords": "",
            }
            if feedback:
                row_data["feedback_score"] = str(feedback.get("score", ""))
                row_data["feedback_text"] = feedback.get("text", "")
                row_data["feedback_sentiment"] = feedback.get("sentiment", "")
                row_data["feedback_keywords"] = feedback.get("keywords", "")
            row = appt_table.insert_row(row_data)
            return row["ROWID"]

        def make_rx(appt_id, doc_idx, pat_idx, diagnosis, medicines, advice, follow_up=""):
            rx_table.insert_row({
                "clinic_id": clinic_id,
                "appointment_id": appt_id,
                "doctor_id": doctor_ids[doc_idx],
                "patient_id": patient_ids[pat_idx],
                "diagnosis": diagnosis,
                "medicines": json.dumps(medicines),
                "advice": advice,
                "follow_up_date": follow_up,
                "prescription_url": "",
            })

        # ══════════════════════════════════════════════════════
        #  TODAY'S APPOINTMENTS — Full active day simulation
        # ══════════════════════════════════════════════════════

        # --- COMPLETED (5) with prescriptions + feedback ---
        a1 = make_appt(0, 0, today_str, "09:00", "completed",
            {"score": 5, "text": "Dr. Alok was very thorough and explained everything clearly. Excellent experience!", "sentiment": "positive", "keywords": "thorough,explained,excellent"})
        make_rx(a1, 0, 0, "Viral fever with body aches",
            [{"name": "Paracetamol 650mg", "dosage": "650mg", "morning": True, "afternoon": True, "night": True, "when": "after_meal", "duration": "5 days", "notes": "Take with warm water"},
             {"name": "Cetirizine", "dosage": "10mg", "morning": False, "afternoon": False, "night": True, "when": "after_meal", "duration": "3 days", "notes": ""},
             {"name": "Vitamin C", "dosage": "500mg", "morning": True, "afternoon": False, "night": False, "when": "after_meal", "duration": "10 days", "notes": ""}],
            "Drink plenty of fluids. Rest for 2-3 days. Avoid cold drinks.",
            (today + timedelta(days=5)).isoformat())

        a2 = make_appt(1, 4, today_str, "10:00", "completed",
            {"score": 4, "text": "Good consultation. Dr. Priya addressed all my concerns about BP.", "sentiment": "positive", "keywords": "good,consultation,BP,concerns"})
        make_rx(a2, 1, 4, "Hypertension Grade 1 — BP 150/95",
            [{"name": "Amlodipine", "dosage": "5mg", "morning": True, "afternoon": False, "night": False, "when": "before_meal", "duration": "30 days", "notes": "Take at same time daily"},
             {"name": "Ecosprin", "dosage": "75mg", "morning": False, "afternoon": True, "night": False, "when": "after_meal", "duration": "30 days", "notes": ""}],
            "Low salt diet. Walk 30 mins daily. Monitor BP weekly.",
            (today + timedelta(days=15)).isoformat())

        a3 = make_appt(2, 8, today_str, "09:30", "completed",
            {"score": 5, "text": "Dr. Rajesh is so patient with kids. My son was comfortable throughout.", "sentiment": "positive", "keywords": "patient,kids,comfortable"})
        make_rx(a3, 2, 8, "Seasonal flu with mild throat infection",
            [{"name": "Amoxicillin Syrup", "dosage": "5ml", "morning": True, "afternoon": True, "night": True, "when": "after_meal", "duration": "5 days", "notes": "Shake well before use"},
             {"name": "Paracetamol Drops", "dosage": "0.6ml", "morning": True, "afternoon": False, "night": True, "when": "after_meal", "duration": "3 days", "notes": "Only if fever above 100F"}],
            "Keep child hydrated. Soft diet for 2 days.",
            (today + timedelta(days=7)).isoformat())

        a4 = make_appt(3, 9, today_str, "11:00", "completed",
            {"score": 4, "text": "Dr. Sneha diagnosed my skin issue quickly. Very professional.", "sentiment": "positive", "keywords": "diagnosed,quickly,professional"})
        make_rx(a4, 3, 9, "Contact dermatitis — allergic reaction",
            [{"name": "Betamethasone Cream", "dosage": "Apply thin layer", "morning": True, "afternoon": False, "night": True, "when": "after_meal", "duration": "7 days", "notes": "Apply on affected area only"},
             {"name": "Cetirizine", "dosage": "10mg", "morning": False, "afternoon": False, "night": True, "when": "after_meal", "duration": "5 days", "notes": ""},
             {"name": "Calamine Lotion", "dosage": "As needed", "morning": True, "afternoon": True, "night": True, "when": "after_meal", "duration": "10 days", "notes": "For itch relief"}],
            "Avoid direct contact with irritants. Use cotton clothes. No hot water on affected area.",
            (today + timedelta(days=10)).isoformat())

        a5 = make_appt(0, 10, today_str, "10:00", "completed",
            {"score": 3, "text": "Consultation was okay but had to wait 20 mins past appointment time.", "sentiment": "neutral", "keywords": "wait,okay"})
        make_rx(a5, 0, 10, "Chronic lower back pain — lumbar strain",
            [{"name": "Diclofenac 50mg", "dosage": "50mg", "morning": True, "afternoon": False, "night": True, "when": "after_meal", "duration": "5 days", "notes": "Do not take on empty stomach"},
             {"name": "Thiocolchicoside", "dosage": "4mg", "morning": True, "afternoon": False, "night": True, "when": "after_meal", "duration": "5 days", "notes": "Muscle relaxant"},
             {"name": "Calcium + Vitamin D3", "dosage": "500mg", "morning": False, "afternoon": True, "night": False, "when": "after_meal", "duration": "30 days", "notes": ""}],
            "Physiotherapy recommended. Avoid heavy lifting. Use lumbar belt while sitting.",
            (today + timedelta(days=14)).isoformat())

        # --- IN-CONSULTATION (2) — currently with doctor ---
        make_appt(0, 1, today_str, "11:30", "in-consultation")
        make_appt(1, 11, today_str, "11:00", "in-consultation")

        # --- IN-QUEUE (3) — waiting to see doctor ---
        make_appt(0, 2, today_str, "12:00", "in-queue")
        make_appt(1, 5, today_str, "12:00", "in-queue")
        make_appt(3, 13, today_str, "12:30", "in-queue")

        # --- BOOKED (4) — afternoon appointments ---
        make_appt(0, 3, today_str, "14:00", "booked")
        make_appt(2, 14, today_str, "13:00", "booked")
        make_appt(1, 6, today_str, "15:00", "booked")
        make_appt(3, 12, today_str, "16:00", "booked")

        # --- CANCELLED (2) ---
        make_appt(2, 7, today_str, "10:30", "cancelled")
        make_appt(0, 5, today_str, "09:30", "cancelled")

        # --- NO-SHOW (1) ---
        make_appt(0, 6, today_str, "10:00", "no-show")

        # ══════════════════════════════════════════════════════
        #  YESTERDAY (day -1) — Full completed day
        # ══════════════════════════════════════════════════════
        d1 = (today - timedelta(days=1)).isoformat()

        a_y1 = make_appt(0, 2, d1, "09:30", "completed",
            {"score": 3, "text": "Had to wait a bit but consultation was okay.", "sentiment": "neutral", "keywords": "wait,okay"})
        make_rx(a_y1, 0, 2, "Acute gastritis",
            [{"name": "Pantoprazole", "dosage": "40mg", "morning": True, "afternoon": False, "night": False, "when": "before_meal", "duration": "14 days", "notes": "30 mins before breakfast"},
             {"name": "Domperidone", "dosage": "10mg", "morning": True, "afternoon": True, "night": True, "when": "before_meal", "duration": "5 days", "notes": ""}],
            "Avoid spicy and oily food. No alcohol.", "")

        a_y2 = make_appt(1, 7, d1, "10:30", "completed",
            {"score": 5, "text": "Lifesaver! Dr. Priya caught an irregular heartbeat early. Very grateful.", "sentiment": "positive", "keywords": "lifesaver,irregular heartbeat,grateful"})
        make_rx(a_y2, 1, 7, "Atrial fibrillation — irregular heartbeat detected",
            [{"name": "Warfarin", "dosage": "2mg", "morning": False, "afternoon": False, "night": True, "when": "after_meal", "duration": "30 days", "notes": "INR monitoring required"},
             {"name": "Metoprolol", "dosage": "25mg", "morning": True, "afternoon": False, "night": False, "when": "after_meal", "duration": "30 days", "notes": ""}],
            "Avoid strenuous exercise. Monthly INR check. Echocardiogram recommended.",
            (today + timedelta(days=25)).isoformat())

        make_appt(2, 8, d1, "11:00", "completed",
            {"score": 4, "text": "Good follow up visit for my son.", "sentiment": "positive", "keywords": "follow up,good"})
        make_appt(0, 5, d1, "14:00", "completed")
        make_appt(3, 9, d1, "15:00", "completed",
            {"score": 2, "text": "Clinic was too crowded. Doctor seemed rushed.", "sentiment": "negative", "keywords": "crowded,rushed"})
        make_appt(0, 11, d1, "09:00", "completed",
            {"score": 5, "text": "Dr. Alok is an amazing doctor. Thorough checkup done.", "sentiment": "positive", "keywords": "amazing,thorough,checkup"})
        make_appt(1, 12, d1, "11:30", "completed",
            {"score": 4, "text": "Good heart specialist. Explained ECG report clearly.", "sentiment": "positive", "keywords": "specialist,ECG,explained"})
        make_appt(3, 13, d1, "12:00", "no-show")

        # ══════════════════════════════════════════════════════
        #  DAY -2
        # ══════════════════════════════════════════════════════
        d2 = (today - timedelta(days=2)).isoformat()

        a_d2_1 = make_appt(0, 3, d2, "09:30", "completed",
            {"score": 4, "text": "Very knowledgeable doctor. Recommended!", "sentiment": "positive", "keywords": "knowledgeable,recommended"})
        make_rx(a_d2_1, 0, 3, "Acute bronchial asthma — mild episode",
            [{"name": "Salbutamol Inhaler", "dosage": "2 puffs", "morning": True, "afternoon": False, "night": True, "when": "before_meal", "duration": "As needed", "notes": "Use spacer for better delivery"},
             {"name": "Montelukast", "dosage": "10mg", "morning": False, "afternoon": False, "night": True, "when": "after_meal", "duration": "30 days", "notes": ""}],
            "Avoid dust and smoke. Keep inhaler handy at all times.",
            (today + timedelta(days=20)).isoformat())

        make_appt(1, 4, d2, "11:00", "completed")
        make_appt(0, 0, d2, "14:00", "completed",
            {"score": 5, "text": "Second visit, consistently great service.", "sentiment": "positive", "keywords": "consistent,great service"})
        make_appt(2, 14, d2, "10:00", "completed",
            {"score": 5, "text": "Best pediatrician in Mumbai! Very gentle with children.", "sentiment": "positive", "keywords": "best,pediatrician,gentle,children"})
        make_appt(3, 10, d2, "14:00", "completed")
        make_appt(2, 8, d2, "11:00", "cancelled")

        # ══════════════════════════════════════════════════════
        #  DAY -3
        # ══════════════════════════════════════════════════════
        d3 = (today - timedelta(days=3)).isoformat()

        make_appt(0, 1, d3, "09:00", "completed",
            {"score": 4, "text": "Quick and effective consultation.", "sentiment": "positive", "keywords": "quick,effective"})
        make_appt(3, 5, d3, "12:00", "completed",
            {"score": 5, "text": "Dr. Sneha is fantastic! My skin cleared up within a week.", "sentiment": "positive", "keywords": "fantastic,skin,cleared"})
        make_appt(1, 6, d3, "16:00", "completed",
            {"score": 3, "text": "Average experience. Nothing special.", "sentiment": "neutral", "keywords": "average"})
        make_appt(0, 12, d3, "10:30", "completed")
        make_appt(2, 14, d3, "09:30", "completed",
            {"score": 4, "text": "Regular checkup for my kid. Everything fine.", "sentiment": "positive", "keywords": "regular,checkup,fine"})

        # ══════════════════════════════════════════════════════
        #  DAY -4
        # ══════════════════════════════════════════════════════
        d4 = (today - timedelta(days=4)).isoformat()

        a_d4_1 = make_appt(0, 7, d4, "10:00", "completed",
            {"score": 5, "text": "Dr. Alok took extra time to explain my mother's condition. God bless!", "sentiment": "positive", "keywords": "extra time,explain,condition"})
        make_rx(a_d4_1, 0, 7, "Uncontrolled diabetes with peripheral neuropathy",
            [{"name": "Metformin 500mg", "dosage": "500mg", "morning": True, "afternoon": False, "night": True, "when": "after_meal", "duration": "30 days", "notes": ""},
             {"name": "Glimepiride", "dosage": "1mg", "morning": True, "afternoon": False, "night": False, "when": "before_meal", "duration": "30 days", "notes": "Before breakfast"},
             {"name": "Methylcobalamin", "dosage": "1500mcg", "morning": False, "afternoon": True, "night": False, "when": "after_meal", "duration": "30 days", "notes": "For nerve health"}],
            "Strict sugar control. Daily foot inspection. HbA1c test after 3 months.",
            (today + timedelta(days=30)).isoformat())

        make_appt(2, 8, d4, "09:30", "completed",
            {"score": 5, "text": "Best pediatrician! My child loves visiting Dr. Rajesh.", "sentiment": "positive", "keywords": "best,pediatrician,loves"})
        make_appt(1, 11, d4, "11:00", "completed")
        make_appt(3, 13, d4, "15:00", "completed",
            {"score": 4, "text": "Good treatment for acne. Seeing improvement already.", "sentiment": "positive", "keywords": "good,treatment,acne,improvement"})

        # ══════════════════════════════════════════════════════
        #  DAY -5
        # ══════════════════════════════════════════════════════
        d5 = (today - timedelta(days=5)).isoformat()

        make_appt(0, 0, d5, "09:30", "completed")
        make_appt(1, 4, d5, "11:00", "completed",
            {"score": 4, "text": "Good doctor, friendly staff.", "sentiment": "positive", "keywords": "good,friendly,staff"})
        make_appt(3, 9, d5, "14:00", "completed")
        make_appt(0, 2, d5, "16:00", "no-show")
        make_appt(2, 14, d5, "10:00", "completed",
            {"score": 3, "text": "Doctor was good but waiting area was crowded.", "sentiment": "neutral", "keywords": "good,crowded,waiting"})

        # ══════════════════════════════════════════════════════
        #  DAY -6
        # ══════════════════════════════════════════════════════
        d6 = (today - timedelta(days=6)).isoformat()

        make_appt(0, 5, d6, "10:00", "completed",
            {"score": 1, "text": "Very long wait time. Doctor was late by 45 minutes. Unacceptable!", "sentiment": "negative", "keywords": "long wait,late,unacceptable"})
        make_appt(1, 3, d6, "11:30", "completed")
        make_appt(0, 10, d6, "14:00", "completed",
            {"score": 4, "text": "Came for back pain follow up. Feeling much better now.", "sentiment": "positive", "keywords": "follow up,back pain,better"})
        make_appt(3, 11, d6, "12:00", "completed",
            {"score": 5, "text": "Dr. Sneha is the best dermatologist. Highly recommend!", "sentiment": "positive", "keywords": "best,dermatologist,recommend"})

        # ══════════════════════════════════════════════════════
        #  DAY -7 (one week ago)
        # ══════════════════════════════════════════════════════
        d7 = (today - timedelta(days=7)).isoformat()

        make_appt(0, 6, d7, "09:00", "completed",
            {"score": 4, "text": "Professional and courteous. Good experience overall.", "sentiment": "positive", "keywords": "professional,courteous,good"})
        make_appt(1, 7, d7, "10:30", "completed",
            {"score": 5, "text": "Dr. Priya saved my mother's life. Forever grateful.", "sentiment": "positive", "keywords": "saved,life,grateful"})
        make_appt(2, 8, d7, "11:00", "completed")
        make_appt(0, 12, d7, "14:00", "completed",
            {"score": 2, "text": "Receptionist was rude. Doctor was okay.", "sentiment": "negative", "keywords": "receptionist,rude"})
        make_appt(3, 5, d7, "16:00", "completed",
            {"score": 4, "text": "Skin treatment working well. Happy with results.", "sentiment": "positive", "keywords": "skin,treatment,working,happy"})

        logger.info("Demo data seeded successfully!")

        return success({
            "message": "Demo data seeded successfully!",
            "doctors": len(doctor_ids),
            "patients": len(patient_ids),
            "summary": {
                "today": "17 appointments (5 completed, 2 in-consultation, 3 in-queue, 4 booked, 2 cancelled, 1 no-show)",
                "day_1": "8 appointments (7 completed, 1 no-show)",
                "day_2": "6 appointments (5 completed, 1 cancelled)",
                "day_3": "5 appointments (all completed)",
                "day_4": "4 appointments (all completed)",
                "day_5": "5 appointments (4 completed, 1 no-show)",
                "day_6": "4 appointments (all completed)",
                "day_7": "5 appointments (all completed)",
                "total": "54 appointments across 8 days",
                "prescriptions": "8 detailed prescriptions with medicines",
                "feedback": "30+ feedback entries with sentiment analysis",
            }
        })

    except Exception as e:
        logger.error(f"Seed demo error: {e}")
        import traceback
        return server_error(f"{e}\n{traceback.format_exc()}")


def seed_multi_tenant(app, request):
    """
    POST /api/seed-multi-tenant — Create multiple clinics with full demo data.
    This demonstrates multi-tenant architecture for the hackathon.
    No auth required — creates everything from scratch.
    """
    try:
        zcql = app.zcql()
        clinic_table = app.datastore().table(TABLE_CLINICS)
        doc_table = app.datastore().table(TABLE_DOCTORS)
        pat_table = app.datastore().table(TABLE_PATIENTS)
        appt_table = app.datastore().table(TABLE_APPOINTMENTS)
        rx_table = app.datastore().table(TABLE_PRESCRIPTIONS)

        today = ist_now().date()
        today_str = today.isoformat()

        # ══════════════════════════════════════════
        #  CLINIC DEFINITIONS — 3 different clinics
        # ══════════════════════════════════════════
        clinics_data = [
            {
                "name": "Sanjeevani Mumbai",
                "slug": "sanj-mum",
                "address": "301, Harmony Tower, Andheri West, Mumbai 400058",
                "phone": "022-26281234",
                "email": "admin@sanjeevani-mumbai.com",
                "logo_url": "",
                "doctors": [
                    {"name": "Alok Shukla", "specialty": "General Medicine", "email": "dr.alok@sanjeevani.com", "phone": "9876543210", "available_from": "09:00", "available_to": "17:00", "consultation_fee": "500", "status": "active"},
                    {"name": "Priya Sharma", "specialty": "Cardiology", "email": "dr.priya@sanjeevani.com", "phone": "9876543211", "available_from": "10:00", "available_to": "18:00", "consultation_fee": "800", "status": "active"},
                    {"name": "Rajesh Patel", "specialty": "Pediatrics", "email": "dr.rajesh@sanjeevani.com", "phone": "9876543212", "available_from": "09:00", "available_to": "14:00", "consultation_fee": "600", "status": "active"},
                    {"name": "Sneha Gupta", "specialty": "Dermatology", "email": "dr.sneha@sanjeevani.com", "phone": "9876543213", "available_from": "11:00", "available_to": "19:00", "consultation_fee": "700", "status": "active"},
                ],
                "patients": [
                    {"name": "Amit Kumar", "phone": "9111111101", "email": "amit.kumar@gmail.com", "age": "32", "gender": "Male", "blood_group": "B+", "medical_history": "Mild hypertension"},
                    {"name": "Sunita Devi", "phone": "9111111102", "email": "sunita.devi@gmail.com", "age": "45", "gender": "Female", "blood_group": "O+", "medical_history": "Diabetes Type 2"},
                    {"name": "Rahul Verma", "phone": "9111111103", "email": "rahul.verma@gmail.com", "age": "28", "gender": "Male", "blood_group": "A+", "medical_history": "No known allergies"},
                    {"name": "Pooja Singh", "phone": "9111111104", "email": "pooja.singh@gmail.com", "age": "35", "gender": "Female", "blood_group": "AB+", "medical_history": "Asthma"},
                    {"name": "Vikram Joshi", "phone": "9111111105", "email": "vikram.joshi@gmail.com", "age": "52", "gender": "Male", "blood_group": "O-", "medical_history": "Cholesterol, BP medication"},
                    {"name": "Meera Nair", "phone": "9111111106", "email": "meera.nair@gmail.com", "age": "25", "gender": "Female", "blood_group": "B-", "medical_history": "None"},
                    {"name": "Rohan Mehta", "phone": "9111111109", "email": "rohan.mehta@gmail.com", "age": "8", "gender": "Male", "blood_group": "B+", "medical_history": "Childhood vaccinations up to date"},
                    {"name": "Ananya Pillai", "phone": "9111111110", "email": "ananya.pillai@gmail.com", "age": "22", "gender": "Female", "blood_group": "A+", "medical_history": "Skin allergies"},
                ],
            },
            {
                "name": "LifeCare Clinic Pune",
                "slug": "lifecare-pune",
                "address": "12, Shivaji Nagar, Pune 411005",
                "phone": "020-25671234",
                "email": "admin@lifecare-pune.com",
                "logo_url": "",
                "doctors": [
                    {"name": "Anil Deshmukh", "specialty": "General Medicine", "email": "dr.anil@lifecare.com", "phone": "9822111101", "available_from": "08:00", "available_to": "16:00", "consultation_fee": "400", "status": "active"},
                    {"name": "Swati Kulkarni", "specialty": "Gynecology", "email": "dr.swati@lifecare.com", "phone": "9822111102", "available_from": "10:00", "available_to": "17:00", "consultation_fee": "700", "status": "active"},
                    {"name": "Manoj Joshi", "specialty": "Orthopedics", "email": "dr.manoj@lifecare.com", "phone": "9822111103", "available_from": "09:00", "available_to": "15:00", "consultation_fee": "900", "status": "active"},
                ],
                "patients": [
                    {"name": "Sachin Pawar", "phone": "9222222201", "email": "sachin.p@gmail.com", "age": "42", "gender": "Male", "blood_group": "A+", "medical_history": "Knee pain, old sports injury"},
                    {"name": "Prerna Joshi", "phone": "9222222202", "email": "prerna.j@gmail.com", "age": "29", "gender": "Female", "blood_group": "B+", "medical_history": "PCOD"},
                    {"name": "Ramesh Kulkarni", "phone": "9222222203", "email": "ramesh.k@gmail.com", "age": "58", "gender": "Male", "blood_group": "O+", "medical_history": "Diabetes, knee replacement 2023"},
                    {"name": "Asha Bhosle", "phone": "9222222204", "email": "asha.b@gmail.com", "age": "34", "gender": "Female", "blood_group": "AB+", "medical_history": "Thyroid"},
                    {"name": "Vikas Patil", "phone": "9222222205", "email": "vikas.patil@gmail.com", "age": "45", "gender": "Male", "blood_group": "O-", "medical_history": "Chronic migraine"},
                    {"name": "Neeta Desai", "phone": "9222222206", "email": "neeta.d@gmail.com", "age": "62", "gender": "Female", "blood_group": "B-", "medical_history": "Osteoporosis, vitamin D deficiency"},
                ],
            },
            {
                "name": "MedPlus Dental & ENT Clinic",
                "slug": "medplus-blr",
                "address": "45, Koramangala 4th Block, Bangalore 560034",
                "phone": "080-41231234",
                "email": "admin@medplus-blr.com",
                "logo_url": "",
                "doctors": [
                    {"name": "Karthik Raman", "specialty": "ENT", "email": "dr.karthik@medplus.com", "phone": "9900111101", "available_from": "09:00", "available_to": "17:00", "consultation_fee": "600", "status": "active"},
                    {"name": "Divya Nair", "specialty": "Dental Surgery", "email": "dr.divya@medplus.com", "phone": "9900111102", "available_from": "10:00", "available_to": "19:00", "consultation_fee": "500", "status": "active"},
                ],
                "patients": [
                    {"name": "Arjun Hegde", "phone": "9333333301", "email": "arjun.h@gmail.com", "age": "27", "gender": "Male", "blood_group": "A+", "medical_history": "Wisdom tooth extraction 2024"},
                    {"name": "Lakshmi Iyer", "phone": "9333333302", "email": "lakshmi.i@gmail.com", "age": "50", "gender": "Female", "blood_group": "O+", "medical_history": "Sinusitis (recurring)"},
                    {"name": "Naveen Kumar", "phone": "9333333303", "email": "naveen.k@gmail.com", "age": "35", "gender": "Male", "blood_group": "B+", "medical_history": "Tinnitus"},
                    {"name": "Sneha Rao", "phone": "9333333304", "email": "sneha.rao@gmail.com", "age": "22", "gender": "Female", "blood_group": "AB+", "medical_history": "None"},
                ],
            },
        ]

        results = []

        for clinic_info in clinics_data:
            # Check if clinic slug already exists
            existing = zcql.execute_query(
                f"SELECT ROWID FROM {TABLE_CLINICS} WHERE slug = '{clinic_info['slug']}'"
            )
            if existing and len(existing) > 0:
                cid = existing[0][TABLE_CLINICS]["ROWID"]
                # Clear existing data
                _delete_all_rows(app, TABLE_PRESCRIPTIONS, cid)
                _delete_all_rows(app, TABLE_APPOINTMENTS, cid)
                _delete_all_rows(app, TABLE_PATIENTS, cid)
                _delete_all_rows(app, TABLE_DOCTORS, cid)
            else:
                # Create new clinic
                row = clinic_table.insert_row({
                    "name": clinic_info["name"],
                    "slug": clinic_info["slug"],
                    "address": clinic_info["address"],
                    "phone": clinic_info["phone"],
                    "email": clinic_info["email"],
                    "logo_url": clinic_info.get("logo_url", ""),
                    "admin_user_id": "",
                })
                cid = row["ROWID"]

            # Insert doctors
            doctor_ids = []
            doctors = clinic_info["doctors"]
            for doc in doctors:
                doc["clinic_id"] = cid
                row = doc_table.insert_row(doc)
                doctor_ids.append(row["ROWID"])

            # Insert patients
            patient_ids = []
            patients = clinic_info["patients"]
            for pat in patients:
                pat["clinic_id"] = cid
                row = pat_table.insert_row(pat)
                patient_ids.append(row["ROWID"])

            # Helper to generate tokens
            from routes.appointment_routes import _generate_token

            def _make_appt(doc_idx, pat_idx, date_str, time, status, feedback=None):
                doc_name = doctors[doc_idx]["name"]
                token = _generate_token(app, cid, date_str, doc_name)
                row_data = {
                    "clinic_id": cid,
                    "doctor_id": doctor_ids[doc_idx],
                    "patient_id": patient_ids[pat_idx],
                    "appointment_date": date_str,
                    "appointment_time": time,
                    "status": status,
                    "token_number": token,
                    "notes": "",
                    "feedback_score": "",
                    "feedback_text": "",
                    "feedback_sentiment": "",
                    "feedback_keywords": "",
                }
                if feedback:
                    row_data["feedback_score"] = str(feedback.get("score", ""))
                    row_data["feedback_text"] = feedback.get("text", "")
                    row_data["feedback_sentiment"] = feedback.get("sentiment", "")
                    row_data["feedback_keywords"] = feedback.get("keywords", "")
                row = appt_table.insert_row(row_data)
                return row["ROWID"]

            def _make_rx(appt_id, doc_idx, pat_idx, diagnosis, medicines, advice, follow_up=""):
                rx_table.insert_row({
                    "clinic_id": cid,
                    "appointment_id": appt_id,
                    "doctor_id": doctor_ids[doc_idx],
                    "patient_id": patient_ids[pat_idx],
                    "diagnosis": diagnosis,
                    "medicines": json.dumps(medicines),
                    "advice": advice,
                    "follow_up_date": follow_up,
                    "prescription_url": "",
                })

            # ── Generate appointments per clinic ──
            num_docs = len(doctor_ids)
            num_pats = len(patient_ids)

            # TODAY — active day
            # Completed appointments
            for i in range(min(3, num_docs)):
                pat = i % num_pats
                aid = _make_appt(i, pat, today_str, f"{9+i}:00", "completed",
                    {"score": 4 + (i % 2), "text": f"Good experience with Dr. {doctors[i]['name']}. Very professional.", "sentiment": "positive", "keywords": "good,professional"})
                _make_rx(aid, i, pat, "General checkup — all vitals normal",
                    [{"name": "Multivitamin", "dosage": "1 tablet", "morning": True, "afternoon": False, "night": False, "when": "after_meal", "duration": "30 days", "notes": ""}],
                    "Balanced diet. Regular exercise. Annual blood work recommended.",
                    (today + timedelta(days=30)).isoformat())

            # In-consultation
            if num_docs > 0 and num_pats > 3:
                _make_appt(0, 3, today_str, "11:30", "in-consultation")

            # In-queue
            if num_docs > 1 and num_pats > 4:
                _make_appt(1 % num_docs, 4 % num_pats, today_str, "12:00", "in-queue")
            if num_pats > 5:
                _make_appt(0, 5 % num_pats, today_str, "12:30", "in-queue")

            # Booked
            for i in range(min(2, num_docs)):
                _make_appt(i, (i + 2) % num_pats, today_str, f"{14+i}:00", "booked")

            # Past days — 5 days of history
            for day_offset in range(1, 6):
                d = (today - timedelta(days=day_offset)).isoformat()
                for i in range(min(2, num_docs)):
                    pat = (i + day_offset) % num_pats
                    score = 3 + (day_offset + i) % 3
                    _make_appt(i, pat, d, f"{9+i}:30", "completed",
                        {"score": score, "text": f"Visit went well. Rating {score}/5.", "sentiment": "positive" if score >= 4 else "neutral", "keywords": "visit,well"})

            results.append({
                "clinic": clinic_info["name"],
                "slug": clinic_info["slug"],
                "clinic_id": cid,
                "doctors": len(doctor_ids),
                "patients": len(patient_ids),
            })

            logger.info(f"Multi-tenant seed done for: {clinic_info['name']}")

        return success({
            "message": "Multi-tenant demo data seeded successfully!",
            "clinics": results,
            "total_clinics": len(results),
        })

    except Exception as e:
        logger.error(f"Multi-tenant seed error: {e}")
        import traceback
        return server_error(f"{e}\n{traceback.format_exc()}")
