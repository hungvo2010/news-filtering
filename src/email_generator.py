"""
Email generation module for news filtering system.
Creates formatted HTML emails with responsive design.
"""

from typing import List, Dict, Any, Tuple
from datetime import datetime


def truncate_text(text: str, max_length: int = 150) -> str:
    """
    Truncate text to specified length with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + '...'


def format_time_vietnamese(dt: datetime) -> str:
    """
    Format datetime in Vietnamese format.
    
    Args:
        dt: Datetime object
        
    Returns:
        Formatted time string
    """
    return dt.strftime('%H:%M, %d/%m/%Y')


def generate_email_subject(current_date: datetime) -> str:
    """
    Generate email subject line.
    
    Args:
        current_date: Current date
        
    Returns:
        Email subject string
    """
    date_str = current_date.strftime('%d/%m/%Y')
    return f"📰 Bản tin tóm tắt ngày {date_str}"


def generate_email_html(articles: List[Dict[str, Any]], current_date: datetime) -> str:
    """
    Generate HTML email body.
    
    Args:
        articles: List of articles to include
        current_date: Current date
        
    Returns:
        HTML email body
    """
    date_str = current_date.strftime('%d/%m/%Y')
    
    # CSS styles for responsive design
    css_styles = """
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            line-height: 1.6; 
            color: #333; 
            max-width: 600px; 
            margin: 0 auto; 
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container { 
            background-color: white; 
            border-radius: 8px; 
            padding: 30px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
            border-bottom: 3px solid #0066cc;
            padding-bottom: 20px;
        }
        .header h1 { 
            color: #0066cc; 
            margin: 0; 
            font-size: 28px;
        }
        .date { 
            color: #666; 
            font-size: 16px; 
            margin-top: 5px;
        }
        .article { 
            margin-bottom: 25px; 
            padding: 20px; 
            border-left: 4px solid #0066cc;
            background-color: #fafafa;
            border-radius: 0 8px 8px 0;
        }
        .article h2 { 
            margin: 0 0 10px 0; 
            color: #0066cc; 
            font-size: 18px;
        }
        .article h2 a { 
            color: #0066cc; 
            text-decoration: none; 
        }
        .article h2 a:hover { 
            text-decoration: underline; 
        }
        .summary { 
            color: #555; 
            margin: 10px 0; 
            font-size: 14px;
        }
        .meta { 
            font-size: 12px; 
            color: #888; 
            border-top: 1px solid #eee;
            padding-top: 10px;
            margin-top: 10px;
        }
        .footer { 
            text-align: center; 
            margin-top: 30px; 
            padding-top: 20px; 
            border-top: 2px solid #eee;
            color: #666;
        }
        .no-articles { 
            text-align: center; 
            color: #666; 
            font-style: italic; 
            padding: 40px;
            background-color: #f9f9f9;
            border-radius: 8px;
        }
        @media only screen and (max-width: 600px) {
            body { padding: 10px; }
            .container { padding: 20px; }
            .header h1 { font-size: 24px; }
            .article { padding: 15px; }
            .article h2 { font-size: 16px; }
        }
    </style>
    """
    
    # Start HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bản tin ngày {date_str}</title>
        {css_styles}
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📰 Bản tin tóm tắt</h1>
                <div class="date">{date_str}</div>
            </div>
    """
    
    # Greeting
    html += """
            <p>Xin chào,</p>
            <p>Đây là bản tóm tắt những tin tức nổi bật trong ngày hôm nay:</p>
    """
    
    # Articles or no articles message
    if articles:
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'Không có tiêu đề')
            summary = truncate_text(article.get('summary', ''), 150)
            url = article.get('url', '#')
            source = article.get('source', 'Không rõ nguồn')
            publish_time = article.get('publish_time')
            
            time_str = format_time_vietnamese(publish_time) if publish_time else 'Không rõ thời gian'
            
            html += f"""
            <div class="article">
                <h2><a href="{url}" target="_blank">{i}. {title}</a></h2>
                <div class="summary">{summary}</div>
                <div class="meta">
                    <strong>Nguồn:</strong> {source} | <strong>Thời gian:</strong> {time_str}
                </div>
            </div>
            """
    else:
        html += """
            <div class="no-articles">
                <p><strong>Không có tin tức phù hợp hôm nay.</strong></p>
                <p>Hệ thống không tìm thấy bài viết nào phù hợp với tiêu chí lọc đã thiết lập.</p>
            </div>
        """
    
    # Footer
    html += """
            <div class="footer">
                <p>Cảm ơn bạn đã theo dõi!</p>
                <p><em>Chúc bạn có một ngày tốt lành! 🌟</em></p>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="font-size: 11px; color: #999;">
                    Email này được tạo tự động bởi hệ thống lọc tin tức.<br>
                    Nếu bạn không muốn nhận email này nữa, vui lòng liên hệ quản trị viên.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


def generate_email_body(articles: List[Dict[str, Any]], current_date: datetime) -> Tuple[str, str]:
    """
    Generate complete email subject and body.
    
    Args:
        articles: List of articles to include
        current_date: Current date
        
    Returns:
        Tuple of (subject, html_body)
    """
    subject = generate_email_subject(current_date)
    html_body = generate_email_html(articles, current_date)
    
    return subject, html_body