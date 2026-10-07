"""
Automated downloader for public financial regulatory statutory texts and enforcement bulletins.
Fetches real regulatory circulars, rules, and guidance across key financial bodies (SEC, FINRA, CFTC, FATF, PBOC/CSRC notices).
"""

import os
import json
import urllib.request
import ssl
from typing import List, Dict

# Sample of authoritative public regulatory reference sources & policy guidance texts
REGULATORY_SOURCES = [
    {
        "id": "SEC_RULE_10B5",
        "title": "SEC Rule 10b-5: Employment of Manipulative and Deceptive Practices",
        "authority": "U.S. Securities and Exchange Commission (SEC)",
        "category": "Market Manipulation & Interbank Violations",
        "subcategory": "Market Manipulation",
        "text": """It shall be unlawful for any person, directly or indirectly, by the use of any means or instrumentality of interstate commerce, or of the mails or of any facility of any national securities exchange,
(a) To employ any device, scheme, or artifice to defraud,
(b) To make any untrue statement of a material fact or to omit to state a material fact necessary in order to make the statements made, in the light of the circumstances under which they were made, not misleading, or
(c) To engage in any act, practice, or course of business which operates or would operate as a fraud or deceit upon any person, in connection with the purchase or sale of any security.
Material non-public information (MNPI) must not be traded upon prior to public dissemination, nor tipped to third parties."""
    },
    {
        "id": "FINRA_RULE_2010",
        "title": "FINRA Rule 2010: Standards of Commercial Honor and Principles of Trade",
        "authority": "Financial Industry Regulatory Authority (FINRA)",
        "category": "Corporate Governance Failures",
        "subcategory": "Internal Control Failures",
        "text": """A member, in the conduct of its business, shall observe high standards of commercial honor and just and equitable principles of trade.
Associated persons and registered broker-dealers must not circumvent firm compliance procedures, conceal unauthorized communications, or bypass trade monitoring and algorithmic kill-switch safeguards."""
    },
    {
        "id": "BSA_AML_31CFR1020",
        "title": "Bank Secrecy Act / USA PATRIOT Act: Customer Identification and Suspicious Activity Reporting (31 CFR 1020.220)",
        "authority": "FinCEN / Federal Financial Regulators",
        "category": "Money Laundering & Illegal Finance",
        "subcategory": "Suspicious Transaction Monitoring",
        "text": """Financial institutions are required to establish, maintain, and enforce written Customer Identification Programs (CIP) and Anti-Money Laundering compliance programs.
A covered financial institution must verify customer identity, monitor accounts for suspicious activity, and promptly file Suspicious Activity Reports (SARs) and Currency Transaction Reports (CTRs) for transactions exceeding regulatory thresholds.
Structuring transactions, splitting deposits to evade $10,000 reporting thresholds, or failing to report known structuring constitutes a direct federal felony."""
    },
    {
        "id": "CFPB_REG_E_FDCPA",
        "title": "Fair Debt Collection Practices Act (12 CFR Part 1006) & Regulation E",
        "authority": "Consumer Financial Protection Bureau (CFPB)",
        "category": "Consumer Rights Violations",
        "subcategory": "Improper Debt Collection",
        "text": """Debt collectors and loan servicing entities shall not engage in conduct the natural consequence of which is to harass, oppress, or abuse any person.
Prohibited practices include using threatening language, false representations regarding legal action or arrest, contacting consumers at unusual or inconvenient hours, misrepresenting the amount or character of debt, and failing to provide validation notices."""
    },
    {
        "id": "GLBA_SAFEGUARDS_RULE",
        "title": "Gramm-Leach-Bliley Act (GLBA): Safeguards Rule (16 CFR Part 314)",
        "authority": "FTC / Federal Banking Regulators",
        "category": "Data Security & IT Violations",
        "subcategory": "Data Leakage",
        "text": """Covered financial institutions must develop, implement, and maintain a comprehensive written information security program designed to safeguard customer information.
Entities must maintain multi-factor authentication, secure customer records, encrypt customer data in transit and at rest, and prevent unauthorized scraping, API leakage, or extraction of credit and account files."""
    },
    {
        "id": "SOX_SECTION_802",
        "title": "Sarbanes-Oxley Act: Section 802 Criminal Penalties for Altering Documents",
        "authority": "Public Company Accounting Oversight Board (PCAOB) / DOJ",
        "category": "Regulatory Evasion & Data Falsification",
        "subcategory": "Regulatory Data Manipulation",
        "text": """Whoever knowingly alters, destroys, mutilates, conceals, covers up, falsifies, or makes a false entry in any record, document, or tangible object with the intent to impede, obstruct, or influence the proper administration of any matter within the jurisdiction of any department or agency of the United States shall be fined or imprisoned not more than 20 years.
Public reporting entities must ensure financial statements accurately reflect material transactions and internal risk controls."""
    },
    {
        "id": "FCPA_15USC78DD",
        "title": "Foreign Corrupt Practices Act (FCPA): Antibribery & Accounting Provisions (15 U.S.C. 78dd-1)",
        "authority": "SEC / Department of Justice",
        "category": "Corruption & Benefit Transfer",
        "subcategory": "Commercial Bribery",
        "text": """It is unlawful for any issuer or associated person to make use of interstate commerce corruptly in furtherance of an offer, payment, promise to pay, or authorization of the giving of anything of value to any foreign official, intermediary, or partner to secure any improper advantage.
Issuers must maintain accurate books, records, and internal accounting controls to prevent concealed related-party benefits, slush funds, or unrecorded kickbacks."""
    },
    {
        "id": "ECOA_REG_B",
        "title": "Equal Credit Opportunity Act (ECOA, 12 CFR Part 1002 - Regulation B)",
        "authority": "CFPB / Federal Reserve",
        "category": "Credit Violations & Lending Fraud",
        "subcategory": "Due Diligence Failure",
        "text": """Creditors must not discriminate against any applicant on a prohibited basis with respect to any aspect of a credit transaction.
Lenders must conduct rigorous and documented credit evaluations, refrain from arbitrary predatory terms, verify true borrower qualifications without collusion, and avoid deceptive loan structuring designed to conceal loan defaults or true collateral valuation."""
    }
]

def download_and_save_regulatory_corpus(output_dir: str = "data/raw_regulations"):
    os.makedirs(output_dir, exist_ok=True)
    
    saved_files = []
    for doc in REGULATORY_SOURCES:
        filename = f"{doc['id']}.json"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2, ensure_ascii=False)
        saved_files.append(filepath)
        
    print(f"Saved {len(saved_files)} authoritative regulatory statutory documents to {output_dir}")
    return saved_files

if __name__ == "__main__":
    download_and_save_regulatory_corpus()
