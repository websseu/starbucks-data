import json
import os
from datetime import datetime

# 변수 설정
REGION = "jeolnam" 
REGION_KR = "전남"  

# 입력 파일 경로
input_file = f"details/{REGION}/{REGION}_2025-07-10.json"

# 출력 파일 경로 (TypeScript, posts 폴더)
output_file = f"posts/{REGION}PostsData.ts"

def slugify(text):
    # 더 이상 사용하지 않음
    return text

def clean_description(description):
    """설명에서 작은 따옴표 제거"""
    return description.replace("'", "")

def transform_store_data(store, index):
    """개별 매장 데이터를 원하는 형식으로 변환"""
    return {
        "title": store.get("name", ""),
        "slug": f"{REGION}-{index + 1:02d}",
        "category": REGION_KR,
        "description": clean_description(store.get("description", "")),
        "numViews": 0,
        "numLikes": 0,
        "storeId": f"{REGION}-{index + 1:02d}",
        "isPublished": True
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
            transformed_store = transform_store_data(store, index)
            transformed_stores.append(transformed_store)
            print(f"변환 완료: {store.get('name', 'Unknown')} -> {transformed_store['slug']}", flush=True)
        
        # TypeScript 파일로 저장
        ts_content = f"export const {REGION}PostsData = [\n"
        
        for i, store in enumerate(transformed_stores):
            ts_content += "  {\n"
            ts_content += f"    title: '{store['title']}',\n"
            ts_content += f"    slug: '{store['slug']}',\n"
            ts_content += f"    category: '{store['category']}',\n"
            ts_content += f"    description:\n"
            ts_content += f"      '{store['description']}',\n"
            ts_content += f"    numViews: {store['numViews']},\n"
            ts_content += f"    numLikes: {store['numLikes']},\n"
            ts_content += f"    storeId: '{store['storeId']}',\n"
            ts_content += f"    isPublished: {str(store['isPublished']).lower()},\n"
            ts_content += "  }"
            
            if i < len(transformed_stores) - 1:
                ts_content += ","
            ts_content += "\n"
        
        ts_content += "]\n"
        
        # posts 폴더가 없으면 생성
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
