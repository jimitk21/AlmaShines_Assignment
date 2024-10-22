import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
import urllib.parse
from bs4 import BeautifulSoup
import html

class StackOverflowSearcher:
    def __init__(self):
       
        load_dotenv()
        self.api_key = os.getenv('STACKOVERFLOW_API_KEY')
        self.base_url = "https://api.stackexchange.com/2.3"
        self.headers = {
            'User-Agent': 'Python/StackOverflowSearch 1.0'
        }

    def get_top_answer(self, question_id: int) -> Optional[Dict]:
        
        answers_url = f"{self.base_url}/questions/{question_id}/answers"
        
        params = {
            'site': 'stackoverflow',
            'order': 'desc',
            'sort': 'votes',
            'filter': 'withbody', 
            'pagesize': 1,  
            'key': self.api_key
        }
        
        try:
            response = requests.get(
                answers_url,
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            if data['items']:
                answer = data['items'][0]
                return {
                    'score': answer['score'],
                    'is_accepted': answer.get('is_accepted', False),
                    'body': answer['body'],
                    'link': f"https://stackoverflow.com/a/{answer['answer_id']}"
                }
            return None
            
        except Exception as e:
            print(f"Error fetching answer: {str(e)}")
            return None

    def _clean_html(self, html_content: str) -> str:
        
        soup = BeautifulSoup(html_content, 'html.parser')
       
        code_blocks = []
        for code in soup.find_all('code'):
            code_blocks.append(f"Code: {code.get_text()}")
            code.decompose()
    
        text = soup.get_text(separator=' ').strip()
    
        text = ' '.join(text.split())
      
        if code_blocks:
            text += '\n\nCode Examples:\n' + '\n'.join(code_blocks[:2]) 
        
        return text

    def search(self,
               query: str,
               tags: Optional[List[str]] = None,
               sort: str = "relevance",
               order: str = "desc",
               page: int = 1,
               pagesize: int = 30) -> Dict:
       
        search_url = f"{self.base_url}/search"
        

        cleaned_query = self._clean_query(query)
        
   
        params = {
            'site': 'stackoverflow',
            'q': cleaned_query,  
            'sort': sort,
            'order': order,
            'page': page,
            'pagesize': min(pagesize, 100),
            'key': self.api_key,
            'filter': 'withbody'  
        }

        if tags:
            params['tagged'] = ';'.join(tags)

        else:
            params['tagged'] = ';'.join(cleaned_query.split(' '))

        try:
            response = requests.get(
                search_url,
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 429:
                return {
                    'error': 'API quota exceeded. Please try again later.',
                    'query': query,
                    'results': []
                }

            response.raise_for_status()
            data = response.json()
            
            processed_results = self._process_results(data['items'])
            
            return {
                'query': query,
                'tags': tags,
                'total_results': len(processed_results),
                'has_more': data.get('has_more', False),
                'quota_remaining': data.get('quota_remaining'),
                'results': processed_results
            }

        except requests.exceptions.RequestException as e:
            error_msg = f"Error making request: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    if 'error_message' in error_details:
                        error_msg += f"\nAPI Error: {error_details['error_message']}"
                except:
                    pass
            print(error_msg)
            return {
                'error': error_msg,
                'query': query,
                'results': []
            }
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(error_msg)
            return {
                'error': error_msg,
                'query': query,
                'results': []
            }

    def _clean_query(self, query: str) -> str:
        
        cleaned = query.replace('"', ' ').replace("'", ' ')
  
        common_replacements = {
            'module not found:': 'modulenotfounderror',
            'no module named': 'modulenotfounderror',
            'cannot import': 'import error',
        }
        
        for old, new in common_replacements.items():
            cleaned = cleaned.lower().replace(old.lower(), new)
            
        return cleaned.strip()

    def _process_results(self, questions: List[Dict]) -> List[Dict]:
      
        processed_questions = []
        
        for question in questions:
            created_date = datetime.fromtimestamp(question['creation_date'])
            last_activity_date = datetime.fromtimestamp(question['last_activity_date'])
            
         
            top_answer = self.get_top_answer(question['question_id'])
            
            processed_question = {
                'id': question['question_id'],
                'title': question['title'],
                'link': question['link'],
                'score': question['score'],
                'answer_count': question['answer_count'],
                'is_answered': question['is_answered'],
                'view_count': question['view_count'],
                'tags': question['tags'],
                'created_at': created_date.isoformat(),
                'last_activity': last_activity_date.isoformat(),
                'owner': {
                    'name': question.get('owner', {}).get('display_name', 'Anonymous'),
                    'reputation': question.get('owner', {}).get('reputation', 0),
                    'link': question.get('owner', {}).get('link', '')
                },
                'top_answer': top_answer
            }
            
            processed_questions.append(processed_question)
        
        return processed_questions

def main():

    searcher = StackOverflowSearcher()
    
    while True:
        print("\nStack Overflow Search")
        print("=" * 50)
        query = input("Enter search query (or 'quit' to exit): ")
        
        if query.lower() == 'quit':
            break
            
        tags_input = input("Enter tags (comma-separated, optional, press Enter to skip): ").strip()
        tags = [tag.strip() for tag in tags_input.split(',')] if tags_input else None
      
        results = searcher.search(
            query=query,
            tags=tags,
            pagesize=10  
        )
        
        
        if 'error' in results:
            print(f"\nError: {results['error']}")
        else:
            print(f"\nFound {results['total_results']} results for '{results['query']}'")
            if results.get('quota_remaining') is not None:
                print(f"API quota remaining: {results['quota_remaining']}")
            
            if results['total_results'] == 0:
                print("\nNo results found. Try these search tips:")
                print("1. Use simpler terms (e.g., 'streamlit install' instead of 'module not found: streamlit')")
                print("2. Check for typos in your search terms")
                print("3. Try searching with fewer tags")
                print("4. Use common error keywords (e.g., 'import error', 'modulenotfounderror')")
            else:
                print("\nTop results:")
                for idx, question in enumerate(results['results'], 1):
                    print(f"\n{idx}. {question['title']}")
                    print(f"   Score: {question['score']} | Answers: {question['answer_count']} "
                          f"| Views: {question['view_count']}")
                    print(f"   Tags: {', '.join(question['tags'])}")
                    print(f"   Asked by: {question['owner']['name']} "
                          f"(reputation: {question['owner']['reputation']})")
                    print(f"   Link: {question['link']}")
                    
                   
                    if question.get('top_answer'):
                        answer = question['top_answer']
                        print(f"\n   Top Answer (Score: {answer['score']}, "
                              f"Accepted: {'Yes' if answer['is_accepted'] else 'No'}):")
                        
                        
                        clean_text = searcher._clean_html(answer['body'])
                      
                        print(f"   {clean_text[:300]}...")
                        print(f"   Answer link: {answer['link']}")
                    else:
                        print("\n   No answers yet.")
                    
                    print("\n   " + "-" * 40)

if __name__ == "__main__":
    main()
