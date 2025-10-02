#!/usr/bin/env python3
"""
Test script to validate Snowflake connection and failover group access.
Run this before starting the monitor to ensure everything is configured correctly.
"""

import os
import sys
import argparse
import snowflake.connector


def test_connection(account: str, user: str = None, password: str = None, 
                   authenticator: str = None):
    """Test connection to Snowflake account."""
    print(f"\n{'='*60}")
    print("Testing Snowflake Connection")
    print(f"{'='*60}\n")
    
    user = user or os.getenv('SNOWFLAKE_USER')
    password = password or os.getenv('SNOWFLAKE_PASSWORD')
    
    if not user:
        print("❌ ERROR: SNOWFLAKE_USER not set")
        return False
    
    if not password and not authenticator:
        print("❌ ERROR: SNOWFLAKE_PASSWORD not set (or use --authenticator)")
        return False
    
    try:
        print(f"Connecting to account: {account}")
        print(f"User: {user}")
        
        conn_params = {
            'account': account,
            'user': user,
        }
        
        if authenticator:
            conn_params['authenticator'] = authenticator
            print(f"Authenticator: {authenticator}")
        else:
            conn_params['password'] = password
        
        conn = snowflake.connector.connect(**conn_params)
        print("✅ Successfully connected to Snowflake\n")
        
        # Test SHOW FAILOVER GROUPS
        print("Testing SHOW FAILOVER GROUPS command...")
        cursor = conn.cursor()
        cursor.execute("SHOW FAILOVER GROUPS")
        
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        
        print(f"✅ Found {len(rows)} failover group(s)\n")
        
        if rows:
            print("Failover Groups:")
            print("-" * 60)
            for row in rows:
                fg_dict = dict(zip(columns, row))
                name = fg_dict.get('name', 'Unknown')
                schedule = fg_dict.get('replication_schedule', 'Not set')
                is_primary = fg_dict.get('is_primary', fg_dict.get('type', 'Unknown'))
                
                print(f"  Name: {name}")
                print(f"  Schedule: {schedule}")
                print(f"  Primary: {is_primary}")
                print("-" * 60)
        else:
            print("⚠️  WARNING: No failover groups found in this account")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_email_config():
    """Test email configuration."""
    print(f"\n{'='*60}")
    print("Testing Email Configuration")
    print(f"{'='*60}\n")
    
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    from_email = os.getenv('FROM_EMAIL')
    to_emails = os.getenv('TO_EMAILS')
    
    all_ok = True
    
    if smtp_server:
        print(f"✅ SMTP_SERVER: {smtp_server}")
    else:
        print("⚠️  SMTP_SERVER: Not set (email notifications disabled)")
        all_ok = False
    
    if smtp_user:
        print(f"✅ SMTP_USER: {smtp_user}")
    else:
        print("⚠️  SMTP_USER: Not set")
        all_ok = False
    
    if smtp_password:
        print(f"✅ SMTP_PASSWORD: {'*' * len(smtp_password)}")
    else:
        print("⚠️  SMTP_PASSWORD: Not set")
        all_ok = False
    
    if from_email:
        print(f"✅ FROM_EMAIL: {from_email}")
    else:
        print("⚠️  FROM_EMAIL: Not set")
        all_ok = False
    
    if to_emails:
        recipients = to_emails.split(',')
        print(f"✅ TO_EMAILS: {len(recipients)} recipient(s)")
        for email in recipients:
            print(f"    - {email.strip()}")
    else:
        print("⚠️  TO_EMAILS: Not set")
        all_ok = False
    
    if not all_ok:
        print("\n⚠️  Email notifications will be disabled without proper configuration")
    
    return all_ok


def test_log_file():
    """Test log file permissions."""
    print(f"\n{'='*60}")
    print("Testing Log File Permissions")
    print(f"{'='*60}\n")
    
    log_file = "/var/log/monitor_snowflake_replication.log"
    
    try:
        # Try to create/write to the log file
        with open(log_file, 'a') as f:
            f.write(f"Test write at {os.popen('date').read().strip()}\n")
        
        print(f"✅ Can write to {log_file}")
        return True
    except PermissionError:
        print(f"❌ ERROR: No write permission to {log_file}")
        print("\nRun these commands to fix:")
        print(f"  sudo touch {log_file}")
        print(f"  sudo chown $USER {log_file}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    """Main test function."""
    parser = argparse.ArgumentParser(
        description='Test Snowflake Replication Monitor setup'
    )
    parser.add_argument('account', help='Snowflake account name')
    parser.add_argument('--user', help='Snowflake username')
    parser.add_argument('--password', help='Snowflake password')
    parser.add_argument('--authenticator', help='Authentication method')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("Snowflake Replication Monitor - Setup Validation")
    print("="*60)
    
    # Run tests
    log_ok = test_log_file()
    conn_ok = test_connection(args.account, args.user, args.password, 
                              args.authenticator)
    email_ok = test_email_config()
    
    # Summary
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}\n")
    
    if log_ok:
        print("✅ Log file permissions: OK")
    else:
        print("❌ Log file permissions: FAILED")
    
    if conn_ok:
        print("✅ Snowflake connection: OK")
    else:
        print("❌ Snowflake connection: FAILED")
    
    if email_ok:
        print("✅ Email configuration: OK")
    else:
        print("⚠️  Email configuration: INCOMPLETE (optional)")
    
    if log_ok and conn_ok:
        print("\n✅ Ready to start monitoring!")
        print(f"\nRun: python monitor_snowflake_replication.py {args.account}")
    else:
        print("\n❌ Please fix the errors above before running the monitor")
        sys.exit(1)


if __name__ == '__main__':
    main()
