"""
Filtering module for news articles.
Handles negative keyword exclusion, positive keyword categorization, and article selection.
"""

from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
import re
try:
    from underthesea import word_tokenize
    UNDERTHESEA_AVAILABLE = True
except ImportError:
    UNDERTHESEA_AVAILABLE = False


def preprocess_vietnamese_text(text: str) -> str:
    """
    Preprocess Vietnamese text for better keyword matching.
    
    Args:
        text: Input Vietnamese text
        
    Returns:
        Processed text with tokenization if available
    """
    if not text:
        return ""
    
    # Convert to lowercase for case-insensitive matching
    text = text.lower()
    
    # Use Vietnamese tokenization if available
    if UNDERTHESEA_AVAILABLE:
        try:
            tokens = word_tokenize(text)
            return ' '.join(tokens)
        except Exception:
            pass  # Fall back to basic processing
    
    # Basic processing without underthesea
    return text


def check_keyword_match(text: str, keywords: List[str]) -> bool:
    """
    Check if any keyword matches in Vietnamese text with enhanced processing.
    
    Args:
        text: Text to search in
        keywords: List of keywords to search for
        
    Returns:
        True if any keyword is found
    """
    if not text or not keywords:
        return False
    
    # Preprocess the text
    processed_text = preprocess_vietnamese_text(text)
    
    # Check for keyword matches
    for keyword in keywords:
        processed_keyword = preprocess_vietnamese_text(keyword)
        if processed_keyword in processed_text:
            return True
    
    return False


def exclude_negative(articles: List[Dict[str, Any]], negative_keywords: List[str]) -> List[Dict[str, Any]]:
    """
    Exclude articles containing negative keywords in title and summary only.
    Uses enhanced Vietnamese text processing.
    
    Args:
        articles: List of article dictionaries
        negative_keywords: List of negative keywords to exclude
        
    Returns:
        Filtered list of articles without negative keywords
    """
    if not negative_keywords:
        return articles
    
    filtered_articles = []
    
    for article in articles:
        title = article.get('title', '')
        summary = article.get('summary', '')
        
        # Only check title and summary to avoid over-filtering
        combined_text = f"{title} {summary}"
        
        # Use enhanced Vietnamese keyword matching
        has_negative = check_keyword_match(combined_text, negative_keywords)
        
        if not has_negative:
            filtered_articles.append(article)
    
    return filtered_articles


def categorize_positive(articles: List[Dict[str, Any]], positive_keywords: Dict[str, List[str]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Categorize articles by positive keywords using full content analysis.
    Uses enhanced Vietnamese text processing.
    
    Args:
        articles: List of article dictionaries
        positive_keywords: Dictionary mapping categories to keyword lists
        
    Returns:
        Dictionary mapping categories to lists of matching articles
    """
    categorized = {}
    
    for category, keywords in positive_keywords.items():
        categorized[category] = []
        
        for article in articles:
            title = article.get('title', '')
            summary = article.get('summary', '')
            full_content = article.get('full_content', '')
            
            # Combine text sources for comprehensive checking
            combined_text = f"{title} {summary} {full_content}"
            
            # Use enhanced Vietnamese keyword matching
            if check_keyword_match(combined_text, keywords):
                categorized[category].append(article)
    
    return categorized


def sort_and_limit(categorized_articles: Dict[str, List[Dict[str, Any]]], limit: int = 5) -> List[Dict[str, Any]]:
    """
    Sort articles by publish time and limit to top articles using round-robin selection.
    Removes duplicates based on URL.
    
    Args:
        categorized_articles: Dictionary of categorized articles
        limit: Maximum number of articles to return
        
    Returns:
        Limited and sorted list of articles without duplicates
    """
    # Remove duplicates within each category based on URL
    for category in categorized_articles:
        seen_urls = set()
        unique_articles = []
        for article in categorized_articles[category]:
            url = article.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        categorized_articles[category] = unique_articles
    
    # First, sort articles in each category by publish_time (newest first)
    for category in categorized_articles:
        categorized_articles[category].sort(
            key=lambda x: x.get('publish_time') or datetime.min.replace(tzinfo=timezone(timedelta(hours=7))), 
            reverse=True
        )
    
    # Round-robin selection to get diverse articles
    selected_articles = []
    category_indices = {category: 0 for category in categorized_articles}
    
    while len(selected_articles) < limit:
        added_in_round = False
        
        for category, articles in categorized_articles.items():
            if len(selected_articles) >= limit:
                break
                
            index = category_indices[category]
            if index < len(articles):
                selected_articles.append(articles[index])
                category_indices[category] += 1
                added_in_round = True
        
        # If no articles were added in this round, break to avoid infinite loop
        if not added_in_round:
            break
    
    # Remove final duplicates across all categories
    final_articles = []
    seen_urls = set()
    for article in selected_articles:
        url = article.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            final_articles.append(article)
    
    # Final sort by publish_time (newest first)
    final_articles.sort(key=lambda x: x.get('publish_time') or datetime.min.replace(tzinfo=timezone(timedelta(hours=7))), reverse=True)
    
    return final_articles[:limit]


def filter_and_select(articles: List[Dict[str, Any]], positive_keywords: Dict[str, List[str]], negative_keywords: List[str], limit: int = 5) -> List[Dict[str, Any]]:
    """
    Complete filtering pipeline: exclude negative, categorize positive, sort and limit.
    
    Args:
        articles: List of article dictionaries
        positive_keywords: Dictionary mapping categories to keyword lists
        negative_keywords: List of negative keywords to exclude
        limit: Maximum number of articles to return
        
    Returns:
        Final filtered and selected list of articles
    """
    # Step 1: Exclude negative keywords
    filtered = exclude_negative(articles, negative_keywords)
    
    # Step 2: Categorize by positive keywords
    categorized = categorize_positive(filtered, positive_keywords)
    
    # Step 3: Sort and limit
    selected = sort_and_limit(categorized, limit)
    
    return selected