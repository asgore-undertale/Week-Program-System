# University Week Schedule System

## Table of Contents
1. [Description](#description)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
5. [Installation](#installation)
   - [Local Setup](#local-setup)
   - [Using Docker](#using-docker)
7. [Database](#database)
10. [License](#license)

---

## Description

The **University Week Schedule System** is a web application built with Python Flask and SQLite that automatically generates weekly course schedules using a genetic algorithm. The system supports three user roles—Admin, Professor, and Student—each with tailored permissions to manage and view schedules.

---

## Features

- **Role-Based Access Control**
  - **Admin**
    - Generate or regenerate the entire university schedule.
    - Manually specify time slots and classrooms for lectures.
    - Set and manage professors' unavailable times.
    - View individual student schedules.
  - **Professor**
    - Define personal availability for scheduling.
  - **Student**
    - Filter and view personal lecture schedules.
- **Genetic Algorithm** for optimized schedule generation.
- **Filter** lectures by professor.

---

## Tech Stack

- **Backend:** Python 3.x, Flask
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript
- **Containerization:** Docker, Docker Compose

---

## Installation

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/university-week-schedule.git
   cd university-week-schedule
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the project:
   ```bash
   python3 app.py
   ```

### Using Docker

#### Build and Run

```bash
# Build images
docker-compose build

# Start containers
docker-compose up
```

#### Pull Pre-built Image

```bash
docker pull ahmaddraie/week-program-system:latest
docker run -p 80:5000 ahmaddraie/week-program-system:latest
```

---

## Database

- The SQLite database file is located at `databases/University.db`.
- To modify users, courses, or classrooms, use a database browser or the SQLite CLI:
  ```bash
  sqlite3 databases/University.db
  ```

---

## License

This project is licensed under the MIT License.