import re
import logging
from urllib.parse import urlparse
from textblob import TextBlob
from spellchecker import SpellChecker

FREE_EMAIL_DOMAINS = {
    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'rediffmail.com',
    'ymail.com', 'live.com', 'msn.com', 'aol.com', 'mail.com', 'protonmail.com',
    'tutanota.com', 'zoho.com', 'icloud.com', 'me.com', 'mac.com'
}

SUSPICIOUS_TLDS = {
    '.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.click', '.download',
    '.stream', '.science', '.date', '.faith', '.accountant', '.loan', '.win',
    '.cricket', '.review', '.trade', '.racing', '.party', '.bid', '.country'
}

SUSPICIOUS_DOMAIN_KEYWORDS = {
    'job', 'career', 'recruit', 'hiring', 'work', 'employment', 'vacancy',
    'jobsearch', 'quickjob', 'easyjob', 'fastjob', 'earnmoney', 'makemoney',
    'workfromhome', 'onlinejob', 'parttime', 'freelance'
}

SCAM_PHRASES = [
    ('no experience needed', 'Legitimate jobs typically require some qualifications or skills'),
    ('no skills required', 'All legitimate jobs require some form of skill or competency'),
    ('earn money fast', 'Get-rich-quick schemes are common scam indicators'),
    ('quick money', 'Promises of quick earnings are typically fraudulent'),
    ('easy money', 'Legitimate work requires effort and is rarely "easy"'),
    ('work from home guaranteed', 'Guarantees of remote work are often misleading'),
    ('immediate hiring', 'Instant hiring without proper process is suspicious'),
    ('urgent hiring', 'Excessive urgency can indicate pressure tactics'),
    ('no interview needed', 'Legitimate employers always conduct some form of screening'),
    ('direct selection', 'Skipping selection process is unprofessional'),
    ('advance payment required', 'Legitimate employers never ask for upfront fees'),
    ('registration fee', 'Job seekers should never pay registration fees'),
    ('training fee', 'Employers should provide free training, not charge for it'),
    ('security deposit', 'Legitimate jobs do not require security deposits from employees'),
    ('processing fee', 'Processing fees are red flags for job scams'),
    ('earn daily', 'Daily earning promises are often associated with scams'),
    ('high salary for freshers', 'Unrealistic salary promises for entry-level positions'),
    ('no background check', 'Legitimate employers conduct proper background verification'),
    ('copy paste job', 'Copy-paste jobs are commonly used in data entry scams'),
    ('data entry from home', 'Home-based data entry jobs are frequently fraudulent'),
    ('typing job', 'Online typing jobs are often scams targeting job seekers'),
    ('form filling job', 'Form filling jobs are commonly used in online scams'),
    ('email processing', 'Email processing jobs are typically fraudulent schemes'),
    ('ad posting job', 'Ad posting jobs are often pyramid or MLM schemes'),
    ('survey job', 'Online survey jobs rarely provide legitimate income'),
    ('click job', 'Paid-to-click jobs are often scams or provide minimal income'),
    ('captcha solving', 'Captcha solving jobs typically pay extremely low wages'),
    ('sms job', 'SMS-based jobs are often part of fraudulent schemes'),
    ('whatsapp job', 'WhatsApp-based job offers are commonly scams'),
    ('telegram job', 'Telegram job channels often promote fraudulent opportunities'),
    ('facebook job', 'Social media job offers are frequently unverified'),
    ('instagram job', 'Instagram job promotions are often misleading'),
    ('youtube job', 'YouTube-promoted jobs are frequently scams'),
    ('tiktok job', 'TikTok job offers are often unverified or fraudulent'),
    ('mobile job', 'Mobile-only jobs without proper company backing are suspicious'),
    ('android job', 'Platform-specific job claims without verification are suspicious'),
    ('iphone job', 'Device-specific job requirements are often misleading'),
    ('part time guaranteed', 'Guarantees of part-time work are often false promises'),
    ('flexible timing guaranteed', 'Guaranteed flexibility without requirements is suspicious'),
    ('weekend job guaranteed', 'Weekend job guarantees without screening are suspicious'),
    ('student job easy', 'Easy jobs specifically targeting students are often scams'),
    ('housewife job', 'Jobs specifically targeting housewives are often exploitative'),
    ('retired person job', 'Jobs targeting specific demographics can be predatory'),
    ('disabled person job', 'Targeting vulnerable populations is a common scam tactic'),
    ('unemployed guaranteed job', 'Guaranteed employment without qualifications is unrealistic'),
    ('100% job guarantee', 'No legitimate employer can guarantee 100% job placement'),
    ('money back guarantee', 'Money back guarantees in job offers are red flags'),
    ('risk free job', 'No job is completely risk-free, such claims are misleading'),
    ('government approved', 'False government endorsements are common in scams'),
    ('ministry approved', 'Fake government approvals are used to gain credibility'),
    ('iso certified company', 'False certifications are often claimed by scam companies'),
    ('international company', 'Vague international company claims without verification'),
    ('multinational opportunity', 'Unverified multinational claims are often false'),
    ('global company hiring', 'Global hiring claims without proper company details'),
    ('fortune 500 company', 'False Fortune 500 affiliations are common lies'),
    ('startup opportunity', 'Vague startup opportunities without clear details'),
    ('unicorn company', 'False unicorn company affiliations to attract candidates'),
    ('funded startup', 'Unverified funding claims are often false'),
    ('ipo bound company', 'False IPO claims to create urgency and credibility'),
    ('pre ipo opportunity', 'Pre-IPO job claims are often misleading'),
    ('equity offered', 'Unverified equity offers in job postings are suspicious'),
    ('stock options guaranteed', 'Stock option guarantees without proper documentation'),
    ('profit sharing guaranteed', 'Profit sharing promises without proper contracts'),
    ('bonus guaranteed', 'Guaranteed bonuses without performance metrics are suspicious'),
    ('incentive guaranteed', 'Guaranteed incentives without clear terms are red flags')
]


