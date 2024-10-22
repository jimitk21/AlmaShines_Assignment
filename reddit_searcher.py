import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import os
# from dotenv import load_dotenv

class RedditSearcher:
    def __init__(self):
        """Initialize the Reddit searcher with base URL and headers"""
        self.base_url = "https://www.reddit.com"
        self.headers = {
            'User-Agent': 'Python/RequestsScript 1.0'
        }

    def search(self, 
               query: str, 
               subreddit: Optional[str] = None,
               sort: str = "relevance",
               time_filter: str = "all",
               limit: int = 25) -> Dict:
        """
        Search Reddit for posts matching the query.
        
        Args:
            query (str): Search query
            subreddit (str, optional): Specific subreddit to search in
            sort (str): Sort method ('relevance', 'hot', 'top', 'new', 'comments')
            time_filter (str): Time range ('hour', 'day', 'week', 'month', 'year', 'all')
            limit (int): Maximum number of results to return (max 100)
        
        Returns:
            Dict: Processed search results
        """
        # Build the search URL
        if subreddit:
            search_url = f"{self.base_url}/r/{subreddit}/search.json"
        else:
            search_url = f"{self.base_url}/search.json"

        # Set up the search parameters
        params = {
            'q': query,
            'sort': sort,
            't': time_filter,
            'limit': min(limit, 100),  # Reddit's max limit is 100
            'restrict_sr': bool(subreddit),  # Restrict to subreddit if specified
            'type': 'link'  # Search for posts
        }

        try:
            # Make the request
            response = requests.get(
                search_url,
                headers=self.headers,
                params=params
            )
            response.raise_for_status()  # Raise exception for bad status codes

            # Parse the response
            data = response.json()
            
            # Process and format the results
            processed_results = self._process_results(data['data']['children'])
            
            return {
                'query': query,
                'subreddit': subreddit,
                'total_results': len(processed_results),
                'results': processed_results
            }

        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            return {
                'error': str(e),
                'query': query,
                'results': []
            }
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return {
                'error': 'Invalid JSON response',
                'query': query,
                'results': []
            }

    def _process_results(self, posts: List[Dict]) -> List[Dict]:
        """
        Process and format the search results.
        
        Args:
            posts (List[Dict]): Raw post data from Reddit
        
        Returns:
            List[Dict]: Processed and formatted posts
        """
        processed_posts = []
        
        for post in posts:
            post_data = post['data']
            
            # Convert timestamp to datetime
            created_utc = datetime.fromtimestamp(post_data['created_utc'])
            
            processed_post = {
                'id': post_data['id'],
                'title': post_data['title'],
                'subreddit': post_data['subreddit'],
                'author': post_data['author'],
                'created_at': created_utc.isoformat(),
                'score': post_data['score'],
                'upvote_ratio': post_data['upvote_ratio'],
                'num_comments': post_data['num_comments'],
                'url': f"https://reddit.com{post_data['permalink']}",
                'is_self': post_data['is_self'],
                'selftext': post_data.get('selftext', ''),
                'link_flair_text': post_data.get('link_flair_text'),
                'domain': post_data['domain']
            }
            
            # Add thumbnail if it exists and is not a default value
            if 'thumbnail' in post_data and post_data['thumbnail'] not in ['self', 'default', 'nsfw']:
                processed_post['thumbnail'] = post_data['thumbnail']
            
            processed_posts.append(processed_post)
        
        return processed_posts

def main():
    """Example usage of the RedditSearcher class"""
    searcher = RedditSearcher()
    
    # Example search
    query = input("Enter search query: ")
    subreddit = input("Enter subreddit (optional, press Enter to skip): ").strip()
    
    # Perform the search
    results = searcher.search(
        query=query,
        subreddit=subreddit if subreddit else None,
        sort='relevance',
        time_filter='month',
        limit=10
    )
    
    # Print results
    if 'error' in results:
        print(f"Error: {results['error']}")
    else:
        print(f"\nFound {results['total_results']} results for '{results['query']}'")
        print("\nTop results:")
        for idx, post in enumerate(results['results'], 1):
            print(f"\n{idx}. {post['title']}")
            print(f"   Subreddit: r/{post['subreddit']}")
            print(f"   Score: {post['score']} | Comments: {post['num_comments']}")
            print(f"   URL: {post['url']}")
            if post['is_self'] and post['selftext']:
                preview = post['selftext'][:150] + '...' if len(post['selftext']) > 150 else post['selftext']
                print(f"   Preview: {preview}")
            print(f"   Posted by: u/{post['author']} on {post['created_at']}")

if __name__ == "__main__":
    main()
