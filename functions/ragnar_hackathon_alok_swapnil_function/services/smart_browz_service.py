import logging

logger = logging.getLogger(__name__)


def generate_prescription_html(data):
    """Generate a professional prescription HTML for PDF conversion."""
    clinic_name = data.get("clinic_name", "CareDesk Clinic")
    clinic_address = data.get("clinic_address", "")
    clinic_phone = data.get("clinic_phone", "")
    doctor_name = data.get("doctor_name", "")
    doctor_specialty = data.get("doctor_specialty", "")
    patient_name = data.get("patient_name", "")
    patient_age = data.get("patient_age", "")
    patient_gender = data.get("patient_gender", "")
    diagnosis = data.get("diagnosis", "")
    medicines = data.get("medicines", [])
    advice = data.get("advice", "")
    follow_up_date = data.get("follow_up_date", "")
    rx_date = data.get("date", "")
    prescription_id = data.get("prescription_id", "")

    # Build medicines rows
    med_rows = ""
    for i, med in enumerate(medicines, 1):
        # Build frequency display (1-0-1 or Morning, Night etc.)
        freq_display = ""
        if "morning" in med:
            m_val = "1" if med.get("morning") else "0"
            a_val = "1" if med.get("afternoon") else "0"
            n_val = "1" if med.get("night") else "0"
            freq_display = f"{m_val}-{a_val}-{n_val}"
            freq_parts = []
            if med.get("morning"): freq_parts.append("Morning")
            if med.get("afternoon"): freq_parts.append("Afternoon")
            if med.get("night"): freq_parts.append("Night")
            freq_label = ", ".join(freq_parts) if freq_parts else ""
        else:
            freq_display = ""
            freq_label = ""

        # Build timing
        when = med.get("when", "")
        when_label = "Before meal" if when == "before_meal" else "After meal" if when == "after_meal" else ""

        # Build instructions — combine structured + notes
        instr_parts = []
        if freq_label:
            instr_parts.append(f'<span style="color:#0d9488;font-weight:600;">{freq_display}</span> ({freq_label})')
        if when_label:
            instr_parts.append(f'<span style="color:#9a3412;">{when_label}</span>')
        notes = med.get("notes", "")
        if notes:
            instr_parts.append(f'<em style="color:#64748b;">{notes}</em>')
        # Fallback for old format
        if not instr_parts:
            old_instr = med.get("instructions", "")
            if old_instr:
                instr_parts.append(old_instr)

        instructions_html = "<br>".join(instr_parts)

        med_rows += f"""
        <tr>
          <td class="sno">{i}</td>
          <td class="med-name">{med.get('name', '')}</td>
          <td>{med.get('dosage', '')}</td>
          <td>{med.get('duration', '')}</td>
          <td class="instructions">{instructions_html}</td>
        </tr>"""

    # Patient info line
    patient_details = patient_name
    if patient_age:
        patient_details += f" &nbsp;|&nbsp; {patient_age} yrs"
    if patient_gender:
        patient_details += f" &nbsp;|&nbsp; {patient_gender}"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Prescription - {patient_name}</title>