SALARY_RANGES = {
    'fresher': {
        'monthly_min': 15000, 'monthly_max': 50000,
        'annual_min': 180000, 'annual_max': 600000,  # 1.8 - 6 LPA
        'hourly_min': 100, 'hourly_max': 500,
        'daily_min': 500, 'daily_max': 2000,
        'weekly_min': 3500, 'weekly_max': 12000,
        'ctc_lpa_min': 2.0, 'ctc_lpa_max': 8.0
    },
    'mid_level': {
        'monthly_min': 40000, 'monthly_max': 120000,
        'annual_min': 480000, 'annual_max': 1440000,  # 4.8 - 14.4 LPA
        'hourly_min': 300, 'hourly_max': 1000,
        'daily_min': 1500, 'daily_max': 5000,
        'weekly_min': 10000, 'weekly_max': 30000,
        'ctc_lpa_min': 6.0, 'ctc_lpa_max': 18.0
    },
    'senior': {
        'monthly_min': 80000, 'monthly_max': 300000,
        'annual_min': 960000, 'annual_max': 3600000,  # 9.6 - 36 LPA
        'hourly_min': 600, 'hourly_max': 2500,
        'daily_min': 3000, 'daily_max': 12000,
        'weekly_min': 20000, 'weekly_max': 75000,
        'ctc_lpa_min': 12.0, 'ctc_lpa_max': 50.0
    }
}

def clean_text(text):

    if not text:
        return ""
    
    text = text.lower().strip()
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\-\@]', ' ', text)
    
    return text

def extract_domains(contact_info):

    if not contact_info:
        return []
    
    domains = []
    
    # Extract email domains
    email_pattern = r'\b[\w\.-]+@([\w\.-]+\.\w+)\b'
    email_matches = re.findall(email_pattern, contact_info.lower())
    domains.extend(email_matches)
    
    # Extract URL domains
    url_pattern = r'https?://([\w\.-]+\.\w+)'
    url_matches = re.findall(url_pattern, contact_info.lower())
    domains.extend(url_matches)
    
    # Extract domains from plain text (like company.com)
    domain_pattern = r'\b([\w-]+\.(?:com|org|net|edu|gov|mil|int|co\.in|in|us|uk|ca|au|de|fr|jp|cn|ru|br|mx|es|it|nl|se|no|dk|fi|pl|cz|hu|ro|bg|hr|si|sk|lt|lv|ee|gr|pt|ie|at|ch|be|lu|is|mt|cy|tk|ml|ga|cf|gq|xyz|top|click|download|stream|science|date|faith|accountant|loan|win|cricket|review|trade|racing|party|bid|country))\b'
    plain_domains = re.findall(domain_pattern, contact_info.lower())
    domains.extend(plain_domains)
    
    return list(set(domains))  # Remove duplicates

