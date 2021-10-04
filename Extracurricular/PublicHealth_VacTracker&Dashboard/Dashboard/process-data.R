## Process data and save long_data for use in app
# Conversion Script by Andy
## Adapted for dashboard use by Shannon
library(data.table)
library(readxl)
library(xts)
library(reshape2)
library(dplyr)
library(stringr)
library(forcats)

## Helper functions for labels
capFirst <- function(s) {
  paste(toupper(substring(s, 1, 1)), substring(s, 2), sep = "")
}

removeCap <- function(s) {
  paste(substring(s, 1, 1), tolower(substring(s, 2, nchar(s))), sep = "")
}

## Read in raw data 
raw_data <- read_excel("/Users/tylerliu/CLSA-RA-Files/follow-up-data/COVIDQuestionnaireBaseline_Frequencies_Discrete_update2.1.xlsx", 
                                                                     sheet = "COVID_discrete")
tmp <- read_excel("/Users/tylerliu/CLSA-RA-Files/follow-up-data/COVIDQuestionnaireBaseline_Frequencies_Discrete_update2.1.xlsx", 
                       sheet = "COVID_discrete")
#raw_data <- read_excel("~/Downloads/COVIDQuestionnaireBaseline_Frequencies_Discrete_update2.1.xlsx", 
#                       sheet = "COVID_discrete")


#raw_data2 <- read_excel("~/Dropbox/CLSA Data Dashboard/Original Data/COVIDQuestionnaireBaseline_1Jun2020fordashboard.xlsx", 
#                       skip = 1)
names(raw_data)[2] <- "variable_label"
#which(is.na(raw_data$variable))
raw_data$variable <- na.locf(raw_data$variable, fromLast = FALSE)
raw_data$variable_label <- na.locf(raw_data$variable_label, fromLast = FALSE)

names(raw_data)[1:3] <- c("question", "label", "category")
names(raw_data)[5] <- "category_label"
raw_data$missing <- NULL
raw_data$Frequency <- NULL

## Add variable labels to newly created categorical change variables
change_var_labels <- c("Decrease","Increase","No Change","Skip pattern","No response recorded")
change_var_qs <- c("Change in Days Worked","Change in Hours Worked",
                   "Change in Days Volunteered","Change in Hours Volunteered")
raw_data[raw_data$question%in%change_var_qs,]$category_label <- change_var_labels

cont_var <- c("Number of people currently living in househld Categorical",
              "Number of people usually living in househld Categorical",
              "Number of times washed hands in past month Categorical",
              "Number of times washed hands prior to one month ago Categorical",
              "Number of one-way trips per week in past month Categorical",
              "Duration of each trip in past month Categorical",
              "Number of one-way trips per week prior to one month ago Categorical",
              "Duration of each trip prior to one month ago Categorical")
raw_data[raw_data$question%in%cont_var,]$category_label <- raw_data[raw_data$question%in%cont_var,]$category

raw_data$category <- NULL


## Compress symptom categories Mild/Moderate/Severe to Yes
tmp <- raw_data %>% 
  mutate(category_label = ifelse(category_label %in% c("Mild","Moderate","Severe"),
                              "Yes", category_label)) %>%
  group_by(question,label,category_label) %>%
  summarise_all(sum)

## Compress "Unknown" category, titled "No response recorded" 
tmp <- tmp %>% 
  mutate(category_label = ifelse(category_label %in% c("Don't know/ No answer",
                                                       "Prefer not to answer",
                                                       "Missing"),
                                 "No response recorded", category_label)) %>%
  group_by(question,label,category_label) %>% 
  summarise_all(sum)

## Convert raw data to long format 
long_data <- melt(tmp, id.vars = c("question", "label", "category_label")) %>%
  arrange(question, category_label) %>%
  filter(variable != "Total" & variable != "%" ) %>%
  mutate(gender = substr(variable, 1, 1),
         age_group = substr(variable, 3, nchar(as.character(variable)))) 
long_data$gender <- as.character(factor(long_data$gender, labels = c("Male", "Female"), levels = c("M", "F")))
long_data$age_group <- as.character(factor(long_data$age_group,
                                           labels = c("<55", "55-64", "65-74", "75-84", "85+"),
                                           levels = c("[<55]","[55-64]", "[65-74]", "[75-84]", "[85+]")))
## Convert long to wide data 
wide_data <- long_data %>%
  select(-label) %>%
  dcast(gender + age_group  + variable ~ question*category_label)

age_group_sizes = c(792 + 725, 4844 + 4079, 5213 + 4860, 3013 + 2914, 1055 + 962)

long_data$category <- long_data$category_label
long_data$category_label <- NULL
## Format data
setDT(long_data)

## Format labels
long_data[, label := capFirst(label)]
long_data[, label := gsub("/ ", " or ",label)]
## fix typo in label
long_data[label=="Diaherria", label := "Diarrhea"]
long_data[label=="Heart", label := "Heart disease"]
long_data[label=="Pneumonia that was confirmed using chest X-rays",
          label := "Pneumonia confirmed via chest X-ray"]
long_data[label=="Fever in past month",label := "Fever"]

