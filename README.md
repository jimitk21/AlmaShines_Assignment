# Code Quest: Knowledge Base Application

Welcome to the **Knowledge Base Application** — a web app designed to help users search and explore relevant information from Reddit and Stack Overflow. This app aims to streamline the process of finding technical answers from both platforms in one centralized hub.

## Features

### 1. Search Functionality
   - The application allows users to search for topics across **Reddit** and **Stack Overflow** using a single query.
   - Search results are displayed in real-time, offering direct access to relevant discussions and solutions from both platforms.

### 2. Result Display
   - The results from Reddit and Stack Overflow are displayed side-by-side for easy comparison and reference.
   - Results are fetched dynamically, showing titles, links, brief summaries.

### 3. Filtering and Sorting
   - Users can filter and sort results based on parameters such as relevance , date and score.

### 4. Email Generation
   - Users can generate an email containing links to selected results and send them directly to their inbox.

### 5. Data Caching
   - The app implements data caching to reduce unnecessary API calls, improving performance and load times when revisiting similar queries this is done using mongoDB.

### 6. Translation
   - The app integrates **Google Translate**, allowing users to translate search results into different languages.


## Live Application

The application is hosted live on AWS:

**[Knowledge Base App (Live)](http://13.49.74.158:5000/)**




## Setup and Installation

1) To run the application locally and ensure full functionality, including Reddit search:

```bash
   git clone https://github.com/jimitk21/AlmaShines_Assignment.git
   cd AlmaShines_Assignment
```

2) Install the required dependencies:
```bash
   pip install -r requirements.txt
```


3) Setup Environment Variables


4) Run the Application:
```bash
   python app.py
```