def check_dummy_domains(contact_info):
    """
    DOMAIN VALIDATION:
    Checks for suspicious domain characteristics
    """
    issues = set()
    reasons = set()
    
    if not contact_info:
        return issues, reasons
    
    domains = extract_domains(contact_info)
    
    for domain in domains:
        domain_lower = domain.lower()
        
        # Check for free email domains
        if domain_lower in FREE_EMAIL_DOMAINS:
            issues.add('free_email_domain')
            reasons.add(f'Use of free email domain: {domain}')
        
        # Check for suspicious TLDs
        for tld in SUSPICIOUS_TLDS:
            if domain_lower.endswith(tld):
                issues.add('suspicious_tld')
                reasons.add(f'Suspicious domain extension: {domain}')
                break
        
        # Check for suspicious keywords in domain
        for keyword in SUSPICIOUS_DOMAIN_KEYWORDS:
            if keyword in domain_lower:
                issues.add('suspicious_domain_keywords')
                reasons.add(f'Suspicious domain with job-related keywords: {domain}')
                break
        
        # Check for very short domains (less than 4 characters before TLD)
        domain_parts = domain_lower.split('.')
        if len(domain_parts) >= 2 and len(domain_parts[0]) < 4:
            issues.add('short_domain')
            reasons.add(f'Suspiciously short domain name: {domain}')
    
    return issues, reasons

