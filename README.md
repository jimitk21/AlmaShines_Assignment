# Code Quest: Knowledge Base Application

Welcome to the **Knowledge Base Application** — a web app designed to help users search and explore relevant information from Reddit and Stack Overflow. This app aims to streamline the process of finding technical answers from both platforms in one centralized hub.

## Features

### 1. Search Functionality
   - The application allows users to search for topics across **Reddit** and **Stack Overflow** using a single query.
   - Search results are displayed in real-time, offering direct access to relevant discussions and solutions from both platforms.

### 2. Result Display
   - The results from Reddit and Stack Overflow are displayed side-by-side for easy comparison and reference.
   - Results are fetched dynamically, showing titles, links, brief summaries, and relevant metadata like upvotes and comments (for Reddit).

### 3. Filtering and Sorting
   - Users can filter and sort results based on parameters such as recency, relevance, and popularity.
   - Tailored filters for both Reddit (e.g., subreddit-based filtering) and Stack Overflow (e.g., filtering by tag or votes) ensure users can quickly find the most useful answers.

### 4. Email Generation
   - Users can generate an email containing links to selected results and send them directly to their inbox or others via the integrated email feature.

### 5. Data Caching
   - The app implements data caching to reduce unnecessary API calls, improving performance and load times when revisiting similar queries.
   - Cached data is refreshed at intervals to ensure up-to-date information is always available.

### 6. Translation
   - The app integrates **Google Translate**, allowing users to translate search results into different languages.
   - This feature ensures that users from various linguistic backgrounds can benefit from the platform.

## Current Limitations

### Reddit API on AWS
- **Note**: The Reddit API is currently **blocked** on AWS IP addresses, which affects the live version hosted on AWS.
- However, the **Reddit search** functionality works seamlessly on local deployments, where the Reddit API is not restricted.
- We are exploring solutions, such as proxying requests or switching hosting services, to restore Reddit functionality on AWS.

## Live Application

The application is hosted live on AWS:

**[Knowledge Base App (Live)](http://13.49.74.158:5000/)**

Due to the request bloackge issue, Reddit search is not working in the live version but will function properly locally.
