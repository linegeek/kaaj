"""
Seed the database with 5 realistic equipment finance lenders,
their programs, and eligibility rules.

Run from the backend directory:
    python -m seed_data.seed
"""
from __future__ import annotations

import asyncio
import uuid

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

LENDERS = [
    {
        "name": "Apex Equipment Finance",
        "contact_email": "originations@apexef.com",
        "contact_phone": "800-555-0101",
        "notes": "Full-service equipment lender specializing in commercial and industrial equipment. Nationwide coverage with competitive rates for established businesses.",
        "programs": [
            {
                "name": "Standard Commercial Program",
                "description": "Primary program for established businesses with solid credit. Covers most commercial equipment categories.",
                "min_amount": 25000,
                "max_amount": 500000,
                "rules": [
                    {"rule_type": "MIN_CREDIT_SCORE", "label": "Minimum Personal Credit Score", "weight": 3.0, "parameters": {"min_score": 650}},
                    {"rule_type": "MAX_BANKRUPTCIES", "label": "No Prior Bankruptcies", "weight": 3.0, "parameters": {"max_count": 0}},
                    {"rule_type": "MIN_YEARS_IN_BUSINESS", "label": "Minimum 2 Years Operating", "weight": 2.0, "parameters": {"min_years": 2}},
                    {"rule_type": "MIN_LOAN_AMOUNT", "label": "Minimum Loan $25,000", "weight": 1.0, "parameters": {"min_amount": 25000}},
                    {"rule_type": "MAX_LOAN_AMOUNT", "label": "Maximum Loan $500,000", "weight": 1.0, "parameters": {"max_amount": 500000}},
                    {"rule_type": "MAX_TERM_MONTHS", "label": "Maximum 72-Month Term", "weight": 1.0, "parameters": {"max_months": 72}},
                    {"rule_type": "ALLOWED_EQUIPMENT_TYPES", "label": "Approved Equipment Categories", "weight": 2.0, "parameters": {"types": ["heavy_equipment", "trucks", "trailers", "construction", "manufacturing", "agricultural"]}},
                    {"rule_type": "MAX_EQUIPMENT_AGE_YRS", "label": "Equipment Under 10 Years", "weight": 1.5, "parameters": {"max_age_yrs": 10}},
                ],
            },
            {
                "name": "Credit-Flex Program",
                "description": "Designed for businesses with minor credit blemishes. Higher rates, shorter terms, smaller ticket sizes.",
                "min_amount": 10000,
                "max_amount": 150000,
                "rules": [
                    {"rule_type": "MIN_CREDIT_SCORE", "label": "Minimum Personal Credit Score", "weight": 3.0, "parameters": {"min_score": 580}},
                    {"rule_type": "MAX_BANKRUPTCIES", "label": "One Prior Bankruptcy Allowed", "weight": 2.0, "parameters": {"max_count": 1}},
                    {"rule_type": "MAX_DEROGATORY_MARKS", "label": "Max Derogatory Marks", "weight": 2.0, "parameters": {"max_count": 3}},
                    {"rule_type": "MIN_YEARS_IN_BUSINESS", "label": "Minimum 3 Years Operating", "weight": 2.0, "parameters": {"min_years": 3}},
                    {"rule_type": "MIN_ANNUAL_REVENUE", "label": "Minimum Annual Revenue", "weight": 1.5, "parameters": {"min_revenue": 150000}},
                    {"rule_type": "MAX_LOAN_AMOUNT", "label": "Maximum Loan $150,000", "weight": 1.0, "parameters": {"max_amount": 150000}},
                    {"rule_type": "MAX_TERM_MONTHS", "label": "Maximum 48-Month Term", "weight": 1.0, "parameters": {"max_months": 48}},
                    {"rule_type": "MIN_DOWN_PAYMENT_PCT", "label": "Minimum 10% Down Payment", "weight": 1.5, "parameters": {"min_pct": 10}},
                ],
            },
        ],
    },
    {
        "name": "Advantage Capital Partners",
        "contact_email": "deals@advantagecap.com",
        "contact_phone": "800-555-0202",
        "notes": "Small business-focused lender with fast approvals. Specializes in serving LLCs and sole proprietors with streamlined documentation requirements.",
        "programs": [
            {
                "name": "Small Business Express",
                "description": "Fast-approval program for small businesses. Minimal documentation, decisions in 24 hours.",
                "min_amount": 5000,
                "max_amount": 100000,
                "rules": [
                    {"rule_type": "MIN_CREDIT_SCORE", "label": "Minimum Credit Score", "weight": 2.5, "parameters": {"min_score": 620}},
                    {"rule_type": "MIN_YEARS_IN_BUSINESS", "label": "Minimum 1 Year in Business", "weight": 1.5, "parameters": {"min_years": 1}},
                    {"rule_type": "ALLOWED_BUSINESS_TYPES", "label": "Eligible Business Structures", "weight": 1.5, "parameters": {"types": ["llc", "sole_proprietor", "partnership", "corporation", "s_corporation"]}},
                    {"rule_type": "MAX_LOAN_AMOUNT", "label": "Maximum Loan $100,000", "weight": 1.0, "parameters": {"max_amount": 100000}},
                    {"rule_type": "MAX_TERM_MONTHS", "label": "Maximum 60-Month Term", "weight": 1.0, "parameters": {"max_months": 60}},
                    {"rule_type": "EXCLUDED_STATES", "label": "Excluded States", "weight": 2.0, "parameters": {"states": ["ND", "VT", "WY"]}},
                ],
            },
            {
                "name": "Growth Capital Program",
                "description": "Larger ticket program for businesses ready to scale. Requires stronger credit profile and revenue history.",
                "min_amount": 100000,
                "max_amount": 750000,
                "rules": [
                    {"rule_type": "MIN_CREDIT_SCORE", "label": "Minimum Credit Score", "weight": 3.0, "parameters": {"min_score": 660}},
                    {"rule_type": "MAX_BANKRUPTCIES", "label": "No Bankruptcies", "weight": 3.0, "parameters": {"max_count": 0}},
                    {"rule_type": "MIN_YEARS_IN_BUSINESS", "label": "Minimum 3 Years in Business", "weight": 2.0, "parameters": {"min_years": 3}},
                    {"rule_type": "MIN_ANNUAL_REVENUE", "label": "Minimum $300K Annual Revenue", "weight": 2.0, "parameters": {"min_revenue": 300000}},
                    {"rule_type": "MIN_LOAN_AMOUNT", "label": "Minimum Loan $100,000", "weight": 1.0, "parameters": {"min_amount": 100000}},
                    {"rule_type": "MAX_LOAN_AMOUNT", "label": "Maximum Loan $750,000", "weight": 1.0, "parameters": {"max_amount": 750000}},
                    {"rule_type": "MAX_TERM_MONTHS", "label": "Maximum 84-Month Term", "weight": 1.0, "parameters": {"max_months": 84}},
                    {"rule_type": "MIN_OWNERSHIP_PCT", "label": "Guarantor Must Own 20%+", "weight": 1.5, "parameters": {"min_pct": 20}},
                ],
            },
        ],
    },
    {
        "name": "National Equipment Funding",
        "contact_email": "submissions@nef-funding.com",
        "contact_phone": "888-555-0303",
        "notes": "Nationwide lender with broad equipment appetite and SBSS-based underwriting. Strong in healthcare and manufacturing verticals.",
        "programs": [
            {
                "name": "Core Commercial Program",
                "description": "Broad nationwide program using FICO SBSS as primary credit indicator alongside personal credit.",
                "min_amount": 15000,
                "max_amount": 750000,
                "rules": [
                    {"rule_type": "MIN_CREDIT_SCORE", "label": "Minimum Personal FICO", "weight": 2.5, "parameters": {"min_score": 640}},
                    {"rule_type": "MIN_FICO_SBSS", "label": "Minimum FICO SBSS Score", "weight": 2.5, "parameters": {"min_score": 140}},
                    {"rule_type": "MAX_BANKRUPTCIES", "label": "No Bankruptcies in 7 Years", "weight": 3.0, "parameters": {"max_count": 0}},
                    {"rule_type": "MIN_YEARS_IN_BUSINESS", "label": "Minimum 2 Years Seasoning", "weight": 2.0, "parameters": {"min_years": 2}},
                    {"rule_type": "MAX_LOAN_AMOUNT", "label": "Maximum Loan $750,000", "weight": 1.0, "parameters": {"max_amount": 750000}},
                    {"rule_type": "MAX_TERM_MONTHS", "label": "Maximum 84-Month Term", "weight": 1.0, "parameters": {"max_months": 84}},
                    {"rule_type": "EXCLUDED_STATES", "label": "Restricted States", "weight": 2.0, "parameters": {"states": ["NV", "ND", "SD"]}},
                ],
            },
            {
                "name": "Healthcare Equipment Specialist",
                "description": "Dedicated program for medical and dental equipment. Higher loan limits and longer terms available.",
                "min_amount": 50000,
                "max_amount": 2000000,
                "rules": [
                    {"rule_type": "MIN_CREDIT_SCORE", "label": "Minimum Credit Score", "weight": 3.0, "parameters": {"min_score": 680}},
                    {"rule_type": "MIN_EXPERIAN_INTELLISCORE", "label": "Minimum Intelliscore", "weight": 2.0, "parameters": {"min_score": 60}},
                    {"rule_type": "MAX_BANKRUPTCIES", "label": "No Prior Bankruptcies", "weight": 3.0, "parameters": {"max_count": 0}},
                    {"rule_type": "ALLOWED_EQUIPMENT_TYPES", "label": "Medical Equipment Only", "weight": 3.0, "parameters": {"types": ["medical"]}},
                    {"rule_type": "MIN_YEARS_IN_BUSINESS", "label": "Minimum 2 Years Practice", "weight": 2.0, "parameters": {"min_years": 2}},
                    {"rule_type": "MIN_LOAN_AMOUNT", "label": "Minimum Loan $50,000", "weight": 1.0, "parameters": {"min_amount": 50000}},
                    {"rule_type": "MAX_LOAN_AMOUNT", "label": "Maximum Loan $2,000,000", "weight": 1.0, "parameters": {"max_amount": 2000000}},
                    {"rule_type": "MAX_TERM_MONTHS", "label": "Maximum 84-Month Term", "weight": 1.0, "parameters": {"max_months": 84}},
                ],
            },
        ],
    },
    {
        "name": "First Western Construction Finance",
        "contact_email": "heavy@firstwesterncf.com",
        "contact_phone": "877-555-0404",
        "notes": "Specialist lender for construction, heavy equipment, and commercial fleet. Deep expertise in yellow iron and over-the-road trucking.",
        "programs": [
            {
                "name": "Heavy Iron Program",
                "description": "For excavators, cranes, bulldozers, and other heavy construction equipment. Equipment must be in good working condition.",
                "min_amount": 50000,
                "max_amount": 1000000,
                "rules": [
                    {"rule_type": "MIN_CREDIT_SCORE", "label": "Minimum Credit Score", "weight": 2.5, "parameters": {"min_score": 660}},
                    {"rule_type": "MAX_BANKRUPTCIES", "label": "No Bankruptcies", "weight": 3.0, "parameters": {"max_count": 0}},
                    {"rule_type": "ALLOWED_EQUIPMENT_TYPES", "label": "Heavy and Construction Equipment Only", "weight": 3.0, "parameters": {"types": ["heavy_equipment", "construction"]}},
                    {"rule_type": "MAX_EQUIPMENT_AGE_YRS", "label": "Equipment 10 Years or Newer", "weight": 2.0, "parameters": {"max_age_yrs": 10}},
                    {"rule_type": "ALLOWED_EQUIPMENT_CONDITIONS", "label": "New or Used Equipment", "weight": 1.5, "parameters": {"conditions": ["new", "used"]}},
                    {"rule_type": "MIN_YEARS_IN_BUSINESS", "label": "Minimum 3 Years in Construction", "weight": 2.0, "parameters": {"min_years": 3}},
                    {"rule_type": "MIN_LOAN_AMOUNT", "label": "Minimum Loan $50,000", "weight": 1.0, "parameters": {"min_amount": 50000}},
                    {"rule_type": "MAX_LOAN_AMOUNT", "label": "Maximum Loan $1,000,000", "weight": 1.0, "parameters": {"max_amount": 1000000}},
                    {"rule_type": "MAX_TERM_MONTHS", "label": "Maximum 84-Month Term", "weight": 1.0, "parameters": {"max_months": 84}},
                    {"rule_type": "ALLOWED_STATES", "label": "Continental US Only", "weight": 2.0, "parameters": {"states": ["AL","AZ","AR","CA","CO","CT","DE","FL","GA","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"]}},
                ],
            },
            {
                "name": "Commercial Fleet Program",
                "description": "Class 6-8 trucks and semi-trailers. Single unit or fleet financing available.",
                "min_amount": 25000,
                "max_amount": 500000,
                "rules": [
                    {"rule_type": "MIN_CREDIT_SCORE", "label": "Minimum Credit Score", "weight": 2.5, "parameters": {"min_score": 640}},
                    {"rule_type": "ALLOWED_EQUIPMENT_TYPES", "label": "Trucks and Trailers Only", "weight": 3.0, "parameters": {"types": ["trucks", "trailers"]}},
                    {"rule_type": "MAX_EQUIPMENT_AGE_YRS", "label": "Trucks Under 5 Years Old", "weight": 2.0, "parameters": {"max_age_yrs": 5}},
                    {"rule_type": "MIN_YEARS_IN_BUSINESS", "label": "Minimum 2 Years Operating", "weight": 2.0, "parameters": {"min_years": 2}},
                    {"rule_type": "MIN_ANNUAL_REVENUE", "label": "Minimum $200K Annual Revenue", "weight": 1.5, "parameters": {"min_revenue": 200000}},
                    {"rule_type": "MAX_LOAN_AMOUNT", "label": "Maximum Loan $500,000", "weight": 1.0, "parameters": {"max_amount": 500000}},
                    {"rule_type": "MAX_TERM_MONTHS", "label": "Maximum 60-Month Term", "weight": 1.0, "parameters": {"max_months": 60}},
                    {"rule_type": "MIN_DOWN_PAYMENT_PCT", "label": "Minimum 10% Down", "weight": 1.5, "parameters": {"min_pct": 10}},
                ],
            },
        ],
    },
    {
        "name": "Balboa Capital",
        "contact_email": "vendors@balboacapital.com",
        "contact_phone": "800-555-0505",
        "notes": "Technology and soft-asset lender with strong vendor partner program. Specializes in office equipment, technology, and restaurant equipment.",
        "programs": [
            {
                "name": "Technology and Office Program",
                "description": "Computers, servers, phone systems, copiers, and other office/tech equipment. New and certified refurbished accepted.",
                "min_amount": 5000,
                "max_amount": 150000,
                "rules": [
                    {"rule_type": "MIN_CREDIT_SCORE", "label": "Minimum Credit Score", "weight": 2.5, "parameters": {"min_score": 620}},
                    {"rule_type": "ALLOWED_EQUIPMENT_TYPES", "label": "Technology and Office Equipment", "weight": 3.0, "parameters": {"types": ["technology", "office"]}},
                    {"rule_type": "MAX_EQUIPMENT_AGE_YRS", "label": "Equipment Under 3 Years", "weight": 2.0, "parameters": {"max_age_yrs": 3}},
                    {"rule_type": "ALLOWED_EQUIPMENT_CONDITIONS", "label": "New or Certified Refurbished", "weight": 2.0, "parameters": {"conditions": ["new", "refurbished"]}},
                    {"rule_type": "MIN_YEARS_IN_BUSINESS", "label": "Minimum 1 Year in Business", "weight": 1.5, "parameters": {"min_years": 1}},
                    {"rule_type": "MAX_LOAN_AMOUNT", "label": "Maximum Loan $150,000", "weight": 1.0, "parameters": {"max_amount": 150000}},
                    {"rule_type": "MAX_TERM_MONTHS", "label": "Maximum 60-Month Term", "weight": 1.0, "parameters": {"max_months": 60}},
                ],
            },
            {
                "name": "Restaurant Equipment Program",
                "description": "Commercial kitchen equipment, refrigeration, POS systems. Designed for food service businesses.",
                "min_amount": 10000,
                "max_amount": 300000,
                "rules": [
                    {"rule_type": "MIN_CREDIT_SCORE", "label": "Minimum Credit Score", "weight": 2.5, "parameters": {"min_score": 640}},
                    {"rule_type": "MAX_BANKRUPTCIES", "label": "No Prior Bankruptcies", "weight": 3.0, "parameters": {"max_count": 0}},
                    {"rule_type": "ALLOWED_EQUIPMENT_TYPES", "label": "Restaurant Equipment Only", "weight": 3.0, "parameters": {"types": ["restaurant"]}},
                    {"rule_type": "MIN_YEARS_IN_BUSINESS", "label": "Minimum 2 Years Operating", "weight": 2.0, "parameters": {"min_years": 2}},
                    {"rule_type": "MIN_ANNUAL_REVENUE", "label": "Minimum $120K Annual Revenue", "weight": 1.5, "parameters": {"min_revenue": 120000}},
                    {"rule_type": "MAX_LOAN_AMOUNT", "label": "Maximum Loan $300,000", "weight": 1.0, "parameters": {"max_amount": 300000}},
                    {"rule_type": "MAX_TERM_MONTHS", "label": "Maximum 84-Month Term", "weight": 1.0, "parameters": {"max_months": 84}},
                    {"rule_type": "MAX_DEROGATORY_MARKS", "label": "Max 2 Derogatory Marks", "weight": 1.5, "parameters": {"max_count": 2}},
                ],
            },
        ],
    },
]


