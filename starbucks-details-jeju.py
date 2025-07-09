from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from datetime import datetime
import os
import time
import json

# 현재 날짜를 문자열로 저장
current_date = datetime.now().strftime("%Y-%m-%d")

# details 폴더 생성
base_folder_path = os.path.join("details", "jeju")
os.makedirs(base_folder_path, exist_ok=True)

# 웹드라이버 설정 및 페이지 로드
options = ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage") 
options.add_argument("--disable-gpu")
options.add_argument("--disable-infobars")
options.add_argument("--disable-notifications")
options.add_experimental_option("prefs", {
    "profile.default_content_setting_values.geolocation": 2,  # 위치 권한 차단
    "profile.default_content_setting_values.notifications": 2  # 알림 차단
})
browser = webdriver.Chrome(options=options)
browser.get("https://www.starbucks.co.kr/store/store_map.do?disp=locale")

# 웹드라이버 설정(로컬)
# browser = webdriver.Chrome()
# wait = WebDriverWait(browser, 10)
# browser.get("https://www.starbucks.co.kr/store/store_map.do")
# time.sleep(10)

# 클릭 및 이동
browser.find_element(By.CSS_SELECTOR, "#container > div > form > fieldset > div > section > article.find_store_cont > article > header.loca_search > h3 > a").click()
time.sleep(3)
print("지역검색 버튼을 클릭했습니다.")
browser.find_element(By.CSS_SELECTOR, ".loca_step1_cont .sido_arae_box li:nth-child(16)").click()
time.sleep(3) 
print("제주 버튼을 클릭했습니다.")
browser.find_element(By.CSS_SELECTOR, "#mCSB_2_container > ul > li:nth-child(1) > a").click()
time.sleep(3) 
print("전체선택 버튼을 클릭했습니다.")

# 전체 점포 리스트 가져오기
stores = browser.find_elements(By.CSS_SELECTOR, ".quickSearchResultBoxSidoGugun .quickResultLstCon")

# 모든 점포 데이터를 저장할 리스트
store_data_list = []

