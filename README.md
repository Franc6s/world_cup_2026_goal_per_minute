# World Cup 2026 — Goal per minute

## Project Overview

The **World Cup 2026 — Goal per minute** is a structured data project developed to capture, organize, and analyze goal-level information from the **2026 FIFA World Cup**.

The project goes beyond a traditional match-results dataset by documenting each goal as an individual event and connecting it to information including the player, match, venue, referee, team, tournament stage, and timing of the event.

The project is developed by **Francis Mangala** who owns the intellectual property and maintained by **Vizual Optima LLC**.

---

## Project Objectives

The World Cup 2026 project was designed around four primary objectives:

1. **Build a detailed goal per minute dataset** of the 2026 FIFA World Cup.
2. **Standardize and validate tournament information** collected from multiple data points.
3. **Transform the dataset into a relational SQL database** suitable for advanced analytics.
4. **Provide reusable data products** for analysts, developers, researchers, students, and football enthusiasts.

Rather than simply recording final scores, the project focuses on the individual events and contextual information behind every goal.

---

# Dataset Coverage

The dataset includes information across several analytical categories.

### Goal Information

* Goal ID
* Match ID
* Player
* Minute scored
* Match half
* Stoppage time
* Stoppage-time goal minute
* Penalty indicator
* Own-goal indicator
* Penalty shootout information
* Penalty shootout winner

### Player Information

* Player name
* First name
* Country
* Age
* Position

### Match Information

* Fixture
* Match ID
* Fixture format
* Group
* Match date
* Kickoff time
* UTC offset

### Venue Information

* Host country
* Host city
* Stadium
* Attendance

### Coach Information

* Coach Name
* Country Coached
* Coach Nationality

### Referee Information

* Referee name
* Referee country
* Confederation
---
# Methodology 

## 1. Unique Identifier Methodology

Two primary identifiers are used throughout the project.

### Match ID

Each match receives a unique identifier using the following structure:

`WC_26_001`

The identifier provides a consistent key that can be used to connect match information across tables.

### Goal ID

Every goal receives its own unique identifier:

`goal_001`, `goal_002`, `goal_003`, ...

Goal IDs are continuous throughout the tournament rather than restarting for each match.

This allows every scoring event to be uniquely identified while maintaining a relationship with its corresponding Match ID.

---

## 2. Chronological Ordering

One challenge when building an international tournament database is that matches may occur:

* On the same date
* At the same local time
* In different cities
* Across different time zones

For this reason, local kickoff time alone is not sufficient for establishing the true chronological sequence of matches.

The project therefore incorporates:

* Match date
* Local kickoff time
* UTC offset

These fields can be combined to normalize kickoff times to **UTC**, allowing matches and goal events to be ordered consistently across host cities.

This chronological methodology is also used to support the generation and validation of Match IDs and Goal IDs.

---

# Data Validation

Several validation procedures are used throughout the project to improve data integrity.

These include:

* Duplicate detection
* Unique Goal ID validation
* Unique Match ID validation
* Player-name standardization
* Fixture validation
* Match-date validation
* UTC/time-zone validation
* Goal-minute validation
* Player-position validation
* Missing-value review
* Referential-integrity checks between database tables

Special attention is also given to players associated with multiple positional classifications to prevent duplicated goal records.

---

# Database Architecture

The dataset is also transformed into a **PostgreSQL relational database**.

The database uses a structured schema designed to separate entities and reduce unnecessary duplication.

Core tables include entities such as:

### Player Dimension

Stores player-level attributes and positional information.

### Team Dimension

Stores participating national-team information.

### Venue Dimension

Stores stadium, city, and host-country information.

### Coach Dimension

Stores coach name , coach nationality , national team coached

### Referee Dimension

Stores referee and confederation information.

### Goal Fact Table

Acts as the central event table containing individual scoring events and relationships to the relevant match and player information.

### Penalty Dimension

Provides additional information for goals classified as penalties.

