# app.py

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict
from PIL import Image
import matplotlib.pyplot as plt

from src.models import TrafficData, ClimateData, SubgradeProperties, MaterialProperties, Pavement
from src.performance import design_new_pavement
from src.lcca import perform_LCCA
from src.reporting import generate_report, export_report_to_pdf
from src.design import design_pavement_structure
from src.utils.helpers import read_excel, save_pdf
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

st.set_page_config(page_title="ME Pavement Design Tool", layout="wide")

st.title("🛣️ Mechanistic-Empirical Pavement Design Tool for Highways and Airports")

image = Image.open('Pavement.jpg')

# Display the image at the top of the sidebar
st.sidebar.image(image, use_container_width=True)

# Sidebar for Navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.selectbox("Choose the app mode",
                                ["Home", "Input Data", "Design Pavement", "Run Simulation", "View Results", "Generate Report"])

# Initialize session state
if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = {}
if 'lcc' not in st.session_state:
    st.session_state.lcc = 0.0
if 'maintenance_costs' not in st.session_state:
    st.session_state.maintenance_costs = {}
if 'lcc_over_time' not in st.session_state:
    st.session_state.lcc_over_time = {}
if 'pavement_design' not in st.session_state:
    st.session_state.pavement_design = {}

# Home Page
if app_mode == "Home":
    st.markdown("""
    ## Welcome to the Mechanistic-Empirical Pavement Design Tool

    This tool allows you to design new pavements and evaluate their performance based on traffic, material, and environmental data. Follow the navigation steps on the sidebar to input data, design pavement structures, run simulations, view results, and generate comprehensive reports.
    """)

