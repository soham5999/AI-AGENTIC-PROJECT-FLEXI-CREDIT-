# Machine Learning Subsystem: Random Forest Model & Evaluation

## 1. Why Random Forest Classifier?
For tabular automotive telemetry data, the **Random Forest Classifier** was selected for several key reasons:
1. **Non-Linear Relationships:** Automotive component failure is non-linear (e.g., brake wear above 80% increases failure risk exponentially). Decision tree ensembles capture these interactions naturally without requiring complex polynomial transformations.
2. **Resistance to Overfitting:** By aggregating 100 decorrelated decision trees trained on bootstrap samples (bagging), Random Forest reduces variance compared to single decision trees.
3. **Intrinsic Feature Importance:** Random Forest calculates the mean decrease in impurity (Gini importance) for each feature, providing transparent explainability for vehicle owners and mechanics.
4. **Fast Training & Inference:** Instantaneous evaluation on CPU without requiring GPU acceleration.

---

## 2. Telemetry Feature Vector

| Feature Name | Type | Physical Range | Meaning |
| :--- | :--- | :--- | :--- |
| `vehicle_age` | Float | 0.5 – 15.0 yrs | Time since vehicle manufacturing |
| `odometer_km` | Integer | 3,000 – 300,000 km | Total lifetime distance driven |
| `days_since_service` | Integer | 5 – 450 days | Elapsed days since last garage check |
| `battery_voltage` | Float | 11.0 – 13.2 V | Open-circuit battery voltage |
| `engine_temp` | Float | 75.0 – 118.0 °C | Coolant temperature |
| `brake_wear_pct` | Float | 5.0 – 98.0 % | Friction pad wear percentage |
| `tire_pressure_avg` | Float | 22.0 – 44.0 PSI | Average 4-tire pressure |
| `oil_life_pct` | Float | 2.0 – 100.0 % | Sensor-calculated lubricant life |

**Target Feature:** `maintenance_required` (0 = Healthy, 1 = Service Required)

---

## 3. Evaluation Metrics

Model evaluation is performed on an **80/20 stratified train/test split**:

### Formulas
- **Accuracy:** $\frac{TP + TN}{TP + TN + FP + FN}$
- **Precision:** $\frac{TP}{TP + FP}$ *(Minimizes unnecessary garage visits)*
- **Recall / Sensitivity:** $\frac{TP}{TP + FN}$ *(Critical: avoids missing hazardous component failures)*
- **F1-Score:** $2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$

### Current Evaluation Results
- **Accuracy:** 90.8%
- **Precision:** 87.2%
- **Recall:** 89.1%
- **F1-Score:** 88.2%
- **Test Samples:** 120

### Feature Importance Breakdown
1. `days_since_service`: 33%
2. `oil_life_pct`: 31%
3. `brake_wear_pct`: 16%
4. `battery_voltage`: 6%
5. `odometer_km`: 5%
6. `engine_temp`: 4%
7. `vehicle_age`: 3%
8. `tire_pressure_avg`: 2%
