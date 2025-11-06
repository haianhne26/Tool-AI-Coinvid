import requests
import json
import time
from datetime import datetime, timedelta

def get_issue_result():
    url = 'https://m.coinvidb.com/api/rocket-api/game/issue-result/page?subServiceCode=RG1M&size=1&current=1'
    headers = {
        "Host": "m.coinvidb.com",
        "Connection": "keep-alive",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Android WebView\";v=\"127\", \"Chromium\";v=\"127\"",
        "user_type": "rocket",
        "Accept-Language": "en-US",
        "sec-ch-ua-mobile": "?1",
        "Authorization": "Basic cm9ja2V0X3dlYjpyb2NrZXRfd2Vi",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "sec-ch-ua-platform": "\"Android\"",
        "X-Requested-With": "mark.via.gp",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://m.coinvidb.com/openHistory?resultUrl=gameList",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Cookie": "JSESSIONID=rSOOApLrwvFv-Hw3URR6-w6wGzt0kTlo9eQjKXBs"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Error: {e}")
        return None

    if data is None or 'data' not in data or 'records' not in data['data'] or not data['data']['records']:
        print("Error: Invalid response or records not found.")
        return None

    latest_record = data['data']['records'][0]
    issue = latest_record.get('issue', 'N/A')
    result_format_value_i18n = latest_record.get('resultFormatValueI18n', [])

    colors = ['Red', 'Green']
    found_colors = [value.strip() for value in result_format_value_i18n if value.strip() in colors]

    if found_colors:
        print(f"┏━━━━━━━━━━━━━ Vchart Tool AI KẾT QUẢ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            f"Số phiên: {issue}\n"
            f"Kết quả: {', '.join(found_colors)}\n"
              f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
        return {
            'issue': issue,
            'result': ', '.join(found_colors),
            'settleTime': latest_record.get('completeSettleTime', 0)
        }
    else:
        print(f"Session: {issue}")
        print("No relevant colors found.")
        return None

def save_history(history, file='dulieu.txt'):
    with open(file, 'w') as f:
        json.dump(history, f)

def load_history(file='dulieu.txt'):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def predict_next(history, pattern_length=4):
    if len(history) < pattern_length:
        return 'Không có dữ liệu', 0

    patterns = {}

    cleaned_history = [item for item in history if item['result'] in ['Red', 'Green']]

    for i in range(len(cleaned_history) - pattern_length):
        pattern = ' '.join([item['result'] for item in cleaned_history[i:i + pattern_length]])
        next_result = cleaned_history[i + pattern_length].get('result')

        if next_result:
            if pattern not in patterns:
                patterns[pattern] = {}
            if next_result not in patterns[pattern]:
                patterns[pattern][next_result] = 0
            patterns[pattern][next_result] += 1

    current_pattern = ' '.join([item['result'] for item in cleaned_history[-pattern_length:]])

    if current_pattern in patterns:
        predictions = patterns[current_pattern]
        total_occurrences = sum(predictions.values())
        predicted_result = max(predictions, key=predictions.get)
        win_rate = min(85, (predictions[predicted_result] / total_occurrences) * 100)
        return predicted_result, win_rate
    else:
        return 'Unknown', 0

history = load_history()
last_processed_issue = None

while True:
    result = get_issue_result()
    if result and result['issue'] != last_processed_issue:
        last_processed_issue = result['issue']
        history.append(result)
        if len(history) > 1000:
            history = history[-1000:]

        save_history(history)

        prediction, win_rate = predict_next(history)
        current_session = int(str(history[-1]['issue'])[-7:])
        next_session = current_session + 1

        if prediction != 'Unknown':
            print(f"┏━━━━━━━━━━━━━ Vchart Tool AI - DỰ BÁO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                f"Dự đoán kết quả phiên {next_session}: {prediction} ({win_rate:.2f}%)\n"
                  f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
        else:
            print(f"Dự đoán kết quả phiên {next_session}: {prediction}")

    time.sleep(60)
