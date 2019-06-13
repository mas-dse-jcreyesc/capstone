
# UCSD MAS-DSE 260
## Mapping the U.S. Non-Profit Space : Classy Data Analysis Project
Advisors: Ben Cipollini and Ilkay Altintas

### CONFIGURATION
```
make build
make start
make stop
```

### MODULES
In broswer window go to:  `localhost:8888`

### APP
In broswer window go to:  `localhost:80` or `localhost`

### INTRO
The social sector is typically viewed in terms of nonprofit
organizations and the cause categories they belong to. It’s
clear, however, that while younger generations are active in
social causes, they think more in terms of current events and
social causes organizations - so much so, that new donor
churn now peaks at over 80%.

It is not clear, however, how to lay out a common “social
space”, where the organizations that drive social change and
potential donors could connect, find organization and cause
recommendations, and where discovery of new causes - and
news events within causes - could be facilitated.

In this project, we build this social space from the ground up.
We use a combination of government IRS form 990 (returns
for nonprofits) data along with external textual information
(i.e. social media) to create a robust semantic space.

### TEAM
Budget Manager: Jeet Nagda
Management of AWS funds and cloud-related activity
Project Manager: Howard Tai
High-level project planning and assignment of responsibilities
Project Coordinator: Erin Hansen
Stakeholder correspondence and record-keeping during meetings
Report Manager: Carlos Pimentel
Tracking and coordinating report deliverables
Record Keeper: Juan Reyes
Management of Github repo and Docker environment

### ARCHITECTURE
Our data pipeline was divided into different modules to accomplish discrete tasks. In our final product, we used Python and Docker throughout as our common language and platform. The purpose of our first module (Form Data Processor) was to gather and fetch information from the AWS repository using the IRSX tool for each of the organizations in a giant manifest. We had an additional experimental module (Website Data Processor) which additionally scraped the HTML text of the organization’s website listed on the form 990. The XML payload was parsed and stored as a document in a MongoDB instance. We then had a clustering module (Cluster Processor) which read data samples from the MongoDB instance to create three labels or cluster IDs for each organization: one for each axis of comparison. These labels were loaded back into the MongoDb document for persistence. Finally our last module (App Web Server) reads from the database to create visualizations for high level queries, or a given input organization


### DOI
Identifier: doi:10.6075/J079431XIdentifier
https://doi.org/10.6075/J079431X

Creators:
* Tai, Howard;
* Hansen, Erin;
* Nagda, Jeet;
* Pimentel, Carlos;
* Reyes, Juan

```
Title:	Classy Data Analysis: Mapping the U.S. Non-Profit Space
Publisher:	UC San Diego Library Digital Collections
Publication year:	2019
Resource type:	Dataset/Dataset
```
