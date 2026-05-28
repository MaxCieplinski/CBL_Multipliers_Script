import pandas as pd
import numpy as np

df = pd.read_csv('chicago_crimes_mapped.csv')

# Time of week: 0 = Monday 00:00, 167 = Sunday 23:00
df['time_of_week'] = df['weekday'] * 24 + df['hour']

# All 168 hours of the week
all_hours = np.arange(168)

# Kernel width from Prieto Curiel 2021
omega = 1.48

# Compute heartbeat for each crime group
heartbeat = {}

for crime_group in df['crimeType'].unique():
    
    # Get all time-of-week values for this crime group
    times = df[df['crimeType'] == crime_group]['time_of_week'].values
    
    # Compute H(t) for each of the 168 hours - vecotorized (fast)
    diff = all_hours[:, None] - times[None, :]
    H = np.exp(-0.5 * (diff / omega) ** 2).sum(axis=1)
    
    # Normalise to sum to 1
    H = H / H.sum()
    heartbeat[crime_group] = H

# Weekday weights
weekday_rows = []
for day_num, day_name in enumerate(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']):
    row = {'day': day_name}
    for crime_group in heartbeat:
        # Sum the 24 hours belonging to this day
        day_total = heartbeat[crime_group][day_num*24 : day_num*24+24].sum()
        row[crime_group] = day_total
        
    weekday_rows.append(row)

weekday_df = pd.DataFrame(weekday_rows).set_index('day')

# Normalise each column to sum to 1
weekday_df = weekday_df.div(weekday_df.sum(axis=0), axis=1)

# hourly weights
hourly_rows = []
for h in range(24):
    row = {'hour': h}
    for crime_group in heartbeat:
        # Average this hour across all 7 days
        same_hour_all_days = [heartbeat[crime_group][h + day*24] for day in range(7)]
        row[crime_group] = np.mean(same_hour_all_days)
    hourly_rows.append(row)

hourly_df = pd.DataFrame(hourly_rows).set_index('hour')

# Normalise each column to sum to 1
hourly_df = hourly_df.div(hourly_df.sum(axis=0), axis=1)


print("\nWEEKDAY WEIGHTS:")
print(weekday_df.round(4))

print("\nHOURLY WEIGHTS:")
print(hourly_df.round(4))

weekday_df.round(4).to_csv('weekday_weights.csv')
hourly_df.round(4).to_csv('hourly_weights.csv')
print("\nSaved.")