from paraview.simple import *

import os

# Set the path to your OpenFOAM data
case_directory = (os.getcwd())

print("case_directory: ", case_directory)

# Set the range and step size for x-coordinates
x_start = 0.12
x_end = 0.33
x_step = 0.01

# Specify the contour filter parameters
contour_field = "alpha.waterMean"  # Replace with the desired field for contouring
contour_value = 0.5  # Replace with the desired contour value

# Create a list to store results
results = []

# Load your OpenFOAM data
foamfoam = OpenFOAMReader(registrationName='foam.foam', FileName=case_directory + '/foam.foam')
# YourOpenFOAMData = OpenDataFile(case_directory)
foamfoam.MeshRegions = ['internalMesh']
foamfoam.CellArrays = ['U', 'UMean', 'Us', 'UsMean', 'alpha.air', 'alpha.water', 'alpha.waterMean']

# Get the list of available time directories
time_directories = foamfoam.TimestepValues

print("time-step directories are: ", time_directories)

# Loop through all time steps
for time_step in time_directories:
    # Set the active time step
    # foamfoam.TimestepValues = [time_step]

    foamfoam.UpdatePipeline(time_step)

    # Create a contour filter
    contour1 = Contour(Input=foamfoam)
    contour1.ContourBy = ["POINTS", contour_field]
    contour1.Isosurfaces = [contour_value]

    #convert to int
    conv_int = 1000
    # Loop through the desired x-coordinates
    for x_coord_int in range(int(x_start * conv_int), int((x_end + x_step) * conv_int), int(x_step * conv_int)):
        # Create a new slice filter for each x-coordinate
        x_coord = float(x_coord_int/conv_int)
        print("x_coord: ", x_coord)
        slice1 = Slice(registrationName='Slice1', Input=contour1)
        slice1.SliceType.Origin = [x_coord, 0.1, 0.1]
        # slice1.HyperTreeGridSlicer.Origin = [x_coord, 0.1, 0.1]

        slice1.SliceType.Normal = [1.0, 0.0, 0.0]

        # Apply the slice filter
        UpdatePipeline()

        integrateVariables1 = IntegrateVariables(registrationName='IntegrateVariables1', Input=slice1)

        integrateVariables1.DivideCellDataByVolume = 1

        integrated_velocity_data = paraview.servermanager.Fetch(integrateVariables1)

        if integrated_velocity_data  is not None:
            integrated_vel = integrated_velocity_data.GetCellData().GetArray('UsMean').GetValue(0)

        else:
            integrated_vel = 0

        print("integrated velocity: ",integrated_vel)

        # Store the results for this time step
        results.append((time_step, x_coord, integrated_vel))

# Export the results to a CSV file
csv_file = case_directory +'/average_velocity.csv'

with open(csv_file, 'w') as f:
    f.write("Time,X-coordinate,integrated_velocity\n")
    for result in results:
        f.write(f"{result[0]},{result[1]},{result[2]}\n")