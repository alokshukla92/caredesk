import logging

logger = logging.getLogger(__name__)


def emit_queue_update(app, clinic_id, event_data):
    """
    Emit a real-time signal when queue status changes.
    Connected clients (queue display) can listen for this.
    """
    try:
        signal = app.signal()
        signal.emit(
            topic=f"queue_{clinic_id}",
            message={
                "event": "queue_update",
                "clinic_id": clinic_id,
                "data": event_data,
            }
        )
        logger.info(f"Signal emitted: queue_update for clinic {clinic_id}")
        return True
    except Exception as e:
        logger.warning(f"Signal emit failed (non-critical): {e}")
        return False


def emit_appointment_event(app, clinic_id, event_type, appointment_data):
    """
    Emit signal for appointment-related events.
    event_type: "booked", "status_changed", "completed"
    """
    try:
        signal = app.signal()
        signal.emit(
            topic=f"appointments_{clinic_id}",
            message={
                "event": event_type,
                "clinic_id": clinic_id,
                "data": appointment_data,
            }
        )
        logger.info(f"Signal emitted: {event_type} for clinic {clinic_id}")
        return True
    except Exception as e:
        logger.warning(f"Signal emit failed (non-critical): {e}")
        return False