# Input Data Page
elif app_mode == "Input Data":
    st.header("Input Data")

    st.markdown("""
    ### 📋 Dataset Format Instructions
    
    Please ensure that your Excel file contains the following sheets with the specified columns like the example dataset.

    **Example Dataset**:
    
    - **Traffic Sheet**:
    
        | Axle_Loads | Traffic_Growth_Rate | Analysis_Period |
        |------------|---------------------|------------------|
        | 80         | 2.0                 | 20               |
        | 100        |                     |                  |
        | 120        |                     |                  |
    
    - **Climate Sheet**:
    
        | Average_Temperature | Temperature_Variation | Rainfall |
        |---------------------|-----------------------|----------|
        | 15                  | 10                    | 500      |
    
    - **Subgrade Sheet**:
    
        | Modulus | CBR |
        |---------|-----|
        | 3000    | 10  |
    
    - **Materials Sheet**:
    
        | Asphalt_Modulus | Concrete_Strength | Thermal_Coeff |
        |-----------------|--------------------|---------------|
        | 3000            | 30                 | 0.0001        |
    """)

    st.subheader("Upload Input Data Excel File")
    uploaded_file = st.file_uploader("Choose an Excel file with required data", type=["xlsx"])

    if uploaded_file:
        try:
            data_sheets = read_excel(uploaded_file)
            # Assuming sheets named 'Traffic', 'Climate', 'Subgrade', 'Materials'
            traffic_df = data_sheets.get('Traffic') or data_sheets.get('Sheet1')  # Fallback to first sheet
            climate_df = data_sheets.get('Climate') or data_sheets.get('Sheet2')
            subgrade_df = data_sheets.get('Subgrade') or data_sheets.get('Sheet3')
            materials_df = data_sheets.get('Materials') or data_sheets.get('Sheet4')

            # Create data model instances
            traffic_data = TrafficData.from_dataframe(traffic_df)
            climate_data = ClimateData.from_dataframe(climate_df)
            subgrade_props = SubgradeProperties.from_dataframe(subgrade_df)
            material_props = MaterialProperties.from_dataframe(materials_df)

            # Store in session state
            st.session_state.traffic_data = traffic_data
            st.session_state.climate_data = climate_data
            st.session_state.subgrade_props = subgrade_props
            st.session_state.material_props = material_props

            st.success("Data loaded successfully from the uploaded Excel file.")
        except Exception as e:
            st.error(f"Failed to load data: {e}")

    st.markdown("""
    ### Alternatively, Enter Data Manually
    """)

    with st.form("manual_data_form"):
        st.subheader("Traffic Data")
        axle_loads = st.text_input("Axle Loads (comma-separated in kN)", value="80, 100, 120")
        traffic_growth_rate = st.number_input("Traffic Growth Rate (% per annum)", min_value=0.0, max_value=100.0, value=2.0, step=0.1)
        analysis_period = st.number_input("Analysis Period (Years)", min_value=1, max_value=100, value=20, step=1)

        st.subheader("Climate Data")
        average_temperature = st.number_input("Average Temperature (°C)", value=15.0)
        temperature_variation = st.number_input("Temperature Variation (°C)", value=10.0)
        rainfall = st.number_input("Annual Rainfall (mm)", value=500.0)

        st.subheader("Subgrade Properties")
        modulus = st.number_input("Modulus of Subgrade Reaction (kPa/m)", value=3000.0)
        CBR = st.number_input("California Bearing Ratio (CBR %)", value=10.0)

        st.subheader("Material Properties")
        asphalt_modulus = st.number_input("Asphalt Modulus (MPa)", value=3000.0)
        concrete_strength = st.number_input("Concrete Strength (MPa)", value=30.0)
        thermal_coeff = st.number_input("Thermal Coefficient (°C^-1)", value=0.0001)

        submitted = st.form_submit_button("Submit Data")
        if submitted:
            try:
                axle_loads_list = [float(load.strip()) for load in axle_loads.split(",")]
                traffic_data = TrafficData(axle_loads=axle_loads_list,
                                           traffic_growth_rate=traffic_growth_rate / 100,
                                           analysis_period=int(analysis_period))
                climate_data = ClimateData(average_temperature=average_temperature,
                                           temperature_variation=temperature_variation,
                                           rainfall=rainfall)
                subgrade_props = SubgradeProperties(modulus=modulus, CBR=CBR)
                material_props = MaterialProperties(asphalt_modulus=asphalt_modulus,
                                                   concrete_strength=concrete_strength,
                                                   thermal_coeff=thermal_coeff)

                # Store in session state
                st.session_state.traffic_data = traffic_data
                st.session_state.climate_data = climate_data
                st.session_state.subgrade_props = subgrade_props
                st.session_state.material_props = material_props

                st.success("Data entered successfully.")
            except Exception as e:
                st.error(f"Error in data entry: {e}")


