import sqlite3
import os
import shutil

DATABASE = os.path.join('instance', 'scholarhub.db')
UPLOAD_FOLDER = os.path.join('instance', 'uploads')

def reset_database():
    if not os.path.exists(DATABASE):
        print("Database not found.")
        return

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    print("Clearing all tables...")
    
    # Clear tables dependent on others first
    tables_to_clear = ['documents', 'saved_scholarships', 'applications', 'users', 'scholarships', 'admins']
    
    for table in tables_to_clear:
        try:
            cursor.execute(f"DELETE FROM {table}")
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'") # Reset Auto Increment
            print(f" - Cleared {table}")
        except sqlite3.OperationalError as e:
            print(f" - Error clearing {table}: {e}")

    conn.commit()
    conn.close()
    print("Database tables cleared.")

def clear_uploads():
    if os.path.exists(UPLOAD_FOLDER):
        print("Clearing uploads folder...")
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
        print("Uploads folder cleared.")
    else:
        print("Uploads folder does not exist.")

if __name__ == '__main__':
    reset_database()
    clear_uploads()
    print("\nReset Complete! All data has been removed.")
    print("Restart your Flask app to recreate the default Admin account and initial scholarships.")
