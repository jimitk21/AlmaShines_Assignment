from flask import Flask, jsonify, request, send_from_directory, render_template_string
from flask_cors import CORS
from reddit_searcher import RedditSearcher
from stackoverflow_searcher import StackOverflowSearcher
from mongo_cache import MongoCache
import os
from concurrent.futures import ThreadPoolExecutor
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import dotenv 
dotenv.load_dotenv()


app = Flask(__name__)
CORS(app)

# Initialize components
reddit_searcher = RedditSearcher()
stackoverflow_searcher = StackOverflowSearcher()
cache = MongoCache()
executor = ThreadPoolExecutor(max_workers=2)

@app.route('/')
def index():
    with open('templates/index.html', 'r') as file:
        return render_template_string(file.read())


@app.route('/api/reddit/search', methods=['GET'])
def reddit_search():
    try:
        query = request.args.get('q', '')
        sort = request.args.get('sort', 'relevance')
        time_filter = request.args.get('time', 'month')
        limit = int(request.args.get('limit', 25))

        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400

        cache_params = {
            'platform': 'reddit',
            'query': query,
            'sort': sort,
            'time_filter': time_filter,
            'limit': limit
        }
        
        cached_results = cache.get_cached_results(**cache_params)
        if cached_results:
            return jsonify(cached_results)

        results = reddit_searcher.search(
            query=query,
            sort=sort,
            time_filter=time_filter,
            limit=limit
        )

        cache.cache_results(results, **cache_params)
        return jsonify(results)

    except Exception as e:
        return jsonify({'error': f'Reddit API Error: {str(e)}'}), 500

@app.route('/api/stackoverflow/search', methods=['GET'])
def stackoverflow_search():
    try:
        query = request.args.get('q', '')
        sort = request.args.get('sort', 'relevance')
        page = int(request.args.get('page', 1))
        pagesize = int(request.args.get('pagesize', 25))
        tags = request.args.get('tags', '').split(',') if request.args.get('tags') else None

        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400

        cache_params = {
            'platform': 'stackoverflow',
            'query': query,
            'sort': sort,
            'page': page,
            'pagesize': pagesize,
            'tags': tags
        }
        
        cached_results = cache.get_cached_results(**cache_params)
        if cached_results:
            return jsonify(cached_results)

        results = stackoverflow_searcher.search(
            query=query,
            sort=sort,
            page=page,
            pagesize=pagesize,
            tags=tags
        )

        cache.cache_results(results, **cache_params)
        return jsonify(results)

    except Exception as e:
        return jsonify({'error': f'Stack Overflow API Error: {str(e)}'}), 500

@app.route('/api/search', methods=['GET'])
def combined_search():
    try:
        query = request.args.get('q', '')
        sort = request.args.get('sort', 'relevance')
        time_filter = request.args.get('time', 'month')
        limit = int(request.args.get('limit', 25))

        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400

        cache_params = {
            'platform': 'combined',
            'query': query,
            'sort': sort,
            'time_filter': time_filter,
            'limit': limit
        }
        
        cached_results = cache.get_cached_results(**cache_params)
        if cached_results:
            return jsonify(cached_results)

        def reddit_search_task():
            try:
                return reddit_searcher.search(
                    query=query,
                    sort=sort,
                    time_filter=time_filter,
                    limit=limit
                )
            except Exception as e:
                return {'error': f'Reddit API Error: {str(e)}', 'results': []}

        def stackoverflow_search_task():
            try:
                return stackoverflow_searcher.search(
                    query=query,
                    sort=sort,
                    page=1,
                    pagesize=limit
                )
            except Exception as e:
                return {'error': f'Stack Overflow API Error: {str(e)}', 'results': []}

        reddit_future = executor.submit(reddit_search_task)
        stackoverflow_future = executor.submit(stackoverflow_search_task)

        reddit_results = reddit_future.result()
        stackoverflow_results = stackoverflow_future.result()

        combined_results = {
            'query': query,
            'reddit': reddit_results,
            'stackoverflow': stackoverflow_results,
            'errors': []
        }

        if 'error' in reddit_results:
            combined_results['errors'].append(reddit_results['error'])
        if 'error' in stackoverflow_results:
            combined_results['errors'].append(stackoverflow_results['error'])


        cache.cache_results(combined_results, **cache_params)
        return jsonify(combined_results)

    except Exception as e:
        return jsonify({'error': f'Search Error: {str(e)}'}), 500


@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    try:
        cache.clear_cache()
        return jsonify({'message': 'Cache cleared successfully'})
    except Exception as e:
        return jsonify({'error': f'Cache clear error: {str(e)}'}), 500


def create_email_html(results):
    """Create HTML email content from search results"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #2563eb; margin-bottom: 10px; }
            .result-card { border: 1px solid #e5e7eb; padding: 15px; margin-bottom: 15px; border-radius: 8px; }
            .source-badge { display: inline-block; padding: 3px 8px; border-radius: 12px; font-size: 12px; margin-bottom: 8px; }
            .reddit { background-color: #ff4500; color: white; }
            .stackoverflow { background-color: #0077cc; color: white; }
            .title { font-size: 18px; color: #1f2937; margin-bottom: 8px; }
            .metadata { font-size: 12px; color: #6b7280; margin-bottom: 8px; }
            .stats { font-size: 12px; color: #374151; }
            .tags { margin-top: 8px; }
            .tag { background-color: #dbeafe; color: #1e40af; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-right: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Tech Search Results</h1>
                <p>Here are your requested search results from Tech Search Hub</p>
            </div>
    """
    
    for result in results:
        html += f"""
            <div class="result-card">
                <span class="source-badge {'reddit' if result['source'] == 'reddit' else 'stackoverflow'}">
                    {result['source'].title()}
                </span>
                <div class="title">{result['title']}</div>
                <div class="metadata">
                    {'Posted by ' + result['author'] if 'author' in result else 'Asked by ' + result['owner']['name']} • 
                    {result['created_at']}
                </div>
        """
        
        if result['source'] == 'reddit':
            html += f"""
                <div class="stats">
                    🔼 {result['score']} • 
                    💬 {result['num_comments']} comments • 
                    {round(result['upvote_ratio'] * 100)}% upvoted
                </div>
            """
        else:
            html += f"""
                <div class="stats">
                    🔼 {result['score']} • 
                    💬 {result['answer_count']} answers • 
                    👁️ {result['view_count']} views
                </div>
                <div class="tags">
                    {''.join([f'<span class="tag">{tag}</span>' for tag in result['tags']])}
                </div>
            """
        
        html += "</div>"
    
    html += """
        </div>
    </body>
    </html>
    """
    return html

@app.route('/api/email-results', methods=['POST'])
def email_results():
    try:
        data = request.get_json()
        recipient_email = data.get('email')
        results = data.get('results')
        query = data.get('query')
        
        if not recipient_email or not results:
            return jsonify({'error': 'Email and results are required'}), 400
            
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Tech Search Results: {query}'
        msg['From'] = os.getenv('MAIL_USERNAME')
        msg['To'] = recipient_email
        

        html_content = create_email_html(results)
        msg.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
            smtp.send_message(msg)
            
        return jsonify({'message': 'Email sent successfully'})
        
    except Exception as e:
        return jsonify({'error': f'Failed to send email: {str(e)}'}), 500


if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True)