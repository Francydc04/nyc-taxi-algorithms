"""Load and clean NYC yellow-taxi trip records using only the standard library."""

import csv
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

MILES_TO_KM = 1.60934
MAX_PLAUSIBLE_SPEED_KMH = 100  # a taxi's *average* speed over a whole trip can't realistically exceed this


@dataclass
class Trip:
    vendor_id: int
    pickup: datetime
    dropoff: datetime
    passengers: Optional[float]
    distance_km: Optional[float]
    fare: Optional[float]
    tip: Optional[float]
    total: Optional[float]
    pickup_zone: Optional[int]
    dropoff_zone: Optional[int]

    @property
    def duration_h(self) -> float:
        return (self.dropoff - self.pickup).total_seconds() / 3600

    @property
    def speed_kmh(self) -> Optional[float]:
        if self.distance_km is None or self.duration_h <= 0:
            return None
        return self.distance_km / self.duration_h


def _num(value: str, cast=float):
    value = value.strip()
    return cast(float(value)) if value else None


def read_trips(path: str) -> List[Trip]:
    """Parse the raw TLC file, keeping only the 10 fields the analysis needs."""
    trips = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            miles = _num(row["trip_distance"])
            trips.append(Trip(
                vendor_id=int(row["VendorID"]),
                pickup=datetime.fromisoformat(row["tpep_pickup_datetime"]),
                dropoff=datetime.fromisoformat(row["tpep_dropoff_datetime"]),
                passengers=_num(row["passenger_count"]),
                distance_km=miles * MILES_TO_KM if miles is not None else None,
                fare=_num(row["fare_amount"]),
                tip=_num(row["tip_amount"]),
                total=_num(row["total_amount"]),
                pickup_zone=_num(row["PULocationID"], int),
                dropoff_zone=_num(row["DOLocationID"], int),
            ))
    return trips


def read_zones(path: str) -> Dict[int, str]:
    """Map TLC zone IDs to readable names, e.g. 132 -> 'JFK Airport'."""
    with open(path, newline="") as f:
        return {int(r["LocationID"]): r["Zone"] for r in csv.DictReader(f)}


def valid_values(trips: List[Trip], field: str) -> List[float]:
    """Non-missing, non-negative values of a numeric field (negative fares are refunds/errors)."""
    return [v for t in trips if (v := getattr(t, field)) is not None and v >= 0]


def summary(values: List[float]) -> Dict[str, float]:
    return {"min": min(values), "max": max(values), "mean": sum(values) / len(values), "n": len(values)}


def plausible_speeds(trips: List[Trip]) -> List[float]:
    return [s for t in trips if (s := t.speed_kmh) is not None and 0 <= s <= MAX_PLAUSIBLE_SPEED_KMH]


def data_quality(trips: List[Trip]) -> Dict[str, int]:
    """Count the records that fail basic sanity checks."""
    return {
        "trips": len(trips),
        "missing_passenger_count": sum(t.passengers is None for t in trips),
        "negative_fare": sum(t.fare is not None and t.fare < 0 for t in trips),
        "non_positive_duration": sum(t.duration_h <= 0 for t in trips),
        "implausible_speed": sum(
            (s := t.speed_kmh) is not None and not 0 <= s <= MAX_PLAUSIBLE_SPEED_KMH for t in trips
        ),
    }


def count_trips_from(trips: List[Trip], zones: Dict[int, str]) -> Dict[str, int]:
    """Number of trips picked up in each of the given zones."""
    counts = Counter(t.pickup_zone for t in trips)
    return {name: counts.get(zone_id, 0) for zone_id, name in zones.items()}
