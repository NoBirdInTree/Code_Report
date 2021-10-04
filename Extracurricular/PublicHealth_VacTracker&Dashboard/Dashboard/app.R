#
library(shiny)
library(shinydashboard)
library(shinythemes)
library(ggplot2)
library(data.table)
library(dashboardthemes)
library(plotly)
library(dplyr)
library(forcats)
library(stringr)

## Check on color-blind legibility of plots with CLSA colors

## Read data and scripts
#source("process-data.R")
source("create-plots.R")
source("dash-theme.R")
source("highlight-boxes.R")
source("about-text.R")

## add menu items for symptoms question
tmp <- unique(long_data[substring(question, 1, 3) == "SYM", c("question","label")])
tmp <- tmp[!(question%in%c("SYM_CT_COVID","SYM_FEVTMP_DNT_COVID","SYM_HOSP_COVID",
              "SYM_NTCONF_COVID","SYM_TEST_COVID","SYM_TESTPOS_COVID",
              "SYM_XRAY_COVID","SYM_CNSLT_COVID","SYM_DRSLT_COVID",
              "SYM_DRYCO_COVID","SYM_SMELL_COVID","SYM_FEVR_COVID","SYM_BREATH_COVID",
              grep("SYM_CNSWHO",unique(long_data$question),value=TRUE)))]
tmp <- tmp[order(tmp$label),]
symptoms <- as.list(tmp$question)
names(symptoms) <- tmp$label

## Increase space between x-axis label and ticks using plotly
layout_ggplotly <- function(gg, x = -0.12, y = -0.08){
    # The 1 and 2 goes into the list that contains the options for the x and y axis labels respectively
    gg[['x']][['layout']][['annotations']][[1]][['y']] <- x
    #gg[['x']][['layout']][['annotations']][[2]][['x']] <- y
    gg
}

## Footer text
gen_footer <- "Participants could select multiple responses"
prov_footer <- "Geographical areas with fewer than 5 participants are not displayed"
health_footer <- "Participants had the option to select any of the conditions shown in the “Most commonly reported” and “Least commonly reported” figures and could select more than one condition"
work_footer <- "Participants could indicate both work and volunteer status"