# Design Pavement Page
elif app_mode == "Design Pavement":
    st.header("Design Pavement Structure")

    if ('traffic_data' in st.session_state and 
        'climate_data' in st.session_state and 
        'subgrade_props' in st.session_state and 
        'material_props' in st.session_state):

        st.subheader("Define Pavement Layers")
        with st.form("pavement_design_form"):
            # User inputs the number of pavement layers
            num_layers = st.number_input(
                "Number of Pavement Layers", 
                min_value=1, 
                max_value=10, 
                value=3, 
                step=1,
                help="Specify the total number of pavement layers you wish to design."
            )

            layers = []
            st.markdown("### Define Each Layer")
            for i in range(1, int(num_layers) + 1):
                st.markdown(f"**Layer {i}**")
                
                # Select layer type
                layer_type = st.selectbox(
                    f"Layer {i} Type", 
                    options=["Asphalt", "Concrete", "Base", "Sub-base"], 
                    key=f"layer_type_{i}",
                    help="Select the material type for this pavement layer."
                )
                
                # Input layer thickness
                thickness = st.number_input(
                    f"Layer {i} Thickness (mm)", 
                    min_value=1.0, 
                    max_value=1000.0, 
                    value=100.0, 
                    step=1.0, 
                    key=f"layer_thickness_{i}",
                    help="Enter the thickness of this layer in millimeters."
                )
                
                layers.append((layer_type, thickness))  # Store as tuple

            st.markdown("### Define Cost per Layer Type")
            st.write("Enter the cost per millimeter for each layer type. These costs will be used to calculate the total estimated cost of the pavement.")

            # Input costs for each layer type
            asphalt_cost = st.number_input(
                "Asphalt Cost per mm ($)", 
                min_value=0.0, 
                value=50.0, 
                step=1.0,
                help="Enter the cost per millimeter for Asphalt layers."
            )
            concrete_cost = st.number_input(
                "Concrete Cost per mm ($)", 
                min_value=0.0, 
                value=80.0, 
                step=1.0,
                help="Enter the cost per millimeter for Concrete layers."
            )
            base_cost = st.number_input(
                "Base Cost per mm ($)", 
                min_value=0.0, 
                value=40.0, 
                step=1.0,
                help="Enter the cost per millimeter for Base layers."
            )
            subbase_cost = st.number_input(
                "Sub-base Cost per mm ($)", 
                min_value=0.0, 
                value=30.0, 
                step=1.0,
                help="Enter the cost per millimeter for Sub-base layers."
            )

            # Submit button to define pavement structure
            submitted = st.form_submit_button("Define Pavement Structure")
            if submitted:
                try:
                    # Create a dictionary for layer costs based on user input
                    layer_costs = {
                        "Asphalt": asphalt_cost,
                        "Concrete": concrete_cost,
                        "Base": base_cost,
                        "Sub-base": subbase_cost
                    }

                    # Store pavement design and layer costs in session state
                    st.session_state.pavement_design = layers
                    st.session_state.layer_costs = layer_costs
                    st.success("Pavement structure defined successfully.")
                except Exception as e:
                    st.error(f"Error in pavement design: {e}")

        if 'pavement_design' in st.session_state and 'layer_costs' in st.session_state:
            st.subheader("Pavement Design Summary")
            design_summary = st.session_state.pavement_design
            layer_costs = st.session_state.layer_costs

            # Perform Calculations Based on User Input
            total_thickness = sum([thickness for _, thickness in design_summary])
            total_cost = sum([layer_costs.get(layer_type, 0) * thickness for layer_type, thickness in design_summary])

            # Predict Distresses (Simplified Example Formulas)
            fatigue_cracking = total_thickness * 0.05  # Placeholder formula
            rutting = total_thickness * 0.03
            thermal_cracking = total_thickness * 0.02

            # Display Calculation Results
            st.write(f"**Total Pavement Thickness:** {total_thickness} mm")
            st.write(f"**Estimated Total Cost:** ${total_cost:,.2f}")
            st.write(f"**Predicted Fatigue Cracking:** {fatigue_cracking:.2f} cracks")
            st.write(f"**Predicted Rutting:** {rutting:.2f} mm")
            st.write(f"**Predicted Thermal Cracking:** {thermal_cracking:.2f} cracks")

            st.subheader("Detailed Pavement Layers")
            design_df = pd.DataFrame(design_summary, columns=["Layer Type", "Thickness (mm)"])
            st.table(design_df)

            # Optional: Visual Representation of Pavement Layers
            st.markdown("### Pavement Structure Visualization")
            fig, ax = plt.subplots(figsize=(6, 3))
            current_y = 0
            for layer_type, thickness in design_summary:
                ax.barh(1, thickness, left=current_y, height=0.5, label=layer_type)
                current_y += thickness
            ax.set_xlabel("Thickness (mm)")
            ax.set_yticks([])
            ax.legend()
            st.pyplot(fig)


