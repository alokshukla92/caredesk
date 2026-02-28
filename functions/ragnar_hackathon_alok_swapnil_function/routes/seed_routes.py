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


def seed_demo(app, request):
    """POST /api/seed-demo — Clear all data and insert demo data for hackathon."""
    try:
        clinic_id, user = require_clinic(app, request)
        if not clinic_id:
            return error("No clinic found", 403)

        # ── Step 1: Clear existing data (order matters for FK) ──
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
            {"name": "Amit Kumar", "phone": "9111111101", "email": "amit@gmail.com", "age": "32", "gender": "Male", "blood_group": "B+", "medical_history": "Mild hypertension"},
            {"name": "Sunita Devi", "phone": "9111111102", "email": "sunita@gmail.com", "age": "45", "gender": "Female", "blood_group": "O+", "medical_history": "Diabetes Type 2"},
            {"name": "Rahul Verma", "phone": "9111111103", "email": "rahul.v@gmail.com", "age": "28", "gender": "Male", "blood_group": "A+", "medical_history": "No known allergies"},
            {"name": "Pooja Singh", "phone": "9111111104", "email": "pooja.s@gmail.com", "age": "35", "gender": "Female", "blood_group": "AB+", "medical_history": "Asthma"},
            {"name": "Vikram Joshi", "phone": "9111111105", "email": "vikram.j@gmail.com", "age": "52", "gender": "Male", "blood_group": "O-", "medical_history": "Cholesterol, BP medication"},
            {"name": "Meera Nair", "phone": "9111111106", "email": "meera.n@gmail.com", "age": "25", "gender": "Female", "blood_group": "B-", "medical_history": "None"},
            {"name": "Arjun Reddy", "phone": "9111111107", "email": "arjun.r@gmail.com", "age": "40", "gender": "Male", "blood_group": "A-", "medical_history": "Previous knee surgery"},
            {"name": "Kavita Rao", "phone": "9111111108", "email": "kavita.r@gmail.com", "age": "60", "gender": "Female", "blood_group": "O+", "medical_history": "Heart condition, diabetes"},
            {"name": "Rohan Mehta", "phone": "9111111109", "email": "rohan.m@gmail.com", "age": "8", "gender": "Male", "blood_group": "B+", "medical_history": "Childhood vaccinations up to date"},
            {"name": "Ananya Pillai", "phone": "9111111110", "email": "ananya.p@gmail.com", "age": "22", "gender": "Female", "blood_group": "A+", "medical_history": "Skin allergies"},
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
        appt_ids = []

        # Helper
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

        # Helper for prescriptions
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

        # ──────────── TODAY'S APPOINTMENTS ────────────
        # 3 Completed (with prescriptions + feedback)
        a1 = make_appt(0, 0, today_str, "09:30", "completed",
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
             {"name": "Paracetamol Drops", "dosage": "0.6ml", "morning": True, "afternoon": False, "night": True, "when": "after_meal", "duration": "3 days", "notes": "Only if fever above 100°F"}],
            "Keep child hydrated. Soft diet for 2 days.",
            (today + timedelta(days=7)).isoformat())

        # 1 In-Consultation
        make_appt(0, 1, today_str, "11:00", "in-consultation")

        # 2 In-Queue
        make_appt(1, 5, today_str, "11:30", "in-queue")
        make_appt(3, 9, today_str, "11:30", "in-queue")

        # 3 Booked (upcoming)
        make_appt(0, 2, today_str, "14:00", "booked")
        make_appt(3, 3, today_str, "14:30", "booked")
        make_appt(1, 6, today_str, "15:00", "booked")

        # 1 Cancelled
        make_appt(2, 7, today_str, "10:30", "cancelled")

        # 1 No-show
        make_appt(0, 6, today_str, "10:00", "no-show")

        # ──────────── YESTERDAY (day-1) ────────────
        d1 = (today - timedelta(days=1)).isoformat()
        a_y1 = make_appt(0, 2, d1, "09:30", "completed",
            {"score": 3, "text": "Had to wait a bit but consultation was okay.", "sentiment": "neutral", "keywords": "wait,okay"})
        make_rx(a_y1, 0, 2, "Acute gastritis",
            [{"name": "Pantoprazole", "dosage": "40mg", "morning": True, "afternoon": False, "night": False, "when": "before_meal", "duration": "14 days", "notes": "30 mins before breakfast"},
             {"name": "Domperidone", "dosage": "10mg", "morning": True, "afternoon": True, "night": True, "when": "before_meal", "duration": "5 days", "notes": ""}],
            "Avoid spicy and oily food. No alcohol.", "")

        a_y2 = make_appt(1, 7, d1, "10:30", "completed",
            {"score": 5, "text": "Lifesaver! Dr. Priya caught an irregular heartbeat early. Very grateful.", "sentiment": "positive", "keywords": "lifesaver,irregular heartbeat,grateful"})
        make_appt(2, 8, d1, "11:00", "completed",
            {"score": 4, "text": "Good follow up visit for my son.", "sentiment": "positive", "keywords": "follow up,good"})
        make_appt(0, 5, d1, "14:00", "completed")
        make_appt(3, 9, d1, "15:00", "completed",
            {"score": 2, "text": "Clinic was too crowded. Doctor seemed rushed.", "sentiment": "negative", "keywords": "crowded,rushed"})

        # ──────────── DAY -2 ────────────
        d2 = (today - timedelta(days=2)).isoformat()
        make_appt(0, 3, d2, "09:30", "completed",
            {"score": 4, "text": "Very knowledgeable doctor. Recommended!", "sentiment": "positive", "keywords": "knowledgeable,recommended"})
        make_appt(1, 4, d2, "11:00", "completed")
        make_appt(0, 0, d2, "14:00", "completed",
            {"score": 5, "text": "Second visit, consistently great service.", "sentiment": "positive", "keywords": "consistent,great service"})
        make_appt(2, 8, d2, "10:00", "cancelled")

        # ──────────── DAY -3 ────────────
        d3 = (today - timedelta(days=3)).isoformat()
        make_appt(0, 1, d3, "09:00", "completed",
            {"score": 4, "text": "Quick and effective consultation.", "sentiment": "positive", "keywords": "quick,effective"})
        make_appt(3, 5, d3, "12:00", "completed")
        make_appt(1, 6, d3, "16:00", "completed",
            {"score": 3, "text": "Average experience. Nothing special.", "sentiment": "neutral", "keywords": "average"})

        # ──────────── DAY -4 ────────────
        d4 = (today - timedelta(days=4)).isoformat()
        make_appt(0, 7, d4, "10:00", "completed",
            {"score": 5, "text": "Dr. Alok took extra time to explain my mother's condition.", "sentiment": "positive", "keywords": "extra time,explain,condition"})
        make_appt(2, 8, d4, "09:30", "completed",
            {"score": 5, "text": "Best pediatrician! My child loves visiting Dr. Rajesh.", "sentiment": "positive", "keywords": "best,pediatrician,loves"})

        # ──────────── DAY -5 ────────────
        d5 = (today - timedelta(days=5)).isoformat()
        make_appt(0, 0, d5, "09:30", "completed")
        make_appt(1, 4, d5, "11:00", "completed",
            {"score": 4, "text": "Good doctor, friendly staff.", "sentiment": "positive", "keywords": "good,friendly,staff"})
        make_appt(3, 9, d5, "14:00", "completed")
        make_appt(0, 2, d5, "16:00", "no-show")

        # ──────────── DAY -6 ────────────
        d6 = (today - timedelta(days=6)).isoformat()
        make_appt(0, 5, d6, "10:00", "completed",
            {"score": 1, "text": "Very long wait time. Doctor was late by 45 minutes.", "sentiment": "negative", "keywords": "long wait,late"})
        make_appt(1, 3, d6, "11:30", "completed")

        logger.info("Demo data seeded successfully!")

        return success({
            "message": "Demo data seeded successfully!",
            "doctors": len(doctor_ids),
            "patients": len(patient_ids),
            "summary": {
                "today": "11 appointments (3 completed, 1 in-consultation, 2 in-queue, 3 booked, 1 cancelled, 1 no-show)",
                "past_6_days": "appointments with feedback, prescriptions, varied sentiments",
            }
        })

    except Exception as e:
        logger.error(f"Seed demo error: {e}")
        import traceback
        return server_error(f"{e}\n{traceback.format_exc()}")
