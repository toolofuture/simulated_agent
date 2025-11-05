"""
LLM 기반 가짜 미술품 검증 시뮬레이션 에이전트
OpenAI API를 사용하여 검증 봇과 고객 봇이 대화합니다.
"""

import random
import hashlib
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from PIL import Image
import io
import openai


@dataclass
class ConversationTurn:
    """대화 턴"""
    turn: int
    customer_message: str
    verification_message: str
    customer_response: str = ""
    timestamp: str = ""


class LLMCustomerBot:
    """LLM 기반 고객 봇"""
    
    def __init__(self, api_key: str, name: str = "고객"):
        self.name = name
        self.api_key = api_key
        self.conversation_history = []
        self.system_prompt = """당신은 미술품을 검증받고 싶어하는 고객입니다.
다양한 미술품을 제출하고, 검증 결과에 대해 자연스럽게 반응합니다.
때로는 진품을 제출하기도 하고, 때로는 가품을 제출하기도 합니다.
검증 결과에 대해 감정적으로 반응하며, 진품 판정을 받으면 기뻐하고, 가품 판정을 받으면 놀라거나 반박합니다."""
        
    def generate_submission(self, turn: int, client) -> str:
        """작품 제출 메시지 생성"""
        artists = ['반 고흐', '피카소', '모네', '세잔', '르누아르', '마네', '고갱', '세라', '마티스', '칸딘스키']
        places = ['경매장', '갤러리', '컬렉터', '미술관', '가족 유산']
        years = random.randint(1800, 2000)
        
        # 랜덤으로 주장 생성
        templates = [
            f"이 작품은 {random.choice(artists)}의 진품입니다. {random.choice(places)}에서 구매했습니다.",
            f"이 작품은 {years}년대 작품입니다. 가족 대대로 내려온 명화입니다.",
            f"이미 전문가에게 검증받은 작품입니다. {random.choice(artists)}의 작품이라고 확신합니다.",
            f"이 작품의 소유 이력이 명확합니다. {random.choice(places)}에서 인증받았습니다.",
        ]
        
        claim = random.choice(templates)
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"작품 제출 시나리오 (턴 {turn}): {claim}\n\n이 상황에서 자연스럽게 작품을 제출하는 메시지를 작성해주세요. 간단하고 자연스럽게."}
                ],
                temperature=0.8,
                max_tokens=150
            )
            message = response.choices[0].message.content.strip()
            return message
        except Exception as e:
            return f"안녕하세요. 이 작품을 검증해주세요. {claim}"
    
    def respond_to_verification(self, verdict: str, reasoning: str, client) -> str:
        """검증 결과에 대한 반응"""
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"검증 결과: {verdict}\n검증 이유: {reasoning}\n\n이 검증 결과에 대한 자연스러운 반응을 작성해주세요. 감정적으로 반응하세요."}
                ],
                temperature=0.8,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if verdict == "진품":
                return "감사합니다! 제가 알고 있던 대로 진품이었네요."
            elif verdict == "가품":
                return "정말요? 믿을 수 없네요. 다시 확인해주실 수 있나요?"
            else:
                return "더 자세한 검증이 필요한가요?"


class LLMVerificationBot:
    """LLM 기반 검증 봇"""
    
    def __init__(self, api_key: str, name: str = "검증 전문가"):
        self.name = name
        self.api_key = api_key
        self.verification_history = []
        self.system_prompt = """당신은 미술품 검증 전문가입니다.
작품의 화풍, 기법, 재료, 연대감 등을 분석하여 진품인지 가품인지 판단합니다.
항상 신중하고 전문적으로 판단하며, 확실하지 않으면 '의심'으로 판정합니다.
판정은 '진품', '가품', '의심' 중 하나이며, 판정 이유를 명확히 설명합니다."""
    
    def verify_artwork(self, customer_message: str, client) -> Dict[str, str]:
        """작품 검증"""
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"고객 메시지: {customer_message}\n\n이 작품을 검증해주세요. 판정은 '진품', '가품', '의심' 중 하나로 답하고, 판정 이유를 간단히 설명해주세요.\n형식: [판정] 이유"}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # 결과 파싱
            if "[진품]" in result_text or "진품" in result_text:
                verdict = "진품"
                reasoning = result_text.replace("[진품]", "").replace("진품", "").strip()
            elif "[가품]" in result_text or "가품" in result_text:
                verdict = "가품"
                reasoning = result_text.replace("[가품]", "").replace("가품", "").strip()
            else:
                verdict = "의심"
                reasoning = result_text.replace("[의심]", "").replace("의심", "").strip()
            
            return {
                "verdict": verdict,
                "reasoning": reasoning if reasoning else "추가 검증이 필요합니다.",
                "full_response": result_text
            }
        except Exception as e:
            # 오류 발생 시 기본 응답
            return {
                "verdict": "의심",
                "reasoning": "검증 중 오류가 발생했습니다. 추가 확인이 필요합니다.",
                "full_response": str(e)
            }