# Run Simulation Page
elif app_mode == "Run Simulation":
    st.header("Run Simulation")

    if 'pavement_design' in st.session_state and 'traffic_data' in st.session_state and 'climate_data' in st.session_state and \
       'subgrade_props' in st.session_state and 'material_props' in st.session_state:

        st.subheader("Simulation Parameters")
        with st.form("simulation_parameters_form"):
            initial_cost = st.number_input("Initial Construction Cost ($)", min_value=0.0, value=1000000.0, step=1000.0)
            maintenance_costs_input = st.text_area("Maintenance Costs (Year:Cost, separated by commas)", 
                                                   value="5:100000, 10:150000, 15:200000, 20:250000")
            discount_rate = st.number_input("Discount Rate (% per annum)", min_value=0.0, max_value=100.0, value=3.0, step=0.1)
            analysis_period = st.number_input("Lifecycle Analysis Period (Years)", min_value=1, max_value=100, value=20, step=1)

            submitted = st.form_submit_button("Run Simulation")
            if submitted:
                try:
                    # Parse maintenance costs
                    maintenance_costs = {}
                    for item in maintenance_costs_input.split(","):
                        if ':' in item:
                            year, cost = item.strip().split(":")
                            maintenance_costs[int(year)] = float(cost)
                        else:
                            st.warning(f"Ignoring invalid maintenance cost entry: '{item}'")

                    # Retrieve data from session state
                    pavement_design = st.session_state.pavement_design
                    traffic_data = st.session_state.traffic_data
                    climate_data = st.session_state.climate_data
                    subgrade_props = st.session_state.subgrade_props
                    material_props = st.session_state.material_props

                    # Run simulation
                    simulation_results = design_new_pavement(pavement_design, traffic_data, climate_data, subgrade_props, material_props)
                    st.session_state.simulation_results = simulation_results

                    # Perform LCCA
                    lcc = perform_LCCA(initial_cost, maintenance_costs, discount_rate / 100, analysis_period)
                    st.session_state.lcc = lcc
                    st.session_state.maintenance_costs = maintenance_costs

                    # Calculate LCCA over time for visualization
                    lcc_over_time = []
                    cumulative_lcc = initial_cost
                    for year in range(1, analysis_period + 1):
                        maintenance_cost = maintenance_costs.get(year, 0)
                        discounted_cost = maintenance_cost / ((1 + discount_rate / 100) ** year)
                        cumulative_lcc += discounted_cost
                        lcc_over_time.append(cumulative_lcc)
                    st.session_state.lcc_over_time = lcc_over_time

                    st.success("Simulation and LCCA completed successfully.")

                except Exception as e:
                    st.error(f"Error during simulation: {e}")
    else:
        st.warning("Please input the necessary data in the 'Input Data' and 'Design Pavement' sections before running simulations.")

