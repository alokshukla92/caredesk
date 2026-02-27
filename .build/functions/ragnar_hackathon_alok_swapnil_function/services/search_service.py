import logging

logger = logging.getLogger(__name__)


def search_patients(app, clinic_id, query_text):
    """
    Search patients using Catalyst Search service.
    Falls back to ZCQL LIKE query if Search is not configured.
    """
    try:
        search = app.search()
        result = search.execute_search_query(
            query_text,
            search_table_columns={
                "Patients": ["name", "phone", "email"]
            }
        )

        # Filter results by clinic_id
        patients = []
        if result:
            for item in result:
                row = item.get("Patients", {})
                if row.get("clinic_id") == str(clinic_id):
                    patients.append({
                        "id": row.get("ROWID", ""),
                        "name": row.get("name", ""),
                        "phone": row.get("phone", ""),
                        "email": row.get("email", ""),
                        "age": row.get("age", ""),
                        "gender": row.get("gender", ""),
                    })
        logger.info(f"Search returned {len(patients)} results for '{query_text}'")
        return patients

    except Exception as e:
        logger.warning(f"Catalyst Search failed, falling back to ZCQL: {e}")
        return None  # Caller should fall back to ZCQL