def check_scam_phrases(job_data):
    """
    ENHANCED SCAM PHRASE DETECTION:
    Searches for red-flag phrases in job posting content with improved detection
    """
    issues = set()
    reasons = set()
    
    # Collect all text fields
    job_title = job_data.get('job_title', '')
    job_description = job_data.get('job_description', '')
    requirements = job_data.get('requirements', '')
    benefits = job_data.get('benefits', '')
    
    # Combine and clean text
    combined_text = clean_text(f"{job_title} {job_description} {requirements} {benefits}")
    
    # Enhanced scam keywords with dynamic detection
    ENHANCED_SCAM_KEYWORDS = [
        # Direct scam indicators
        ('fake', 'Direct mention of "fake" indicates potential scam content'),
        ('scam', 'Direct mention of "scam" indicates potential fraudulent content'),
        ('fraud', 'Direct mention of "fraud" indicates potential illegal activity'),
        ('cheat', 'Direct mention of "cheat" indicates potential dishonest practices'),
        
        # Urgency and pressure tactics
        ('urgent', 'Urgent language creates pressure and is common in scams'),
        ('immediate join', 'Immediate joining requirements are pressure tactics'),
        ('immediate hiring', 'Immediate hiring without proper process is suspicious'),
        ('immediate start', 'Immediate start requirements are often scam indicators'),
        ('join today', 'Same-day joining requirements are unrealistic'),
        ('start today', 'Same-day start requirements are unrealistic'),
        ('limited vacancy', 'Limited vacancy claims create false urgency'),
        ('only few seats', 'Limited seats claims create artificial scarcity'),
        ('hurry up', 'Hurry up language is a pressure tactic'),
        ('act fast', 'Act fast language creates unnecessary urgency'),
        ('limited time', 'Limited time offers are pressure tactics'),
        ('offer expires', 'Expiring offers create false urgency'),
        
        # Unrealistic promises
        ('guaranteed job', 'Job guarantees without proper process are unrealistic'),
        ('100% guarantee', '100% guarantees are unrealistic promises'),
        ('no rejection', 'No rejection promises are unrealistic'),
        ('everyone selected', 'Universal selection claims are false'),
        ('all will be hired', 'Universal hiring claims are unrealistic'),
        
        # Financial red flags
        ('advance payment', 'Advance payments from job seekers are scam indicators'),
        ('registration fee', 'Registration fees are red flags in job postings'),
        ('processing fee', 'Processing fees should never be charged to applicants'),
        ('security deposit', 'Security deposits from employees are inappropriate'),
        ('training fee', 'Training fees should be covered by legitimate employers'),
        ('admin fee', 'Administrative fees are red flags'),
        ('form fee', 'Form fees are inappropriate charges'),
        ('verification fee', 'Verification fees are scam indicators'),
        
        # Work-from-home scams
        ('work from home guaranteed', 'Guaranteed remote work is often misleading'),
        ('home based job guaranteed', 'Guaranteed home-based work is suspicious'),
        ('no office work', 'No office work claims can be misleading'),
        ('only mobile work', 'Mobile-only work claims are often false'),
        ('whatsapp job', 'WhatsApp-based jobs are commonly scams'),
        ('telegram work', 'Telegram-based work is often fraudulent'),
        
        # Skill/experience red flags
        ('no experience needed', 'No experience requirements are often unrealistic'),
        ('no skills required', 'No skills requirements are suspicious'),
        ('no qualification needed', 'No qualification requirements are red flags'),
        ('anyone can do', 'Anyone can do claims are often false'),
        ('very easy work', 'Very easy work claims are suspicious'),
        ('simple copy paste', 'Copy-paste job claims are often scams'),
        
        # Communication red flags
        ('no interview needed', 'No interview processes are unprofessional'),
        ('direct selection', 'Direct selection without process is suspicious'),
        ('selection guaranteed', 'Selection guarantees are unrealistic'),
        ('no questions asked', 'No questions asked policies are red flags')
    ]
    
    # Check for enhanced scam keywords
    detected_keywords = []
    for keyword, reason in ENHANCED_SCAM_KEYWORDS:
        if keyword.lower() in combined_text.lower():
            issue_key = f'scam_keyword_{keyword.replace(" ", "_").replace("/", "_")}'
            issues.add(issue_key)
            reasons.add(f'Detected scam keyword: "{keyword}". {reason}')
            detected_keywords.append(keyword)
    
    # Check for original scam phrases (keep existing logic)
    for phrase, reason in SCAM_PHRASES:
        if phrase in combined_text:
            issue_key = f'suspicious_phrase_{phrase.replace(" ", "_")}'
            issues.add(issue_key)    
            reasons.add(f'Found suspicious phrase: "{phrase}". {reason}')
    
    # Check for excessive exclamation marks (unprofessional tone)
    exclamation_count = combined_text.count('!')
    if exclamation_count > 5:
        issues.add('excessive_exclamation')
        reasons.add(f'Excessive use of exclamation marks ({exclamation_count}) indicates unprofessional communication')
    
    # Check for excessive capitalization
    if len(combined_text) > 0:
        caps_ratio = sum(1 for c in combined_text if c.isupper()) / len(combined_text)
        if caps_ratio > 0.3:
            issues.add('excessive_capitalization')
            reasons.add('Excessive capitalization suggests unprofessional or spam content')
    
    # Enhanced pattern detection
    # Check for suspicious number patterns (like fake phone numbers)
    suspicious_numbers = re.findall(r'\b(?:1234567890|9876543210|0000000000|1111111111|9999999999)\b', combined_text)
    if suspicious_numbers:
        issues.add('fake_contact_numbers')
        reasons.add('Detected potentially fake contact numbers')
    
    # Check for repeated words (sign of poor quality content)
    words = combined_text.split()
    word_count = {}
    for word in words:
        if len(word) > 3:  # Only check words longer than 3 characters
            word_count[word.lower()] = word_count.get(word.lower(), 0) + 1
    
    repeated_words = [word for word, count in word_count.items() if count > 5]
    if repeated_words:
        issues.add('excessive_word_repetition')
        reasons.add(f'Excessive repetition of words: {", ".join(repeated_words[:3])}')
    
    return issues, reasons

