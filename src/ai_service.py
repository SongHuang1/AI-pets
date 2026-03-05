import requests
from typing import List, Dict, Optional


class AIService:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = 30

    def chat(self, messages: List[Dict]) -> str:
        """
        调用 AI API 进行对话
        messages: [{"role": "user/assistant/system", "content": "..."}]
        return: AI 的回复文本
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return "AI 返回了空响应"

        except requests.exceptions.Timeout:
            return "请求超时，请检查网络连接"
        except requests.exceptions.ConnectionError:
            return "网络连接失败，请检查网络"
        except requests.exceptions.HTTPError as e:
            return f"API 错误: {e.response.status_code}"
        except KeyError:
            return "API 返回格式错误"
        except Exception as e:
            return f"发生错误: {str(e)}"
