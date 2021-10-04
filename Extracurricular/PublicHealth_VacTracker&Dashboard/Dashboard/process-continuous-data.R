
library(data.table)

## Set data path to continous data variables
dat_path <- "~/Dropbox/CLSA Data Dashboard/Original Data/Continuous Variables/August 7 Update/"

## List all files within folder of interest
files_sources <- list.files(file.path(dat_path),
                            full.names = TRUE)

## Read in data and add variable for file name
read_cnt_data <- function(x){
  tmp <- read.csv(files_sources[x])
  tmp$Question <- basename(files_sources[x])
  return(tmp)
}

## Combine files of all continous data
aggregated_continuous_data <- do.call(rbind,lapply(1:length(files_sources), read_cnt_data))
setDT(aggregated_continuous_data)
aggregated_continuous_data[, X := NULL]

## Change column names
setnames(aggregated_continuous_data, c("Age.Group"),c("Age_Group"))

## Remove .csv from question title
aggregated_continuous_data[, Question := gsub(".csv","", Question)]

## Add names of continuous variables
var_names <- data.frame(Question = c("In past month number of times washed hands on average in a day",
                                     "In the past month average length of trips on public transportation",
                                     "In the past month number of one-way trips on public transportation per week",
                                     "Number of people (including yourself) currently living in your residence",
                                     "Number of people (including yourself) usually living in your residence",
                                     "Prior to one month ago average length of trips on public transportation",
                                     "Prior to one month ago number of one-way trips on public transportation per week",
                                     "Prior to one month ago number of times washed hands on average in a day"),
                        variable = c("current_hand_wash","current_pt_length","current_pt_trips",
                                     "current_living_household","usually_living_household",
                                     "past_pt_length","past_pt_trips","past_hand_wash"))
aggregated_continuous_data <- merge(aggregated_continuous_data,var_names,by="Question",all.x=TRUE)

write.csv(aggregated_continuous_data, paste0(dat_path,"aggregated_continuous_data.csv"))

