dashboard_box_size <- 3

boxes_demographics <- fluidRow(
  valueBox(
    color="green",
    value="28,559",
    subtitle="Survey Participants",
    width = dashboard_box_size),
  valueBox(
    color="yellow",
    value="52.4%",
    subtitle="Female",
    width = dashboard_box_size),
  valueBox(
    color="purple",
    value="30.8%",
    subtitle="75+ years old",
    width = dashboard_box_size),
  valueBox(
    color="maroon",
    value="77.8%",
    subtitle="Living in a House",
    width = dashboard_box_size))

boxes_health <- fluidRow(
  valueBox(
    color="yellow",
    value="64.1%",
    subtitle="Received Flu Vaccine",
    width = dashboard_box_size),
  valueBox(
    color="purple",
    value="34.9%",
    subtitle="Have High Blood Pressure",
    width = dashboard_box_size),
  valueBox(
    color="maroon",
    value="11.8%",
    subtitle="Have Diabetes",
    width = dashboard_box_size),
  valueBox(
    color="green",
    value="91.5%",
    subtitle="Haven't Smoked Cigarettes in Past 30 Days",
    width = dashboard_box_size))

boxes_covid <- fluidRow(
  valueBox(
    color="purple",
    value="73",
    subtitle="Diagnosed with COVID-19",
    width = dashboard_box_size),
  valueBox(
    color="maroon",
    value="237",
    subtitle="Were Hospitalized in the Past Month",
    width = dashboard_box_size),
  valueBox(
    color="green",
    value="11.8%",
    subtitle="Had any Health Care Visit in the Past Month",
    width = dashboard_box_size),
  valueBox(
    color="yellow",
    value="25.9%",
    subtitle="Had a Dry Cough in the Past Month",
    width = dashboard_box_size))

boxes_behavior <- fluidRow(
  valueBox(
    color="maroon",
    value="90.9%",
    subtitle="Left Home in the Past Month",
    width = dashboard_box_size),
  valueBox(
    color="green",
    value="47.5%",
    subtitle="Been in Self-Quarantine in the Past Month",
    width = dashboard_box_size),
  valueBox(
    color="yellow",
    value="77.9%",
    subtitle="Left Home to Buy Food",
    width = dashboard_box_size),
  valueBox(
    color="purple",
    value="59.2%",
    subtitle="Left Home for Physical Activity",
    width = dashboard_box_size)
)

boxes_work <- fluidRow(
  valueBox(
    color="green",
    value="27.6%",
    subtitle="Usually Work Outside their Residence",
    width = dashboard_box_size),
  valueBox(
    color="yellow",
    value="20.7%",
    subtitle="of Workplaces Completely Closed",
    width = dashboard_box_size),
  valueBox(
    color="purple",
    value="48.5%",
    subtitle="of Workplaces Partially Closed",
    width = dashboard_box_size),
  valueBox(
    color="maroon",
    value="77.2%",
    subtitle="of Workers Changed Frequency or Duration of Work in Past Month",
    width = dashboard_box_size))

boxes_mental_health <- fluidRow(
  valueBox(
    color="yellow",
    value="59.1%",
    subtitle="Separated from Family",
    width = dashboard_box_size),
  valueBox(
    color="purple",
    value="22.4%",
    subtitle="Unable to Access Usual Healthcare",
    width = dashboard_box_size),
  valueBox(
    color="maroon",
    value="20.4%",
    subtitle="Presence of Depressive Symptoms",
    width = dashboard_box_size),
  valueBox(
    color="green",
    value="5.9%",
    subtitle="Experiencing Moderate or Severe Anxiety",
    width = dashboard_box_size))
