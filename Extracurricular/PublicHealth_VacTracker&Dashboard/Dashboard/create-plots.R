## Read data
long_data <- readRDS("long_data.rds")
aggregated_continuous_data <- read.csv("aggregated_continuous_data.csv", stringsAsFactors = F)
aggregated_continuous_data <- aggregated_continuous_data %>%
  mutate(Question = ifelse(variable=="usually_living_household","Usual number of people",Question)) %>%
  mutate(Question = ifelse(variable=="current_living_household","Current number of people",Question))

## Reshape data function
reshape_cat_data <- function(gen, age,variables_of_interest){
  data <- if(gen & age){
    long_data[which(long_data$question %in% variables_of_interest)] %>%
      filter(category != "Skip pattern") %>%
      group_by(question, gender, age_group, category, label) %>%
      summarize(grouped_sum = sum(value)) %>% ungroup() %>%
      group_by(question, gender, age_group) %>%
      mutate(percent  = grouped_sum/sum(grouped_sum)*100) %>%
      mutate(text = paste0("Percent: ",round(percent,digits=2),"% \nCount: ",grouped_sum," of ",sum(grouped_sum)))
  } else if(gen & !age){
    long_data[which(long_data$question %in% variables_of_interest)] %>%
      filter(category != "Skip pattern") %>%
      group_by(question,gender, category, label) %>%
      summarize(grouped_sum = sum(value)) %>% ungroup() %>%
      group_by(question, gender) %>%
      mutate(percent  = grouped_sum/sum(grouped_sum)*100)%>%
      mutate(text = paste0("Percent: ",round(percent,digits=2),"% \nCount: ",grouped_sum," of ",sum(grouped_sum)))
  } else if(!gen & age){
    long_data[which(long_data$question %in% variables_of_interest)] %>%
      filter(category != "Skip pattern") %>%
      group_by(question,age_group, category, label) %>%
      summarize(grouped_sum = sum(value)) %>% ungroup() %>%
      group_by(question, age_group) %>%
      mutate(percent  = grouped_sum/sum(grouped_sum)*100)%>%
      mutate(text = paste0("Percent: ",round(percent,digits=2),"% \nCount: ",grouped_sum," of ",sum(grouped_sum)))
  } else{
    long_data[which(long_data$question %in% variables_of_interest)] %>%
      filter(category != "Skip pattern") %>%
      group_by(question, category, label) %>%
      summarize(grouped_sum = sum(value)) %>% ungroup() %>%
      group_by(question) %>%
      mutate(percent  = grouped_sum/sum(grouped_sum)*100)%>%
      mutate(text = paste0("Percent: ",round(percent,digits=2),"% \nCount: ",grouped_sum," of ",sum(grouped_sum)))
  }
  return(data)
}

stacked_plot <- function(data, gen, age, y_size = 0){
  p <- ggplot(data, aes(x = label, y = percent, fill = category)) + geom_bar(stat = "identity") + scale_y_continuous(labels = scales::percent) +
    coord_flip() + xlab("") + ylab("") + theme(legend.title = element_blank()) + 
    aes(text=text)
  p <- if(gen & age){
    p + facet_grid(gender ~ age_group)
  } else if(gen & !age){
    p + facet_grid(gender ~ .)
  } else if(!gen & age){
    p + facet_grid(. ~ age_group)
  } else{
    p 
  }
  if(y_size>0){p = p + theme(axis.text.y=element_text(size=y_size))}
  return(p)
}

dodged_plot <- function(data, gen, age, y_size = 0){
  if(!is.null(data$grouped_sum)){
  data <- data %>%
    mutate(category = factor(category, levels = category[order(-grouped_sum)]))}
  #data$category <- factor(data$category,levels=sort(unique(data$category),decreasing=TRUE))
  p <- ggplot(data, aes(fct_rev(as.factor(category)), percent)) + 
    geom_bar(stat="identity",position = position_dodge2(reverse=TRUE)) + 
    ggtheme_clsa() + coord_flip() + aes(text=text) +
    labs(x="",y="Percent of Participants") 
  p <- if(gen & age){
    p + aes(fill=age_group) + labs(fill="") + facet_wrap( ~ gender) + 
      scale_fill_manual(values=mycols)
  } else if(gen & !age){
    p + aes(fill=gender) + labs(fill="") + 
      scale_fill_manual(values=mycols[3:4])
  } else if(!gen & age){
    p + aes(fill=age_group) + labs(fill="")  + 
      scale_fill_manual(values=mycols)
  } else{
    p 
  }
  if(y_size>0){p = p + theme(axis.text.y=element_text(size=y_size))}
  return(p)
}

select_all_plot <- function(data, gen, age, y_size = 0){
  data$label <- reorder(data$label, data$grouped_sum) 
  p <- ggplot(data, aes(label, percent)) + 
    geom_bar(stat="identity",position = position_dodge2(reverse=TRUE)) + 
    ggtheme_clsa() + coord_flip() + aes(text=text) +
    labs(x="",y="Percent of Participants") 
  p <- if(gen & age){
    p + aes(fill=age_group) + labs(fill="") + 
      facet_wrap( ~ gender) + scale_fill_manual(values=mycols)
  } else if(gen & !age){
    p + aes(fill=gender) + labs(fill="") + 
      scale_fill_manual(values=mycols[3:4])
  } else if(!gen & age){
    p + aes(fill=age_group) + labs(fill="") +
      scale_fill_manual(values=mycols)
  } else{
    p 
  }
  if(y_size>0){p = p + theme(axis.text.y=element_text(size=y_size))}
  return(p)
}