ui <- dashboardPage(
    dashboardHeader(title = "CLSA Dashboard"),
    dashboardSidebar(
        sidebarMenu(
            menuItem("Participant Demographics", tabName = "demographics"),
            menuItem("Participant Physical Health", tabName = "health"),
            menuItem("Participant COVID-19 Health", tabName = "covid19_health"),
            menuItem("Participant Behaviour", tabName = "behavior"),
            menuItem("Participant Work", tabName = "work"),
            menuItem("Participant Mental Health", tabName = "mental_health"),
            menuItem("About the Survey", tabName = "about")
        )
    ),
    dashboardBody(
        theme_clsa_flatly,
        tags$style(".small-box.bg-yellow { background-color: #006aaa !important; color: #FFFFFF !important; }"), # blue
        tags$style(".small-box.bg-purple { background-color: #8cc641 !important; color: #FFFFFF !important; }"), # green
        tags$style(".small-box.bg-maroon { background-color: #009aa1 !important; color: #FFFFFF !important; }"), # teal
        tags$style(".small-box.bg-green { background-color: #013667 !important; color: #FFFFFF !important; }"), # navy
        
        tabItems(
            tabItem(tabName = "demographics",
                    h2('COVID-19 Baseline Survey: Who participated?',align="center"),
                    h4('Survey collection dates: April 15 2020 – May 30 2020',align="center"),
                    boxes_demographics,
                    fluidRow(
                        box(title = "Age (n = 28,559)", status = "primary",
                            collapsible=TRUE, solidHeader = TRUE,
                            checkboxGroupInput(inputId='group_age', label="Compare Results by:",
                                               choices = list("Sex"="sex"), inline = TRUE),
                            plotlyOutput("AgeDist")),
                        box(title="Location (n = 28,559)", status = "primary",
                            solidHeader = TRUE, collapsible = TRUE,
                            checkboxGroupInput(inputId='group_location', label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), inline = TRUE),
                            plotlyOutput("LocationDist"),
                            h4(prov_footer))
                    ), # end row
                    fluidRow(
                        box(title = "Dwelling Type (n = 28,559)",
                            status = "success",
                            collapsible=TRUE,solidHeader = TRUE,
                            width=12,
                        checkboxGroupInput(inputId='group_demographics', label="Compare Results by:",
                                          choices = list("Age Group"="age_group","Sex"="sex"), 
                                          #selected = c("age_group","sex"),
                                          inline = TRUE),
                        column(width=12,
                               plotlyOutput("DwlgPlot"))
                    )),
                    fluidRow(
                        box(title="Number of People (including Participant) Living in Residence (n = 28,559)",
                            status = "success",
                            width = 12,
                            collapsible = TRUE, solidHeader = TRUE,
                            checkboxGroupInput(inputId='group_household', label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), 
                                               selected = c("age_group","sex"),
                                               inline = T),
                            plotOutput("HouseholdPlot"))
                    )),
            tabItem(tabName = "health",
                    h2('COVID-19 Baseline Survey: How healthy are participants and what are their smoking habits?',align="center"),
                    h4('Survey collection dates: April 15 2020 – May 30 2020',align="center"),
                    boxes_health, 
                    fluidRow(
                        box(title = "Most Commonly Reported Chronic Health Conditions (n = 28,559)",
                            status = "primary",
                            collapsible = TRUE, solidHeader = TRUE,
                            width=12,checkboxGroupInput(inputId='group_chronic', label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), 
                                               #selected = c("age_group","sex"),
                                               inline = TRUE),
                            plotlyOutput("ChronPlotCommon"),
                            h4(health_footer))
                    ), # end row
                    fluidRow(
                        box(title = "Least Commonly Reported Chronic Health Conditions (n = 28,559)",
                            status = "primary",
                            collapsible = TRUE, solidHeader = TRUE,
                            width=12,
                            checkboxGroupInput(inputId='group_chronic2', label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), 
                                               #selected = c("age_group","sex"),
                                               inline = TRUE),
                            plotlyOutput("ChronPlotUncommon"),
                            h4(health_footer))
                    ), # end row
                    fluidRow(
                        box(title = "Current Smoking Habits (n = 28,559)",
                            status = "info",
                            collapsible = TRUE, solidHeader = TRUE,
                            width=12,
                            checkboxGroupInput(inputId='group_smoking', label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), 
                                               #selected = c("age_group","sex"),
                                               inline = TRUE),
                                   plotlyOutput("SmokingPlot"),
                                   plotlyOutput("MarijuanaPlot"))
                    )),
            tabItem(tabName = "covid19_health",
                    h2('COVID-19 Baseline Survey: How have participants been diagnosed with COVID-19, what are their symptoms, and have they been able to access care?',align="center"),
                    h4('Survey collection dates: April 15 2020 – May 30 2020',align="center"),
                    boxes_covid,
                    fluidRow(
                        box(title = "COVID-19 Diagnosis (n = 28,559)",
                            status = "primary",
                            collapsible = TRUE, solidHeader = TRUE,
                            width = 12, 
                            checkboxGroupInput(inputId='group_covid', label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), 
                                               #selected = c("age_group","sex"),
                                               inline = TRUE),
                            plotlyOutput("CovPlot"))
                    ),
                    fluidRow(
                        box(title = "Had Testing for COVID-19 in the Past Month (n = 28,559)",
                            status = "primary",
                            collapsible = TRUE, solidHeader = TRUE,
                            width = 12, 
                            checkboxGroupInput(inputId='group_test', label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), 
                                               #selected = c("age_group","sex"),
                                               inline = TRUE),
                            plotlyOutput("TestingPlot"))
                    ),
                    fluidRow(
                        box(title = "COVID-19 Symptoms in Past Month (n = 28,559)",
                            status = "info",
                            collapsible = TRUE, solidHeader = TRUE,
                            width = 12, 
                            checkboxGroupInput(inputId='group_symp19', label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), 
                                               #selected = c("age_group","sex"),
                                               inline = TRUE),
                            plotlyOutput("CharacteristicSympPlot"),
                            h4(gen_footer))
                        ), # end row
                    fluidRow(    
                        box(title="Other Symptoms in Past Month (n = 28,559)",
                            status = "info",
                            collapsible = TRUE, solidHeader = TRUE,
                            width = 12, 
                            column(4, 
                                   selectInput(inputId = 'symptom', h3("Select Symptoms to Compare:"),
                                               choices = symptoms,
                                               selected = symptoms[7:8],
                                               multiple = TRUE),
                                   checkboxGroupInput(inputId='group_symp', label="Compare Results by:",
                                                      choices = list("Age Group"="age_group","Sex"="sex"), 
                                                      #selected = c("age_group","sex"), 
                                                      inline = TRUE)),
                            column(8, 
                                   plotlyOutput("SympPlot")),
                            h4(gen_footer))
                        ), # end row
                    fluidRow(
                        box(title="Consulted Health Care Practitioner in the Past Month, if had any Symptoms (n = 24,253)",
                            status = "success",
                            collapsible = TRUE, solidHeader = TRUE,
                            checkboxGroupInput(inputId='group_hc', label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), 
                                               #selected = c("age_group","sex"), 
                                               inline = TRUE),
                               plotlyOutput("HlthCarePlot")),
                        box(title="Types of Visit with Health Care Practitioners in the Past Month (n = 3,380)",
                            status = "success",
                            collapsible = TRUE, solidHeader = TRUE,
                            checkboxGroupInput(inputId='group_hctype', label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), 
                                               #selected = c("age_group","sex"), 
                                               inline = TRUE),
                               plotlyOutput("HCTypePlot"),
                            h4(gen_footer))
                    )),
            tabItem(tabName = "behavior",
                    h2('COVID-19 Baseline Survey: How has participant behaviour changed during the COVID-19 pandemic?',align="center"),
                    h4('Survey collection dates: April 15 2020 – May 30 2020',align="center"),
                    boxes_behavior, ## to be changed as we design highlights for other tabs
                    
                    fluidRow(
                        box(title = "General Behaviour in the Past Month (n = 28,559)",
                            status = "primary",
                            width = 6,
                            collapsible = T, solidHeader = TRUE,
                            checkboxGroupInput(inputId='gen_behav_questions', label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), 
                                               #selected = c("age_group","sex"), 
                                               inline = T),
                            plotlyOutput("behavior_plot"),
                            h4(gen_footer)),
                            #span(textOutput("gen_footer"),style="font-size:18px")),
                        box(title = "Among Those who had not Left Home in Past Month, Methods of Staying in Contact (n = 867)",
                            status = "primary",
                            width = 6,
                            collapsible = T, solidHeader = TRUE,
                            checkboxGroupInput(inputId='contact_questions', label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), 
                                               #selected = c("age_group","sex"), 
                                               inline = T),
                            plotlyOutput("contact_plot"),
                            h4(gen_footer))
                            #span(textOutput("gen_footer"),style="font-size:18px"))
                    ), 
                    fluidRow(
                        box(title = "Reasons for Leaving Home in the Past Month (n = 25,954)",
                            status = "info",
                            width = 12,
                            collapsible = T, solidHeader = TRUE,
                            checkboxGroupInput(inputId='leave_home_questions', label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), 
                                               #selected = c("age_group","sex"), 
                                               inline = T),
                            plotlyOutput("leave_home_plot"),
                            h4(gen_footer))
                    ),
                    
                    fluidRow(
                        box(title="Handwashing (n = 28,559)",
                            status = "success",
                            width = 12,
                            collapsible = TRUE, solidHeader = TRUE,
                            checkboxGroupInput(inputId='handwashing', label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), 
                                               selected = c("age_group","sex"), inline = T),
                            plotOutput("hand_washing_plot"))
                    ),
                    fluidRow(
                        
                        box(title="Use of Public Transportation at Least Once per Week (n = 28,559)",
                            status = "primary",
                            width = 12,
                            collapsible = TRUE, solidHeader = TRUE,
                            checkboxGroupInput(inputId='public_transport', label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), inline = T,
                                               selected = c("age_group", "sex")),
                            plotlyOutput("public_transit_plot"))
                    ),
                    fluidRow(
                        box(title="Number of One-Way Trips per Week Among those Using Public Transport (n = 2,747)",
                            status = "info",
                            width = 12,
                            collapsible = TRUE, solidHeader = TRUE,
                            checkboxGroupInput(inputId='pt_trips', label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"),
                                               selected = c("age_group","sex"),
                                               inline = T),
                            plotOutput("pt_trips_plot"))),
                    fluidRow(
                        box(title="Length (Minutes) of One-Way Trips per Week Among those Using Public Transport (n = 2,747)",
                            status = "success",
                            width = 12,
                            collapsible = TRUE, solidHeader = TRUE,
                            checkboxGroupInput(inputId="pt_length", label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), 
                                               selected = c("age_group","sex"),
                                               inline = T),
                            plotOutput("pt_length_plot"))
                    ),
                    
                    # fluidRow(
                    #     box(title="Behavior",
                    #         status="primary",
                    #         collapsible = TRUE, solidHeader = TRUE,
                    #         width = 12,
                    #           plotlyOutput("public_transit_plot")))
            ),
            tabItem(tabName = "work",
                    h2('COVID-19 Baseline Survey: How are participants working and volunteering during COVID-19?', align="center"),
                    h4('Survey collection dates: April 15 2020 – May 30 2020',align="center"),
                    boxes_work,
                    fluidRow(
                        box(title = "Work and Volunteer Status (n = 28,559)",
                            status = "primary",
                            collapsible = TRUE, solidHeader = TRUE,
                            width=12,
                            checkboxGroupInput(inputId="group_work", label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), inline = T,
                                               selected = c("age_group", "sex")),
                            plotlyOutput("WorkStatusPlot"),
                            h4(work_footer))
                    ),
                    fluidRow(
                        box(title = "Physical Distancing Measures Implemented in Workplace in the Past Month (n = 7,876)",
                            status = "info",
                            collapsible = TRUE, solidHeader = TRUE,
                            width = 12,
                            checkboxGroupInput(inputId="group_dist", label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), 
                                               #selected = c("age_group","sex"),
                                               inline = T),
                            plotlyOutput("WorkDistancingPlot"),
                            h4(gen_footer))
                        ), # end of row
                    fluidRow(
                        box(title="Change in Number of Days per Week at Workplace in the Past Month from Usual (n = 7,876)",
                            status = "success",
                            width = 6,
                            collapsible = TRUE, solidHeader = TRUE,
                            checkboxGroupInput(inputId='group_work_days', label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), 
                                               #selected = c("age_group","sex"), 
                                               inline = T),
                            plotlyOutput("WorkDaysPlot")),
                        box(title="Change in Number of Hours per Week at Workplace in the Past Month from Usual (n = 7,876)",
                            status = "success",
                            width = 6,
                            collapsible = TRUE, solidHeader = TRUE,
                            checkboxGroupInput(inputId="group_work_hrs", label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), 
                                               #selected = c("age_group","sex"), 
                                               inline = T),
                            plotlyOutput("WorkHoursPlot")),
                        box(title="Change in Number of Days per Week Volunteering in the Past Month from Usual (n = 7,813)",
                            status = "warning",
                            width = 6,
                            collapsible = TRUE, solidHeader = TRUE,
                            checkboxGroupInput(inputId='group_vol_days', label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), 
                                               #selected = c("age_group","sex"), 
                                               inline = T),
                            plotlyOutput("VolDaysPlot")),
                        box(title="Change in Number of Hours per Week Volunteering in the Past Month from Usual (n = 7,813)",
                            status = "warning",
                            width = 6,
                            collapsible = TRUE, solidHeader = TRUE,
                            checkboxGroupInput(inputId="group_vol_hrs", label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), 
                                               #selected = c("age_group","sex"), 
                                               inline = T),
                            plotlyOutput("VolHoursPlot"))
                    )
            ), # end work tab
            
            tabItem(tabName = "mental_health",
                    h2('COVID-19 Baseline Survey: How is participant mental health during COVID-19?',align="center"), 
                    h4('Survey collection dates: April 15 2020 – May 30 2020',align="center"),
                    boxes_mental_health,
                    fluidRow(
                        box(title="Consequences of COVID-19 on Participant and their Household (n = 28,559)",
                            status = "info",
                            collapsible = TRUE, solidHeader = TRUE,
                            width = 12, 
                            checkboxGroupInput(inputId='group_conseq', label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), 
                                               #selected = c("age_group","sex"), 
                                               inline = TRUE),
                            plotlyOutput("ConseqPlot"))
                        ),
                    fluidRow(
                        box(title="Depressive Symptoms (n = 28,559)",
                            status="success",
                            collapsible=TRUE, solidHeader = TRUE,
                            checkboxGroupInput(inputId='group_dep', label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), 
                                               #selected = c("age_group","sex"), 
                                               inline = TRUE),
                            plotlyOutput("DepPlot")),
                        box(title="Anxiety Severity Classification (n = 28,559)",
                            status="success",
                            collapsible=TRUE, solidHeader = TRUE,
                            checkboxGroupInput(inputId='group_anx', label="Compare Results by:",
                                           choices = list("Age Group"="age_group","Sex"="sex"), 
                                           #selected = c("age_group","sex"), 
                                           inline = TRUE),
                            plotlyOutput("AnxPlot"))),
                    fluidRow(
                        box(title="Most Commonly Reported Experiences During COVID-19 (n = 28,559)",
                            status="primary",
                            collapsible = TRUE, solidHeader = TRUE,
                            checkboxGroupInput(inputId='group_imp', label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), 
                                               #selected = c("age_group","sex"), 
                                               inline = TRUE),
                            width=12,
                            plotlyOutput("ImpactPlotCommon"),
                            h4(gen_footer))
                    ), # end row
                    fluidRow(
                        box(title="Least Commonly Reported Experiences During COVID-19 (n = 28,559)",
                            status="primary",
                            collapsible = TRUE, solidHeader = TRUE,
                            checkboxGroupInput(inputId='group_imp_un', label="Compare Results by:",
                                               choices = list("Age Group"="age_group","Sex"="sex"), 
                                               #selected = c("age_group","sex"), 
                                               inline = TRUE),
                            width=12,
                            plotlyOutput("ImpactPlotUncommon"),
                            h4(gen_footer))
                    ) # end row
                ), # end tab
            tabItem(tabName = "about",
                    h2("About the Survey"),
                    htmlOutput("text"))
        )
    ))

