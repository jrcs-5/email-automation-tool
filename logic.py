import threading
import schedule
import time
from database import Database
from email_reminder import Email

def process_reminders():
    db = Database()
    email_service = Email()
    
    
    try:
        reminders = db.get_reminders()
        if reminders:
            print(f"Se encontraron {len(reminders)} mensajes por enviar.")
            for reminder in reminders:
                try:
                    email_service.send_email(reminder[0], reminder[1], reminder[2])
                    db.mark_as_sent(reminder[3], reminder[4])
                except Exception as e:
                    print(f"Error al enviar email a {reminder[0]}: {e}")
                    db.mark_as_failed(reminder[3], reminder[4])
            
    except Exception as e:
        print(f"Error al procesar recordatorios: {e}")
    finally:
        db.close()
        del email_service
        
def start_schedule():
    schedule.every(1).minute.do(process_reminders)
    while True:
        schedule.run_pending()
        time.sleep(10)
        
def start_scheduler_in_thread():
    scheduler_thread = threading.Thread(target=start_schedule, daemon=True)
    scheduler_thread.start()