## move individual plots to separate functions; call in main function
## Plot function
produce_plot <- function(data,gen, age, plot_type, adjustment = F, y_size = 0){
  if(adjustment == F){
    if(plot_type=="stacked"){
      p <- stacked_plot(data = data, gen = gen, age = age)
    }
    if(plot_type=="dodged"){
      p <- dodged_plot(data = data, gen = gen, age = age)
    }
    if(plot_type=="sel_all"){
      p <- select_all_plot(data = data, gen = gen, age = age)
    }
  }
  else{
    if(plot_type=="stacked"){
      p <- stacked_plot(data = data, gen = gen, age = age, y_size = y_size)
    }
    if(plot_type=="dodged"){
      p <- dodged_plot(data = data, gen = gen, age = age, y_size = y_size)
    }
    if(plot_type=="sel_all"){
      p <- select_all_plot(data = data, gen = gen, age = age, y_size = y_size)
    }
  }
  m <- list(
    l = 0,
    r = 0,
    b = 50,
    t = 50,
    pad = -3
  )
  return(p)
}

### Continuous Variable Plotting Function
continuous_data_plotting_function <- function(data, variables_of_interest, Sex_check, Age_check){
  data <- aggregated_continuous_data %>% filter(variable %in% variables_of_interest)
  if(Sex_check){
    Sex_filter <- c("Male", "Female")
  } else{
    Sex_filter <- c("Both")
  }
  if(Age_check){
    Age_filter <- c("<55", "55-64", "65-74", "75-84", "85+")
  } else{
    Age_filter <- c("All")
  }
  plotting_data_temp <- data %>% filter(variable %in% variables_of_interest) %>% filter(Sex %in% Sex_filter, Age_Group %in% Age_filter)
  p <- ggplot(plotting_data_temp, aes(x = Question)) +
    geom_errorbar(aes(ymin = Q1, ymax = Q3, width = .25)) + 
    geom_point(aes(y = Median, color = Question), size = 7) + coord_flip()  + ggtheme_clsa() + 
    scale_color_manual(values = c("#003a66", "#afcd6d")) + theme(legend.position = "none") + 
    #annotate("text",  x=-Inf, y = Inf, label = "Error Bars Represent First and Third Quartile", vjust=-1, hjust=1) + 
    xlab("") + ylab("Median Number of People (Bars represent 25th and 75th percentile)") +
    theme(axis.text.y = element_text(size = 16),
          axis.title.x = element_text(size = 16)) +
    theme(strip.text.x = element_text(size = 16),
          strip.text.y = element_text(size = 16))
  p <- if(Sex_check & Age_check){
    p + facet_grid(Sex ~ Age_Group)
  } else if(Sex_check & !Age_check){
    p + facet_grid(Sex ~ .)
  } else if(!Sex_check & Age_check){
    p + facet_grid(. ~ Age_Group)
  } else{
    p 
  } 
  return(p)
}





# Still working on implementing Echo's Faceting Code - ANDY 7/13/2020

# stacked_plot <- function(data, gen, age){
#   p <- ggplot(data, aes(x = label, y = percent, fill = category)) + geom_bar(stat = "identity") + scale_y_continuous(labels = scales::percent) +
#     coord_flip() + xlab("") + ylab("") + theme(legend.title = element_blank()) + facet_grid(NULL ~ NULL)
#   # p <- if(gen & age){
#   #   p + facet_grid(gender ~ age_group)
#   # } else if(gen & !age){
#   #   p + facet_grid(gender ~ .)
#   # } else if(!gen & age){
#   #   p + facet_grid(. ~ age_group)
#   # } else{
#   #   p 
#   # }
#   return(p)
# }
# 
# variables_of_interest <- behavior_variable_table[which(behavior_variable_table[,2] %in% input$behavior_variable_list),1]
# #if(length(variables_of_interest) == 0){
# #    return("Please Select Behavior Variables to Display")
# #}
# B = ifelse("age_group" %in% input$group_behavior, T, F)
# A = ifelse("gender" %in% input$group_behavior, T, F)
# 
# variables_of_interest <- behavior_variable_table[1,1]
# B = F
# A = F
# 
# #produce_categorical_plot(A, B, variables_of_interest)
# tmpdt <- reshape_cat_data(A, B, variables_of_interest)
# behav_plot <- stacked_plot(tmpdt, A, B)
# behav_plot <- produce_plot(tmpdt, A, B, "stacked")
# behav_plot
# 
# #Echo's code related to better faceting. Should be implemented instead of the the if statements
# 
# # select_LBF_4() %>%
# #   filter(category == "Yes") %>% unique() %>%
# #   ggplot(aes(x = label, y = prop_val, 
# #              text = paste0(round(prop_val,2), "% (", sum_val, ")"))) +
# #   geom_bar(stat = "identity") +
# #   coord_flip() +
# #   facet_grid(rows = switch(("gender" %in% input$LBF_4_groupby), 
# #                            vars(!!sym("gender")), NULL), 
# #              cols = switch(("age_group" %in% input$LBF_4_groupby), 
# #                            vars(!!sym("age_group")), NULL)) +
# #   xlab("") + ylab("") +
# #   ggtheme_clsa()
