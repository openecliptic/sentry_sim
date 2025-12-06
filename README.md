# ☀️ Sentry Node: Advanced PV Physics Engine

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Prototype-orange)

> **"Transitioning from raw light harvesting to knowledge-based energy management."**

## 📖 Overview

**Sentry Node** is not just a monitoring tool; it is a **physics-based simulation engine** designed to model, analyze, and optimize photovoltaic (PV) farm performance under extreme climatic conditions (e.g., dust storms, high angular losses).

Unlike standard commercial software (like PVsyst) that often relies on linear loss factors, this engine solves **differential equations** governing semiconductor behavior and optical physics to simulate the dynamic response of a "Smart Tracking System" vs. a "Static System."

This repository contains the core simulation logic (`DustyDaySimulator.py`) used to validate the Sentry hardware architecture.

## 🚀 Key Features

* **🧪 Physics-First Approach:** Uses the **Martin-Ruiz Model** for accurate optical loss calculation, not generic approximations.
* **🌪️ Stochastic Storm Modeling:** Simulates real-time dust accumulation and "Cloud Events" using randomized noise functions to test system resilience.
* **📐 Dynamic Geometry:** Calculates precise solar azimuth and elevation to simulate single-axis tracking gains using the Cosine Law.
* **🧠 AI-Cleaning Logic:** Implements a threshold-based algorithm to trigger cleaning cycles only when economically viable (minimizing water usage).

## 🧮 The Physics Behind The Code

The core of this simulation relies on rigorous mathematical modeling:

### 1. Optical Losses (IAM) - The Martin-Ruiz Model
[cite_start]To account for non-linear reflection losses at high incidence angles (especially in static panels), we implemented the Martin-Ruiz model[cite: 58]:

$$IAM(\theta) = 1 - a_r \cdot \left( \frac{1}{\cos(\theta)} - 1 \right) - a_{coupling} \cdot \sin(\theta)$$

Where:
* $\theta$ is the incidence angle.
* $a_r$ is the angular loss coefficient.
* This model captures the "mirror effect" of glass at angles $>60^\circ$.

### 2. Geometric Gain (Cosine Law)
The power generated is directly proportional to the cosine of the incidence angle. Sentry utilizes a tracking algorithm to keep $\theta \approx 0$:

$$P_{inc} = DNI \cdot \cos(\theta_{incidence})$$

### 3. Thermal Dynamics
Cell temperature ($T_{cell}$) is calculated dynamically based on ambient temperature, wind speed, and POA (Plane of Array) irradiance to determine thermal efficiency losses.

## 📊 Simulation Results

Running the `DustyDaySimulator.py` generates a comprehensive performance report.

**Scenario:** A typical summer day in the Iranian Central Plateau with a severe mid-day dust storm.

| Metric | Static System (Legacy) | Sentry Node (AI + Tracker) |
| :--- | :--- | :--- |
| **Angle Strategy** | Fixed ($30^\circ$ South) | Active Tracking |
| **Cleaning** | None (Accumulated Soiling) | AI-Triggered (Spot Cleaning) |
| **Resilience** | Failed (Optical Choking) | **Stable Operation** |
| **Total Energy Gain** | - | **+115.3%** (in storm conditions) |

*(Note: The 115% gain represents a critical stress test scenario. Annual nominal gain is estimated between 25-35%.)*

## 🛠️ Installation & Usage

### Prerequisites
You need Python installed along with the scientific stack:

```bash
pip install numpy matplotlib
```
Running the Simulation
Simply run the main script to visualize the physics engine in action:
```python
python DustyDaySimulator.py
```
👨‍💻 Author: 
Martin Weysi, Physics Researcher & Developer at Ecliptic Energy Innovations.

Copyright © 2025 Ecliptic Energy Innovations.


---
