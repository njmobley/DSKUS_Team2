# 데이터 불러오기
library(readr)
library(readxl)
library(dplyr)
library(ggplot2)
library(tidyr)
library(plotly)

## migration
migration = read_excel('undesa_pd_2020_ims_stock_by_sex_and_origin.xlsx', sheet = 'Table 1', skip = 10)

# 필요없는 데이터 치우고 column명 바꾸기
migration = migration %>% 
  select(`Region, development group, country or area`:`2020...12`) %>%
  slice(-c(1:21)) %>%
  select(-`Notes`, -`Type of data`) %>% 
  rename(`1990` = `1990...6`,
         `1995` = `1995...7`,
         `2000` = `2000...8`,
         `2005` = `2005...9`,
         `2010` = `2010...10`,
         `2015` = `2015...11`,
         `2020` = `2020...12`,
         country = `Region, development group, country or area`)


# 대륙별 이주민 수 나타내기
migration1 = migration %>% 
  filter(country %in% c('AFRICA', 'ASIA', 'EUROPE', 'LATIN AMERICA AND THE CARIBBEAN', 'NORTHERN AMERICA', 'OCEANIA', 'OTHER')) %>%
  pivot_longer(names_to = 'year', values_to = 'n_migrants', -c(country, `Location code`)) %>%
  ggplot(aes(x = year, y = n_migrants, group = country)) +
  geom_point(aes(color = country)) +
  geom_line(aes(color = country)) +
  scale_y_continuous(labels = scales::comma)
  
ggplotly(migration1)


# 나라별 이주민 수 나타내기
migration2 = subset(migration, !(country %in% c('AFRICA', 'Eastern Africa', 'Middle Africa', 'Northern Africa', 'Southern Africa', 'Western Africa', 'ASIA', 'Central Asia', 'Eastern Asia', 'South-Eastern Asia', 'Southern Asia', 'Western Asia', 'EUROPE', 'Eastern Europe', 'Northern Europe', 'Southern Europe', 'Western Europe', 'LATIN AMERICA AND THE CARIBBEAN', 'Caribbean', 'Central America', 'South America', 'NORTHERN AMERICA', 'OCEANIA', 'Australia and New Zealand', 'Melanesia', 'Micronesia', 'Polynesia*', 'OTHER'))) %>% 
  pivot_longer(names_to = 'year', values_to = 'n_migrants', -c(country, `Location code`))

View(migration2)

migration2_plot = migration2 %>%
  top_n(100) %>% 
  ggplot(aes(x = year, y = n_migrants, group = country)) +
  geom_point(aes(color = country)) +
  geom_line(aes(color = country)) +
  scale_y_continuous(labels = scales::comma)

ggplotly(migration2_plot)


## poverty
poverty = read_csv('share-of-population-in-extreme-poverty.csv')
poverty %>% group_by(Entity) %>% count(Entity)

poverty_plot = poverty %>%
  filter(Entity %in% c('Japan', 'Russia', 'South Korea', 'Sweden', 'United Kingdom', 'United States', 'Hungary', 'Australia', 'Austria', 'Denmark', 'Canada')) %>%
  mutate(share_of_population_below_poverty_line = `$1.90 per day - share of population below poverty line`) %>% 
  ggplot(aes(x = Year, y = share_of_population_below_poverty_line, group = Entity)) +
  geom_line(aes(color = Entity))

ggplotly(poverty_plot)

