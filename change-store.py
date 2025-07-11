import json
import os
import re
from datetime import datetime

# 변수 설정
REGION = "jeolnam" 
REGION_KR = "전남"  

# 입력 파일 경로
input_file = f"details/{REGION}/{REGION}_2025-07-10.json"

# 출력 파일 경로 (TypeScript, stores 폴더)
output_file = f"stores/{REGION}StoresData.ts"

def clean_string(text):
    """문자열에서 작은따옴표와 줄바꿈을 이스케이프 처리"""
    if not text:
        return ""
    return text.replace("'", "\\'").replace("\n", "\\n").replace("\r", "\\r")

def parse_services_and_facilities(services, facilities):
    """services와 facilities 이미지 URL을 분석해서 서비스/시설 태그로 변환"""
    service_tags = []
    facility_tags = []
    
    if services:
        for image_url in services:
            if 'icon01' in image_url:
                service_tags.append('리저브')
            elif 'icon02' in image_url:
                service_tags.append('커뮤니티 스토어')
            elif 'icon03' in image_url:
                service_tags.append('드라이브 스루')
            elif 'icon04' in image_url:
                service_tags.append('주차가능')
            elif 'icon07' in image_url:
                service_tags.append('공항내')
            elif 'icon08' in image_url:
                service_tags.append('대학가')
            elif 'icon09' in image_url:
                service_tags.append('해안가')
            elif 'icon10' in image_url:
                service_tags.append('입점')
            elif 'icon11' in image_url:
                service_tags.append('리조트')
            elif 'icon12' in image_url:
                service_tags.append('터미널/기차역')
            elif 'icon13' in image_url:
                service_tags.append('병원')
            elif 'icon14' in image_url:
                service_tags.append('지하철')
            elif 'icon18' in image_url:
                service_tags.append('나이트로 콜드 브루커피')
            elif 'icon19' in image_url:
                service_tags.append('장애인 편의시설')
            elif 'icon20' in image_url:
                service_tags.append('현금없는 매장')
            elif 'icon21' in image_url:
                service_tags.append('공기청정기')
            elif 'icon22' in image_url:
                service_tags.append('피지오')
            elif 'icon23' in image_url:
                service_tags.append('블론드')
            elif 'icon24' in image_url:
                service_tags.append('식약처 위생등급제 인증')
            elif 'EV' in image_url:
                service_tags.append('전기차 충전소')
            elif 'pet' in image_url:
                service_tags.append('펫존매장')
            elif 'delivers' in image_url:
                service_tags.append('딜리버스')
            elif 'Moon' in image_url:
                service_tags.append('21시 이후 영업종료매장')
            elif 'now' in image_url:
                service_tags.append('나우 브루잉 매장')
            elif 'fast' in image_url:
                service_tags.append('패스트 서브 매장')
            elif 'wt' in image_url:
                service_tags.append('워크스루')
    if facilities:
        for image_url in facilities:
            if 'icon01' in image_url:
                facility_tags.append('리저브')
            elif 'icon02' in image_url:
                facility_tags.append('커뮤니티 스토어')
            elif 'icon03' in image_url:
                facility_tags.append('드라이브 스루')
            elif 'icon04' in image_url:
                facility_tags.append('주차가능')
            elif 'icon07' in image_url:
                facility_tags.append('공항내')
            elif 'icon08' in image_url:
                facility_tags.append('대학가')
            elif 'icon09' in image_url:
                facility_tags.append('해안가')
            elif 'icon10' in image_url:
                facility_tags.append('입점')
            elif 'icon11' in image_url:
                facility_tags.append('리조트')
            elif 'icon12' in image_url:
                facility_tags.append('터미널/기차역')
            elif 'icon13' in image_url:
                facility_tags.append('병원')
            elif 'icon14' in image_url:
                facility_tags.append('지하철')
            elif 'icon18' in image_url:
                facility_tags.append('나이트로 콜드 브루커피')
            elif 'icon19' in image_url:
                facility_tags.append('장애인 편의시설')
            elif 'icon20' in image_url:
                facility_tags.append('현금없는 매장')
            elif 'icon21' in image_url:
                facility_tags.append('공기청정기')
            elif 'icon22' in image_url:
                facility_tags.append('피지오')
            elif 'icon23' in image_url:
                facility_tags.append('블론드')
            elif 'icon24' in image_url:
                facility_tags.append('식약처 위생등급제 인증')
            elif 'EV' in image_url:
                facility_tags.append('전기차 충전소')
            elif 'pet' in image_url:
                facility_tags.append('펫존매장')
            elif 'delivers' in image_url:
                facility_tags.append('딜리버스')
            elif 'Moon' in image_url:
                facility_tags.append('21시 이후 영업종료매장')
            elif 'now' in image_url:
                facility_tags.append('나우 브루잉 매장')
            elif 'fast' in image_url:
                facility_tags.append('패스트 서브 매장')
            elif 'wt' in image_url:
                facility_tags.append('워크스루')
    return service_tags, facility_tags

