from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep
from openai import OpenAI
from langchain_ollama import ChatOllama

OPENAI_API_KEY=''

client = OpenAI(api_key=OPENAI_API_KEY)

llm = ChatOllama(url="http://localhost:11434",
                 temperature=0.1,
                 model="llama3.1:8b")




def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=C:\\Users\\nouri\\AppData\\Local\\Google\\Chrome\\User Data")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver
 

def is_hiring(post_text):
    print(post_text[0:100])
    prompt = f"""
    Here are the three criterias for determining if the post is relevant to me.
    1.Is the Linkedin post related to hiring a junior software engineer, full-stack engineer, AI related , robotics engineer or similar role?
    2.The role should require less than 2 years of experience.
    3.Is the post related to a startup or YC company raising money and thus potentially hiring engineers?
    if any of the above criterias are True, respond with Yes.
    If all the statements are False, respond with No.
    Respond only with the word Yes or No. No explanation is needed
    Post: : {post_text}"""
    
    # response = client.chat.completions.create(
    #     model="gpt-4",
    #     messages=[{"role": "system", "content": prompt}],
    # )
    response = llm.invoke(prompt)
    print(response.content)
    return "yes" in response.content.strip().lower()
    
    #return "yes" in response.choices[0].message.content.lower().strip()

def is_good_content(post_text):
    print(post_text[0:100])
    prompt = f"""
    Does this linkedin post contain useful information about Large language models, Robotics, or web applications that will enhance my knowledge and skillsets.
    Is the post about a new research project by Meta or NVIDIA ?
    If any of the criteria is true, say Yes. Otherwise, say No.
    Respond only with the word Yes or No. No explanation is needed
    Post: : {post_text}"""
    
    # response = client.chat.completions.create(
    #     model="gpt-4",
    #     messages=[{"role": "system", "content": prompt}],
    # )
    response = llm.invoke(prompt)
    print(response.content)
    return "yes" in response.content.strip().lower()
    
    #return "yes" in response.choices[0].message.content.lower().strip()
def is_helpful(post_text):
    prompt = f"""
    Does this linkedin post contain useful information about resume, interview or other things that will increase my chance of getting a job?
    Does this post contain any tips for resume, jobhunt, interviews or side projects?
    if any of these statements are True, respond with Yes.
    If all the statements are False, respond with No.
    Respond only with the word Yes or No. No explanation is needed
    Post: : {post_text}"""

    response = llm.invoke(prompt)
    print(response.content)
    return "yes" in response.content.strip().lower()
    
def process_linkedin_feed(driver, linkedin_feed):
    driver.get(linkedin_feed)
    sleep(5)
    
    action = ActionChains(driver)
    processed_posts = set()
    
    count = 0
    
    while count <100:
        posts = driver.find_elements(By.XPATH, "//div[contains(@data-urn, 'urn:li:activity')]")
        for post in posts:
            try:
                post_id = post.get_attribute("data-urn")
                if not post_id or post_id in processed_posts:
                    continue
                try:
                    content_span = post.find_element(By.XPATH, ".//span[contains(@class, 'break-words') and contains(@class, 'tvm-parent-container')]")
                    post_text = content_span.text.strip()
                except Exception as e:
                    post_text = ""
                if not post_text:
                    continue
                processed_posts.add(post_id)
                
                if is_hiring(post_text) or is_good_content(post_text) or is_helpful(post_text):
                    print("relevant **************")
                    count += 1
                    sleep(2)
                    try:
                        ember_id = post.get_attribute("id")
                        post_element = driver.find_element(By.ID, ember_id)  # Replace with the appropriate selector
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post_element)
                        sleep(2)
                        dropdown_button = post.find_element(By.XPATH, ".//button[contains(@class, 'feed-shared-control-menu__trigger')]")
                        driver.execute_script("arguments[0].click();", dropdown_button)
                        sleep(2)
                        save_button = post.find_element(By.XPATH, ".//li[contains(@class, 'feed-shared-control-menu__item') and contains(@class, 'option-save')]")
                        save_button.click()
                        sleep(2)
                        
                    except Exception as e:
                        print(f"Error saving post: {e}")
            except Exception as e:
                print(f"Error processing post: {e}")        
        action.send_keys(Keys.PAGE_DOWN).perform()
        sleep(2)
        action.send_keys(Keys.PAGE_DOWN).perform()
        count+=1
    return

if __name__ == "__main__":
    linkedin_feed = "https://www.linkedin.com/feed/"
    driver = setup_driver()
    
    try:
        process_linkedin_feed(driver, linkedin_feed)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
