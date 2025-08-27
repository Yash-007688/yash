#!/usr/bin/env python3
"""
Single Instagram Account Test Script
Demonstrates the single Instagram account system for reel watching
"""

import random
import string
from datetime import datetime

def generate_random_username(prefix="reel_watcher"):
    """Generate a random Instagram username"""
    random_suffix = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}_{random_suffix}"

def generate_strong_password(length=12):
    """Generate a strong password"""
    characters = string.ascii_letters + string.digits + '!@#$%^&*'
    return ''.join(random.choices(characters, k=length))

def create_single_instagram_account(username_prefix="reel_watcher"):
    """Create a single Instagram account for reel watching"""
    
    # Generate random username and password
    username = generate_random_username(username_prefix)
    password = generate_strong_password()
    
    # Simulate account creation
    account_data = {
        'username': username,
        'password': password,
        'is_active': True,
        'login_status': 'new',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return account_data

def test_single_account_system():
    """Test the single Instagram account system"""
    
    print("🆕 Single Instagram Account System Test")
    print("=" * 50)
    
    print("\n🎯 Creating Single Instagram Account...")
    print("-" * 40)
    
    # Create single account
    account = create_single_instagram_account("reel_watcher")
    
    print(f"\n✅ Single Instagram Account Created Successfully!")
    print(f"   Username: @{account['username']}")
    print(f"   Password: {account['password']}")
    print(f"   Purpose: Reel Watcher")
    print(f"   Status: {account['login_status'].title()}")
    print(f"   Created: {account['created_at']}")
    
    # Test login simulation
    print("\n🔐 Testing Account Login...")
    print("-" * 40)
    
    # Simulate login test (75% success rate)
    success = random.choice([True, True, True, False])
    
    if success:
        account['login_status'] = 'active'
        account['last_login'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"✅ @{account['username']}: Login Successful")
    else:
        account['login_status'] = 'failed'
        print(f"❌ @{account['username']}: Login Failed")
    
    # Display account summary
    print("\n📊 Account Summary")
    print("=" * 50)
    
    print(f"Instagram Account: @{account['username']}")
    print(f"Status: {account['login_status'].title()}")
    print(f"Purpose: Watch reels from target accounts")
    
    if account['login_status'] == 'active':
        print("\n🎯 Ready for Reel Watching!")
        print("-" * 40)
        print("✅ Account is ready to watch reels from target Instagram accounts")
        print("🎯 Next steps:")
        print("   1. Add target Instagram accounts to monitor")
        print("   2. Start automated reel watching")
        print("   3. Monitor content extraction progress")
        print("   4. Review extracted reels")
    else:
        print("\n⚠️  Account login failed. Please retry login test.")
    
    return account

def simulate_reel_watching(account):
    """Simulate reel watching using single account"""
    
    print("\n🤖 Simulating Reel Watching...")
    print("=" * 50)
    
    if account['login_status'] != 'active':
        print("❌ Account not active. Cannot watch reels.")
        return
    
    # Sample target accounts
    target_accounts = [
        "@funny_hindi_videos",
        "@gaming_india", 
        "@lifestyle_creator",
        "@comedy_central_india"
    ]
    
    print(f"🔐 Using Instagram account: @{account['username']}")
    print(f"🎯 Watching {len(target_accounts)} target accounts")
    
    print(f"\n🔐 Instagram Account: @{account['username']}")
    print("-" * 40)
    
    for target_account in target_accounts:
        print(f"🔍 Watching {target_account}...")
        
        # Simulate finding content
        if random.choice([True, False, False]):  # 33% chance of finding content
            print(f"📱 Found new reel from {target_account}")
            print(f"⏰ Posted: {random.randint(1, 60)} minutes ago")
            print(f"📊 Engagement: {random.randint(100, 2000)}+ likes")
            
            # Simulate content processing
            print(f"🎬 Downloading reel using @{account['username']}...")
            print(f"🎤 Extracting audio...")
            print(f"📝 AI Analysis: Content processed")
            print(f"🎯 Generated title: 'INSANE Hindi Comedy That Will Make You CRY! 😂'")
            print(f"🎨 Creating EPIC thumbnail...")
            print(f"📺 Uploading to YouTube...")
            print(f"✅ Success! Video uploaded")
        else:
            print(f"⏳ No new reels found from {target_account}")

def demonstrate_single_account_benefits():
    """Demonstrate benefits of single account system"""
    
    print("\n💡 Single Account System Benefits")
    print("=" * 50)
    
    benefits = [
        "🎯 **Simplified Management**: Only one account to manage",
        "🔒 **Better Security**: Single point of control",
        "⚡ **Faster Setup**: Quick account creation and configuration",
        "📊 **Clear Monitoring**: Easy to track account status",
        "🛡️ **Reduced Risk**: Less chance of account detection",
        "💰 **Cost Effective**: No need for multiple accounts",
        "🎯 **Focused Purpose**: Dedicated for reel watching only",
        "📱 **Easy Maintenance**: Simple login and status checks"
    ]
    
    for benefit in benefits:
        print(f"   {benefit}")
    
    print("\n🎯 **Perfect for**:")
    print("   • Watching specific Instagram accounts")
    print("   • Extracting reels from target accounts")
    print("   • Automated content monitoring")
    print("   • YouTube content creation")

if __name__ == "__main__":
    print("🚀 Single Instagram Account - Reel Watching System")
    print("=" * 60)
    
    # Create single account
    account = test_single_account_system()
    
    # Simulate reel watching
    simulate_reel_watching(account)
    
    # Show benefits
    demonstrate_single_account_benefits()
    
    print("\n🎉 Single Account System Demo Complete!")
    print("=" * 40)
    print("This demonstrates the simplified single Instagram account system.")
    print("In the web application, you can:")
    print("1. Create ONE Instagram account for reel watching")
    print("2. Add target accounts you want to monitor")
    print("3. Start automated reel watching and extraction")
    print("4. Monitor the entire process with one account")
    
    print("\n🎯 **Key Features**:")
    print("   • Single Instagram account per user")
    print("   • Dedicated for reel watching")
    print("   • Simple account management")
    print("   • Focused content extraction")
    print("   • Easy monitoring and control")