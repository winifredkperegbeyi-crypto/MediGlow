from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import math

app = FastAPI(title="Telehealth Backend API", version="1.0")

# --- 1. CORS CONFIGURATION ---
# This allows your HTML/JS frontend to securely communicate with this Python backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (change to specific frontend URL in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. PYDANTIC DATA MODELS (Request Validation) ---

class EmergencyData(BaseModel):
    user_id: str
    latitude: float | None = None
    longitude: float | None = None

class LoginData(BaseModel):
    username: str
    password: str

class AppointmentData(BaseModel):
    user_id: str
    specialty: str
    symptoms: str


# --- 3. IN-MEMORY DATABASES (Temporary storage for MVP) ---
EMERGENCY_DATABASE = []
APPOINTMENT_DATABASE = []


# --- 4. API ENDPOINTS ---

@app.get("/")
def home():
    return {"status": "online", "message": "Telehealth Python Backend is running successfully!"}


@app.post("/api/emergency")
def receive_emergency(data: EmergencyData):
    """
    Receives emergency SOS triggers from the HTML frontend, 
    calculates distance using the Haversine geolocator formula, and logs it.
    """
    # Central hospital / dispatch coordinates (Example: Lagos coordinates)
    hospital_lat, hospital_lon = 6.5244, 3.3792 
    
    distance_km = None
    if data.latitude and data.longitude:
        # Haversine Distance Calculation Formula
        lat1, lon1, lat2, lon2 = map(math.radians, [data.latitude, data.longitude, hospital_lat, hospital_lon])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance_km = round(c * 6371, 2)  # 6371 km is Earth's radius

    # Create emergency alert record
    alert_record = {
        "id": len(EMERGENCY_DATABASE) + 1,
        "user_id": data.user_id,
        "latitude": data.latitude,
        "longitude": data.longitude,
        "distance_km": distance_km,
        "status": "Pending"
    }
    
    EMERGENCY_DATABASE.append(alert_record)
    print(f"🚨 EMERGENCY LOGGED: {alert_record}")

    return {
        "status": "success",
        "message": f"Emergency received! Nearest response unit is {distance_km} km away.",
        "alert_id": alert_record["id"]
    }


@app.post("/api/login")
def login_user(credentials: LoginData):
    """
    Simple role-based authentication check for your frontend users.
    """
    username = credentials.username.lower()
    password = credentials.password
    
    # Mock user database check
    if username == "admin" and password == "secret":
        return {"status": "success", "role": "admin", "message": "Welcome Admin"}
    elif username == "doctor" and password == "secret":
        return {"status": "success", "role": "doctor", "message": "Welcome Doctor"}
    elif username == "patient" and password == "secret":
        return {"status": "success", "role": "patient", "message": "Welcome Patient"}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")


@app.post("/api/book-appointment")
def book_appointment(data: AppointmentData):
    """
    Handles standard appointment booking and basic symptom triage.
    """
    # Simple keyword-based triage check
    critical_keywords = ["breathing", "chest pain", "fainting", "severe"]
    is_critical = any(keyword in data.symptoms.lower() for keyword in critical_keywords)
    
    appointment_record = {
        "id": len(APPOINTMENT_DATABASE) + 1,
        "user_id": data.user_id,
        "specialty": data.specialty,
        "symptoms": data.symptoms,
        "priority": "High / Emergency" if is_critical else "Standard",
        "status": "Confirmed"
    }
    
    APPOINTMENT_DATABASE.append(appointment_record)
    
    return {
        "status": "success",
        "priority": appointment_record["priority"],
        "message": "Appointment booked successfully. A healthcare provider has been assigned."
    }