def enhanced_spelling_grammar_check(text):
    """
    Enhanced spelling and grammar checking with better error detection
    """
    issues = set()
    reasons = set()
    
    if not text or len(text.strip()) < 20:
        return issues, reasons
    
    try:
        # Spelling check with improved accuracy
        spell = SpellChecker()
        # Extract words, excluding common abbreviations and technical terms
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())  # Only words 3+ characters
        
        if words and len(words) > 10:  # Only check if there are enough words
            # Filter out common technical terms and abbreviations
            common_terms = {
                'covid', 'api', 'sql', 'html', 'css', 'javascript', 'python', 'java',
                'android', 'ios', 'app', 'tech', 'startup', 'saas', 'crm', 'erp',
                'linkedin', 'facebook', 'instagram', 'whatsapp', 'gmail', 'email',
                'internship', 'freelance', 'parttime', 'fulltime', 'wfh', 'bpo', 'kpo'
            }
            
            filtered_words = [word for word in words if word not in common_terms]
            
            if filtered_words:
                misspelled = spell.unknown(filtered_words)
                error_rate = len(misspelled) / len(filtered_words)
                
                if error_rate > 0.15:  # More than 15% spelling errors
                    issues.add('high_spelling_errors')
                    reasons.add(f'High spelling error rate ({error_rate:.1%}) suggests unprofessional content')
                elif error_rate > 0.08:  # More than 8% spelling errors
                    issues.add('moderate_spelling_errors')
                    reasons.add(f'Moderate spelling error rate ({error_rate:.1%}) indicates poor quality')
        
        # Enhanced grammar checking
        sentences = re.split(r'[.!?]+', text)
        valid_sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
        
        if valid_sentences:
            # Check for very short sentences (might indicate poor grammar)
            short_sentences = [s for s in valid_sentences if len(s.split()) < 4]
            if len(short_sentences) / len(valid_sentences) > 0.4:
                issues.add('poor_sentence_structure')
                reasons.add('Many very short sentences suggest poor grammar or rushed writing')
            
            # Check for missing punctuation
            no_punctuation = [s for s in valid_sentences if not re.search(r'[.!?]$', s.strip())]
            if len(no_punctuation) / len(valid_sentences) > 0.3:
                issues.add('missing_punctuation')
                reasons.add('Missing punctuation suggests poor writing quality')
            
            # Check for run-on sentences (very long sentences)
            long_sentences = [s for s in valid_sentences if len(s.split()) > 30]
            if long_sentences:
                issues.add('run_on_sentences')
                reasons.add('Very long sentences suggest poor writing structure')
    
    except Exception as e:
        logging.warning(f"Enhanced spelling/grammar check failed: {e}")
    
    return issues, reasons



def determine_experience_level(required_experience):
    """
    Helper function to determine experience level from text
    """
    if not required_experience:
        return 'fresher'
    
    exp_text = clean_text(required_experience)
    
    # Keywords for different experience levels
    fresher_keywords = ['fresher', 'entry', 'graduate', '0 year', 'no experience', 'beginner', 'trainee']
    senior_keywords = ['senior', 'lead', 'manager', 'director', '5+ year', '6+ year', '7+ year', '8+ year', 'experienced', 'expert']
    
    for keyword in fresher_keywords:
        if keyword in exp_text:
            return 'fresher'
    
    for keyword in senior_keywords:
        if keyword in exp_text:
            return 'senior'
    
    # Check for numeric experience mentions
    years_match = re.search(r'(\d+)\s*(?:to|-)\s*(\d+)\s*year', exp_text)
    if years_match:
        min_years = int(years_match.group(1))
        if min_years >= 5:
            return 'senior'
        elif min_years >= 2:
            return 'mid_level'
        else:
            return 'fresher'
    
    # Single year mention
    year_match = re.search(r'(\d+)\s*year', exp_text)
    if year_match:
        years = int(year_match.group(1))
        if years >= 5:
            return 'senior'
        elif years >= 2:
            return 'mid_level'
        else:
            return 'fresher'
    
    return 'mid_level'  # Default assumption

def parse_salary_info(salary_info):
    """
    Helper function to parse salary information and extract numeric values
    """
    if not salary_info:
        return []
    
    salary_text = clean_text(salary_info)
    
    # Extract all numeric values (including decimals and with commas)
    numeric_pattern = r'[\d,]+\.?\d*'
    numbers = re.findall(numeric_pattern, salary_text)
    
    parsed_salaries = []
    for num in numbers:
        try:
            # Remove commas and convert to float
            value = float(num.replace(',', ''))
            parsed_salaries.append(value)
        except ValueError:
            continue
    
    return parsed_salaries


