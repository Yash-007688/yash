#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import create_catchy_thumbnail, save_thumbnail
import time

def test_thumbnail_generation():
    print("🎨 Testing EPIC Thumbnail Generator...")
    
    # Test titles
    test_titles = [
        "INSANE Hindi Comedy That Will Make You CRY! 😂",
        "EPIC Gaming Moment You Won't Believe! 🎮",
        "OMG This Vlog Will BLOW YOUR MIND! 🔥",
        "CRAZY Prank That Went Too Far! 😱"
    ]
    
    styles = ["gaming", "vlog", "default"]
    
    for i, title in enumerate(test_titles):
        style = styles[i % len(styles)]
        print(f"\n🎯 Creating {style} thumbnail: {title}")
        
        try:
            # Create thumbnail
            thumbnail_img = create_catchy_thumbnail(title, style)
            
            # Save thumbnail
            filename = f"test_thumbnail_{style}_{i}.jpg"
            thumbnail_path = save_thumbnail(thumbnail_img, filename)
            
            print(f"✅ Successfully created: {thumbnail_path}")
            
        except Exception as e:
            print(f"❌ Error creating thumbnail: {e}")
    
    print("\n🎉 Thumbnail generation test completed!")
    print("📁 Check the 'static/thumbnails/' folder for generated images")

if __name__ == "__main__":
    test_thumbnail_generation()