<style>
  @page {{
    size: A4;
    margin: 0;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #1e293b;
    background: #fff;
    padding: 0;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  .page {{
    width: 210mm;
    min-height: 297mm;
    padding: 28mm 22mm 20mm;
    position: relative;
  }}

  /* ── Header ── */
  .header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-bottom: 3px solid #0d9488;
    padding-bottom: 14px;
    margin-bottom: 18px;
  }}
  .header-left h1 {{
    font-size: 22px;
    color: #0d9488;
    font-weight: 700;
    letter-spacing: -0.3px;
  }}
  .header-left .subtitle {{
    font-size: 11px;
    color: #94a3b8;
    margin-top: 2px;
  }}
  .header-left .clinic-info {{
    font-size: 10px;
    color: #64748b;
    margin-top: 4px;
    line-height: 1.5;
  }}
  .header-right {{
    text-align: right;
    font-size: 11px;
    color: #475569;
    line-height: 1.6;
  }}
  .header-right .doctor-name {{
    font-size: 14px;
    font-weight: 600;
    color: #0f172a;
  }}
  .header-right .specialty {{
    color: #0d9488;
    font-size: 11px;
    font-weight: 500;
  }}

  /* ── Patient Info ── */
  .patient-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #f0fdfa;
    border: 1px solid #ccfbf1;
    border-radius: 8px;
    padding: 10px 16px;
    margin-bottom: 18px;
  }}
  .patient-bar .label {{
    font-size: 10px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
  }}
  .patient-bar .value {{
    font-size: 13px;
    font-weight: 600;
    color: #0f172a;
    margin-top: 1px;
  }}

  /* ── Diagnosis ── */
  .section-title {{
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #94a3b8;
    font-weight: 700;
    margin-bottom: 6px;
    padding-bottom: 4px;
    border-bottom: 1px solid #f1f5f9;
  }}
  .diagnosis-box {{
    margin-bottom: 20px;
  }}
  .diagnosis-box p {{
    font-size: 13px;
    color: #334155;
    line-height: 1.6;
    margin-top: 4px;
  }}

  /* ── Rx Symbol ── */
  .rx-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
  }}
  .rx-symbol {{
    font-size: 28px;
    font-weight: 700;
    color: #0d9488;
    font-style: italic;
    font-family: 'Times New Roman', serif;
    line-height: 1;
  }}
  .rx-label {{
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #94a3b8;
    font-weight: 700;
  }}

  /* ── Medicines Table ── */
  .med-table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 22px;
    font-size: 12px;
  }}
  .med-table thead tr {{
    background: #0d9488;
    color: #fff;
  }}
  .med-table th {{
    padding: 8px 12px;
    text-align: left;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }}
  .med-table th:first-child {{
    border-radius: 6px 0 0 0;
    width: 36px;
    text-align: center;
  }}
  .med-table th:last-child {{
    border-radius: 0 6px 0 0;
  }}
  .med-table td {{
    padding: 9px 12px;
    border-bottom: 1px solid #f1f5f9;
    color: #475569;
    vertical-align: top;
  }}
  .med-table .sno {{
    text-align: center;
    color: #94a3b8;
    font-weight: 600;
  }}
  .med-table .med-name {{
    font-weight: 600;
    color: #1e293b;
  }}
  .med-table .instructions {{
    font-style: italic;
    color: #64748b;
    font-size: 11px;
  }}
  .med-table tbody tr:nth-child(even) {{
    background: #f8fafc;
  }}
  .med-table tbody tr:last-child td {{
    border-bottom: 2px solid #e2e8f0;
  }}

  /* ── Advice & Follow-up ── */
  .advice-section {{
    margin-bottom: 18px;
  }}
  .advice-section p {{
    font-size: 12px;
    color: #475569;
    line-height: 1.6;
    margin-top: 4px;
  }}
  .followup-box {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #fff7ed;
    border: 1px solid #fed7aa;
    border-radius: 6px;
    padding: 8px 14px;
    margin-bottom: 20px;
  }}
  .followup-box .icon {{
    font-size: 16px;
  }}
  .followup-box .text {{
    font-size: 12px;
    color: #9a3412;
    font-weight: 600;
  }}

  /* ── Footer ── */
  .footer {{
    position: absolute;
    bottom: 18mm;
    left: 22mm;
    right: 22mm;
    border-top: 2px solid #f1f5f9;
    padding-top: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .footer-left {{
    font-size: 9px;
    color: #cbd5e1;
  }}
  .footer-right {{
    text-align: right;
  }}
  .footer-right .sig-line {{
    border-top: 1px solid #cbd5e1;
    width: 150px;
    margin-left: auto;
    margin-bottom: 4px;
  }}
  .footer-right .sig-text {{
    font-size: 10px;
    color: #64748b;
    font-weight: 600;
  }}

  .watermark {{
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-30deg);
    font-size: 100px;
    color: rgba(13, 148, 136, 0.03);
    font-weight: 900;
    letter-spacing: 12px;
    pointer-events: none;
    z-index: 0;
  }}
</style>
</head>
<body>
<div class="page">
  <div class="watermark">CareDesk</div>

  <!-- Header -->
  <div class="header">
    <div class="header-left">
      <h1>{clinic_name}</h1>
      <div class="subtitle">Smart Clinic Management System</div>
      {'<div class="clinic-info">' + clinic_address + '</div>' if clinic_address else ''}
      {'<div class="clinic-info">' + clinic_phone + '</div>' if clinic_phone else ''}
    </div>
    <div class="header-right">
      <div class="doctor-name">Dr. {doctor_name}</div>
      {'<div class="specialty">' + doctor_specialty + '</div>' if doctor_specialty else ''}
      <div style="margin-top:6px;">Date: {rx_date}</div>
      {'<div>Rx #' + str(prescription_id) + '</div>' if prescription_id else ''}
    </div>
  </div>

  <!-- Patient Info -->
  <div class="patient-bar">
    <div>
      <div class="label">Patient</div>
      <div class="value">{patient_details}</div>
    </div>
    <div style="text-align:right;">
      <div class="label">Appointment Date</div>
      <div class="value">{rx_date}</div>
    </div>
  </div>

  <!-- Diagnosis -->
  <div class="diagnosis-box">
    <div class="section-title">Diagnosis</div>
    <p>{diagnosis}</p>
  </div>

  <!-- Medicines -->
  <div class="rx-header">
    <span class="rx-symbol">&#8478;</span>
    <span class="rx-label">Prescribed Medicines</span>
  </div>
  <table class="med-table">
    <thead>
      <tr>
        <th>#</th>
        <th>Medicine</th>
        <th>Dosage</th>
        <th>Duration</th>
        <th>Instructions</th>
      </tr>
    </thead>
    <tbody>{med_rows if med_rows else '<tr><td colspan="5" style="text-align:center;color:#94a3b8;padding:16px;">No medicines prescribed</td></tr>'}</tbody>
  </table>

  <!-- Advice -->
  {'<div class="advice-section"><div class="section-title">Advice</div><p>' + advice + '</p></div>' if advice else ''}

  <!-- Follow-up -->
  {'<div class="followup-box"><span class="icon">&#128197;</span><span class="text">Follow-up: ' + follow_up_date + '</span></div>' if follow_up_date else ''}

  <!-- Footer -->
  <div class="footer">
    <div class="footer-left">
      Generated by CareDesk &mdash; Smart Clinic Management System<br>
      This is a digitally generated prescription.
    </div>
    <div class="footer-right">
      <div class="sig-line"></div>
      <div class="sig-text">Dr. {doctor_name}</div>
    </div>
  </div>
</div>
</body>
</html>"""
    return html


def generate_pdf(app, html_content):
    """
    Generate a PDF from HTML using Catalyst SmartBrowz.
    Returns PDF bytes or None on failure.
    """
    try:
        smart_browz = app.smart_browz()
        result = smart_browz.convert_to_pdf(
            source=html_content,
            pdf_options={
                "format": "A4",
                "print_background": True,
                "scale": 1,
            },
        )
        logger.info("SmartBrowz PDF generated successfully")
        return result
    except Exception as e:
        logger.warning(f"SmartBrowz PDF generation failed: {e}")
        return None