def check_red_flag_density(job_data):
    """
    Check the density of red flags to determine overall risk level
    """
    issues = set()
    reasons = set()
    
    # Collect all text fields
    job_title = job_data.get('job_title', '')
    job_description = job_data.get('job_description', '')
    requirements = job_data.get('requirements', '')
    benefits = job_data.get('benefits', '')
    
    combined_text = clean_text(f"{job_title} {job_description} {requirements} {benefits}")
    
    # Count different types of red flags
    red_flag_categories = {
        'urgency_flags': 0,
        'payment_flags': 0,
        'unrealistic_flags': 0,
        'communication_flags': 0,
        'quality_flags': 0
    }
    
    # Urgency red flags
    urgency_terms = ['urgent', 'immediate', 'hurry', 'fast', 'quick', 'asap', 'today', 'now']
    red_flag_categories['urgency_flags'] = sum(1 for term in urgency_terms if term in combined_text.lower())
    
    # Payment red flags
    payment_terms = ['fee', 'payment', 'deposit', 'advance', 'money', 'pay', 'charge', 'cost']
    red_flag_categories['payment_flags'] = sum(1 for term in payment_terms if term in combined_text.lower())
    
    # Unrealistic promise flags
    unrealistic_terms = ['guarantee', 'easy', 'simple', 'no experience', 'anyone', 'everyone', '100%']
    red_flag_categories['unrealistic_flags'] = sum(1 for term in unrealistic_terms if term in combined_text.lower())
    
    # Communication red flags
    comm_terms = ['whatsapp', 'telegram', 'sms', 'call now', 'contact immediately']
    red_flag_categories['communication_flags'] = sum(1 for term in comm_terms if term in combined_text.lower())
    
    # Quality red flags
    if combined_text.count('!') > 3:
        red_flag_categories['quality_flags'] += 1
    if len(combined_text) > 0 and sum(1 for c in combined_text if c.isupper()) / len(combined_text) > 0.2:
        red_flag_categories['quality_flags'] += 1
    
    # Calculate total red flag score
    total_flags = sum(red_flag_categories.values())
    active_categories = sum(1 for count in red_flag_categories.values() if count > 0)
    
    if total_flags >= 8 or active_categories >= 4:
        issues.add('high_red_flag_density')
        reasons.add(f'High concentration of red flags detected (Total: {total_flags}, Categories: {active_categories})')
    elif total_flags >= 5 or active_categories >= 3:
        issues.add('moderate_red_flag_density')
        reasons.add(f'Moderate concentration of red flags detected (Total: {total_flags}, Categories: {active_categories})')
    
    return issues, reasons

