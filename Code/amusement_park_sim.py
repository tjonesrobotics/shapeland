from park import Park
from behavior_reference import BEHAVIOR_ARCHETYPE_PARAMETERS
import sys    

VERSION = "GUI DEVELOPMENT"
VERBOSITY = 0
SHOW_PLOTS = True
RNG_SEED = 5


import readXL
fileName=sys.argv[1]
var, ATTRACTIONS, ACTIVITIES, restaurants, waypoints=readXL.readSimParams(fileName)
for a,b in var:
    locals()[a]=b

PLOT_RANGE = {
    "Attraction Queue Length": 1800,
    "Attraction Wait Time": 200,
    "Attraction Expedited Queue Length": 6000,
    "Attraction Expedited Wait Time": 500,
    "Activity Vistors": 20000,
    "Approximate Agent Distribution (General)": 1.0,
    "Approximate Agent Distribution (Specific)": 1.0,
    "Attraction Average Wait Times": 120,
    "Agent Attractions Histogram": 1.0,
    "Attraction Total Visits": 46000,
    "Expedited Pass Distribution": 150000,
    "Age Class Distribution": 20000,
}

# Initialize Park
RNG_SEED = 5

park = Park(
    attraction_list=ATTRACTIONS,
    activity_list=ACTIVITIES,
    plot_range=PLOT_RANGE,
    random_seed=RNG_SEED,
    version=VERSION,
    verbosity=VERBOSITY
)

# Build Arrivals

park.generate_arrival_schedule(
    arrival_seed=HOURLY_PERCENT, 
    total_daily_agents=TOTAL_DAILY_AGENTS, 
    perfect_arrivals=PERFECT_ARRIVALS,
)

# Build Agents
park.generate_agents(
    behavior_archetype_distribution=AGENT_ARCHETYPE_DISTRIBUTION,
    exp_ability_pct=EXP_ABILITY_PCT,
    exp_wait_threshold=EXP_THRESHOLD,
    exp_limit=EXP_LIMIT
)

# Build Attractions + Activities
park.generate_attractions()
park.generate_activities()

# Pass Time
timeSpentPerActivity={0:{}}
peoplePerActivity={0:{}}
for _ in range(len(HOURLY_PERCENT.keys()) * 60):
    park.step()
    timeSpentPerActivity[park.time] = park.calculate_agents_per_action()
    peoplePerActivity[park.time] = timeSpentPerActivity[park.time].copy()

actionSet=[]
for i in timeSpentPerActivity.values():
    for act in i.keys():
        if act not in actionSet:
            actionSet.append(act)

for time, i1 in peoplePerActivity.items():
    for act in actionSet:
        if act not in i1: i1[act]=0


for time,i1 in timeSpentPerActivity.items():
    for act in actionSet:
        if act not in i1: i1[act]=0
        if time+1 in timeSpentPerActivity:
            i2=timeSpentPerActivity[time+1]
            if act not in i2: i2[act]=0
            i2[act]+=i1[act]
for i in timeSpentPerActivity.values():
    for k in i.keys():
        i[k] /= TOTAL_DAILY_AGENTS


# Save Parameters of Current Run
sim_parameters = {
    "VERSION": VERSION,
    "VERBOSITY": VERBOSITY,
    "SHOW_PLOTS": SHOW_PLOTS,
    "RNG_SEED": RNG_SEED,
    "TOTAL_DAILY_AGENTS": TOTAL_DAILY_AGENTS,
    "PERFECT_ARRIVALS": PERFECT_ARRIVALS,
    "HOURLY_PERCENT": HOURLY_PERCENT,
    "EXP_ABILITY_PCT": EXP_ABILITY_PCT,
    "EXP_THRESHOLD": EXP_THRESHOLD,
    "EXP_LIMIT": EXP_LIMIT,
    "AGENT_ARCHETYPE_DISTRIBUTION": AGENT_ARCHETYPE_DISTRIBUTION,
    "ATTRACTIONS": ATTRACTIONS,
    "ACTIVITIES": ACTIVITIES,
    "BEHAVIOR_ARCHETYPE_PARAMETERS": BEHAVIOR_ARCHETYPE_PARAMETERS,
}
park.write_data_to_file(
    data=sim_parameters, 
    output_file_path=f"{VERSION}/parameters", 
    output_file_format="json"
)


# Store + Print Data
#park.make_plots(show=SHOW_PLOTS)
#park.print_logs(N = 5)
#park.print_logs(selected_agent_ids = [778])

import gui
parkSummary=[["Attendance", "--"],["Average Wait per Ride","--"],["Rides per Person","6"],["Ride-Activity to Wait Time Ratio","0.3"]]
g=gui.GUI_CLASS(PARK_MAP_FILENAME,parkSummary,park,ATTRACTIONS,HOURLY_PERCENT,timeSpentPerActivity,peoplePerActivity)