# View Results Page
elif app_mode == "View Results":
    st.header("Simulation Results")

    if 'simulation_results' in st.session_state and st.session_state.simulation_results:
        simulation_results = st.session_state.simulation_results
        lcc = st.session_state.lcc
        maintenance_costs = st.session_state.maintenance_costs
        lcc_over_time = st.session_state.lcc_over_time

        st.subheader("Pavement Performance Predictions")
        df_results = pd.DataFrame(list(simulation_results.items()), columns=["Distress Type", "Value"])
        st.table(df_results)

        st.subheader("Lifecycle Cost Analysis (LCCA)")
        st.write(f"**Total Lifecycle Cost:** ${lcc:,.2f}")

        # Visualization 1: Pie Chart of Distress Types
        st.subheader("Distribution of Pavement Distresses")
        pie_chart_data = df_results.set_index('Distress Type')
        st.pyplot(pie_chart_data.plot.pie(y='Value', autopct='%1.1f%%', figsize=(6, 6)).figure)

        # Visualization 2: Bar Chart of Distress Types
        st.subheader("Pavement Distresses Overview")
        st.bar_chart(df_results.set_index('Distress Type'))

        # Visualization 3: Line Chart of Lifecycle Cost Over Time
        if lcc_over_time:
            st.subheader("Lifecycle Cost Over Time")
            years = list(range(1, len(lcc_over_time) + 1))
            cost_data = pd.DataFrame({
                'Year': years,
                'Cumulative LCC': lcc_over_time
            })
            st.line_chart(cost_data.set_index('Year'))

            # Detailed Breakdown Table
            st.subheader("Maintenance Costs Over Time")
            maintenance_df = pd.DataFrame({
                'Year': list(maintenance_costs.keys()),
                'Maintenance Cost ($)': list(maintenance_costs.values())
            }).sort_values('Year')
            st.table(maintenance_df)

            # Visualization 4: Line Chart of Cumulative LCCA
            st.subheader("Cumulative Lifecycle Cost Analysis")
            st.line_chart(cost_data.set_index('Year'))

        # Visualization 5: Comparison of Initial Cost vs LCCA
        st.subheader("Initial Cost vs Total Lifecycle Cost")
        initial_cost = st.session_state.get('initial_cost', 0)
        comparison_df = pd.DataFrame({
            'Cost Type': ['Initial Construction Cost', 'Total Lifecycle Cost'],
            'Amount ($)': [initial_cost, lcc]
        })
        st.bar_chart(comparison_df.set_index('Cost Type'))

        # Additional Visualization: Pie Chart of Maintenance Cost Distribution
        if maintenance_costs:
            st.subheader("Maintenance Cost Distribution")
            maintenance_df_pie = pd.DataFrame({
                'Year': list(maintenance_costs.keys()),
                'Maintenance Cost ($)': list(maintenance_costs.values())
            }).sort_values('Year')
            st.pyplot(maintenance_df_pie.plot.pie(y='Maintenance Cost ($)', labels=maintenance_df_pie['Year'], autopct='%1.1f%%', figsize=(6,6)).figure)

        # Pavement Design Results
        if 'pavement_design' in st.session_state and st.session_state.pavement_design:
            st.subheader("Pavement Design Results")
            pavement_design = st.session_state.pavement_design
            design_df = pd.DataFrame(pavement_design, columns=["Layer Type", "Thickness (mm)"])
            st.table(design_df)

    else:
        st.warning("No simulation results to display. Please run a simulation first.")

# Generate Report Page
elif app_mode == "Generate Report":
    st.header("Generate Report")

    if 'simulation_results' in st.session_state and st.session_state.simulation_results and \
       'lcc' in st.session_state and st.session_state.lcc > 0 and \
       'maintenance_costs' in st.session_state and st.session_state.maintenance_costs:
        simulation_results = st.session_state.simulation_results
        lcc = st.session_state.lcc
        maintenance_costs = st.session_state.maintenance_costs
        lcc_over_time = st.session_state.lcc_over_time

        st.subheader("Review Results Before Report Generation")
        df_results = pd.DataFrame(list(simulation_results.items()), columns=["Distress Type", "Value"])
        st.table(df_results)
        st.write(f"**Lifecycle Cost Analysis (LCCA):** ${lcc:,.2f}")

        st.subheader("Maintenance Costs Breakdown")
        maintenance_df = pd.DataFrame({
            'Year': list(maintenance_costs.keys()),
            'Maintenance Cost ($)': list(maintenance_costs.values())
        }).sort_values('Year')
        st.table(maintenance_df)

        st.subheader("Lifecycle Cost Over Time")
        if lcc_over_time:
            years = list(range(1, len(lcc_over_time) + 1))
            cost_data = pd.DataFrame({
                'Year': years,
                'Cumulative LCC': lcc_over_time
            })
            st.line_chart(cost_data.set_index('Year'))

        generate_report_btn = st.button("Generate and Download Report")
        if generate_report_btn:
            try:
                report_content = generate_report(simulation_results, lcc)
                report_path = "pavement_design_report.pdf"
                export_report_to_pdf(report_content, report_path)
                with open(report_path, "rb") as pdf_file:
                    PDFbyte = pdf_file.read()
                st.download_button(label="Download Report as PDF", data=PDFbyte, file_name="pavement_design_report.pdf", mime='application/octet-stream')
                st.success("Report generated and ready for download.")
            except Exception as e:
                st.error(f"Failed to generate report: {e}")
    else:
        st.warning("No simulation results available. Please run a simulation first.")