class LLMArtworkSimulator:
    """LLM 기반 미술품 검증 시뮬레이터"""
    
    def __init__(self, api_key: str, num_turns: int = 100):
        self.api_key = api_key
        self.num_turns = num_turns
        self.client = openai.OpenAI(api_key=api_key)
        self.customer_bot = LLMCustomerBot(api_key, "고객 봇")
        self.verification_bot = LLMVerificationBot(api_key, "검증 전문가")
        self.conversations: List[ConversationTurn] = []
        self.results_dir = Path("simulation_results")
        self.results_dir.mkdir(exist_ok=True)
    
    def generate_sample_image_hash(self) -> str:
        """샘플 이미지 해시 생성"""
        # 더미 이미지 생성
        img = Image.new('RGB', (800, 600), color=(random.randint(0, 255), 
                                                   random.randint(0, 255), 
                                                   random.randint(0, 255)))
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        image_bytes = img_bytes.getvalue()
        return hashlib.sha256(image_bytes).hexdigest()
    
    def run_simulation(self, progress_callback=None):
        """시뮬레이션 실행"""
        results = []
        
        for turn in range(1, self.num_turns + 1):
            try:
                # 1. 고객이 작품 제출
                customer_message = self.customer_bot.generate_submission(turn, self.client)
                
                # 2. 검증 봇이 분석
                verification_result = self.verification_bot.verify_artwork(customer_message, self.client)
                verification_message = f"[{verification_result['verdict']}] {verification_result['reasoning']}"
                
                # 3. 고객 반응
                customer_response = self.customer_bot.respond_to_verification(
                    verification_result['verdict'],
                    verification_result['reasoning'],
                    self.client
                )
                
                # 대화 기록
                conversation = ConversationTurn(
                    turn=turn,
                    customer_message=customer_message,
                    verification_message=verification_message,
                    customer_response=customer_response,
                    timestamp=datetime.now().isoformat()
                )
                self.conversations.append(conversation)
                
                results.append({
                    "turn": turn,
                    "customer": customer_message,
                    "verification": verification_message,
                    "customer_response": customer_response,
                    "verdict": verification_result['verdict']
                })
                
                # 진행 상황 콜백
                if progress_callback:
                    progress_callback(turn, self.num_turns, conversation)
                
                # API 레이트 제한 방지
                time.sleep(0.5)
                
            except Exception as e:
                print(f"턴 {turn} 오류: {e}")
                continue
        
        # 결과 저장
        self.save_results(results)
        
        return results
    
    def save_results(self, results: List[Dict]):
        """결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 대화 기록 저장
        conversations_file = self.results_dir / f"conversations_{timestamp}.json"
        with open(conversations_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(conv) for conv in self.conversations], 
                     f, ensure_ascii=False, indent=2)
        
        # 전체 결과 저장
        results_file = self.results_dir / f"results_{timestamp}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        return conversations_file, results_file
    
    def get_statistics(self) -> Dict:
        """통계 계산"""
        if not self.conversations:
            return {}
        
        total = len(self.conversations)
        verdicts = {}
        for conv in self.conversations:
            verdict = conv.verification_message.split(']')[0].replace('[', '')
            verdicts[verdict] = verdicts.get(verdict, 0) + 1
        
        return {
            "total_turns": total,
            "verdict_breakdown": verdicts
        }

