# Tracking Number Generator API

A scalable, efficient RESTful API built with Django REST Framework that generates unique tracking numbers for parcels. Designed to handle high concurrency and scale horizontally.

--- Features

- Generates unique tracking numbers matching regex pattern `^[A-Z0-9]{1,16}$`.
- Uses Redis for atomic, concurrency-safe sequence generation.
- Accepts origin/destination countries, weight, timestamp, customer info as inputs.
- Returns tracking number and generation timestamp in RFC 3339 format.
- Easily scalable across multiple instances.

---

## Tech Stack

- Python 3.x
- Django 4.x
- Django REST Framework
- Redis (for concurrency-safe counters)
- Gunicorn (for production WSGI server)

--- Prerequisites

- Python 3.8+
- Redis server running locally or remotely
- `pip` package manager

---

--- Installation

1. Clone the repo:

```bash
git clone https://github.com/yourusername/tracking-number-api.git
cd tracking-number-api