def check_salary_range(job_data):
    """
    SALARY VALIDATION:
    Validates salary ranges against realistic expectations
    """
    issues = set()
    reasons = set()
    
    salary_info = job_data.get('salary_info_raw', '')
    required_experience = job_data.get('required_experience', '')
    
    if not salary_info:
        return issues, reasons
    
    # Determine experience level
    exp_level = determine_experience_level(required_experience)
    salary_ranges = SALARY_RANGES[exp_level]
    
    # Parse salary values
    salary_values = parse_salary_info(salary_info)
    
    if not salary_values:
        return issues, reasons
    
    salary_text = clean_text(salary_info)
    
    # Check each salary value against appropriate ranges
    for salary in salary_values:
        # Check different salary types
        if any(term in salary_text for term in ['per day', 'daily', '/day']):
            if salary < salary_ranges['daily_min'] or salary > salary_ranges['daily_max']:
                issues.add('unrealistic_daily_salary')
                reasons.add(f'Unrealistic daily salary: ₹{salary:,.0f} for {exp_level} level (expected: ₹{salary_ranges["daily_min"]:,} - ₹{salary_ranges["daily_max"]:,})')
        
        elif any(term in salary_text for term in ['per week', 'weekly', '/week']):
            if salary < salary_ranges['weekly_min'] or salary > salary_ranges['weekly_max']:
                issues.add('unrealistic_weekly_salary')
                reasons.add(f'Unrealistic weekly salary: ₹{salary:,.0f} for {exp_level} level (expected: ₹{salary_ranges["weekly_min"]:,} - ₹{salary_ranges["weekly_max"]:,})')
        
        elif any(term in salary_text for term in ['per month', 'monthly', '/month', 'pm']):
            if salary < salary_ranges['monthly_min'] or salary > salary_ranges['monthly_max']:
                issues.add('unrealistic_monthly_salary')
                reasons.add(f'Unrealistic monthly salary: ₹{salary:,.0f} for {exp_level} level (expected: ₹{salary_ranges["monthly_min"]:,} - ₹{salary_ranges["monthly_max"]:,})')
        
        elif any(term in salary_text for term in ['per hour', 'hourly', '/hour', '/hr']):
            if salary < salary_ranges['hourly_min'] or salary > salary_ranges['hourly_max']:
                issues.add('unrealistic_hourly_salary')
                reasons.add(f'Unrealistic hourly rate: ₹{salary:,.0f} for {exp_level} level (expected: ₹{salary_ranges["hourly_min"]:,} - ₹{salary_ranges["hourly_max"]:,})')
        
        elif any(term in salary_text for term in ['lpa', 'per annum', 'annually', 'yearly', '/year']):
            # Handle LPA (Lakhs Per Annum)
            if 'lpa' in salary_text:
                lpa_value = salary
                annual_value = salary * 100000  # Convert LPA to actual amount
                if lpa_value < salary_ranges['ctc_lpa_min'] or lpa_value > salary_ranges['ctc_lpa_max']:
                    issues.add('unrealistic_annual_salary')
                    reasons.add(f'Unrealistic annual salary: {lpa_value} LPA for {exp_level} level (expected: {salary_ranges["ctc_lpa_min"]} - {salary_ranges["ctc_lpa_max"]} LPA)')
            else:
                if salary < salary_ranges['annual_min'] or salary > salary_ranges['annual_max']:
                    issues.add('unrealistic_annual_salary')
                    reasons.add(f'Unrealistic annual salary: ₹{salary:,.0f} for {exp_level} level (expected: ₹{salary_ranges["annual_min"]:,} - ₹{salary_ranges["annual_max"]:,})')
        
        elif any(term in salary_text for term in ['ctc', 'cost to company']):
            # Assume CTC values are in LPA if less than 100, otherwise in actual rupees
            if salary < 100:  # Likely LPA
                if salary < salary_ranges['ctc_lpa_min'] or salary > salary_ranges['ctc_lpa_max']:
                    issues.add('unrealistic_ctc')
                    reasons.add(f'Unrealistic CTC: {salary} LPA for {exp_level} level (expected: {salary_ranges["ctc_lpa_min"]} - {salary_ranges["ctc_lpa_max"]} LPA)')
            else:  # Actual amount
                if salary < salary_ranges['annual_min'] or salary > salary_ranges['annual_max']:
                    issues.add('unrealistic_ctc')
                    reasons.add(f'Unrealistic CTC: ₹{salary:,.0f} for {exp_level} level (expected: ₹{salary_ranges["annual_min"]:,} - ₹{salary_ranges["annual_max"]:,})')
        
        else:
            # No specific time period mentioned - try to infer from value range
            if salary < 1000:  # Likely hourly
                if salary < salary_ranges['hourly_min'] or salary > salary_ranges['hourly_max']:
                    issues.add('unclear_salary_range')
                    reasons.add(f'Unclear salary specification: ₹{salary:,.0f} (please specify time period)')
            elif salary < 10000:  # Likely daily
                if salary < salary_ranges['daily_min'] or salary > salary_ranges['daily_max']:
                    issues.add('unclear_salary_range')
                    reasons.add(f'Unclear salary specification: ₹{salary:,.0f} (please specify time period)')
            elif salary < 200000:  # Likely monthly
                if salary < salary_ranges['monthly_min'] or salary > salary_ranges['monthly_max']:
                    issues.add('unclear_salary_range')
                    reasons.add(f'Unclear salary specification: ₹{salary:,.0f} (please specify time period)')
            else:  # Likely annual
                if salary < salary_ranges['annual_min'] or salary > salary_ranges['annual_max']:
                    issues.add('unclear_salary_range')
                    reasons.add(f'Unclear salary specification: ₹{salary:,.0f} (please specify time period)')
    
    return issues, reasons

def detect_scam_job(job_data):
    """
    SCAM DETECTION CONTROLLER:
    Main function that orchestrates all validation checks
    """
    all_issues = set()
    all_reasons = set()
    
    # Get contact information
    contact_info = job_data.get('application_link_or_email', '') or job_data.get('company_website', '')
    
    # 1. Domain validation
    domain_issues, domain_reasons = check_dummy_domains(contact_info)
    all_issues.update(domain_issues)
    all_reasons.update(domain_reasons)
    
    # 2. Scam phrase detection
    phrase_issues, phrase_reasons = check_scam_phrases(job_data)
    all_issues.update(phrase_issues)
    all_reasons.update(phrase_reasons)
    
    # 3. Salary validation
    salary_issues, salary_reasons = check_salary_range(job_data)
    all_issues.update(salary_issues)
    all_reasons.update(salary_reasons)
    
    # 4. Additional checks
    
    # Check for missing company information
    company_name = job_data.get('company_name', '').strip()
    if not company_name or len(company_name) < 3:
        all_issues.add('missing_company_info')
        all_reasons.add('Missing or insufficient company information')
    
    # Check remote job without location
    remote_status = job_data.get('remote_status', '').lower()
    job_location = job_data.get('job_location', '').strip()
    if 'remote' in remote_status and not job_location:
        all_issues.add('remote_no_location')
        all_reasons.add('Remote job without company location specified')
    
    # Check for unrealistic response time claims
    response_time = job_data.get('response_time_claimed', '').lower()
    if any(term in response_time for term in ['immediate', 'within 24 hours', 'urgent', 'instant']):
        all_issues.add('unrealistic_response_time')
        all_reasons.add('Unrealistically quick response time promised')
    
    # Check for payment requests from applicants
    all_text = ' '.join([
        job_data.get('job_title', ''),
        job_data.get('job_description', ''),
        job_data.get('requirements', ''),
        job_data.get('benefits', '')
    ]).lower()
    
    payment_keywords = ['registration fee', 'processing fee', 'advance payment', 'security deposit', 'training fee']
    for keyword in payment_keywords:
        if keyword in all_text:
            all_issues.add('payment_request')
            all_reasons.add('Job posting mentions payment or fees from applicants')
            break
    
    # Determine experience level for context
    required_experience = job_data.get('required_experience', '')
    experience_level = determine_experience_level(required_experience)
    
    # Determine if it's a scam based on number of issues
    # More than 2 distinct issues indicate high probability of scam
    is_scam = len(all_issues) >= 3
    
    return {
        'is_scam': is_scam,
        'issues': list(all_issues),
        'reasons': list(all_reasons),
        'experience_level': experience_level,
        'total_issues': len(all_issues)
    }

