#!/usr/bin/env python3
"""
Example usage of the Image Classification and Organization Tool
"""

from image_classifier import ImageOrganizer, ClassificationConfig
import os


def organize_photos():
    """Example: Organize personal photos"""
    config = ClassificationConfig(
        source_directory="/Users/greatmaster/Pictures/Unsorted",
        target_base_directory="/Users/greatmaster/Desktop/automated/organized_images",
        model_name="qwen2.5vl",
        confidence_threshold=0.6,
        create_date_folders=True,
        organize_by_quality=True,
        backup_originals=True
    )
    
    organizer = ImageOrganizer(config)
    results = organizer.process_directory()
    organizer.save_classification_report()
    
    return results


def organize_screenshots():
    """Example: Organize screenshots separately"""
    config = ClassificationConfig(
        source_directory="/Users/greatmaster/Desktop/Screenshots",
        target_base_directory="/Users/greatmaster/Desktop/automated/organized_screenshots",
        model_name="qwen2.5vl",
        confidence_threshold=0.5,  # Lower threshold for screenshots
        create_date_folders=True,
        organize_by_quality=False,  # Don't organize screenshots by quality
        backup_originals=False
    )
    
    organizer = ImageOrganizer(config)
    results = organizer.process_directory()
    organizer.save_classification_report()
    
    return results


def cleanup_downloads():
    """Example: Clean up Downloads folder images"""
    config = ClassificationConfig(
        source_directory="/Users/greatmaster/Downloads",
        target_base_directory="/Users/greatmaster/Desktop/automated/sorted_downloads",
        model_name="qwen2.5vl",
        confidence_threshold=0.7,
        create_date_folders=False,
        organize_by_quality=True,
        backup_originals=True
    )
    
    organizer = ImageOrganizer(config)
    results = organizer.process_directory()
    organizer.save_classification_report()
    
    # Auto-delete low quality images in downloads
    organizer.delete_low_quality_images(dry_run=False)
    
    return results


def batch_process_multiple_directories():
    """Example: Process multiple directories"""
    directories = [
        "/Users/greatmaster/Pictures/Camera Roll",
        "/Users/greatmaster/Pictures/Screenshots",
        "/Users/greatmaster/Downloads"
    ]
    
    all_results = []
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"\nProcessing: {directory}")
            
            config = ClassificationConfig(
                source_directory=directory,
                target_base_directory=f"/Users/greatmaster/Desktop/automated/organized_{os.path.basename(directory)}",
                model_name="qwen2.5vl"
            )
            
            organizer = ImageOrganizer(config)
            results = organizer.process_directory()
            organizer.save_classification_report()
            
            all_results.append({
                'directory': directory,
                'results': results
            })
    
    return all_results


if __name__ == "__main__":
    # Choose which function to run
    print("Image Classification and Organization Tool")
    print("1. Organize personal photos")
    print("2. Organize screenshots")
    print("3. Clean up downloads")
    print("4. Batch process multiple directories")
    
    choice = input("Enter your choice (1-4): ").strip()
    
    if choice == "1":
        organize_photos()
    elif choice == "2":
        organize_screenshots()
    elif choice == "3":
        cleanup_downloads()
    elif choice == "4":
        batch_process_multiple_directories()
    else:
        print("Invalid choice")
