"""
Filtering module for news articles.
Handles negative keyword exclusion, positive keyword categorization, and article selection.
"""

from typing import List, Dict, Any
import re


def exclude_negative(articles: List[Dict[str, Any]], negative_keywords: List[str]) -> List[Dict[str, Any]]:
    """
    Exclude articles containing negative keywords in title or summary.
    
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
        title = article.get('title', '').lower()
        summary = article.get('summary', '').lower()
        
        # Check if any negative keyword is present
        has_negative = False
        for keyword in negative_keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in title or keyword_lower in summary:
                has_negative = True
                break
        
        if not has_negative:
            filtered_articles.append(article)
    
    return filtered_articles


def categorize_positive(articles: List[Dict[str, Any]], positive_keywords: Dict[str, List[str]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Categorize articles by positive keywords.
    
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
            title = article.get('title', '').lower()
            summary = article.get('summary', '').lower()
            
            # Check if any keyword in this category matches
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in title or keyword_lower in summary:
                    categorized[category].append(article)
                    break  # Only add once per category
    
    return categorized


def sort_and_limit(categorized_articles: Dict[str, List[Dict[str, Any]]], limit: int = 5) -> List[Dict[str, Any]]:
    """
    Sort articles by publish time and limit to top articles using round-robin selection.
    
    Args:
        categorized_articles: Dictionary of categorized articles
        limit: Maximum number of articles to return
        
    Returns:
        Limited and sorted list of articles
    """
    # First, sort articles in each category by publish_time (newest first)
    for category in categorized_articles:
        categorized_articles[category].sort(
            key=lambda x: x.get('publish_time', 0), 
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
    
    # Final sort by publish_time (newest first)
    selected_articles.sort(key=lambda x: x.get('publish_time', 0), reverse=True)
    
    return selected_articles[:limit]


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