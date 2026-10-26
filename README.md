# Anime Lounge API 🐉⚡

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%25-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red?style=flat&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![License: ISC](https://img.shields.io/badge/License-ISC-yellow.svg)](https://opensource.org/licenses/ISC)

---

## 📌 Summary

**Anime Lounge API** is a high-performance, modular backend built with **FastAPI** and **SQLAlchemy**. It is designed to manage and query detailed statistics about anime characters—featuring a specialized dataset tracking Dragon Ball Z characters, power levels, sagas, and series. The project incorporates robust data ingestion scripts using **Pandas** to clean, format, and seed raw CSV data into a relational database.

---

## 🏗️ Project Architecture

The project follows a clean separation of concerns, separating routing, business logic, data validation, and database configuration:

```text
anime_lounge_api/
├── api/
│   ├── models.py       # SQLAlchemy ORM Database Models
│   ├── router.py       # FastAPI Endpoints & Route Definitions
│   ├── schema.py       # Pydantic Validation & Serialization Models
│   └── services.py     # Database Query & Business Logic Layer
├── config/
│   └── db.py           # Database Connection & Session Management
├── data/
│   ├── data.csv        # Raw Character & Power Level Dataset
│   └── script.py       # Automated CSV Parsing & Seeding Utility
└── main.py             # FastAPI Application Entrypoint