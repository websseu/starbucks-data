from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup
import time
import re
import os
import json
from datetime import datetime

# 현재 날짜
current_date = datetime.now().strftime("%Y-%m-%d")

# 한글 지역명과 영문 지역명 매핑
location_name_mapping = {
    "서울": "seoul",
    "경기": "gyeonggi",
    "광주": "gwangju",
    "대구": "daegu",
    "대전": "daejeon",
    "부산": "busan",
    "울산": "ulsan",
    "인천": "incheon",
    "강원": "gangwon",
    "경남": "gyeongnam",
    "경북": "gyeongbuk",
    "전남": "jeolnam",
    "전북": "jeolbuk",
    "충남": "chungnam",
    "충북": "chungbuk",
    "제주": "jeju",
    "세종": "sejong",
}

# 폴더 생성
base_folder = "index"
count_folder = os.path.join(base_folder, "count")
os.makedirs(count_folder, exist_ok=True) 

# 웹드라이버 설정
# options = ChromeOptions()
# options.add_argument("--headless")
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-dev-shm-usage") 
# options.add_argument("--disable-gpu")
# options.add_argument("--disable-infobars")
# options.add_argument("--disable-notifications")  
# options.add_experimental_option("prefs", {
#     "profile.default_content_setting_values.geolocation": 2,  # 위치 권한 차단
#     "profile.default_content_setting_values.notifications": 2  # 알림 차단
# })
# browser = webdriver.Chrome(options=options)
# wait = WebDriverWait(browser, 10)

# 웹드라이버 설정(로컬)
browser = None
try:
    browser = webdriver.Chrome()
    wait = WebDriverWait(browser, 10)
except Exception as e:
    print(f"웹드라이버 초기화 실패: {e}")
    exit(1)

# 지역별 매장 수를 저장할 딕셔너리
region_counts = {}
total_count = 0

try:
    browser.get("https://www.starbucks.co.kr/store/store_map.do?disp=locale")
    time.sleep(10)

    # 페이지가 완전히 로드될 때까지 대기
    try:
        WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "store_map_layer_cont"))
        )
        print("페이지가 완전히 로드되었습니다.")
        time.sleep(10)
    except TimeoutException:
        print("페이지 로딩 시간 초과. 계속 진행합니다.")
        time.sleep(5)

    for index, (region_name_kor, location_name_eng) in enumerate(location_name_mapping.items(), start=1):
        try:
            print(f"\n{region_name_kor} 지역 처리 중... ({index}/{len(location_name_mapping)})")
            
            # 지역 버튼 클릭
            button_selector = f".sido_arae_box li:nth-child({index}) a"
            try:
                button = browser.find_element(By.CSS_SELECTOR, button_selector)
                browser.execute_script("arguments[0].click();", button)
                print(f"{region_name_kor} 버튼을 클릭했습니다.")
                time.sleep(10)
            except NoSuchElementException:
                print(f"{region_name_kor} 버튼을 찾을 수 없습니다. 건너뜁니다.")
                continue

            if region_name_kor != "세종":
                # 전체 버튼 클릭 (세종을 제외한 지역)
                try:
                    all_button = browser.find_element(By.CSS_SELECTOR, ".gugun_arae_box li:nth-child(1) a")
                    browser.execute_script("arguments[0].click();", all_button)
                    print("전체 버튼을 클릭했습니다.")
                    time.sleep(5)
                except NoSuchElementException:
                    print("전체 버튼을 찾을 수 없습니다. 계속 진행합니다.")
                    time.sleep(5)

            # 페이지 소스를 BeautifulSoup을 사용하여 저장
            soup = BeautifulSoup(browser.page_source, 'html.parser')

            # 지역 매장 수 추출
            try:
                total_count_element = soup.select_one(".result_num_wrap .sidoSetResult")
                if total_count_element:
                    region_count_text = total_count_element.text.strip()
                    region_count = int(re.sub(r'[^\d]', '', region_count_text)) if region_count_text else 0
                else:
                    region_count = 0
                print(f"{region_name_kor} 매장 수: {region_count}")
            except (ValueError, AttributeError) as e:
                print(f"{region_name_kor} 매장 수 추출 실패: {e}")
                region_count = 0

            # 지역별 매장 수 저장
            region_counts[region_name_kor] = region_count
            total_count += region_count

            # 매장 데이터 수집
            store_data = []
            try:
                stores = soup.select(".quickSearchResultBoxSidoGugun li.quickResultLstCon")
                for store in stores:
                    try:
                        # 이름, 주소, 위도, 경도 추출
                        name = store.get("data-name", "")
                        address_element = store.select_one(".result_details")
                        address = address_element.text.strip() if address_element else ""
                        
                        # 주소에서 전화번호 형식을 제거
                        if address:
                            address = re.sub(r'\d{4}-\d{4}', '', address).strip()  # 전화번호 패턴 제거
                        
                        latitude = store.get("data-lat", "")
                        longitude = store.get("data-long", "")

                        # 수집된 정보를 딕셔너리에 저장
                        if name:  # 이름이 있는 경우만 저장
                            store_data.append({
                                "name": name,
                                "address": address,
                                "latitude": latitude,
                                "longitude": longitude
                            })
                    except Exception as e:
                        print(f"개별 매장 데이터 추출 실패: {e}")
                        continue
                        
                print(f"{region_name_kor} 매장 데이터 {len(store_data)}개 수집 완료")
            except Exception as e:
                print(f"{region_name_kor} 매장 데이터 수집 실패: {e}")
                store_data = []
            
            # 지역별 JSON 데이터 생성
            final_data = {
                "location": region_name_kor,
                "count": len(store_data),
                "date": current_date,
                "item": store_data
            }

            # 지역 폴더 생성 및 데이터 저장
            try:
                location_folder_path = os.path.join(base_folder, location_name_eng)
                os.makedirs(location_folder_path, exist_ok=True)
                file_name = f"{location_folder_path}/{location_name_eng}_{current_date}.json"
                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(final_data, f, ensure_ascii=False, indent=4)
                print(f"{location_name_eng} 데이터가 '{file_name}' 파일에 저장되었습니다.")
            except Exception as e:
                print(f"{location_name_eng} 파일 저장 실패: {e}")
                
        except Exception as e:
            print(f"{region_name_kor} 지역 처리 중 오류 발생: {e}")
            continue

    # 전체 매장 수 JSON 생성
    try:
        count_data = {
            "날짜": current_date,
            "전체": total_count,
            **region_counts
        }  

        count_file_path = os.path.join(count_folder, f"starbucks-count_{current_date}.json")
        with open(count_file_path, "w", encoding="utf-8") as json_file:
            json.dump(count_data, json_file, ensure_ascii=False, indent=4)
        print(f"\n전체 데이터가 JSON 파일로 저장되었습니다: {count_file_path}")
        print(f"총 매장 수: {total_count}")
    except Exception as e:
        print(f"전체 데이터 저장 실패: {e}")
   
except WebDriverException as e:
    print(f"웹드라이버 에러 발생: {e}")
except TimeoutException as e:
    print(f"타임아웃 에러 발생: {e}")
except Exception as e:
    print(f"예상치 못한 에러 발생: {e}")
    import traceback
    traceback.print_exc()

finally:
    if browser:
        try:
            browser.quit()
            print("브라우저가 종료되었습니다.")
        except Exception as e:
            print(f"브라우저 종료 중 오류: {e}")
