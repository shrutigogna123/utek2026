# imports
import streamlit as st
import pandas as pd
import numpy as np
import uuid
import time
import heapq
import plotly.graph_objects as go
import backend
import grid as map_data
import logic  

st.set_page_config(layout="wide", page_title="Medical Supply Chain Optimization", page_icon="")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    div.stButton > button { background-color: #ff4b4b; color: white; border-radius: 5px; width: 100%; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #4CAF50; }
</style>
""", unsafe_allow_html=True)


# init state
if 'init' not in st.session_state:
    st.session_state.init = True
    st.session_state.grid = map_data.create_floor_plan()
    st.session_state.tasks = []
    st.session_state.batch_stage = []
    st.session_state.logs = []
    st.session_state.co2_saved = 0.0
    
    
    drone_init = [(1, 0), (2, 1), (1, 2)]
    d_objs = [backend.Drone(f"D{i+1}") for i in range(3)]
    
    for i, d in enumerate(d_objs):
        r, c = drone_init[i]
        d.xposition = c
        d.yposition = r
        d.battery = 100.0

    st.session_state.drones = [
        {"id": f"D{i+1}", "obj": d_objs[i], "pos": list(drone_init[i]), "bat": 100.0, "status": "IDLE", "path": []}
        for i in range(3)
    ]

# pathfinding helpers
def get_neighbors(pos):
    r, c = pos
    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
        nr, nc = r+dr, c+dc
        if map_data.is_walkable(st.session_state.grid, nr, nc):
            yield (nr, nc)

# implemented the A* algorithm to find the shortest path
def find_path(start, end):
    # assign tasks to idle drones
    start, end = tuple(start), tuple(end)
    pq = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    while pq:
        _, current = heapq.heappop(pq)
        if current == end: break
        
        for next_node in get_neighbors(current):
            new_cost = cost_so_far[current] + 1
            if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                prio = new_cost + abs(end[0]-next_node[0]) + abs(end[1]-next_node[1])
                heapq.heappush(pq, (prio, next_node))
                came_from[next_node] = current
                cost_so_far[next_node] = new_cost
    
    if end not in came_from: return []
    path = []
    curr = end
    while curr != start:
        path.append(curr)
        curr = came_from[curr]
    return path[::-1]

# drone movement
def update_simulation():
   # multiple deliveries parallely
    avail_indices = [i for i, d in enumerate(st.session_state.drones) if d['status'] == 'IDLE' and d['obj'].battery > 30]
    
    if st.session_state.tasks and hasattr(logic, 'prioritize_patients'):
        st.session_state.tasks = logic.prioritize_patients(st.session_state.tasks)
    elif st.session_state.tasks: 
        st.session_state.tasks.sort(key=lambda x: x['priority'])

    while st.session_state.tasks and avail_indices:
        task = st.session_state.tasks.pop(0)
        d_idx = avail_indices.pop(0)
        drone = st.session_state.drones[d_idx]
        d_obj = drone['obj']
        
        hub_center = map_data.TARGETS["Hub"]
        target_loc = map_data.TARGETS[task['target']]
        
        # pickup
        p1 = []
        curr_r, curr_c = int(drone['pos'][0]), int(drone['pos'][1])
        if st.session_state.grid[curr_r, curr_c] != map_data.ID_HUB:
             p1 = find_path(drone['pos'], hub_center)
        
        # hub to dest
        start_node = p1[-1] if p1 else drone['pos']
        p2 = find_path(start_node, target_loc)
        
        if not p2 and start_node != target_loc:
             st.session_state.logs.append(f"Path failed for {task['target']}")
             continue

        drone['path'] = p1 + p2
        drone['status'] = f"DELIVERING: {task['item']}"
        
        s = backend.Supply(task['item'], task['weight'])
        d_obj.load_supply(s)
        st.session_state.logs.append(f"{drone['id']} dispatched -> {task['target']}")

    # drone states
    any_moving = False
    
    for d in st.session_state.drones:
        d_obj = d['obj']
        curr_r, curr_c = int(d['pos'][0]), int(d['pos'][1])
        in_hub = (st.session_state.grid[curr_r, curr_c] == map_data.ID_HUB)

        # moving?
        if d['path']:
            any_moving = True
            next_step = d['path'].pop(0)
            
            # update backend
            dy = next_step[0] - d_obj.yposition
            dx = next_step[1] - d_obj.xposition
            dirs = {(0,1):"right", (0,-1):"left", (1,0):"down", (-1,0):"up"}
            cmd = dirs.get((dy, dx))
            
            if cmd:
                d_obj.set_command(cmd)
                d_obj.update()
            
            d['pos'] = [d_obj.yposition, d_obj.xposition]
            d['bat'] = d_obj.battery
            st.session_state.co2_saved += 0.05
            
            continue 

        # task done
        if d['status'].startswith("DELIVERING"):
            d['status'] = "IDLE"
            d_obj.unload_supply()
            st.session_state.logs.append(f"{d['id']} Arrived at Destination.")

        # return
        elif d['status'] == "RETURNING":
            d['status'] = "IDLE"
            st.session_state.logs.append(f"{d['id']} Returned to Base.")

        # returning/charging
        elif d['status'] == "IDLE" or d['status'] == "CHARGING":
            
            # if at hub and battery low then CHARGE
            if in_hub and d_obj.battery < 100:
                d['status'] = "CHARGING"
                d_obj.battery = min(100, d_obj.battery + 2.0)
                d['bat'] = d_obj.battery
            
            # if at hub and battery full then IDLE
            elif in_hub and d_obj.battery >= 100:
                d['status'] = "IDLE"
            
            # if not at hub and battery low then RETURN
            elif not in_hub and d_obj.battery < 30:
                d['path'] = find_path(d['pos'], map_data.TARGETS["Hub"])
                d['status'] = "RETURNING"
                st.session_state.logs.append(f"{d['id']} Battery Low (<30% remaining). Returning to hub.")

    return any_moving

# frontend built with streamlit
st.title("Medical Supply Chain Optimization")

with st.sidebar:
    st.header("Dispatch Resources")
    mode = st.radio("Mode", ["Single", "Batch"], horizontal=True)
    
    with st.form("dispatch"):
        item = st.text_input("Item", "Medical Supplies")
        
        # location input
        dest_options = [k for k in map_data.TARGETS.keys() if k != "Hub"]
        target = st.selectbox("Destination", dest_options)
        
        # urgency
        urgency_map = {
            1: "1 - Low (30-60 min)",
            2: "2 - Moderate (15-30 min)",
            3: "3 - High (8-15 min)",
            4: "4 - Severe (4-8 min)",
            5: "5 - Life-Critical (0-4 min)"
        }
        urgency_display = st.select_slider("Urgency Level", options=list(urgency_map.keys()), format_func=lambda x: urgency_map[x])
        
        # CTAS values
        ctas = st.slider("CTAS Level (1=Resuscitation)", 1, 5, 3)

        # weight class
        
        weight_classes = {
            1: ("<0.5kg", 0.4),
            2: ("0.5-2kg", 1.5),
            3: ("2-5kg", 3.5),
            4: ("5-15kg", 10.0),
            5: ("15-50kg", 30.0),
            6: (">50kg", 60.0)
        }
        w_class = st.selectbox("Weight Class", options=list(weight_classes.keys()), format_func=lambda x: f"Class {x}: {weight_classes[x][0]}")
        
        if st.form_submit_button("Submit"):
            
            real_weight = weight_classes[w_class][1]
            
            payload = {
                "id": str(uuid.uuid4())[:4],
                "item": item,
                "target": target,
                "urgency": urgency_display, 
                "ctas": ctas,               
                "supply_weight": w_class,   
                "weight": real_weight,      
                "location": target,         
                "arrival_time": time.time() 
            }
            
            if mode == "Single":
                st.session_state.tasks.append(payload)
                # sorting
                st.session_state.tasks = logic.prioritize_patients(st.session_state.tasks)
                st.success("Queued & Prioritized.")
            else:
                st.session_state.batch_stage.append(payload)
                st.success("Added to Batch")

    if mode == "Batch" and st.session_state.batch_stage:
        st.info(f"Staged: {len(st.session_state.batch_stage)} tasks")
        if st.button("Launch as Batch"):
            st.session_state.tasks.extend(st.session_state.batch_stage)
            # sort whole batch
            st.session_state.tasks = logic.prioritize_patients(st.session_state.tasks)
            st.session_state.batch_stage = []
            st.rerun()

    st.divider()
    run = st.toggle("See Simulation", value=False)
    
    if st.button("RESET"):
        st.session_state.clear()
        st.rerun()

# tabs
tab1, tab2, tab3 = st.tabs(["Floor Plan", "Queues", "Drone Status"])

with tab1:
    col_viz, col_data = st.columns([3, 1])
    
    with col_viz:
        fig = go.Figure()

        # map as trace
        fig.add_trace(go.Heatmap(z=st.session_state.grid, colorscale=map_data.COLOR_MAP, showscale=False, hoverinfo='skip'))

        # add label
        fig.add_trace(go.Scatter(
            x=[l['x'] for l in map_data.LABELS], 
            y=[l['y'] for l in map_data.LABELS],
            text=[l['txt'] for l in map_data.LABELS],
            mode="text", textfont=dict(color="white", size=14, family="Arial Black")
        ))

        # draw paths
        for d in st.session_state.drones:
            if d['path']:
                px = [d['pos'][1]] + [p[1] for p in d['path']]
                py = [d['pos'][0]] + [p[0] for p in d['path']]
                fig.add_trace(go.Scatter(x=px, y=py, mode='lines', line=dict(color='#00FF00', width=2, dash='dot'), hoverinfo='skip'))

        # drones
        dx = [d['pos'][1] for d in st.session_state.drones]
        dy = [d['pos'][0] for d in st.session_state.drones]
        c_map = {"IDLE":"#00FF00", "CHARGING":"#00FFFF"}
        colors = [c_map.get(d['status'], "#FFA500") for d in st.session_state.drones]

        fig.add_trace(go.Scatter(
            x=dx, y=dy, mode='markers+text',
            marker=dict(size=20, color=colors, line=dict(width=2, color='white')),
            text=[f"{d['id']}" for d in st.session_state.drones],
            textposition="top center", textfont=dict(color="white")
        ))

        fig.update_layout(height=650, margin=dict(l=0, r=0, t=0, b=0), yaxis=dict(autorange='reversed', visible=False, scaleanchor="x"), xaxis=dict(visible=False), plot_bgcolor='#0e1117', paper_bgcolor='#0e1117')
        st.plotly_chart(fig, width="stretch")

    with col_data:
        st.subheader("Live Stats")
        st.metric("Queue", len(st.session_state.tasks))
        st.metric("CO₂ Saved", f"{st.session_state.co2_saved:.2f}g")
        log_box = st.container(height=350)
        for l in reversed(st.session_state.logs[-10:]):
            log_box.caption(l)

with tab2:
    # display queue with new priority fields
    if st.session_state.tasks:
        df = pd.DataFrame(st.session_state.tasks)[['id', 'item', 'target', 'ctas', 'urgency', 'supply_weight']]
        st.dataframe(df, width="stretch")
    else:
        st.info("No tasks in queue")

with tab3:
    cols = st.columns(3)
    for i, d in enumerate(st.session_state.drones):
        with cols[i]:
            bat = d['bat']
            color = "green" if bat > 50 else "red"
            st.metric(f"{d['id']}", f"{int(bat)}%")
            st.progress(int(bat)/100)
            st.caption(d['status'])

if run:
    update_simulation()
    time.sleep(0.1)
    st.rerun()