## Process the follow-up data the forma
library(data.table)
library(readxl)
library(xts)
library(reshape2)
library(dplyr)
library(stringr)
library(forcats)


## Read in raw data  (Give your path)
raw_data <- as.data.table(read.csv("/Users/tylerliu/CLSA-RA-Files/follow-up-data/week1_summary.csv",header=T, na.strings=c("","NA")))


names(raw_data)[1:3] <- c("question", "label", "category")
raw_data$question <- na.locf(raw_data$question, fromLast = FALSE)
raw_data$label <- na.locf(raw_data$label, fromLast = FALSE )
raw_data$Frequency <- NULL
raw_data$Relative.Frequency <- NULL
raw_data[,3] <- sapply(raw_data[,3],as.character)
colnames(raw_data)[4:13] <- c("F [<55]","F [55-64]","F [65-74]","F [75-84]","F [85+]","M [<55]","M [55-64]","M [65-74]","M [75-84]","M [85+]")
## Merge the choice "MILD", "MODERATE", "SEVERE" to "Yes"
raw_data$category_label
raw_data <- raw_data %>% 
  mutate(category = ifelse(category %in% c("MILD","MODERATE","SEVERE"),"Yes", category)) %>%
  group_by(question,label,category) %>%
  summarise_all(sum)

## Merge the choice "DKNA(Don’t know / No answer)","REFUSED","MISSING","SKIP PATTERN" to "No response recorded"
raw_data <- raw_data %>% 
  mutate(category = ifelse(category %in% c("DKNA","REFUSED","MISSING","SKIP PATTERN"),"No response recorded",category)) %>%
  group_by(question,label,category) %>% 
  summarise_all(sum)

## Change "RSLT_NOT_AVAIL" to "Tested but result not available yet"
raw_data <- raw_data %>% 
  mutate(category = ifelse(category == "RSLT_NOT_AVAIL","Tested but result not available yet", category))

## Convert raw data to long format 
long_data <- melt(raw_data, id.vars = c("question", "label", "category")) %>%
  arrange(question, category) %>%
  filter(variable != "Total" & variable != "%" ) %>%
  mutate(gender = substr(variable, 1, 1),
         age_group = substr(variable, 3, nchar(as.character(variable)))) 
long_data$gender <- as.character(factor(long_data$gender, labels = c("Male", "Female"), levels = c("M", "F")))
long_data$age_group <- as.character(factor(long_data$age_group,
                                           labels = c("<55", "55-64", "65-74", "75-84", "85+"),
                                           levels = c("[<55]","[55-64]", "[65-74]", "[75-84]", "[85+]")))

## Save long_data.rds file  (Give your path)
saveRDS(long_data,file="/Users/tylerliu/CLSA-RA-Files/follow-up-data/week1_long_data.rds")