server <- function(input, output, session) { 
    
    ##### Demographic tab plots #####
    output$AgeDist <- 
        renderPlotly({
            sex = ifelse("sex" %in% input$group_age, T, F)
            
            if(sex == TRUE){
                tmpdt <- long_data[which(long_data$question %in% "SEX_CLSA")] %>%
                    group_by(question, gender, age_group) %>%
                    summarize(grouped_sum = sum(value)) %>% ungroup() %>%
                    filter(grouped_sum!=0) %>% 
                    group_by(question, age_group) %>%
                    mutate(percent  = grouped_sum/sum(grouped_sum)*100) %>%
                    mutate(text = paste0("Percent: ",round(percent,digits=2),"% \nCount: ",grouped_sum," of ",sum(grouped_sum)))
            }
            else {
                tmpdt <- long_data[which(long_data$question %in% "SEX_CLSA")] %>%
                    group_by(question, age_group) %>%
                    summarize(grouped_sum = sum(value)) %>% ungroup() %>%
                    filter(grouped_sum!=0) %>% 
                    mutate(percent  = grouped_sum/sum(grouped_sum)*100) %>%
                    mutate(text = paste0("Percent: ",round(percent,digits=2),"% \nCount: ",grouped_sum," of ",sum(grouped_sum)))
            }
            if (sex == TRUE){
                age_plot <- ggplot(tmpdt, aes(age_group, percent, fill=gender)) + 
                    geom_bar(stat = "identity",position = position_dodge2(reverse=TRUE)) + 
                    aes(text=text) + 
                    ggtheme_clsa() + 
                    labs(x = "Age Group", y = "Percent of Participants", fill = "") + 
                    scale_fill_manual(values=mycols[3:4])
            }
            else {
                age_plot <- ggplot(tmpdt, aes(age_group, percent)) + 
                    aes(text=text) + 
                    geom_bar(stat = "identity") + ggtheme_clsa() + 
                    labs(x = "Age Group", y = "Percent of Participants")
            }
            clsa_plotly(age_plot, "text")  %>% 
                layout(autosize = TRUE, margin = list(l = 20, r = 10, b = 80, t = 30, pad = 1)) %>%
                layout_ggplotly
        })
    
    output$LocationDist <-
        renderPlotly({
            gen = ifelse("sex" %in% input$group_location, T, F)
            age = ifelse("age_group" %in% input$group_location, T, F)
            tmpdt <- reshape_cat_data(gen,age,"PROV_COVID") %>%
                filter(grouped_sum > 3)
            ## Change provinces to abbreviations
            #provinces <- data.frame(prov=c("Alberta","British Columbia","Manitoba",
            #                               "New Brunswick","Newfoundland","Nova Scotia",
            #                               "Ontario","Prince Edward Island","Quebec",
            #                               "Saskatchewan"),
            #                        abbr=c("AB","BC","MB","NB","NL","NS","ON","PEI","QC","SK"))
            tmpdt$category <- recode(tmpdt$category,Alberta="AB",`British Columbia`="BC",
                                     Manitoba="MB",`New Brunswick` = "NB",Newfoundland="NL",
                                     `Nova Scotia`="NS",Ontario="ON",`Prince Edward Island`="PEI",
                                     Quebec="QC",Saskatchewan="SK")
            
            lc_plot <- produce_plot(tmpdt,gen,age,"dodged") +
                scale_x_discrete(labels = function(x) str_wrap(x, width = 40))
            clsa_plotly(lc_plot, "text")  %>% 
                layout(autosize = TRUE, margin = list(l = 0, r = 10, b = 80, t = 30, pad = 1)) %>%
                layout_ggplotly
        })
    output$DwlgPlot <- 
        renderPlotly({
            A = ifelse("sex" %in% input$group_demographics, T, F)
            B = ifelse("age_group" %in% input$group_demographics, T, F)
            tmpdt <- reshape_cat_data(A,B,"OWN_DWLG_COVID") 
            dwlg_plot <- produce_plot(tmpdt,A,B,"dodged") +
                scale_x_discrete(labels = function(x) str_wrap(x, width = 40))
            clsa_plotly(dwlg_plot,"text")  %>% 
                layout(autosize = TRUE, margin = list(l = 0, r = 10, b = 80, t = 30, pad = 1)) %>%
                layout_ggplotly
        })
    output$HouseholdPlot <- 
        renderPlot({
            gen = ifelse("sex" %in% input$group_household, T, F)
            age = ifelse("age_group" %in% input$group_household, T, F)
            variables_of_interest <- c("current_living_household", "usually_living_household")
            #variables_of_interest <- c("Number of people currently living in househld Categorical","Number of people usually living in househld Categorical")
            #tmpdt <- long_data[question%in%variables_of_interest]
            #tmpdt <- reshape_cat_data(gen, age, variables_of_interest)
            #ggplot(tmpdt, aes(category, percent, fill = label)) + geom_bar(position = position_dodge2(reverse=TRUE),stat="identity")            
            household_plot <- continuous_data_plotting_function(data, variables_of_interest, gen, age)
            household_plot
            #clsa_plotly(hand_wash_plot)
        })
    
    ##### Health tab plots #####
    chronic_cond_common <- c("CCC_LTC_HBP_COVID",
                             "CCC_LTC_DIA_COVID","CCC_LTC_HEART_COVID",
                             "CCC_LTC_ASTHM_COVID","CCC_LTC_CANC_COVID",
                             "CCC_LTC_NONE_COVID")
    chronic_cond_uncommon <- c("CCC_LTC_AUTOIMD_COVID","CCC_LTC_DRPNEU_COVID",
                               "CCC_LTC_COPD_COVID","CCC_LTC_FAIL_COVID",
                               "CCC_LTC_OTLD_COVID","CCC_LTC_HIV_COVID")
    output$ChronPlotCommon <-
        renderPlotly({
            A = ifelse("sex" %in% input$group_chronic, T, F)
            B = ifelse("age_group" %in% input$group_chronic, T, F)
            tmpdt <- reshape_cat_data(A,B,
                       chronic_cond_common) %>%
                     filter(category=="Yes") %>%
                mutate(label=ifelse(label=="None of the above","None of the conditions listed",label))
            ccc_plot <- produce_plot(tmpdt,A,B,"sel_all") + 
                aes(x = factor(label, levels=c("None of the conditions listed", "Cancer",
                                               "Asthma","Heart disease",
                                               "Diabetes","High blood pressure"
                                               ))) + 
                labs(x="") +
                scale_x_discrete(labels = function(x) str_wrap(x, width = 40)) +
                ylim(0,65) 
            clsa_plotly(ccc_plot, "text") %>%
                layout_ggplotly %>%
                layout(autosize = TRUE, margin = list(l = 0, r = 10, b = 70, t = 30, pad = -3))
        })
    output$ChronPlotUncommon <-
        renderPlotly({
            A = ifelse("sex" %in% input$group_chronic2, T, F)
            B = ifelse("age_group" %in% input$group_chronic2, T, F)
            tmpdt <- reshape_cat_data(A,B,
                                      chronic_cond_uncommon) %>%
                filter(category=="Yes") 
            #tmpdt$label <- forcats::fct_rev(as.factor(tmpdt$label))
            #tmpdt$label <- relevel(tmpdt$label,"None of the above")
            ccc_plot <- produce_plot(tmpdt,A,B,"sel_all") + 
                aes(x = reorder(label, grouped_sum)) + 
                labs(x="") +
                scale_x_discrete(labels = function(x) str_wrap(x, width = 40)) +
                ylim(0,45)
            clsa_plotly(ccc_plot, "text") %>%
            layout(autosize = TRUE, margin = list(l = 0, r = 10, b = 70, t = 30, pad = -3)) %>%
                layout_ggplotly
        })
    output$SmokingPlot <- 
        renderPlotly({
            A = ifelse("sex" %in% input$group_smoking, T, F)
            B = ifelse("age_group" %in% input$group_smoking, T, F)
            tmpdt <- reshape_cat_data(A,B,"SMK_CURRCG_COVID")
            tmpdt$category <- factor(tmpdt$category, levels = c("Not at all","At least one daily",
                                                                "Occasionally, but not every day",
                                                                   "No response recorded"))
            tmpdt$grouped_sum <- NULL
            smk_plot <- produce_plot(tmpdt,A,B,"dodged") + labs(title="Cigarettes in the past 30 days")
            clsa_plotly(smk_plot, "text") %>%
                layout(autosize = TRUE, margin = list(l = 0, r = 10, b = 70, t = 70, pad = -3)) %>%
                layout_ggplotly
        })
    output$MarijuanaPlot <- 
        renderPlotly({
            A = ifelse("sex" %in% input$group_smoking, T, F)
            B = ifelse("age_group" %in% input$group_smoking, T, F)
            tmpdt <- reshape_cat_data(A,B,"SMK_CANNCUR_COVID") 
            tmpdt$category <- factor(tmpdt$category, levels = c("Never in my lifetime","Not currently",
                                                                "Occasionally, but not every day",
                                                                "At least once daily",
                                                                "No response recorded"))
            tmpdt$grouped_sum <- NULL
            smk_mar_plot <- produce_plot(tmpdt,A,B,"dodged") + labs(title="Current Marijuana/Cannabis Smoking Habits")
            clsa_plotly(smk_mar_plot, "text") %>%
                layout(autosize = TRUE, margin = list(l = 0, r = 10, b = 70, t = 70, pad = -3)) %>%
                layout_ggplotly
        })
    
    output$CharacteristicSympPlot <- 
        renderPlotly({
            A = ifelse("sex" %in% input$group_symp19, T, F)
            B = ifelse("age_group" %in% input$group_symp19, T, F)
            tmpdt <- reshape_cat_data(A,B,c("SYM_DRYCO_COVID","SYM_BREATH_COVID",
                                                   "SYM_SMELL_COVID","SYM_FEVR_COVID")) %>%
                filter(category=="Yes")
            p1 <- produce_plot(tmpdt,A,B,"sel_all") +
                scale_x_discrete(labels = function(x) str_wrap(x, width = 25))
            clsa_plotly(p1, "text") %>%
                layout(autosize = TRUE, margin = list(l = 0, r = 10, b = 70, t = 30, pad = -3)) %>%
                layout_ggplotly
        })
    
    output$SympPlot <- 
        renderPlotly({
            A = ifelse("sex" %in% input$group_symp, T, F)
            B = ifelse("age_group" %in% input$group_symp, T, F)
            tmpdt <- reshape_cat_data(A,B,input$symptom) %>%
                filter(category=="Yes")
            tmpdt$label <- forcats::fct_rev(as.factor(tmpdt$label))
            #tmpdt$label <- paste0(tmpdt$N," of ",tmpdt$total)
            #title_str <- paste0(names(symptoms[symptoms==input$symptom[1]]))
            p1 <- produce_plot(tmpdt,A,B,"sel_all") +
                scale_x_discrete(labels = function(x) str_wrap(x, width = 20))
            clsa_plotly(p1, "text") %>%
                layout(autosize = TRUE, margin = list(l = 0, r = 10, b = 70, t = 30, pad = -3)) %>%
                layout_ggplotly
        })
    
    output$CovPlot <- 
        renderPlotly({
            A = ifelse("sex" %in% input$group_covid, T, F)
            B = ifelse("age_group" %in% input$group_covid, T, F)
            tmpdt <- reshape_cat_data(A,B,"SYM_DRSLT_COVID")
            cov_plot <- produce_plot(tmpdt,A,B,"dodged",adjustment = T, y_size = 12) +
                scale_x_discrete(labels = function(x) str_wrap(x, width = 50))
            clsa_plotly(cov_plot, "text") %>%
                layout(autosize = TRUE, margin = list(l = 70, r = 10, b = 70, t = 30, pad = -3)) %>%
                layout_ggplotly
        })
    output$TestingPlot <- 
        renderPlotly({
            A = ifelse("sex" %in% input$group_test, T, F)
            B = ifelse("age_group" %in% input$group_test, T, F)
            tmpdt <- reshape_cat_data(A,B,"SYM_TEST_COVID")
            test_plot <- produce_plot(tmpdt,A,B,"dodged") + 
                scale_x_discrete(labels = function(x) str_wrap(x, width = 40))
            clsa_plotly(test_plot, "text") %>%
                layout(autosize = TRUE, margin = list(l = 70, r = 10, b = 70, t = 30, pad = -3)) %>%
                layout_ggplotly
        })
    output$HlthCarePlot <- 
        renderPlotly({
            A = ifelse("sex" %in% input$group_hc, T, F)
            B = ifelse("age_group" %in% input$group_hc, T, F)
            tmpdt <- reshape_cat_data(A,B,"SYM_CNSLT_COVID") #%>%
                #filter(category == "Yes")
            #tmpdt <- tmpdt[tmpdt$category=="Yes",]
            #tmpdt[, txt := paste0(value," of ",totalN)]
            #hc_plot <- ggplot(tmpdt, aes(age_group,y=percent,fill=sex)) + 
            #    geom_bar(stat="identity",position="dodge") + 
            #    ggtheme_clsa() + labs(y="% Consulted Health Care Practitioner") #+
                                      #title="Participants Consulting Health Care \nPractitioner in the Past Month") + 
                #scale_fill_manual(values=mycols[3:4])
            hc_plot <- produce_plot(tmpdt,A,B,"dodged")
            clsa_plotly(hc_plot,"text") %>%
                layout_ggplotly  %>%
                layout(autosize = TRUE, margin = list(l = 0, r = 10, b = 70, t = 30, pad = -3))
        })
    output$HCTypePlot <- 
        renderPlotly({
            ## SYM_CNSWHO_COVID
            ## type of consultation
            A = ifelse("sex" %in% input$group_hctype, T, F)
            B = ifelse("age_group" %in% input$group_hctype, T, F)
            tmpdt <- reshape_cat_data(A,B,
                                      grep("SYM_CNSWHO",unique(long_data$question),value=TRUE)) %>%
                filter(category=="Yes")
            #tmpdt[label=="None of the above", label := "Other"]
            #tmpdt[, label := fct_rev(as.factor(label))]
            hc_type_plot <- produce_plot(tmpdt,A,B,"sel_all",adjustment=T,y_size=12) + 
                labs(y="Percent of Visits") +
                scale_x_discrete(labels = function(x) str_wrap(x, width = 25))
            clsa_plotly(hc_type_plot,"text") %>%
                layout_ggplotly  %>%
                layout(autosize = TRUE, margin = list(l = 0, r = 10, b = 70, t = 30, pad = -3))
        })
    
    ##### Transportation Plots #####
    output$public_transit_plot <- 
        renderPlotly({
            gen = ifelse("sex" %in% input$public_transport, T, F)
            age = ifelse("age_group" %in% input$public_transport, T, F)
            temp1 <- reshape_cat_data(gen, age, "BHV_PTRMT_COVID")
            temp1 <- temp1[temp1$category=="Yes",] %>% mutate(lab = "In Past Month")
            temp1
            temp2 <- reshape_cat_data(gen, age, "BHV_PTRPT_COVID")
            temp2 <- temp2[temp2$category=="Yes",] %>% mutate(lab = "Prior to Past Month")
            temp2
            if(gen & age){
                temp <- temp1 %>% left_join(temp2, by = c("gender", "age_group")) 
            } else if (gen & !age){
                temp <- temp1 %>% left_join(temp2, by = c("gender"))
            } else if (!gen & age){
                temp <- temp1 %>% left_join(temp2, by = c( "age_group")) 
            } else{
                temp <- temp1 %>% left_join(temp2, by = c("category")) 
            }
            
            p <- ggplot(temp) +
                geom_segment(aes(x = 1, xend = 1, y = percent.x, yend = percent.y ), color = "grey", size = 2) +
                geom_point(aes(x = 1, y = percent.x, col = lab.x), size = 5) +
                geom_point(aes(x = 1, y = percent.y, col = lab.y), size = 5) + 
                theme_bw() + 
                scale_color_manual(values = c("#003a66", "#afcd6d")) + 
                theme(axis.title.y=element_blank(),
                      axis.text.y=element_blank(),
                      axis.ticks.y=element_blank(),
                      legend.title = element_blank(),
                      legend.position = "top"
                ) +
                labs(x = "", y = "% Using Transit At Least Once Per Week") + 
                coord_flip() +
                theme(strip.text.x = element_text(size = 12),
                      strip.text.y = element_text(size = 12))
            p <- if(gen & age){
                p + facet_grid(gender ~ age_group)
            } else if(gen & !age){
                p + facet_grid(gender ~ .)
            } else if(!gen & age){
                p + facet_grid(. ~ age_group)
            } else{
                p 
            } 
            
            #clsa_plotly(p, "all")
            #Can't do clean labeling because of hte wayin which it has been created...
            clsa_plotly(p, "percent") %>%
                layout(legend = list(
                    orientation = "h"
                ),
                xaxis=list(fixedrange=TRUE),
                yaxis=list(fixedrange=TRUE)) %>%
                layout(autosize = TRUE, margin = list(l = 0, r = 30, b = 0, t = 30, pad = 1)) %>%
                layout_ggplotly
        })
    
    #behaviour Plots
    output$behavior_plot <- renderPlotly({
        variables_of_interest <- c("BHV_SELFQ_COVID",
                                   "BHV_LPBG_COVID",
                                   "BHV_LEAVH_COVID")
        gen = ifelse("sex" %in% input$gen_behav_questions, T, F)
        age = ifelse("age_group" %in% input$gen_behav_questions, T, F)
        tmp <- reshape_cat_data(gen, age,variables_of_interest)
        tmp <- tmp[tmp$category == "Yes", ]
        behav_plot <- produce_plot(tmp, gen, age,"sel_all")  +
            scale_x_discrete(labels = function(x) str_wrap(x, width = 20))
        clsa_plotly(behav_plot, "text") %>%
            layout(autosize = TRUE, margin = list(l = 0, r = 10, b = 70, t = 30, pad = 1)) %>%
            layout_ggplotly
    })
    
    output$contact_plot <- renderPlotly({
        variables_of_interest <- c(#"BHV_CONTACT_COVID",
            "BHV_CNTCT_SM_COVID",
            "BHV_CNTCT_TL_COVID",
            "BHV_CNTCT_VC_COVID")
        gen = ifelse("sex" %in% input$contact_questions, T, F)
        age = ifelse("age_group" %in% input$contact_questions, T, F)
        tmp <- reshape_cat_data(gen, age,variables_of_interest)
        tmp <- tmp[tmp$category == "Yes",]
        tmp$label <- gsub("-", 
                          "\n", 
                          tmp$label)
        #tmp <- bind_rows(tmp[4,], tmp[-4,])
        #tmp[1,"percent"] <- tmp$grouped_sum[1 ]/1963
        #tmp[2:4, "percent"] <- tmp$grouped_sum[2:4]/1963
        contact_plot <- produce_plot(tmp, gen, age,"sel_all") +
            scale_x_discrete(labels = function(x) str_wrap(x, width = 20))
        clsa_plotly(contact_plot, "text") %>%
            layout(autosize = TRUE, margin = list(l = 0, r = 10, b = 60, t = 30, pad = -3)) %>%
            layout_ggplotly
    })
    
    output$leave_home_plot <- 
        renderPlotly({
            gen = ifelse("sex" %in% input$leave_home_questions, T, F)
            age = ifelse("age_group" %in% input$leave_home_questions, T, F)
            #variables_of_interest <- c("BHV_RSN_BR_COVID",
            #                           "BHV_RSN_FD_COVID",
            #                           "BHV_RSN_FR_COVID",
            #                           "BHV_RSN_HLT_COVID",
            #                           "BHV_RSN_IN_COVID",
            #                           "BHV_RSN_PA_COVID",
            #                           "BHV_RSN_PET_COVID",
            #                           "BHV_RSN_PH_COVID",
            #                           "BHV_RSNTC_COVID",
            #                           "BHV_RSN_WRK_COVID")
            tmp <- reshape_cat_data(gen, age,grep("BHV_RSN",unique(long_data$question),value=TRUE))
            tmp <- tmp[tmp$category == "Yes",]
            leave_home_plot <- produce_plot(tmp, gen, age,"sel_all")
            clsa_plotly(leave_home_plot, "text") %>%
                layout(autosize = TRUE, margin = list(l = 0, r = 10, b = 70, t = 30, pad = -3)) %>%
                layout_ggplotly 
        })
    output$hand_washing_plot <- 
        renderPlot({
            gen = ifelse("sex" %in% input$handwashing, T, F)
            age = ifelse("age_group" %in% input$handwashing, T, F)
            variables_of_interest <- c("current_hand_wash", "past_hand_wash")
            hand_wash_plot <- continuous_data_plotting_function(data, variables_of_interest, gen, age)
            hand_wash_plot
            #clsa_plotly(hand_wash_plot)
        })
    
    output$pt_trips_plot <- 
        renderPlot({
            gen = ifelse("sex" %in% input$pt_trips, T, F)
            age = ifelse("age_group" %in% input$pt_trips, T, F)
            variables_of_interest <- c("current_pt_trips", "past_pt_trips")
            pt_trips_plot <- continuous_data_plotting_function(data, variables_of_interest, gen, age) + 
                scale_y_continuous(breaks=c(3,6,9))
            pt_trips_plot
            #clsa_plotly(hand_wash_plot)
        })
    output$pt_length_plot <- 
        renderPlot({
            gen = ifelse("sex" %in% input$pt_length, T, F)
            age = ifelse("age_group" %in% input$pt_length, T, F)
            variables_of_interest <- c("current_pt_length", "past_pt_length")
            pt_length_plot <- continuous_data_plotting_function(data, variables_of_interest, gen, age)
            pt_length_plot
            #clsa_plotly(hand_wash_plot)
        })
    
    ##### Work/voln tab plots #####
    
    output$WorkStatusPlot <- 
        renderPlotly({
            gen = ifelse("sex" %in% input$group_work, T, F)
            age = ifelse("age_group" %in% input$group_work, T, F)
            tmpdt <- reshape_cat_data(gen, age,c("LBF_WRK_COVID", "LBF_VOLN_COVID")) %>%
                filter(category == "Yes")
            work_plot <- produce_plot(tmpdt, gen, age,"sel_all")  +
                scale_x_discrete(labels = function(x) str_wrap(x, width = 20))
            clsa_plotly(work_plot, "text") %>%
                layout(autosize = TRUE, margin = list(l = 0, r = 10, b = 70, t = 30, pad = 1)) %>%
                layout_ggplotly
        })
    output$WorkDistancingPlot <- 
        renderPlotly({
            dist_var <- c("LBF_HOME_COVID","LBF_TELECON_COVID",
                          "LBF_COMPCL_COVID","LBF_PARTLCL_COVID")
            gen = ifelse("sex" %in% input$group_dist, T, F)
            age = ifelse("age_group" %in% input$group_dist, T, F)
            tmpdt <- reshape_cat_data(gen,age,dist_var) %>%
                filter(category=="Yes")
            dist_plot <- produce_plot(tmpdt,gen,age,"sel_all")
            clsa_plotly(dist_plot,"text") %>%
                layout(autosize = TRUE, margin = list(l = 0, r = 10, b = 70, t = 30, pad = 1)) %>%
                layout_ggplotly
        })
    output$WorkDaysPlot <- 
        renderPlotly({
            gen = ifelse("sex" %in% input$group_work_days, T, F)
            age = ifelse("age_group" %in% input$group_work_days, T, F)
            #variables_of_interest <- c("current_days_workplace", "past_days_workplace")
            #work_days_plot <- continuous_data_plotting_function(data, variables_of_interest, gen, age)
            tmpdt <- reshape_cat_data(gen,age,"Change in Days Worked")
            work_days_plot <- produce_plot(tmpdt,gen,age,"dodged")
            clsa_plotly(work_days_plot,"text") %>%
                layout(autosize = TRUE, margin = list(l = 0, r = 10, b = 70, t = 30, pad = 1)) %>%
                layout_ggplotly
        })
    output$WorkHoursPlot <- 
        renderPlotly({
            gen = ifelse("sex" %in% input$group_work_hrs, T, F)
            age = ifelse("age_group" %in% input$group_work_hrs, T, F)
            #variables_of_interest <- c("current_hours_workplace", "past_hours_workplace")
            #work_hrs_plot <- continuous_data_plotting_function(data, variables_of_interest, gen, age)
            tmpdt <- reshape_cat_data(gen,age,"Change in Hours Worked")
            work_hrs_plot <- produce_plot(tmpdt,gen,age,"dodged")
            clsa_plotly(work_hrs_plot,"text") %>%
                layout(autosize = TRUE, margin = list(l = 0, r = 10, b = 70, t = 30, pad = 1)) %>%
                layout_ggplotly
        })
    output$VolDaysPlot <- 
        renderPlotly({
            gen = ifelse("sex" %in% input$group_vol_days, T, F)
            age = ifelse("age_group" %in% input$group_vol_days, T, F)
            tmpdt <- reshape_cat_data(gen,age,"Change in Days Volunteered")
            vol_days_plot <- produce_plot(tmpdt,gen,age,"dodged")
            clsa_plotly(vol_days_plot,"text") %>%
                layout(autosize = TRUE, margin = list(l = 0, r = 10, b = 70, t = 30, pad = 1)) %>%
                layout_ggplotly
        })
    output$VolHoursPlot <- 
        renderPlotly({
            gen = ifelse("sex" %in% input$group_vol_hrs, T, F)
            age = ifelse("age_group" %in% input$group_vol_hrs, T, F)
            #variables_of_interest <- c("current_hours_workplace", "past_hours_workplace")
            #work_hrs_plot <- continuous_data_plotting_function(data, variables_of_interest, gen, age)
            tmpdt <- reshape_cat_data(gen,age,"Change in Hours Volunteered")
            vol_hrs_plot <- produce_plot(tmpdt,gen,age,"dodged")
            clsa_plotly(vol_hrs_plot,"text") %>%
                layout(autosize = TRUE, margin = list(l = 0, r = 10, b = 70, t = 30, pad = 1)) %>%
                layout_ggplotly
        })
    
    ##### Mental health tab plots #####
    
    output$ConseqPlot <- 
        renderPlotly({
        A = ifelse("sex" %in% input$group_conseq, T, F)
        B = ifelse("age_group" %in% input$group_conseq, T, F)
        tmpdt <- reshape_cat_data(A,B,"EXP_CONSEQ_COVID")
        tmpdt$category <- factor(tmpdt$category, levels = c("Very negative","Negative",
                                                            "No effect", "Positive","Very positive",
                                                            "No response recorded"))
        tmpdt$grouped_sum <- NULL
        conseq_plot <- produce_plot(tmpdt,A,B,"dodged") 
        clsa_plotly(conseq_plot, "text") %>%
            layout(autosize = TRUE, margin = list(l = 0, r = 10, b = 70, t = 30, pad = -3)) %>%
            layout_ggplotly 
    })
    
    exp_common <- c("EXP_PAND_SE_COVID",
                             "EXP_PAND_HC_COVID","EXP_PAND_LI_COVID",
                             "EXP_PAND_SF_COVID","EXP_PAND_UN_COVID",
                             "EXP_PAND_CL_COVID")
    exp_uncommon <- c("EXP_PAND_CG_COVID","EXP_PAND_YI_COVID",
                               "EXP_PAND_MD_COVID","EXP_PAND_DP_COVID",
                               "EXP_PAND_CO_COVID")
    output$ImpactPlotCommon <- 
        renderPlotly({
            A = ifelse("sex" %in% input$group_imp, T, F)
            B = ifelse("age_group" %in% input$group_imp, T, F)
            tmpdt <- reshape_cat_data(A,B,exp_common) %>%
                filter(category=="Yes")
            
            impact_plot <- produce_plot(tmpdt,A,B,"sel_all") +
                aes(x = reorder(label, grouped_sum)) + 
                labs(x="") + 
                scale_x_discrete(labels = function(x) str_wrap(x, width = 60))
            clsa_plotly(impact_plot, "text") %>%
                layout_ggplotly %>%
                layout(autosize = TRUE, margin = list(l = 450, r = 10, b = 70, t = 30, pad = 1))
    })
    output$ImpactPlotUncommon <- 
        renderPlotly({
            A = ifelse("sex" %in% input$group_imp_un, T, F)
            B = ifelse("age_group" %in% input$group_imp_un, T, F)
            tmpdt <- reshape_cat_data(A,B,exp_uncommon) %>%
                filter(category=="Yes")
            
            impact_plot <- produce_plot(tmpdt,A,B,"sel_all") +
                aes(x = reorder(label, grouped_sum)) + 
                labs(x="") + 
                scale_x_discrete(labels = function(x) str_wrap(x, width = 60))
            clsa_plotly(impact_plot, "text") %>%
                layout_ggplotly %>%
                layout(autosize = TRUE, margin = list(l = 450, r = 10, b = 70, t = 30, pad = 1))
        })
    
    output$DepPlot <- 
        renderPlotly({
            A = ifelse("sex" %in% input$group_dep, T, F)
            B = ifelse("age_group" %in% input$group_dep, T, F)
            tmpdt <- reshape_cat_data(A,B,"DEP_DPSFD_COVID") %>%
                mutate(category = case_when(category=="Negative screen for depression" ~ "Absence",
                       category=="Positive screen for depression" ~ "Presence",
                       category=="Inconclusive result of depression screening due to missing values" ~ "Inconclusive"))
            
            dep_plot <- produce_plot(tmpdt,A,B,"dodged")
            clsa_plotly(dep_plot, "text") %>%
                layout(autosize = TRUE, margin = list(l = 0, r = 10, b = 70, t = 30, pad = -3)) %>%
                layout_ggplotly 
        })
    
    output$AnxPlot <- 
        renderPlotly({
            A = ifelse("sex" %in% input$group_anx, T, F)
            B = ifelse("age_group" %in% input$group_anx, T, F)
            tmpdt <- reshape_cat_data(A,B,"GAD_DGRP_COVID")
            #tmpdt$category <- factor(tmpdt$category,levels=sort(unique(tmpdt$category),decreasing=TRUE))
            anx_plot <- produce_plot(tmpdt,A,B,"dodged") + 
                aes(x = factor(category, levels=c("Inconclusive","Severe","Moderate",
                                               "Mild","None"))) +
                labs(x="") 
            clsa_plotly(anx_plot, "text") %>%
                layout(autosize = TRUE, margin = list(l = 0, r = 10, b = 70, t = 30, pad = -3)) %>%
                layout_ggplotly 
        })
    
    ## About Survey Text
    output$text <- renderUI({
        HTML('<p style="font-size: 12pt">',paste(about_text, collapse="<br/><br/>"))})
}

shinyApp(ui, server)
