#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chess
import chess.engine
import time
import os
import sys
import subprocess
from datetime import datetime
import uuid
import shutil

class ChessBot:
    def __init__(self):
        self.board = chess.Board()
        self.engine = None
        self.driver = None
        self.stockfish_path = "/home/dev/intelligent_agent/stockfish"
        self.user_data_dir = os.path.expanduser("~/.chess_assistant/user_data")  # دليل ثابت لبيانات المستخدم
        self.is_player_white = True
        self.debug_address = "127.0.0.1:9222"
        self.debug_port_file = os.path.expanduser("~/.chess_assistant/debug_port.txt")
        self.created_debug_file = False
        self.is_remote_connection = False

    def ensure_user_data_dir(self):
        """تأكيد وجود دليل بيانات المستخدم"""
        if not os.path.exists(self.user_data_dir):
            os.makedirs(self.user_data_dir)
            print(f"📁 تم إنشاء دليل بيانات مستخدم جديد: {self.user_data_dir}")

    def cleanup_old_sessions(self):
        """تنظيف الجلسات القديمة مع الحفاظ على بيانات المستخدم"""
        try:
            base_dir = os.path.expanduser("~/.chess_assistant")
            if os.path.exists(base_dir):
                for item in os.listdir(base_dir):
                    item_path = os.path.join(base_dir, item)
                    # حذف كل شيء ما عدا دليل بيانات المستخدم
                    if os.path.isdir(item_path) and item != "user_data":
                        shutil.rmtree(item_path)
                        print(f"🧹 تم حذف جلسة قديمة: {item}")
                    elif os.path.isfile(item_path) and item != "debug_port.txt":
                        os.remove(item_path)
                        print(f"🧹 تم حذف ملف قديم: {item}")
        except Exception as e:
            print(f"⚠️ تعذر حذف الجلسات القديمة: {e}")

    def kill_chrome_processes(self):
        """إنهاء عمليات Chrome"""
        try:
            subprocess.run(["pkill", "-f", "chrome"], capture_output=True)
            subprocess.run(["pkill", "-f", "chromium"], capture_output=True)
            time.sleep(2)
            print("🔄 تم إنهاء عمليات Chrome السابقة")
        except Exception as e:
            print(f"⚠️ تعذر إنهاء عمليات Chrome: {e}")

    def setup_engine(self):
        """تهيئة محرك Stockfish"""
        try:
            if os.path.exists(self.stockfish_path):
                self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
                self.engine.configure({
                    "Threads": 8,
                    "Hash": 4096,
                    "Skill Level": 20
                })
                print("✅ تم تهيئة محرك Stockfish بنجاح")
            else:
                print("❌ لم يتم العثور على محرك Stockfish")
                sys.exit(1)
        except Exception as e:
            print(f"❌ خطأ في تهيئة المحرك: {e}")
            sys.exit(1)

    def setup_browser(self, headless=True, use_existing=False):
        """تهيئة المتصفح مع الحفاظ على بيانات المستخدم"""
        try:
            # التأكد من وجود دليل بيانات المستخدم
            self.ensure_user_data_dir()
            
            if use_existing:
                # الاتصال بمتصفح موجود
                if not os.path.exists(self.debug_port_file):
                    print("❌ لم يتم العثور على جلسة متصفح نشطة. الرجاء تشغيل الخيار 1 أولاً.")
                    return False
                
                print("🌐 جاري الاتصال بمتصفح موجود...")
                
                options = webdriver.ChromeOptions()
                options.debugger_address = self.debug_address
                self.driver = webdriver.Chrome(options=options)
                self.is_remote_connection = True
                print("✅ تم الاتصال بالمتصفح المفتوح مسبقاً بنجاح")
                return True
            else:
                # فتح متصفح جديد مع الحفاظ على البيانات
                print("🌐 جاري فتح متصفح جديد مع الحفاظ على البيانات...")
                self.kill_chrome_processes()
                
                options = webdriver.ChromeOptions()
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--remote-debugging-port=9222')
                options.add_argument(f'--user-data-dir={self.user_data_dir}')
                options.add_argument('--profile-directory=Default')
                
                if headless:
                    options.add_argument('--headless')
                    options.add_argument('--window-size=1920,1080')
                else:
                    options.add_argument('--start-maximized')
                
                self.driver = webdriver.Chrome(options=options)
                
                # حفظ معلومات الجلسة
                with open(self.debug_port_file, 'w') as f:
                    f.write(self.debug_address)
                self.created_debug_file = True
                
                print("✅ تم فتح متصفح جديد بنجاح مع الاحتفاظ بالبيانات")
                return True
        except Exception as e:
            print(f"❌ خطأ في فتح المتصفح: {e}")
            return False

    def start_game(self):
        """بدء لعبة جديدة"""
        try:
            print("🎮 جاري فتح موقع chess.com...")
            self.driver.get("https://www.chess.com/play/computer")
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "board"))
            )
            
            # اختيار اللون الأبيض
            try:
                time.sleep(2)
                color_button = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-cy='new-game-color-white']"))
                )
                color_button.click()
                print("✅ تم اختيار اللون الأبيض")
            except:
                print("ℹ️ تعذر تغيير اللون، نفترض أننا نلعب بالأبيض")
            
            print("✅ تم فتح اللعبة بنجاح")
        except Exception as e:
            print(f"❌ خطأ في فتح اللعبة: {e}")
            sys.exit(1)

    def attach_to_game(self):
        """الاتصال باللعبة الحالية"""
        try:
            print("🔗 جاري الاتصال باللعبة الحالية...")
            
            # تحديد لون اللاعب
            try:
                color_button = self.driver.find_element(By.CSS_SELECTOR, "[data-cy='new-game-color-white']")
                if "selected" in color_button.get_attribute("class"):
                    self.is_player_white = True
                    print("✅ لون اللاعب: أبيض")
                else:
                    self.is_player_white = False
                    print("✅ لون اللاعب: أسود")
            except:
                print("⚠️ تعذر تحديد لون اللاعب، افتراضي: أبيض")
                self.is_player_white = True
            
            print("✅ تم الاتصال باللعبة بنجاح")
        except Exception as e:
            print(f"❌ خطأ في الاتصال باللعبة: {e}")
            sys.exit(1)

    def get_moves(self):
        """قراءة الحركات من الواجهة"""
        try:
            move_list = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "wc-simple-move-list"))
            )
            
            moves = []
            white_moves = move_list.find_elements(By.CSS_SELECTOR, ".white-move .node-highlight-content")
            black_moves = move_list.find_elements(By.CSS_SELECTOR, ".black-move .node-highlight-content")
            
            for white_move, black_move in zip(white_moves, black_moves):
                white_text = white_move.text.strip()
                black_text = black_move.text.strip()
                if white_text and white_text != "...":
                    moves.append(white_text)
                if black_text and black_text != "...":
                    moves.append(black_text)
                    
            return moves
        except Exception as e:
            print(f"❌ خطأ في قراءة الحركات: {e}")
            return []

    def update_position(self, moves):
        """تحديث لوحة الشطرنج بالحركات"""
        self.board = chess.Board()
        for move_text in moves:
            try:
                move = self.board.parse_san(move_text)
                self.board.push(move)
            except ValueError:
                print(f"⚠️ تعذر تحليل الحركة: {move_text}")

    def get_best_move(self):
        """الحصول على أفضل حركة"""
        if not self.engine:
            return None
        
        try:
            result = self.engine.play(
                self.board,
                chess.engine.Limit(time=2.0),
                info=chess.engine.INFO_ALL
            )
            
            best_move = result.move
            score = result.info.get('score', chess.engine.PovScore(chess.engine.Cp(0), chess.WHITE))
            
            if score.is_mate():
                eval_text = f"كش مات في {score.relative.mate()} حركة"
            else:
                eval_value = score.relative.score() / 100.0
                if eval_value > 0:
                    eval_text = f"موقف جيد (تقييم: +{eval_value:.1f})"
                else:
                    eval_text = f"موقف صعب (تقييم: {eval_value:.1f})"
            
            return {
                'move': self.board.san(best_move),
                'evaluation': eval_text
            }
        except Exception as e:
            print(f"❌ خطأ في تحليل الموقف: {e}")
            return None

    def get_move_squares(self, move):
        """الحصول على المربعات للحركة"""
        try:
            chess_move = self.board.parse_san(move)
            from_square = chess.square_name(chess_move.from_square)
            to_square = chess.square_name(chess_move.to_square)
            return f"{from_square} ➜ {to_square}"
        except ValueError:
            return ""

    def print_status(self):
        """طباعة حالة اللعبة الحالية"""
        last_moves_count = 0
        
        while True:
            moves = self.get_moves()
            current_moves_count = len(moves)
            
            if current_moves_count != last_moves_count:
                os.system('clear')
                print("\n=== مساعد الشطرنج ===")
                
                if moves:
                    print("\n📝 الحركات السابقة:", " ".join(moves))
                    self.update_position(moves)
                    
                    analysis = self.get_best_move()
                    if analysis:
                        move_squares = self.get_move_squares(analysis['move'])
                        print(f"\n💡 أفضل حركة: {analysis['move']}")
                        print(f"📍 المربعات: {move_squares}")
                        print(f"📊 التقييم: {analysis['evaluation']}")
                        
                        # تحديد دور اللاعب
                        if self.is_player_white:
                            is_our_turn = current_moves_count % 2 == 0
                        else:
                            is_our_turn = current_moves_count % 2 == 1
                            
                        if is_our_turn:
                            print(f"\n🎯 دورك للعب! يُنصح بـ: {analysis['move']} ({move_squares})")
                        else:
                            print("\n⏳ انتظر دورك...")
                else:
                    print("\nℹ️ ابدأ اللعب!")
                
                print("\nℹ️ اضغط Ctrl+C للخروج")
                last_moves_count = current_moves_count
            
            time.sleep(0.5)

    def cleanup(self):
        """تنظيف الموارد"""
        if self.engine:
            self.engine.quit()
            
        if self.driver and not self.is_remote_connection:
            self.driver.quit()
        
        # لا تحذف دليل بيانات المستخدم للحفاظ على الجلسة
        if self.created_debug_file and os.path.exists(self.debug_port_file):
            try:
                os.remove(self.debug_port_file)
                print(f"🧹 تم حذف ملف معلومات الجلسة")
            except Exception as e:
                print(f"⚠️ تعذر حذف ملف معلومات الجلسة: {e}")

    def show_menu(self):
        """عرض القائمة الرئيسية"""
        while True:
            os.system('clear')
            print("\n=== مساعد الشطرنج ===")
            print("\nالرجاء اختيار أحد الخيارات:")
            print("1. فتح المتصفح وبدء اللعبة")
            print("2. تشغيل المساعد على الجلسة الحالية")
            print("3. تنظيف الجلسات القديمة (مع الحفاظ على البيانات)")
            print("4. خروج")
            
            try:
                choice = input("\nاختيارك (1-4): ").strip()
                if choice in ['1', '2', '3', '4']:
                    return choice
                else:
                    print("\n⚠️ الرجاء إدخال رقم من 1 إلى 4")
                    time.sleep(2)
            except Exception:
                print("\n⚠️ خطأ في الإدخال")
                time.sleep(2)

    def start_browser_only(self):
        """فتح المتصفح فقط"""
        try:
            print("\n🌐 جاري فتح المتصفح مع الاحتفاظ بالبيانات...")
            if self.setup_browser(headless=False):
                self.start_game()
                print("\n✅ تم فتح اللعبة بنجاح")
                print("\nيمكنك الآن البدء باللعب!")
                print("عندما تكون جاهزاً للمساعدة، عد إلى هذا البرنامج واختر الخيار 2")
                print("\nاضغط Enter للعودة للقائمة الرئيسية...")
                input()
        except Exception as e:
            print(f"\n❌ خطأ: {e}")
            time.sleep(3)

    def start_assistant(self):
        """تشغيل المساعد على الجلسة الحالية"""
        try:
            print("\n🤖 جاري تشغيل المساعد الذكي...")
            self.setup_engine()
            if self.setup_browser(use_existing=True):
                self.attach_to_game()
                self.print_status()
        except Exception as e:
            print(f"\n❌ خطأ: {e}")
            time.sleep(3)

    def cleanup_all_sessions(self):
        """تنظيف الجلسات مع الحفاظ على بيانات المستخدم"""
        try:
            self.cleanup_old_sessions()
            self.kill_chrome_processes()
            
            if os.path.exists(self.debug_port_file):
                os.remove(self.debug_port_file)
                
            print("\n✅ تم تنظيف الجلسات القديمة مع الحفاظ على بيانات المستخدم")
            print("\nاضغط Enter للعودة للقائمة...")
            input()
        except Exception as e:
            print(f"\n❌ خطأ في التنظيف: {e}")
            time.sleep(3)

def main():
    bot = ChessBot()
    
    try:
        while True:
            choice = bot.show_menu()
            
            if choice == '1':
                bot.start_browser_only()
            elif choice == '2':
                bot.start_assistant()
            elif choice == '3':
                bot.cleanup_all_sessions()
            else:  # choice == '4'
                print("\n👋 مع السلامة!")
                break
                
    except KeyboardInterrupt:
        print("\n👋 تم إنهاء البرنامج.")
    finally:
        bot.cleanup()

if __name__ == "__main__":
    main()