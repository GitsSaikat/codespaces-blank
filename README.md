<h1 align="center">
  <a href="https://github.com/GitsSaikat/Pavement-App">
    <img src="Pavement.jpg" width="215" /></a><br>
  <b>🛣️ Mechanistic-Empirical Pavement Design Tool</b><br>
</h1>


Welcome to the **Mechanistic-Empirical Pavement Design Tool for Highways and Airports**! This application is designed to assist engineers and researchers in designing and evaluating pavement structures based on traffic, material, and environmental data. 

**The app is available at:** [https://pavement-design-app.streamlit.app/](https://pavement-design-app.streamlit.app/)


---

## 🚀 Features

- **Input Data**: Upload or manually input traffic, climate, subgrade, and material data.
- **Pavement Design**: Define pavement layers, material properties, and costs.
- **Simulation**: Analyze pavement performance under various conditions.
- **Lifecycle Cost Analysis (LCCA)**: Evaluate the economic efficiency of pavement designs.
- **Results Visualization**: View performance predictions, cost analysis, and pavement design details with interactive charts.
- **Report Generation**: Create and download detailed reports in PDF format.

---

## 🛠️ Installation

   ```bash
   git clone https://github.com/GitsSaikat/Pavement-App.git
   cd pavement-design-tool
   pip install -r requirements.txt
   streamlit run app.py
  ```

## Project Structure


-   `app.py`: Main Streamlit application file.
-   `Pavement.jpg`: Image used in the application.
-   `src/`: Source code directory.
    -   `models.py`: Contains data model classes.
    -   `performance.py`: Includes functions for pavement performance simulation.
    -   `lcca.py`: Functions for life cycle cost analysis.
    -   `reporting.py`: Functions for report generation.
    -   `design.py`: Functions for designing the pavement structure.
    -   `utils/`: Contains utility scripts.
        -   `helpers.py`: Helper functions for file reading and saving.
        -   `logger.py`: Setting up logging.
-   `README.md`: This file, contains project documentation

## Usage

**Input Data**: Either upload your data using an Excel file or manually enter all the required data to proceed with the design.
    -   **Excel File**: Make sure your Excel file contains sheets named 'Traffic', 'Climate', 'Subgrade' and 'Materials' with the correct columns. See instructions on the page.
    -   **Manual Entry**: Alternatively, fill the forms with the respective data fields, in which the comma separated values are supported in axle loads inputs.

**Design Pavement**: Define the pavement layers by entering the number of layers and then configure the type and thickness of each one.

**Run Simulation**: Set initial costs, maintenance costs, discount rate, and analysis period to run the pavement simulation and LCCA.

**View Results**: Analyze the simulation results, lifecycle cost, and pavement design details through tables and charts.

**Generate Report**: Create a comprehensive PDF report of your analysis.

## Contributing

Contributions are welcome! If you find a bug or have suggestions for new features, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
   