## Format responses to categorical questions
long_data[category=="DKNA", category := "Don't know"]
long_data[question!="PROV", category := removeCap(category)]
long_data[, category := gsub("_"," ",category)]

## Format responses to depression questions
long_data[category=="All time",     category := "All of the time (5-7 days)"]
long_data[category=="Occasionally", category := "Occasionally (3-4 days)"]
long_data[category=="Some time",    category := "Some of the time (1-2 days)"]
long_data[category=="Rarely never", category := "Rarely or never (less than 1 day)"]

## Format responses to consequences of COVID-19 questions
long_data[category=="Very neg", category := "Very negative"]
long_data[category=="Very pos", category := "Very positive"]
long_data[label=="Unable to care for people require assistance due to limitation",
          label := "Unable to care for people who require assistance due to health condition or limitation"]
long_data[label=="Unable to access necessary food or supplies", 
          label := "Unable to access necessary supplies or food"]
long_data[label=="Increased caregiving",
          label := "Increased time caregiving"]
long_data[label=="Increased physical or verbal conflict",
          label := "Increased verbal or physical conflict"]

## Additional formatting of responses
long_data[category=="Not all", category := "Not at all"]

## Format responses to Health Care Visit Type
long_data[question=="SYM_CNSWHO_NN_COVID", label := "Other"]
long_data[label%in%grep("Consulted",unique(long_data$label),value=TRUE),
          label := gsub("Consulted ","",label)]

## Format marijuana questions: 
## Separate categories "Not currently" and "Never in my lifetime" 
#tmp <- long_data[question=="SMK_CANN_COVID"&category=="No"]
long_data[question=="SMK_CANNCUR_COVID"&category=="Not at all",
          category := "Not currently"]
long_data[question=="SMK_CANNCUR_COVID"&category=="Daily",
          category := "At least once daily"]
long_data[question=="SMK_CANNCUR_COVID"&category=="Occasionally (3-4 days)",
          category := "Occasionally, but not every day"]
long_data[question=="SMK_CANNCUR_COVID"&category=="Skip pattern",
          category := "Never in my lifetime"]

## Format smoking labels
long_data[question=="SMK_CURRCG_COVID"&category=="Daily",
          category := "At least one daily"]
long_data[question=="SMK_CURRCG_COVID"&category=="Occasionally (3-4 days)",
          category := "Occasionally, but not every day"]

## Format behavior labels
long_data[, label := gsub(" - past month","",label)]
long_data[, label := gsub("Left home ","",label)]
long_data[label=="To the pharmacy", label := "To go to the pharmacy"]
long_data[label=="To go to hospital", label := "To go to the hospital/receive medical treatment"]
long_data[label=="Been in self quarantine", label := "Been in self-quarantine"]
long_data[label=="Been in large public gathering (250+)",
          label := "Been in large public gathering (250+) since 1/1/2020"]
long_data[label=="Contact through video conferencing",
          label := "Video Conferencing or Video Calling"]
long_data[label=="Contact through telephone",
          label := "Telephone"]
long_data[label=="Social media contact",
          label := "Social Media"]

## Format anxiety labels
long_data[category=="severe anxiety", category := "Severe"]
long_data[category=="moderate anxiety", category := "Moderate"]
long_data[category=="minimal anxiety", category := "None"]
long_data[category=="mild anxiety", category := "Mild"]
long_data[category=="Cannot be calculated due to missing items", category := "Inconclusive"]
  
## Format province labels
long_data[category=="New brunswick", category := "New Brunswick"]
long_data[category=="British columbia", category := "British Columbia"]
long_data[category=="Nova scotia", category := "Nova Scotia"]
long_data[category=="Prince edward island", category := "Prince Edward Island"]

## Format continuous variable labels
long_data[category=="Dk/ref/mis", category := "No response recorded"]
long_data[category=="NANA", category := "1"]

long_data[question=="Number of people usually living in househld Categorical", label := "Usual number of people"]
long_data[question=="Number of people currently living in househld Categorical", label := "Current number of people"]

## Re-label COVID categories
long_data[category=="Tested negative and not told by health provider had covid",
          category := "Tested Negative & Not Provider Diagnosed"]
long_data[category=="Either tested positive or told by health provider had covid",
          category := "Tested Positive or Provider Diagnosed Positive"]
long_data[category=="Tested but result not available and not told by health provider had covid",
          category := "Tested & Result Unknown & Provider Diagnosis Unknown"]
long_data[category=="Testing status and what told by health provider both unknown",
          category := "Testing Status Unknown & Provider Diagnosis Unknown"]
long_data[category=="Either not tested and not told by health provider had covid or unknown testing status but known to not be told by health provider had covid",
          category := "Either Not Tested or Unknown Testing Status & Not Provider Diagnosed"]

long_data[, label := capFirst(label)]

saveRDS(long_data,file="~/Dropbox/CLSA Data Dashboard/Shannon CLSA/clsa-dashboard/long_data.rds")
#saveRDS(long_data,file="~/Documents/UMN/RA - Basta/CLSA Dashboard/clsa-dashboard/long_data.rds")