async def seed(database_url: str) -> None:
    engine = create_async_engine(database_url, echo=False)
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Import models here so they're available after engine creation
    from app.models.lender import Lender, LenderProgram, EligibilityRule

    async with Session() as session:
        for lender_data in LENDERS:
            lender = Lender(
                id=uuid.uuid4(),
                name=lender_data["name"],
                contact_email=lender_data.get("contact_email"),
                contact_phone=lender_data.get("contact_phone"),
                notes=lender_data.get("notes"),
            )
            session.add(lender)
            await session.flush()

            for prog_data in lender_data["programs"]:
                program = LenderProgram(
                    id=uuid.uuid4(),
                    lender_id=lender.id,
                    name=prog_data["name"],
                    description=prog_data.get("description"),
                    min_amount=prog_data.get("min_amount"),
                    max_amount=prog_data.get("max_amount"),
                )
                session.add(program)
                await session.flush()

                for rule_data in prog_data["rules"]:
                    rule = EligibilityRule(
                        id=uuid.uuid4(),
                        program_id=program.id,
                        rule_type=rule_data["rule_type"],
                        label=rule_data.get("label"),
                        weight=rule_data.get("weight", 1.0),
                        parameters=rule_data.get("parameters", {}),
                    )
                    session.add(rule)

        await session.commit()
        print(f"Seeded {len(LENDERS)} lenders successfully.")

    await engine.dispose()


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()
    db_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://kaaj:kaaj@localhost:5432/kaaj")
    asyncio.run(seed(db_url))
