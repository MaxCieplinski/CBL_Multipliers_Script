import pandas as pd
from sodapy import Socrata

client = Socrata("data.cityofchicago.org", "MY_PERSONAL_TOKEN")

results = client.get(
    "ijzp-q8t2",
    select="date, primary_type, description",
    limit=9000000
)

df = pd.DataFrame.from_records(results)

df['timestamp'] = pd.to_datetime(df['date'], utc=True)
df['timestamp_london'] = df['timestamp'].dt.tz_convert('Europe/London')

df['year']        = df['timestamp_london'].dt.year
df['weekOfYear']  = df['timestamp_london'].dt.isocalendar().week.astype(int)
df['weekday']     = df['timestamp_london'].dt.dayofweek   # 0 = Monday, 6 = Sunday
df['hour']        = df['timestamp_london'].dt.hour

def map_crime_group(row):
    pt = row['primary_type']
    desc = row['description']

    if pt == 'ROBBERY':
        return 'Person theft'
    if pt == 'THEFT' and desc in ['POCKET-PICKING', 'PURSE-SNATCHING']:
        return 'Person theft'
    if pt == 'THEFT' and desc == 'RETAIL THEFT':
        return 'Commercial theft'
    if pt == 'BURGLARY':
        return 'Residential/Property theft'
    if pt == 'MOTOR VEHICLE THEFT' and desc not in [
        'THEFT / RECOVERY - AUTOMOBILE',
        'THEFT / RECOVERY - TRUCK, BUS, MOBILE HOME',
        'THEFT / RECOVERY - CYCLE, SCOOTER, BIKE WITH VIN',
        'THEFT / RECOVERY - CYCLE, SCOOTER, BIKE NO VIN'
    ]:
        return 'Vehicles'
    if pt == 'NARCOTICS':
        return 'Illegal items'
    if pt == 'WEAPONS VIOLATION' and desc in [
        'UNLAWFUL USE - HANDGUN',
        'UNLAWFUL USE - OTHER FIREARM',
        'UNLAWFUL USE - OTHER DANGEROUS WEAPON',
        'UNLAWFUL POSSESSION - HANDGUN',
        'UNLAWFUL POSSESSION - OTHER FIREARM',
        'UNLAWFUL POSSESSION - AMMUNITION',
        'UNLAWFUL SALE - HANDGUN',
        'UNLAWFUL SALE - OTHER FIREARM',
        'POSSESS FIREARM / AMMUNITION - NO FOID CARD',
        'SALE OF METAL PIERCING BULLETS'
    ]:
        return 'Illegal items'
    if pt == 'CRIMINAL SEXUAL ASSAULT':
        return 'Violence'
    if pt == 'HOMICIDE' and desc in [
        'FIRST DEGREE MURDER',
        'SECOND DEGREE MURDER',
        'INVOLUNTARY MANSLAUGHTER',
        'RECKLESS HOMICIDE'
    ]:
        return 'Violence'
    if pt == 'BATTERY' and desc in [
        'SIMPLE',
        'AGGRAVATED - HANDGUN',
        'AGGRAVATED - OTHER FIREARM',
        'AGGRAVATED - KNIFE / CUTTING INSTRUMENT',
        'AGGRAVATED - OTHER DANGEROUS WEAPON',
        'AGGRAVATED - HANDS, FISTS, FEET, NO / MINOR INJURY',
        'AGGRAVATED - HANDS, FISTS, FEET, SERIOUS INJURY',
        'DOMESTIC BATTERY SIMPLE',
        'AGGRAVATED DOMESTIC BATTERY - HANDGUN',
        'AGGRAVATED DOMESTIC BATTERY - OTHER FIREARM',
        'AGGRAVATED DOMESTIC BATTERY - KNIFE / CUTTING INSTRUMENT',
        'AGGRAVATED DOMESTIC BATTERY - OTHER DANGEROUS WEAPON',
        'AGG. DOMESTIC BATTERY - HANDS, FISTS, FEET, SERIOUS INJURY',
        'AGGRAVATED OF A CHILD',
        'AGGRAVATED OF A SENIOR CITIZEN'
    ]:
        return 'Violence'
    if pt == 'ASSAULT' and desc in [
        'SIMPLE',
        'AGGRAVATED - HANDGUN',
        'AGGRAVATED - OTHER FIREARM',
        'AGGRAVATED - KNIFE / CUTTING INSTRUMENT',
        'AGGRAVATED - OTHER DANGEROUS WEAPON',
        'AGGRAVATED - HANDS, FISTS, FEET, NO INJURY',
        'PROTECTED EMPLOYEE - HANDS, FISTS, FEET, NO / MINOR INJURY'
    ]:
        return 'Violence'
    if pt == 'CRIMINAL DAMAGE' and desc in [
        'TO PROPERTY',
        'TO VEHICLE',
        'CRIMINAL DEFACEMENT',
        'TO STATE SUPPORTED PROPERTY',
        'TO CITY OF CHICAGO PROPERTY',
        'INSTITUTIONAL VANDALISM',
        'LIBRARY VANDALISM',
        'TO FIRE FIGHT.APP.EQUIP'
    ]:
        return 'Social disruption'
    if pt == 'ARSON' and desc in [
        'BY FIRE',
        'BY EXPLOSIVE',
        'AGGRAVATED',
        'ATTEMPT ARSON'
    ]:
        return 'Social disruption'
    if pt == 'PUBLIC PEACE VIOLATION' and desc == 'RECKLESS CONDUCT':
        return 'Social disruption'

    return None  # unmapped — filtered out

df['crimeType'] = df.apply(map_crime_group, axis=1)

df = df[df['crimeType'].notna()][['year', 'weekOfYear', 'weekday', 'hour', 'crimeType']]

df.to_csv('chicago_crimes_mapped.csv', index=False)
print("Saved")