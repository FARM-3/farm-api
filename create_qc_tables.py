"""
Temporary script to create production and processing QC tables
Run with: python create_qc_tables.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

from django.db import connection

def create_tables():
    with connection.cursor() as cursor:
        print("Creating production tables...")

        # Create production_harvests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS production_harvests (
                harvest_id VARCHAR(20) PRIMARY KEY,
                worker_name VARCHAR(100) NOT NULL,
                block_id VARCHAR(10) NOT NULL,
                weight_on_delivery NUMERIC(10, 2) NOT NULL,
                date_of_delivery DATE NOT NULL,
                amount_paid NUMERIC(10, 2) NOT NULL,
                paid_by VARCHAR(100) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );
        """)
        print("✓ Created production_harvests table")

        # Create production_block table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS production_block (
                block_id VARCHAR(50) PRIMARY KEY,
                no_of_trees INTEGER NOT NULL,
                date_planted DATE NOT NULL,
                type_of_coffee VARCHAR(100) NOT NULL,
                source_of_seedling VARCHAR(200) NOT NULL,
                type_of_seedling VARCHAR(200) NOT NULL,
                age_of_seedling INTEGER NOT NULL,
                fertilizers VARCHAR(255) DEFAULT 'Not Specified',
                fertilizer_names TEXT,
                use_pesticides VARCHAR(255) NOT NULL,
                pesticides_list TEXT,
                standard_practices VARCHAR(255) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                created_by_id BIGINT
            );
        """)
        print("✓ Created production_block table")

        # Create processing_ripeness table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processing_ripeness (
                harvest_id VARCHAR(20) PRIMARY KEY REFERENCES production_harvests(harvest_id) ON DELETE CASCADE,
                date DATE NOT NULL DEFAULT CURRENT_DATE,
                sample_size INTEGER NOT NULL DEFAULT 100 CHECK (sample_size >= 1),
                no_of_redcherry INTEGER NOT NULL CHECK (no_of_redcherry >= 0),
                ripeness_score NUMERIC(5, 2) NOT NULL CHECK (ripeness_score >= 0 AND ripeness_score <= 100),
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );
        """)
        print("✓ Created processing_ripeness table")

        # Create processing_floating table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processing_floating (
                grade_id VARCHAR(20) PRIMARY KEY,
                harvest_id VARCHAR(20) NOT NULL REFERENCES production_harvests(harvest_id) ON DELETE CASCADE,
                grade VARCHAR(50) NOT NULL,
                weight NUMERIC(10, 2) NOT NULL CHECK (weight >= 0),
                date DATE NOT NULL DEFAULT CURRENT_DATE,
                ripeness_score NUMERIC(5, 2) CHECK (ripeness_score >= 0 AND ripeness_score <= 100),
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );
        """)
        print("✓ Created processing_floating table")

        # Create indexes
        print("\nCreating indexes...")

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS processing_ripeness_date_idx ON processing_ripeness(date DESC);
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS processing_floating_date_idx ON processing_floating(date DESC);
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS processing_floating_harvest_idx ON processing_floating(harvest_id);
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS processing_floating_grade_idx ON processing_floating(grade);
        """)

        print("✓ Created indexes")

        print("\n✅ All tables created successfully!")
        print("\nNext steps:")
        print("1. Run: python manage.py migrate production --fake")
        print("2. Run: python manage.py migrate processing --fake")
        print("3. Verify with: python manage.py dbshell")

if __name__ == '__main__':
    try:
        create_tables()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNote: This script requires the production_harvests table to exist first.")
        print("If you get FK errors, create production_harvests table first.")
