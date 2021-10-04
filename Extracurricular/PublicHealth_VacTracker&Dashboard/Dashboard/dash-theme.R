
## CLSA color codes: 
## dark green - #003A66 rgb(174,205,109)
## light green - #dceab7 rgb(220,234,183)
## navy - #003A66 rgb(0,58,102)
## added light blue - #60a0c3 rgb(96,160,195)
#mycols <- c("#013667","#60a0c3","#8cc641","#dceab7")
#mycols <- c("#dceab7","#AECD6D","#60a0c3","#003A66")
mycols <- c("#202d61","#009aa1","#006aaa","#63bdc4","#539bd5")

theme_clsa_flatly <- shinyDashboardThemeDIY(
  
  ### general
  appFontFamily = "Arial"
  ,appFontColor = "rgb(33,37,41)" 
  ,primaryFontColor = "rgb(245,245,245)" 
  ,infoFontColor = "rgb(245,245,245)"
  ,successFontColor = "rgb(245,245,245)"
  ,warningFontColor = "rgb(245,245,245)"
  ,dangerFontColor = "rgb(33,37,41)"
  ,bodyBackColor = "rgb(255,255,255)" # white
  
  ### header
  ,logoBackColor = "rgb(0,58,102)" # mint
  
  ,headerButtonBackColor = "rgb(0,58,102)" 
  ,headerButtonIconColor = "rgb(174,205,109)" 
  ,headerButtonBackColorHover = "rgb(0,58,102)" 
  ,headerButtonIconColorHover = "rgb(0,0,0)" 
  
  ,headerBackColor = "rgb(0,58,102)"
  ,headerBoxShadowColor = ""
  ,headerBoxShadowSize = "0px 0px 0px"
  
  ### sidebar
  ,sidebarBackColor = "rgb(145,145,145)"
  ,sidebarPadding = 0
  
  ,sidebarMenuBackColor = "inherit"
  ,sidebarMenuPadding = 0
  ,sidebarMenuBorderRadius = 0
  
  ,sidebarShadowRadius = ""
  ,sidebarShadowColor = "0px 0px 0px"
  
  ,sidebarUserTextColor = "rgb(255,255,255)"
  
  ,sidebarSearchBackColor = "rgb(255,255,255)"
  ,sidebarSearchIconColor = "rgb(44,62,80)"
  ,sidebarSearchBorderColor = "rgb(255,255,255)"
  
  ,sidebarTabTextColor = "rgb(255,255,255)"
  ,sidebarTabTextSize = 16
  ,sidebarTabBorderStyle = "none"
  ,sidebarTabBorderColor = "none"
  ,sidebarTabBorderWidth = 0
  
  ,sidebarTabBackColorSelected = "rgb(0,58,102)"
  ,sidebarTabTextColorSelected = "rgb(255,255,255)"
  ,sidebarTabRadiusSelected = "0px"
  
  ,sidebarTabBackColorHover = "rgb(44,62,80)"
  ,sidebarTabTextColorHover = "rgb(255,255,255)"
  ,sidebarTabBorderStyleHover = "none"
  ,sidebarTabBorderColorHover = "none"
  ,sidebarTabBorderWidthHover = 0
  ,sidebarTabRadiusHover = "0px"
  
  ### boxes
  ,boxBackColor = "rgb(245,245,245)"
  ,boxBorderRadius = 0
  ,boxShadowSize = "0px 0px 0px"
  ,boxShadowColor = ""
  ,boxTitleSize = 19
  ,boxDefaultColor = "rgb(52,152,219)"
  ,boxPrimaryColor = "rgb(0,58,102)" # navy
  ,boxInfoColor = "rgb(0,106,170)" # blue
  ,boxSuccessColor = "rgb(140,198,65)" # green
  ,boxWarningColor = "rgb(0,154,161)" # teal
  ,boxDangerColor = "rgb(231,76,60)" # red
  
  ,tabBoxTabColor = "rgb(44,62,80)"
  ,tabBoxTabTextSize = 14
  ,tabBoxTabTextColor = "rgb(24, 188, 156)"
  ,tabBoxTabTextColorSelected = "rgb(255, 255, 255)"
  ,tabBoxBackColor = "rgb(255,255,255)"
  ,tabBoxHighlightColor = "rgb(255,255,255)"
  ,tabBoxBorderRadius = 10
  
  ### inputs
  ,buttonBackColor = "rgb(44,62,80)"
  ,buttonTextColor = "rgb(255,255,255)"
  ,buttonBorderColor = "rgb(44,62,80)"
  ,buttonBorderRadius = 5
  
  ,buttonBackColorHover = "rgb(30,43,55)"
  ,buttonTextColorHover = "rgb(255,255,255)"
  ,buttonBorderColorHover = "rgb(30,43,55)"
  
  ,textboxBackColor = "rgb(255,255,255)"
  ,textboxBorderColor = "rgb(206,212,218)"
  ,textboxBorderRadius = 5
  ,textboxBackColorSelect = "rgb(255,255,255)"
  ,textboxBorderColorSelect = "rgb(89,126,162)"
  
  ### tables
  ,tableBackColor = "rgb(255,255,255)"
  ,tableBorderColor = "rgb(236,240,241)"
  ,tableBorderTopSize = 1
  ,tableBorderRowSize = 1
  
)

## ggplot theme for dashboard
ggtheme_clsa <- function(){
  theme_bw() + 
    theme(axis.text = element_text(color="black",size=14),
          axis.title = element_text(color="black",size=14))
}

## Convert ggplot to plotly consistently
clsa_plotly <- function(fig, txt = "text"){
  ggplotly(fig, tooltip = txt) %>% 
    config(displayModeBar = FALSE) %>% 
    layout(xaxis=list(fixedrange=TRUE)) %>%
    layout(yaxis=list(fixedrange=TRUE))
}

reverse_legend_labels <- function(plotly_plot) {
  n_labels <- length(plotly_plot$x$data)
  plotly_plot$x$data[1:n_labels] <- plotly_plot$x$data[n_labels:1]
  plotly_plot
}

