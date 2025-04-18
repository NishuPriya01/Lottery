import time
import random
import threading
from datetime import datetime
import signal
import sys

class LotterySystem:
    def __init__(self):
        self.registered_users = set()
        self.registration_open = True
        self.start_time = time.time()
        self.log_file = "lottery_log.txt"
        self.extension_count = 0
        self.last_save_time = time.time()
        
        with open(self.log_file, "a") as f:
            f.write(f"\n\n--- New Lottery Session Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
    
    def save_progress(self):
        """Save current registrations to log file"""
        with open(self.log_file, "a") as f:
            f.write(f"[Progress Save at {datetime.now().strftime('%H:%M:%S')}] Current participants: {len(self.registered_users)}\n")
            if self.registered_users:
                f.write("Current registrations:\n")
                for user in self.registered_users:
                    f.write(f"- {user}\n")
    
    def handle_interrupt(self, signum, frame):
        """Handle interrupt signals"""
        print("\n\nInterrupt received. Saving progress and exiting...")
        self.save_progress()
        sys.exit(0)
    
    def countdown_timer(self):
        """Display remaining registration time"""
        original_duration = 10
        remaining = original_duration - (time.time() - self.start_time)
        
        while remaining > 0 and self.registration_open:
            print(f"\rRegistration time remaining: {int(remaining)} seconds | Registered users: {len(self.registered_users)}", end="", flush=True)
            time.sleep(0.1)
            remaining = original_duration - (time.time() - self.start_time)
            
            if time.time() - self.last_save_time >= 2:
                self.save_progress()
                self.last_save_time = time.time()

        if len(self.registered_users) < 5 and self.extension_count == 0:
            self.extension_count += 1
            print("\nLess than 5 users registered. Extending registration for 3 seconds...")
            extension_start = time.time()
            remaining_extension = 3 - (time.time() - extension_start)
            
            while remaining_extension > 0 and self.registration_open:
                print(f"\rExtended time remaining: {int(remaining_extension)} seconds | Registered users: {len(self.registered_users)}", end="", flush=True)
                time.sleep(0.1)
                remaining_extension = 3 - (time.time() - extension_start)
        
        elapsed_with_extension = (time.time() - self.start_time)
        if len(self.registered_users) == 0 and elapsed_with_extension >= 5:
            print("\nNo users registered in the allowed time. Exiting...")
            with open(self.log_file, "a") as f:
                f.write("No participants registered. Lottery cancelled.\n")
            self.registration_open = False
            sys.exit(0)
        
        self.registration_open = False
        print("\n\nRegistration closed!")
    
    def register_user(self, username):
        """Register a new user if valid and unique"""
        if not self.registration_open:
            return False, "Registration is closed!"
        
        if not username:
            return False, "Username cannot be empty!"
        if not username.isalnum():
            return False, "Username can only contain letters and numbers!"
        if len(username) > 20:
            return False, "Username too long (max 20 characters)!"
        
        
        if username in self.registered_users:
            return False, "Username already registered!"
        
        
        self.registered_users.add(username)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}] Registered user: {username}\n")
        
        return True, "Registration successful!"
    
    def draw_winner(self):
        """Select and announce a random winner"""
        if not self.registered_users:
            return "No participants to draw from!"
        
        winner = random.choice(list(self.registered_users))
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(self.log_file, "a") as f:
            f.write(f"\n[{timestamp}] Lottery Draw Results:\n")
            f.write(f"Total participants: {len(self.registered_users)}\n")
            f.write("Participants:\n")
            for user in self.registered_users:
                f.write(f"- {user}\n")
            f.write(f"\nWINNER: {winner}\n")
            f.write("--- Lottery Session Ended ---\n")
        
        announcement = f"""
        {'*' * 50}
        {'LOTTERY RESULTS'.center(50)}
        {'*' * 50}
        Total Participants: {len(self.registered_users)}
        Participants: {', '.join(self.registered_users)}
        {'-' * 50}
        {'WINNER:'.center(50)}
        {winner.center(50)}
        {'*' * 50}
        """
        
        return announcement

def main():
    lottery = LotterySystem()
    
    signal.signal(signal.SIGINT, lottery.handle_interrupt)
    
    timer_thread = threading.Thread(target=lottery.countdown_timer)
    timer_thread.daemon = True
    timer_thread.start()
    
    print("Welcome to the Lottery System!")
    print("You have 10 seconds to register. Enter your username below:")
    
    while lottery.registration_open:
        try:
            username = input("\nEnter username: ").strip()
            success, message = lottery.register_user(username)
            print(message)
        except EOFError:
            break  
    
    timer_thread.join()
    
    if lottery.registered_users:
        print(lottery.draw_winner())

if __name__ == "__main__":
    main()
