import os
from datetime import datetime
from typing import List, Optional, Dict

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents

app = FastAPI(title="Trip Itinerary Aggregator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ItineraryIn(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime
    locations: Optional[List[str]] = []
    notes: Optional[str] = None


class ItineraryOut(ItineraryIn):
    id: str


class ReservationIn(BaseModel):
    itinerary_id: str
    provider: str
    category: str
    title: str
    location: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    confirmation_number: Optional[str] = None
    details: Optional[dict] = None
    source: Optional[str] = None


@app.get("/")
def read_root():
    return {"message": "Trip Itinerary Aggregator Backend"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


# ------------------- Itineraries -------------------
@app.post("/api/itineraries")
def create_itinerary(payload: ItineraryIn):
    data = payload.model_dump()
    inserted_id = create_document("itinerary", data)
    return {"id": inserted_id, **data}


@app.get("/api/itineraries")
def list_itineraries():
    docs = get_documents("itinerary")
    for d in docs:
        d["id"] = str(d.pop("_id", ""))
    return docs


# ------------------- Reservations -------------------
@app.post("/api/reservations")
def add_reservation(payload: ReservationIn):
    # ensure itinerary exists
    from bson import ObjectId
    try:
        _ = db["itinerary"].find_one({"_id": ObjectId(payload.itinerary_id)})
        if _ is None:
            raise HTTPException(status_code=404, detail="Itinerary not found")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid itinerary_id")

    data = payload.model_dump()
    inserted_id = create_document("reservation", data)
    return {"id": inserted_id, **data}


@app.get("/api/itineraries/{itinerary_id}/reservations")
def list_reservations(
    itinerary_id: str,
    q: Optional[str] = Query(None, description="Search text in title/location/provider"),
    category: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    start: Optional[datetime] = Query(None, description="Start time filter"),
    end: Optional[datetime] = Query(None, description="End time filter"),
):
    from bson import ObjectId
    try:
        _ = ObjectId(itinerary_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid itinerary_id")

    filters = {"itinerary_id": itinerary_id}
    if category:
        filters["category"] = category
    if provider:
        filters["provider"] = provider
    if location:
        filters["location"] = location

    cursor = db["reservation"].find(filters)

    results = []
    for doc in cursor:
        if start or end:
            st = doc.get("start_time")
            et = doc.get("end_time")
            ok = True
            if start and st and st < start:
                ok = False
            if end and et and et > end:
                ok = False
            if not ok:
                continue
        if q:
            text = " ".join(
                [
                    str(doc.get("title", "")),
                    str(doc.get("location", "")),
                    str(doc.get("provider", "")),
                ]
            ).lower()
            if q.lower() not in text:
                continue

        doc["id"] = str(doc.pop("_id", ""))
        results.append(doc)

    return results


# ------------------- Provider integrations -------------------
SUPPORTED_PROVIDERS: Dict[str, str] = {
    "booking.com": "providers.booking",
    "agoda": "providers.agoda",
    "viator": "providers.viator",
    "klook": "providers.klook",
    "getyourguide": "providers.getyourguide",
}


@app.get("/api/providers")
def get_supported_providers():
    return {"providers": list(SUPPORTED_PROVIDERS.keys())}


class EmailImportIn(BaseModel):
    itinerary_id: str
    provider_hint: Optional[str] = None
    raw_eml: Optional[str] = None
    imap_config: Optional[dict] = None


@app.post("/api/import/email")
def import_from_email(payload: EmailImportIn):
    # Placeholder for future: parse emails to reservations
    return {"status": "accepted", "message": "Email import queued", "itinerary_id": payload.itinerary_id}


class ProviderImportIn(BaseModel):
    itinerary_id: str
    provider: str
    access_token: Optional[str] = None


@app.post("/api/import/provider")
def import_from_provider(payload: ProviderImportIn):
    # Validate itinerary
    from bson import ObjectId
    try:
        _ = db["itinerary"].find_one({"_id": ObjectId(payload.itinerary_id)})
        if _ is None:
            raise HTTPException(status_code=404, detail="Itinerary not found")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid itinerary_id")

    provider_key = payload.provider.lower()
    if provider_key not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    # Dynamically import connector
    module_path = SUPPORTED_PROVIDERS[provider_key]
    try:
        import importlib
        connector = importlib.import_module(module_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connector load error: {str(e)[:120]}")

    # Fetch reservations from provider (mock connectors return sample data)
    try:
        account = {"access_token": payload.access_token}
        fetched: List[Dict] = connector.fetch_reservations(account)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Provider fetch failed: {str(e)[:120]}")

    # Insert into DB tied to itinerary
    created = 0
    items = []
    for item in fetched:
        data = {
            **item,
            "itinerary_id": payload.itinerary_id,
        }
        try:
            inserted_id = create_document("reservation", data)
            data["id"] = inserted_id
            items.append(data)
            created += 1
        except Exception as e:
            # Skip individual failures but continue
            continue

    return {"status": "ok", "provider": provider_key, "created": created, "items": items}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
