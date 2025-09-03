"""
Email preview generator - shows what the email would look like
"""
import sys
import os
from datetime import datetime, timezone, timedelta

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from email_generator import generate_email_body

# Sample filtered news articles (simulated)
sample_articles = [
    {
        'title': 'Việt Nam đẩy mạnh phát triển trí tuệ nhân tạo trong giáo dục',
        'summary': 'Bộ Giáo dục và Đào tạo đang triển khai nhiều chương trình ứng dụng AI vào giảng dạy, giúp nâng cao chất lượng học tập...',
        'url': 'https://vnexpress.net/viet-nam-day-manh-phat-trien-tri-tue-nhan-tao-trong-giao-duc-4789123.html',
        'publish_time': datetime(2024, 9, 3, 8, 30, tzinfo=timezone(timedelta(hours=7))),
        'source': 'vnexpress.net'
    },
    {
        'title': 'GDP Việt Nam tăng trưởng 6,82% trong 9 tháng đầu năm',
        'summary': 'Theo số liệu của Tổng cục Thống kê, GDP 9 tháng đầu năm 2024 tăng 6,82% so với cùng kỳ năm trước, cao hơn mục tiêu...',
        'url': 'https://tuoitre.vn/gdp-viet-nam-tang-truong-6-82-trong-9-thang-dau-nam-20240903151234567.htm',
        'publish_time': datetime(2024, 9, 3, 10, 15, tzinfo=timezone(timedelta(hours=7))),
        'source': 'tuoitre.vn'
    },
    {
        'title': 'Đội tuyển Việt Nam chuẩn bị cho vòng loại World Cup 2026',
        'summary': 'HLV Troussier đã công bố danh sách 25 cầu thủ cho trận đấu sắp tới trong khuôn khổ vòng loại World Cup 2026...',
        'url': 'https://laodong.vn/doi-tuyen-viet-nam-chuan-bi-cho-vong-loai-world-cup-2026-987654321.html',
        'publish_time': datetime(2024, 9, 3, 14, 20, tzinfo=timezone(timedelta(hours=7))),
        'source': 'laodong.vn'
    }
]

def main():
    print("🔍 Generating Email Preview for hungvochanhdp1@gmail.com")
    print("=" * 60)
    
    # Get current date in Vietnam timezone
    current_date = datetime.now(timezone(timedelta(hours=7)))
    print(f"Date: {current_date.strftime('%d/%m/%Y %H:%M')} (Vietnam Time)")
    
    # Generate email content
    subject, html_body = generate_email_body(sample_articles, current_date)
    
    print(f"\n📧 Email Subject:")
    print(f"   {subject}")
    
    print(f"\n📊 Email Stats:")
    print(f"   - Recipient: hungvochanhdp1@gmail.com")
    print(f"   - Articles: {len(sample_articles)}")
    print(f"   - Content length: {len(html_body):,} characters")
    print(f"   - Format: Responsive HTML")
    
    print(f"\n📰 Articles to be sent:")
    for i, article in enumerate(sample_articles, 1):
        print(f"   {i}. {article['title'][:60]}...")
        print(f"      Source: {article['source']} | Time: {article['publish_time'].strftime('%H:%M')}")
        print(f"      Summary: {article['summary'][:80]}...")
        print()
    
    # Save HTML preview
    with open('/root/news-filter/email_preview.html', 'w', encoding='utf-8') as f:
        f.write(html_body)
    
    print("✅ Email preview saved as: email_preview.html")
    print("\n🔧 To actually send this email, you need to:")
    print("   1. Update config/.env with your Gmail credentials:")
    print("      SMTP_USERNAME=your-gmail@gmail.com")
    print("      SMTP_PASSWORD=your-app-password")
    print("   2. Run: python3 main.py --mode=run-once")
    print("\n💡 Note: Use Gmail App Password, not regular password")
    print("   Create at: https://myaccount.google.com/apppasswords")

if __name__ == "__main__":
    main()