import time
import pytest
import concurrent.futures
from qvalidate.db import DatabaseManager

def test_atomic_device_reservation_invariant():
    """Verify invariant: successful_reservations <= 1 when 10 threads race to reserve the same device."""
    db = DatabaseManager()
    target_device = "DEVICE-001"
    db.release_device(target_device)

    successful_reservations = []

    def race_worker(worker_id):
        res = db.reserve_device(target_device)
        if res:
            successful_reservations.append(worker_id)
        return res

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(race_worker, i) for i in range(10)]
        concurrent.futures.wait(futures)

    assert len(successful_reservations) == 1, f"Expected exactly 1 successful reservation, got {len(successful_reservations)}"
    db.release_device(target_device)

def test_duplicate_reservation_prevention():
    db = DatabaseManager()
    dev_id = "DEVICE-002"
    db.release_device(dev_id)

    res1 = db.reserve_device(dev_id)
    assert res1 is True

    res2 = db.reserve_device(dev_id)
    assert res2 is False

    db.release_device(dev_id)
    res3 = db.reserve_device(dev_id)
    assert res3 is True
    db.release_device(dev_id)

def test_stale_reservation_recovery():
    db = DatabaseManager()
    dev_id = "DEVICE-003"
    db.release_device(dev_id)

    db.reserve_device(dev_id)
    # Artificially set reserved_at in past
    conn = db.get_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE devices SET reserved_at = ? WHERE device_id = ?", (time.time() - 100.0, dev_id))
        conn.commit()
    finally:
        db.release_connection(conn)

    recovered_count = db.recover_stale_reservations(timeout_sec=30.0)
    assert recovered_count >= 1

    device = db.get_device(dev_id)
    assert device["is_reserved"] == 0