The relational architecture allows users to perform SQL joins and build analytical models without relying exclusively on a single flat spreadsheet.

---

# ETL Workflow

The project follows an **Extract, Transform, Load (ETL)** methodology.

**Extract**

Tournament and goal information is collected from available tournament information and supporting sources.

**Transform**

The information is cleaned, standardized, validated, assigned unique identifiers, and prepared for analysis.

**Load**

The transformed data is loaded into PostgreSQL staging and production tables.

The general workflow is:

`Source Data → Data Collection → Cleaning → Standardization → Validation → Staging Tables → SQL Transformations → Relational Database → Analytics`

---

# Products

The World Cup 2026 project is available in multiple formats depending on the user's analytical requirements.

## Product 1 — [World Cup 2026 Dataset](https://www.viz-optima.com/category/all-products)

**Price: $29.99**

The standard product provides the analysis-ready World Cup 2026 goal-level dataset.

Designed for users who want to perform their own analysis using tools such as:

* Microsoft Excel
* Google Sheets
* Python
* R
* Tableau
* Power BI
* Plotly
* Streamlit

This version is suitable for analysts, students, researchers, football enthusiasts, and visualization developers who primarily need the prepared data.

---

## Product 2 — [World Cup 2026 Dataset + Database Schema](https://www.viz-optima.com/category/all-products)

**Price: $49.99**

The database package includes the World Cup 2026 dataset together with the relational database structure developed for the project.

It is intended for users interested in:

* SQL analysis
* Database development
* Data engineering
* Relational data modeling
* ETL workflows
* BI development
* Application development

The database architecture demonstrates how the original dataset can be transformed into structured analytical tables using relational database principles.

---

# Potential Applications

The dataset can support projects involving:

* Football analytics
* Sports business intelligence
* Goal-scoring analysis
* Player performance analysis
* Match analysis
* Stadium and venue analysis
* Tournament-stage comparisons
* Penalty analysis
* Stoppage-time analysis
* Player-position analysis
* SQL portfolio projects
* Tableau dashboards
* Power BI dashboards
* Python exploratory data analysis
* R statistical analysis
* Plotly Dash applications
* Streamlit applications
* Machine-learning experimentation
* Sports-data education and research

---

# Technology Stack

The project incorporates several technologies across the data lifecycle:

**Data Preparation**

* Microsoft Excel
* Google Sheets

**Database**

* PostgreSQL
* DBeaver
* pgAdmin

**Programming & Analytics**

* SQL
* Python
* R

**Visualization**

* Tableau
* Power BI
* Plotly / Dash
* Streamlit

---

# Data Quality Philosophy

The primary focus of this project is not simply the volume of information collected, but the **structure, consistency, traceability, and analytical usefulness of the data**.

The dataset is designed so that a user can move from a single goal event to broader dimensions such as:

`Goal → Player → Match → Team → Venue → Referee → Tournament Context`

This structure makes the project suitable both as a standalone dataset and as the foundation for more advanced sports-analytics applications.

---

# License & Usage

This repository demonstrates the methodology, structure, and analytical design of the World Cup 2026 project.

The complete commercial dataset and database products are distributed separately by **Vizual Optima LLC**.

Purchasing the dataset provides access according to the licensing terms supplied with the product. Redistribution, resale, or republishing of the complete commercial dataset or database files is not permitted unless explicitly authorized.

---

# About Vizual Optima

**Vizual Optima LLC** provides data analytics and business intelligence solutions, including custom datasets, data visualization, database development, ETL processes, analytics applications, reporting, and data-driven business solutions.

The World Cup 2026 project demonstrates the application of data collection, data engineering, relational database design, and business intelligence principles to a large international sporting event.

---

**Project:** World Cup 2026
**Developer:** Francis Mangala
**Business :** Vizual Optima LLC
**Category:** Sports Analytics / Data Engineering / Business Intelligence
**Status:** Active