# Additional utility functions for enhanced detection

def check_grammar_and_spelling(text):
    """
    Additional check for grammar and spelling quality
    """
    issues = set()
    reasons = set()
    
    if not text or len(text.strip()) < 50:
        return issues, reasons
    
    try:
        # Check spelling using spellchecker
        spell = SpellChecker()
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        if words:
            misspelled = spell.unknown(words)
            error_rate = len(misspelled) / len(words)
            
            if error_rate > 0.15:  # More than 15% spelling errors
                issues.add('poor_spelling')
                reasons.add(f'High spelling error rate ({error_rate:.1%}) suggests unprofessional content')
        
        # Check for grammar using TextBlob
        blob = TextBlob(text)
        sentences = blob.sentences
        
        if len(sentences) > 0:
            # Check for very short sentences (might indicate poor grammar)
            short_sentences = [s for s in sentences if len(s.words) < 4]
            if len(short_sentences) / len(sentences) > 0.3:
                issues.add('poor_grammar')
                reasons.add('Many very short sentences suggest poor grammar or rushed writing')
    
    except Exception as e:
        logging.warning(f"Grammar/spelling check failed: {e}")
    
    return issues, reasons

def enhanced_scam_detection(job_data):
    """
    Enhanced version with improved scam detection and red flag analysis
    """
    # Get basic scam detection results
    basic_results = detect_scam_job(job_data)
    
    # Add enhanced spelling and grammar checks
    all_text = ' '.join([
        job_data.get('job_title', ''),
        job_data.get('job_description', ''),
        job_data.get('requirements', ''),
        job_data.get('benefits', '')
    ])
    
    # Enhanced spelling and grammar check
    spelling_issues, spelling_reasons = enhanced_spelling_grammar_check(all_text)
    
    # Red flag density check
    density_issues, density_reasons = check_red_flag_density(job_data)
    
    # Combine all results
    all_issues = set(basic_results['issues'])
    all_reasons = set(basic_results['reasons'])
    
    all_issues.update(spelling_issues)
    all_reasons.update(spelling_reasons)
    
    all_issues.update(density_issues)
    all_reasons.update(density_reasons)
    
    # Enhanced scam determination logic
    # Count different types of critical issues
    critical_issues = [
        issue for issue in all_issues 
        if any(keyword in issue for keyword in [
            'scam_keyword', 'fake_contact', 'high_red_flag_density', 
            'payment_request', 'high_spelling_errors', 'unrealistic_'
        ])
    ]
    
    # Determine if it's a scam with improved logic
    # More than 2 critical issues OR more than 4 total issues indicates high probability of scam
    is_scam = len(critical_issues) >= 2 or len(all_issues) >= 5 or basic_results['is_scam']
    
    # Calculate confidence score based on issue severity
    confidence_score = min(100, len(critical_issues) * 35 + len(all_issues) * 15)
    
    return {
        'is_scam': is_scam,
        'issues': list(all_issues),
        'reasons': list(all_reasons),
        'experience_level': basic_results['experience_level'],
        'total_issues': len(all_issues),
        'critical_issues': len(critical_issues),
        'confidence_score': confidence_score
    }