# utek2026 - team 2
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

## How to Run Locally

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/your-username/utek-logistics-pro.git](https://github.com/your-username/utek-logistics-pro.git)
    cd utek-logistics-pro
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

---

## Algorithm Details

### 1. The Priority Algorithm
We implemented a custom priority queue that weighs patients based on:


### 2. A* Pathfinding
The drones use the A* search algorithm to find the shortest path between the **Hub** and the **Target Room**. The heuristic used is the **Manhattan Distance**:


### 3. Battery Physics
Battery drain is calculated dynamically per step based on payload weight:
* **< 0.5kg:** 1.0x Drain (Base Rate)
* **2.0 - 5.0kg:** 1.5x Drain
* **> 15.0kg:** 2.0x Drain

---

## Installing the Database
1. Check python and pip versions
    `python --version`
    `pip --version`
2. Install Flask: `pip install Flask`
3. Install psycopg2-binary: `pip install psycopg2-binary`
4. Configure the database: create a new database in PostgreSQL
5. Update the .env file (make sure it's present within .gitignore)
    `DB_USER=your_pg_user
    DB_PASSWORD=your_pg_password
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=your_database_name`
6. Run the database using `flask run`
7. Copy the server into Postman to make HTTP requests
