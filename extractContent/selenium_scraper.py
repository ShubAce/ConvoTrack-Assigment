import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

def setup_driver():
    """
    Set up Chrome driver with appropriate options
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        print("Make sure you have Chrome installed and chromedriver in your PATH")
        return None

def get_website_text_selenium(url, driver):
    """
    Fetches a webpage using Selenium and extracts the main content
    """
    try:
        driver.get(url)
        
        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Additional wait for dynamic content
        time.sleep(3)
        
        # Try to find main content areas
        content_selectors = [
            "main",
            "article", 
            ".content",
            ".main-content",
            ".post-content",
            ".entry-content",
            ".case-study",
            ".page-content",
            "#content",
            "#main"
        ]
        
        main_content = None
        for selector in content_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    main_content = elements[0]
                    break
            except:
                continue
        
        # If no main content found, try to get content from body but exclude nav/header/footer
        if not main_content:
            try:
                # Remove navigation, header, footer elements from consideration
                driver.execute_script("""
                    var elements = document.querySelectorAll('nav, header, footer, .nav, .header, .footer');
                    for (var i = 0; i < elements.length; i++) {
                        elements[i].style.display = 'none';
                    }
                """)
                main_content = driver.find_element(By.TAG_NAME, "body")
            except:
                pass
        
        if main_content:
            text_content = main_content.text
            
            # Clean up the text
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            # Remove common navigation items
            filtered_lines = []
            nav_items = ['consumer insights', 'influencers', 'case studies', 'contact us', 'copyright', 'privacy policy', 'terms of service', 'cookie policy']
            
            for line in lines:
                if not any(nav_item in line.lower() for nav_item in nav_items):
                    filtered_lines.append(line)
            
            cleaned_content = '\n'.join(filtered_lines)
            return cleaned_content if cleaned_content else "No meaningful content found on the page."
        else:
            return "Could not find the main content of the page."
            
    except TimeoutException:
        return f"Timeout while loading {url}"
    except WebDriverException as e:
        return f"WebDriver error for {url}: {e}"
    except Exception as e:
        return f"An error occurred while processing {url}: {e}"

# --- Main part of the script ---
if __name__ == "__main__":
    # URLs to scrape
    urls_to_scrape = [
        'https://convotrack.ai/case-studies/emotional-storytelling-engagement-strategy/',
        'https://convotrack.ai/case-studies/ice-cream-category-analysis/',
        'https://convotrack.ai/case-studies/drama-series-content-strategy/',
        'https://convotrack.ai/case-studies/beauty-brand-influencer-landscape-analysis/',
        'https://convotrack.ai/case-studies/protein-consumption-strategy-analysis/',
        'https://convotrack.ai/case-studies/female-celebrity-brand-partnership-strategy/',
        'https://convotrack.ai/case-studies/rtd-tea-market-entry-strategy/',
        'https://convotrack.ai/case-studies/topical-pain-relief-innovation-strategy/',
        'https://convotrack.ai/case-studies/tribal-primitive-trends-analysis/',
        'https://convotrack.ai/case-studies/consumer-meal-innovation-strategy/',
        'https://convotrack.ai/case-studies/infant-nutrition-content-activation-strategy/',
        'https://convotrack.ai/case-studies/cross-category-innovation-strategy/',
        'https://convotrack.ai/case-studies/sugar-free-products-category-analysis/',
        'https://convotrack.ai/case-studies/oral-care-market-entry-strategy/',
        'https://convotrack.ai/case-studies/deodorant-category-trend-analysis/',
        'https://convotrack.ai/case-studies/digital-science-storytelling-evolution-analysis/',
        'https://convotrack.ai/case-studies/longevity-insights-and-trend-analysis/',
        'https://convotrack.ai/case-studies/modern-male-grooming-market-analysis/',
        'https://convotrack.ai/case-studies/dental-care-engagement-trends-and-insights/',
        'https://convotrack.ai/case-studies/optimizing-digital-strategy-for-hair-removal-brands/',
        'https://convotrack.ai/case-studies/sexual-wellness-market-strategy/',
        'https://convotrack.ai/case-studies/modern-parenting-dynamics-explorer/',
        'https://convotrack.ai/case-studies/global-skincare-trends/',
        'https://convotrack.ai/case-studies/diabetes-care-engagement-strategy/',
        'https://convotrack.ai/case-studies/social-crisis-response-tracking/',
        'https://convotrack.ai/case-studies/global-skincare-trend-mapping/',
        'https://convotrack.ai/case-studies/korean-skincare-market-intelligence/',
        'https://convotrack.ai/case-studies/indonesian-parenting-insights-explorer/',
        'https://convotrack.ai/case-studies/product-innovation-intelligence-system/',
        'https://convotrack.ai/case-studies/beverage-cultural-moments-explorer/',
        'https://convotrack.ai/case-studies/influencer-content-quality-control/'
    ]

    # Set up the driver
    driver = setup_driver()
    if not driver:
        print("Failed to set up driver. Exiting.")
        exit(1)

    # Create output folder
    output_folder = "scraped_articles_selenium"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    successful_scrapes = 0
    failed_scrapes = 0
    
    try:
        for i, url in enumerate(urls_to_scrape):
            print(f"Scraping {i+1}/{len(urls_to_scrape)}: {url}")
            
            content = get_website_text_selenium(url, driver)
            
            file_name = f"article_{i+1}.txt"
            file_path = os.path.join(output_folder, file_name)
            
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(f"Source URL: {url}\n")
                    file.write("="*50 + "\n\n")
                    file.write(content)
                
                content_length = len(content)
                print(f"✅ Success! Content saved to '{file_path}' ({content_length} characters)")
                
                # Show first 100 characters as preview
                preview = content[:100].replace('\n', ' ')
                print(f"   Preview: {preview}...")
                print()
                successful_scrapes += 1
                
            except Exception as e:
                print(f"❌ Error saving file for {url}: {e}\n")
                failed_scrapes += 1
                
    finally:
        driver.quit()

    print(f"--- Scraping complete ---")
    print(f"Successful: {successful_scrapes}")
    print(f"Failed: {failed_scrapes}")
    print(f"Total: {len(urls_to_scrape)}")
