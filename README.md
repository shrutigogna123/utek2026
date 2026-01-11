# UTEK2026 - Team 2
# Area 1 - Medical Supply Chain Optimization

**An Autonomous Multi-Agent Drone Delivery System for Hospital Logistics.**

## The Problem
Hospitals face critical bottlenecks in internal logistics. Essential items like blood packs, surgical kits, and pharmaceuticals are often delayed by manual portering, elevator traffic, and inefficient routing. This leads to longer patient wait times, higher operational costs, and increased carbon footprints from inefficient delivery methods.

## Our Solution
simulation of an indoor drone fleet. It uses autonomous agents to deliver supplies between key hospital zones (ER, OR, ICU, Pharmacy) while minimizing energy consumption.

### Key Capabilities
* **Multi-Agent Pathfinding:** 3 drones operate simultaneously on a 20x20 grid using **A* (A-Star) Pathfinding** to navigate hallways, avoid walls, and reach specific room coordinates.
* **Smart Triage Logic:** Requests are prioritized not just by time, but by medical urgency (CTAS Level), patient condition, and supply weight. **CTAS 1 (Resuscitation)** cases automatically bypass the queue.
* **Energy (Battery-Life) Based Simulation:** Drones have realistic battery constraints. Heavy payloads (e.g., >15kg) drain battery 2x faster. Drones automatically return to the **Hub** to recharge when low (<30%).
* **Sustainability Tracking:** Real-time calculation of CO₂ emissions saved compared to traditional manual delivery methods.

---

## Dashboard Preview
<img width="944" height="437" alt="image" src="https://github.com/user-attachments/assets/0ef47567-e63a-4e86-bf19-a56b6132a7cd" />

---

## Tech Stack
* **Frontend:** Streamlit (Python)
* **Visualization:** Plotly (Interactive Heatmaps & Scatter Plots)
* **Logic:** NumPy (Grid Management), Heapq (Pathfinding Algorithm)
---

## Project Structure

| File | Description |
| :--- | :--- |
| **`app.py`** | The main controller, handles the Simulation Loop, streamlit rendering, state management for drones, and drone assignment. |
| **`grid.py`** | The map grid, contains the 20x20 floor plan, wall logic, and coordinate targets for rooms (OR, ICU, Maternity, ER, Hub). |
| **`backend.py`** | Defines the `Drone` class, payload weight calculations, and battery drain logic. |
| **`logic.py`** |Contains the **Priority Sorting Algorithms** (Insertion Sort) based on CTAS and Urgency scores. |

---

## Deployed on Streamlit, access via browser:
https://amgq4spfg5j9e4pnku64v9.streamlit.app/

## Run Locally

### Frontend

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/shrutigogna123/utek2026/tree/main
    cd " the repo you cloned "
    ```

2.  **Install Dependencies**
    ```bash
    pip install streamlit pandas numpy plotly
    ```

3.  **Run the App**
    ```bash
    streamlit run app.py
    ```

4.  **View Dashboard**
    Open your browser to `http://localhost:8501`.

### Database

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/shrutigogna123/utek2026/tree/main
    cd database
    ```

2.  **Install Dependencies**
    ```bash
    pip install Flask, psycopg2-binary, SQLAlchemy
    ```

3. **Configure the database:** create a new database in PostgreSQL

4. **Update the .env file** (make sure it's present within .gitignore)
    ```bash
    DB_USER=your_pg_user
    DB_PASSWORD=your_pg_password
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=your_database_name
    ```

5. **Run the database*** using `flask run`

6. Copy the server link into Postman to make HTTP requests

---

## Algorithm Details

### 1. The Priority Algorithm [8], [9]
We implemented a custom priority queue that weighs resource allocation based on:
- **Urgency**: the relative amount of time that the resource is required
- **CTAS Levels**: the critical care the patient requires


### 2. A* Pathfinding
The drones use the A* search algorithm to find the shortest path between the Hub and the Target Room. The heuristic used is the Manhattan Distance.

### 3. Battery Drain Algorithm
Battery drain is calculated dynamically per step based on payload weight:
* **< 0.5kg:** 1.0x Drain (Base Rate)
* **2.0 - 5.0kg:** 1.5x Drain
* **> 15.0kg:** 2.0x Drain

---
## Supplementary file 

### Trial.py
We used file to help visualize the program in a d20x20 bitmap that can runs in the terminal of VScode. This simplifies the movement and decisions of the drones and entails the steps in the process. This file is not used in the intended/main program and is instead used as a guideline, hence it is a supplementary file.

---
## Limitations and Known Issues

### Concurrency in Requests
- Only tested and developed solution to handle one resource request at a time.
- In future: will test with multiple users requesting for resources simultaneously, to accurately reflect the hospital environment

### Instantaneous Updates to Database
- Database schema are not being updated instantaneously
    - Distances of drones to each room needs to be calculated and updated
    - Modifying the quantity of a resource after a completed request
- In future: handle concurrent requests and allow for instantaneous database update
 
---
## References

[1] Streamlit Inc., Streamlit: Turn data scripts into shareable web apps, 2019. [Online]. Available: https://streamlit.io

[2] W. McKinney, pandas: Python Data Analysis Library, 2010. [Online]. Available: https://pandas.pydata.org

[3] C. R. Harris, K. J. Millman, S. J. van der Walt, et al., NumPy: Fundamental package for scientific computing in Python, 2020. [Online]. Available: https://numpy.org

[4] Plotly Technologies Inc., Plotly: Collaborative data visualization, 2015. [Online]. Available: https://plotly.com/python

[5] M. Grinberg, Flask: Web development, one drop at a time, 2018. [Online]. Available: https://flask.palletsprojects.com

[6] O. Kubat, psycopg2-binary: PostgreSQL adapter for Python, 2020. [Online]. Available: https://www.psycopg.org

[7] M. Bayer, SQLAlchemy: Database toolkit for Python, 2006. [Online]. Available: https://www.sqlalchemy.org

[8] Team Medical Supplies, “A Breakdown of Essential Supplies for Every Hospital,” Teammed.com.au, 16 Aug. 2022. [Online]. Available: https://www.teammed.com.au/a-breakdown-of-essential-supplies-for-every-hospital/?srsltid=AfmBOoo3AcL41IO3aM3k1mjcuaLB8BmMMC1dlin2L3R45RRhYk2qyxBW. [Accessed: 10-Jan-2026]. :contentReference[oaicite:0]{index=0}

[9] R. Regua, “The Comprehensive Guide to Delivering Medical Supplies,” Detrack.com, 2023. [Online]. Available: https://www.detrack.com/blog/delivering-medical-supplies/. [Accessed: 10-Jan-2026]. :contentReference[oaicite:1]{index=1}