def generate_tags(name, address, services, facilities):
    """매장명과 주소에서 태그 생성"""
    tags = [REGION_KR]
    
    # 구 이름 추출 (부산의 경우)
    if REGION == "busan":
        gu_match = re.search(r'부산광역시\s*(\w+구)', address)
        if gu_match:
            tags.append(gu_match.group(1))
    # 다른 지역의 경우 해당 지역의 구/군 추출 로직 추가 가능
    
    # DT 여부 확인
    if 'DT' in name:
        tags.append('DT')
    if 'R' in name:
        tags.append('리저브')
    if '이마트' in name:
        tags.append('이마트')
    
    return tags

def transform_store_data(store, index):
    """개별 매장 데이터를 store 형식으로 변환"""
    # 주차 정보 처리 (원본 그대로 사용)
    parking_info = store.get("parking", "")
    
    # 태그 생성
    tags = generate_tags(store.get("name", ""), store.get("address", ""), store.get("services", []), store.get("facilities", []))
    
    # 서비스/시설 태그 분리
    services_arr, facilities_arr = parse_services_and_facilities(store.get("services", []), store.get("facilities", []))
    
    # 전화번호 정리
    phone = store.get("phone", "")
    if phone:
        # 전화번호만 추출 (괄호 안 설명 제거)
        phone_match = re.search(r'(\d{4}-\d{4})', phone)
        if phone_match:
            phone = phone_match.group(1)
    
    return {
        "storeId": f"{REGION}-{index + 1:02d}",
        "name": clean_string(store.get("name", "")),
        "address": clean_string(store.get("address", "")),
        "location": REGION_KR,
        "parking": clean_string(parking_info),
        "directions": clean_string(store.get("directions", "")),
        "since": "",
        "phone": clean_string(phone),
        "tags": tags,
        "services": services_arr,
        "facilities": facilities_arr,
        "images": store.get("images", [])
    }

def main():
    try:
        print(f"입력 파일 경로: {input_file}", flush=True)
        print(f"파일 존재 여부: {os.path.exists(input_file)}", flush=True)
        
        # 입력 파일 읽기
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"JSON 데이터 로드 완료", flush=True)
        print(f"데이터 키: {list(data.keys())}", flush=True)
        
        # 매장 데이터 변환
        stores = data.get("item", [])
        print(f"총 매장 수: {len(stores)}", flush=True)
        
        transformed_stores = []
        
        for index, store in enumerate(stores):
            try:
                transformed_store = transform_store_data(store, index)
                transformed_stores.append(transformed_store)
                print(f"변환 완료: {store.get('name', 'Unknown')} -> {transformed_store['storeId']}", flush=True)
            except Exception as e:
                print(f"매장 변환 실패 ({store.get('name', 'Unknown')}): {e}", flush=True)
                continue
        
        # TypeScript 파일로 저장
        ts_content = f"export const {REGION}StoresData = [\n"
        
        for i, store in enumerate(transformed_stores):
            ts_content += "    {\n"
            ts_content += f"      storeId: '{store['storeId']}',\n"
            ts_content += f"      name: '{store['name']}',\n"
            ts_content += f"      address: '{store['address']}',\n"
            ts_content += f"      location: '{store['location']}',\n"
            ts_content += f"      parking: '{store['parking']}',\n"
            ts_content += f"      directions: '{store['directions']}',\n"
            ts_content += f"      since: '{store['since']}',\n"
            ts_content += f"      phone: '{store['phone']}',\n"
            ts_content += f"      tags: {json.dumps(store['tags'], ensure_ascii=False)},\n"
            ts_content += f"      services: {json.dumps(store['services'], ensure_ascii=False)},\n"
            ts_content += f"      facilities: {json.dumps(store['facilities'], ensure_ascii=False)},\n"
            ts_content += f"      images: {json.dumps(store['images'], ensure_ascii=False)},\n"
            ts_content += "    }"
            
            if i < len(transformed_stores) - 1:
                ts_content += ","
            ts_content += "\n"
        
        ts_content += "]\n"
        
        # stores 폴더가 없으면 생성
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 출력 파일 저장
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(ts_content)
        
        print(f"\n변환 완료!", flush=True)
        print(f"입력 파일: {input_file}", flush=True)
        print(f"출력 파일: {output_file}", flush=True)
        print(f"총 {len(transformed_stores)}개 매장 변환됨", flush=True)
        
    except FileNotFoundError as e:
        print(f"파일을 찾을 수 없습니다: {e}", flush=True)
    except json.JSONDecodeError as e:
        print(f"JSON 파일 형식이 올바르지 않습니다: {e}", flush=True)
    except Exception as e:
        print(f"오류 발생: {e}", flush=True)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
