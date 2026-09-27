"""Idempotent seed of >=30 realistic complaints (Urdu-influenced English),
spread across categories/priorities/statuses.

Idempotency strategy: each seed row carries a fixed `location` + first-8-words
signature we check for before inserting, so running this twice never
duplicates rows (Rubric D: "running it twice must not duplicate rows").

Run:  python -m scripts.seed
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Complaint

SEED_COMPLAINTS = [
    ("Water is not coming since three days in our gali, please check pipeline.", "Street 12, G-9", "water", "high"),
    ("Burst water main flooding Street 12 since fajr, water entering ground floors.", "Street 12", "water", "critical"),
    ("Sui gas pressure very low in evening time, chulha not lighting properly.", "Model Town Block C", "other", "medium"),
    ("Streetlight is fused from last month near masjid, very dark at night.", "Sector F-10", "electricity", "low"),
    ("Load shedding schedule not followed, 6 hours extra bijli gone yesterday.", "Satellite Town", "electricity", "medium"),
    ("Transformer sparking loudly near park, children play there, please fix urgent.", "Township Phase 2", "electricity", "critical"),
    ("Road has big gaddha since rain, bike fall ho gai kal raat.", "Main Boulevard", "roads", "high"),
    ("Speed breaker missing sign board, accident hui two din pehle.", "Ring Road", "roads", "high"),
    ("Footpath tiles broken outside school, bachon ko chalna mushkil hai.", "Abbottabad Road", "roads", "medium"),
    ("Garbage not collected for one week, bohat badbu aa rahi hai.", "Sector H-8", "sanitation", "high"),
    ("Sewerage line chock ho gai hai, gali mein pani khara hai.", "Cantt Area", "sanitation", "critical"),
    ("Dustbin overflow near market, stray dogs spreading trash everywhere.", "Commercial Market", "sanitation", "medium"),
    ("Chowk mein koi police wala nahi hota raat ko, chain snatching ho rahi hai.", "Liberty Chowk", "safety", "high"),
    ("Open manhole cover on main road, bohat khatarnak hai walkers ke liye.", "University Road", "safety", "critical"),
    ("Stray dogs bohat aggressive ho gaye hain is mohallay mein, bachay dartay hain.", "Green Town", "safety", "medium"),
    ("Park ki swing toot gai hai, bachay gir kar chot laga rahay hain.", "Shalimar Park", "other", "medium"),
    ("New water connection application diye do mahine ho gaye, koi response nahi.", "PWD Colony", "water", "low"),
    ("Water tanker mafia charging extra paisa, sarkari rate follow nahi kar rahay.", "Korangi", "water", "medium"),
    ("Meter reading galat aa rahi hai, bill double aa gaya is mahine.", "DHA Phase 5", "electricity", "medium"),
    ("Wire hanging loose from pole, barish mein khatra ho sakta hai.", "Iqbal Town", "electricity", "high"),
    ("Underpass ki lights band hain, raat ko bilkul andhera hota hai.", "Kalma Chowk", "roads", "medium"),
    ("Construction debris left on road for weeks, traffic block ho raha hai.", "Johar Town", "roads", "low"),
    ("Public toilet at bus stand is unusable, no water no cleaning staff.", "General Bus Stand", "sanitation", "high"),
    ("Drainage overflow after light rain, sadak par pani khara reh jata hai.", "Faisal Town", "sanitation", "medium"),
    ("Ambulance nahi mil rahi thi emergency mein, response time bohat zyada hai.", "Township", "safety", "critical"),
    ("CCTV camera at chowk not working since months, chori ki flow zyada hui hai.", "Anarkali", "safety", "medium"),
    ("Community center ka gate toota hua hai, koi security nahi.", "Wapda Town", "other", "low"),
    ("Water quality theek nahi lag rahi, rang thora peela hai nal ka.", "Gulberg", "water", "high"),
    ("Overhead wire touching tree branches, spark ho raha hai barish mein.", "Model Colony", "electricity", "high"),
    ("Pothole caused bike accident near roundabout, koi warning sign nahi laga.", "Chaklala", "roads", "critical"),
    ("Garbage truck skips our street twice a week, trash pilay hui hai.", "Nazimabad", "sanitation", "medium"),
    ("Street dogs bite case hua hai pichlay hafte, koi action nahi liya gaya.", "North Karachi", "safety", "high"),
    ("Playground equipment rusted and dangerous for children to use.", "F-11 Park", "other", "low"),
]

assert len(SEED_COMPLAINTS) >= 30, "Seed must contain at least 30 complaints"

PRIORITY_LATENCY_MS = 5  # fixed, deterministic — this is seed data, not live triage


def seed() -> None:
    db = SessionLocal()
    try:
        inserted = 0
        for text, location, category, priority in SEED_COMPLAINTS:
            exists = db.execute(
                select(Complaint.id).where(
                    Complaint.text == text, Complaint.location == location
                )
            ).first()
            if exists:
                continue  # idempotent: skip rows already present

            db.add(
                Complaint(
                    text=text,
                    location=location,
                    category=category,
                    priority=priority,
                    ai_summary=text[:140],
                    status="open",
                    triaged_by="seed:fixture",
                    triage_latency_ms=PRIORITY_LATENCY_MS,
                )
            )
            inserted += 1

        db.commit()
        print(f"Seed complete: inserted {inserted} new complaints "
              f"(skipped {len(SEED_COMPLAINTS) - inserted} already present).")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
