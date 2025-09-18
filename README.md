# 🚦 Smart Traffic Control System - Zamboanga KCC

A comprehensive SUMO-based traffic simulation system for the Zamboanga KCC intersection, featuring AI-driven traffic light control and comprehensive metrics collection.

## 📋 Project Overview

This project simulates and optimizes traffic flow at the Zamboanga KCC intersection using:
- **SUMO (Simulation of Urban Mobility)** for traffic simulation
- **Python TraCI** for real-time traffic control
- **AI-based adaptive traffic light control**
- **Comprehensive metrics collection** for performance analysis

## 🗂️ Repository Structure

```
📁 Daloy_Simulation/
├── 🗺️ KCCIntersection.osm           # Original OpenStreetMap data
├── 🌐 KCCIntersection.net.xml       # SUMO network file
├── 🚗 KCCIntersection.rou.xml       # Vehicle routes and trips
├── ⚙️ KCCIntersection.sumocfg       # SUMO configuration file
├── 📊 KCCIntersectionConfig.add.xml # Detector definitions
├── 🧠 traffic_controller.py         # Main AI traffic control system
├── 📈 traffic_analyzer.py           # Data analysis and visualization
├── 🚀 run_simulation.bat            # Easy simulation launcher
├── 📋 requirements.txt              # Python dependencies
├── 🔧 osmNetconvert.typ.xml         # SUMO type mapping
└── 📄 README.md                     # This file
```

## 🎯 Features

### Smart Traffic Control
- **Real-time adaptive control** based on detector data
- **Intersection coordination** between two major junctions
- **Queue length optimization** using 30+ traffic detectors
- **Phase change tracking** and optimization

### Comprehensive Metrics Collection
- **Vehicle Delay & Travel Time** - Individual journey analysis
- **Queue Length Monitoring** - Real-time queue tracking
- **Emissions Analysis** - CO2, NOx, PMx environmental impact
- **Traffic Flow Statistics** - Throughput and efficiency metrics

### Long-term Analysis
- **200-hour simulation** capability for comprehensive data
- **Hourly summary reports** for trend analysis
- **Performance comparison** between intersections
- **Visualization dashboards** for data insights

## 🚀 Quick Start

### Prerequisites
- **SUMO** (Simulation of Urban Mobility) installed
- **Python 3.7+** with TraCI support
- **SUMO_HOME** environment variable set

### Basic Usage

1. **Quick Launch:**
   ```batch
   run_simulation.bat
   ```

2. **Manual Python Execution:**
   ```bash
   python traffic_controller.py
   ```

3. **Analysis (after simulation):**
   ```bash
   pip install -r requirements.txt
   python traffic_analyzer.py
   ```

## 📊 Data Output

The simulation generates three main data files:

### 1. `traffic_metrics.csv`
Step-by-step detailed metrics including:
- Vehicle counts and speeds
- Queue lengths at both intersections
- Traffic light phases
- Real-time emissions data

### 2. `vehicle_details.csv`
Individual vehicle journey data:
- Entry/exit times and travel duration
- Route length and average speed
- Total waiting time and emissions per vehicle

### 3. `intersection_summary.csv`
Hourly performance summaries:
- Average delays and queue lengths
- Vehicle throughput statistics
- Phase change frequencies
- Environmental impact metrics

## 🎮 Traffic Control Algorithm

The AI system uses a simple but effective approach:

```python
# Intersection 1 (Complex Junction)
if (East_West_Traffic) > (North_South_Traffic):
    set_green_phase(East_West)
else:
    set_green_phase(North_South)

# Intersection 2 (4-Way Junction) - with coordination
if (West_Traffic * 1.5 + East_Traffic) > (North_Traffic + South_Traffic):
    set_green_phase(East_West)  # Prioritize flow from Intersection 1
else:
    set_green_phase(North_South)
```

## 📈 Performance Metrics

The system tracks key performance indicators:

| Metric | Description | Purpose |
|--------|-------------|---------|
| **Average Delay** | Time vehicles spend waiting | Traffic efficiency |
| **Queue Length** | Number of vehicles waiting | Congestion level |
| **Throughput** | Vehicles processed per hour | System capacity |
| **Emissions** | Environmental impact (CO2, NOx, PMx) | Sustainability |
| **Phase Changes** | Traffic light switching frequency | System stability |

## 🛠️ Configuration

### Simulation Duration
Modify `KCCIntersection.sumocfg`:
```xml
<time>
    <begin value="0"/>
    <end value="720000"/>  <!-- 200 hours -->
</time>
```

### Detector Sensitivity
Edit detector periods in `KCCIntersectionConfig.add.xml`:
```xml
<laneAreaDetector period="300.00" length="30.00" />
```

### AI Parameters
Adjust coordination weights in `traffic_controller.py`:
```python
# Give extra priority to traffic from Intersection 1
if ((cars_J2_W * 1.5) + cars_J2_E) > (cars_J2_N + cars_J2_S):
```

## 📖 Research Applications

This system is designed for:
- **Traffic Engineering Research** - Performance optimization studies
- **AI Algorithm Testing** - Adaptive control algorithm development
- **Urban Planning** - Infrastructure impact assessment
- **Environmental Studies** - Emissions reduction analysis
- **Academic Thesis** - Comprehensive data for research

## 🤝 Contributing

This project is part of ongoing research. Feel free to:
- Report issues or suggestions
- Improve the AI control algorithms
- Add new metrics or analysis features
- Optimize simulation performance

## 📝 License

This project is developed for academic research purposes.

## 🙋‍♀️ Contact

For questions about this traffic simulation system, please refer to the project documentation or simulation logs.

---

*Generated on September 19, 2025 - Smart Traffic Control System v1.0*