# 모든 점포에 대해 순차적으로 작업
for index, store in enumerate(stores):
    try:
        print(f"\n=== 매장 {index + 1}/{len(stores)} 처리 시작 ===")
        
        # store.click()
        # JavaScript를 사용하여 요소 클릭
        browser.execute_script("arguments[0].click();", store)
        time.sleep(2)

        # 점포 이름과 주소 추출
        try:
            store_name = browser.find_element(By.CSS_SELECTOR, ".map_marker_pop header").text.strip()
            store_address = browser.find_element(By.CSS_SELECTOR, ".map_marker_pop .addr").text.strip()
            print(f"매장명: {store_name}")
            print(f"주소: {store_address}")
        except Exception as e:
            print(f"매장명/주소 추출 실패: {e}")
            continue

        # "상세 정보 보기" 버튼 클릭
        try:
            detail_button = browser.find_element(By.CSS_SELECTOR, ".map_marker_pop .btn_marker_detail")
            browser.execute_script("arguments[0].click();", detail_button)
            time.sleep(2) 
            print(f"상세 정보 보기 버튼을 클릭했습니다.")
        except Exception as e:
            print(f"상세 정보 보기 버튼 클릭 실패: {e}")
            continue

        # 상세 정보 페이지의 HTML 가져오기
        try:
            detail_page_html = browser.page_source
            soup = BeautifulSoup(detail_page_html, 'html.parser')

            # 각종 정보 추출 
            store_description = ""
            description_element = soup.select_one(".shopArea_pop01 .asm_stitle p")
            if description_element:
                store_description = description_element.text.strip()

            # 주차정보 추출 
            store_parking_info = ""
            parking_dt = soup.find("dt", string="주차정보")
            if parking_dt:
                parking_dd = parking_dt.find_next_sibling("dd")
                if parking_dd:
                    store_parking_info = parking_dd.text.strip()

            # 전화번호 추출 
            store_phone = ""
            phone_dt = soup.find("dt", string="대표번호")
            if phone_dt:
                phone_dd = phone_dt.find_next_sibling("dd")
                if phone_dd:
                    store_phone = phone_dd.text.strip()

            # 오시는 길 추출 
            store_direction = ""
            direction_dt = soup.find("dt", string="오시는 길")
            if direction_dt:
                direction_dd = direction_dt.find_next_sibling("dd")
                if direction_dd:
                    store_direction = direction_dd.text.strip()

            # 서비스 이미지 URL 리스트 추출 (안전한 방식)
            store_services = []
            service_dt = soup.find("dt", string="서비스")
            if service_dt:
                service_dd = service_dt.find_next_sibling("dd")
                if service_dd:
                    store_services = [
                        f"https:{img['src']}" for img in service_dd.find_all("img")
                    ]

            # 위치 및 시설 이미지 URL 리스트 추출 (안전한 방식)
            store_facilities = []
            facility_dt = soup.find("dt", string="위치 및 시설")
            if facility_dt:
                facility_dd = facility_dt.find_next_sibling("dd")
                if facility_dd:
                    store_facilities = [
                        f"https:{img['src']}" for img in facility_dd.find_all("img")
                    ]

            # 이미지 URL 리스트 추출
            image_urls = [
                f"https:{img['src']}" for img in soup.select(".shopArea_left .s_img li img")
            ]

            # 영업 시간 추출 (안전한 방식)
            store_hours = []
            hours_sections = soup.select(".date_time dl")
            for dl in hours_sections:
                dt_tags = dl.select("dt")
                dd_tags = dl.select("dd")
                for dt, dd in zip(dt_tags, dd_tags):
                    dt_text = dt.get_text(strip=True) if dt else ""
                    dd_text = dd.get_text(strip=True) if dd else ""
                    if dt_text and dd_text:
                        store_hours.append(f"{dt_text} {dd_text}")

            # JSON 데이터 생성
            store_data = {
                "number": index + 1, 
                "name": store_name,
                "description": store_description,
                "address": store_address,
                "parking": store_parking_info,
                "directions": store_direction,
                "phone": store_phone,
                "services": store_services,
                "facilities": store_facilities,
                "images": image_urls,
                "hours": store_hours, 
            }

            # 모든 탭을 순차적으로 처리 (첫 번째 탭 제외, 이미 기본 영업시간으로 수집됨)
            all_tabs = browser.find_elements(By.CSS_SELECTOR, "dt.tab a")
            
            # 첫 번째 탭은 건너뛰고 나머지 탭들 처리
            for tab_index, tab in enumerate(all_tabs[1:], 1):
                try:
                    # 탭 클릭
                    browser.execute_script("arguments[0].click();", tab)
                    time.sleep(2)
                    
                    # 탭 텍스트 확인
                    tab_text = tab.text.strip()
                    print(f"탭 {tab_index} 텍스트: {tab_text}")
                    
                    # 페이지 소스 다시 파싱
                    updated_soup = BeautifulSoup(browser.page_source, 'html.parser')
                    
                    # 활성화된 탭의 패널에서 영업시간 추출 (display: block인 패널 찾기)
                    active_panel = updated_soup.find("dd", class_="panel", style="display: block;")
                    if active_panel:
                        # 영업시간 요소들 찾기
                        time_elements = active_panel.find_all(["dt", "dd"])
                        additional_hours = []
                        current_day = ""
                        
                        for element in time_elements:
                            if element.name == 'dt':
                                current_day = element.get_text(strip=True) if element else ""
                            elif element.name == 'dd' and current_day:
                                time_info = element.get_text(strip=True) if element else ""
                                if current_day and time_info:
                                    additional_hours.append(f"{current_day} {time_info}")
                        
                        # 탭 텍스트에 따라 다른 키로 저장
                        if "Delivers 영업시간 보기" in tab_text:
                            store_data["deliversHours"] = additional_hours
                            print(f"Delivers 영업시간 수집 완료: {len(additional_hours)}개")
                        elif "리저브존 영업시간 보기" in tab_text:
                            store_data["reserveHours"] = additional_hours
                            print(f"리저브존 영업시간 수집 완료: {len(additional_hours)}개")
                        elif "Drive Thru 영업시간 보기" in tab_text:
                            store_data["driveThruHours"] = additional_hours
                            print(f"Drive Thru 영업시간 수집 완료: {len(additional_hours)}개")
                        elif "펫존 영업시간 보기" in tab_text:
                            store_data["petHours"] = additional_hours
                            print(f"펫존 영업시간 수집 완료: {len(additional_hours)}개")
                        else:
                            # 여러 개의 추가 탭이 있을 수 있으므로 리스트로 관리
                            if "additionalHours" not in store_data:
                                store_data["additionalHours"] = []
                            store_data["additionalHours"].append({
                                "tab_name": tab_text,
                                "hours": additional_hours
                            })
                            print(f"추가 영업시간 수집 완료: {len(additional_hours)}개")
                            
                except Exception as e:
                    print(f"탭 {tab_index} 처리 중 오류: {e}")
                    continue

            store_data_list.append(store_data)
            print(f"매장 {store_name} 데이터 수집 완료")

            # 상세 정보 창 닫기
            try:
                close_button = browser.find_element(By.CSS_SELECTOR, ".btn_pop_close .isStoreViewClosePop")
                browser.execute_script("arguments[0].click();", close_button)
                time.sleep(2)
            except Exception as e:
                print(f"팝업 닫기 실패: {e}")

        except Exception as e:
            print(f"매장 {index + 1} 상세 정보 수집 실패: {e}")
            continue

    except Exception as e:
        print(f"매장 {index + 1} 전체 처리 실패: {e}")
        continue

# JSON 파일 구조화
final_data = {
    "kind": "Korea Starbucks",
    "date": current_date,
    "location": "제주(jeju)",
    "count": len(store_data_list),
    "item": store_data_list
}

# JSON 파일 저장
output_file_path = os.path.join(base_folder_path, f"jeju_{current_date}.json")
with open(output_file_path, 'w', encoding='utf-8') as f:
    json.dump(final_data, f, ensure_ascii=False, indent=4)

print(f"파일이 저장되었습니다: {output_file_path}")

# 브라우저 닫기
browser.quit()